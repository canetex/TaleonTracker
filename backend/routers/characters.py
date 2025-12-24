from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, text
from typing import List, Dict, Any
from datetime import datetime, timedelta
from database import get_db, engine
from models.character import Character
from models.character_history import CharacterHistory
from schemas.character import CharacterCreate, CharacterResponse
from services.scraper import scrape_character_data, update_all_characters
from services.character_discovery import discover_and_add_characters
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

def enrich_character_response(character: Character, db: Session = None) -> Dict[str, Any]:
    """
    Enriquece a resposta do personagem com dados do histórico mais recente
    Se não houver histórico, busca dados de character_snapshots
    Complexidade: O(m) onde m é o tamanho do histórico
    """
    # Ordena o histórico por timestamp (mais recente primeiro)
    sorted_history = sorted(character.history, key=lambda h: h.timestamp, reverse=True) if character.history else []
    # Filtra apenas registros reais (id > 0) para pegar level e experience
    real_history = [h for h in sorted_history if h.id > 0]
    latest_history = real_history[0] if real_history else None
    previous_history = real_history[1] if len(real_history) > 1 else None
    
    # Se não há histórico, tenta buscar do character_snapshots
    experience = 0
    level = character.level
    outfit = getattr(character, 'outfit', '') or ''
    
    if latest_history:
        # Usa total_experience se disponível, senão usa experience, senão calcula baseado no level
        if latest_history.total_experience is not None:
            experience = latest_history.total_experience
        elif latest_history.experience:
            experience = latest_history.experience
        else:
            # Calcula baseado no level usando a tabela do Tibia
            from services.experience_lookup import get_experience_from_level_table
            experience = get_experience_from_level_table(latest_history.level)
        level = latest_history.level
    elif db:
        # Busca do character_snapshots
        try:
            result = db.execute(text("""
                SELECT experience, level, outfit_image_url 
                FROM character_snapshots 
                WHERE character_id = :char_id 
                ORDER BY scraped_at DESC 
                LIMIT 1
            """), {"char_id": character.id})
            row = result.fetchone()
            if row:
                experience = float(row[0]) if row[0] else 0
                level = row[1] if row[1] else character.level
                outfit = row[2] if row[2] else outfit
        except Exception as e:
            logger.warning(f"Erro ao buscar snapshot para {character.name}: {str(e)}")
    
    # Calcula experiência nas últimas 24 horas
    # Busca registros reais das últimas 24 horas
    from datetime import timedelta
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    
    daily_experience = 0
    real_history = [h for h in sorted_history if h.id > 0]  # Apenas registros reais
    
    if len(real_history) >= 1:
        # Busca o registro mais recente
        latest_real = real_history[0]
        latest_exp = latest_real.total_experience if latest_real.total_experience is not None else latest_real.experience
        
        # Busca o registro mais antigo dentro das últimas 24 horas
        # Procura do mais recente para o mais antigo
        previous_real = None
        for h in real_history[1:]:
            # Se o registro está dentro das últimas 24h, usa ele
            if h.timestamp >= last_24h:
                previous_real = h
            else:
                # Se passou das 24h, para a busca
                break
        
        # Se não encontrou registro nas últimas 24h, usa o registro anterior mais próximo
        if previous_real is None and len(real_history) > 1:
            previous_real = real_history[1]
        
        if previous_real:
            previous_exp = previous_real.total_experience if previous_real.total_experience is not None else previous_real.experience
            daily_experience = latest_exp - previous_exp
            # Permite valores negativos (perda por morte)
        else:
            # Se não há registro anterior, usa o valor salvo do daily_experience do registro mais recente
            daily_experience = latest_real.daily_experience or 0
    else:
        # Se não há registros reais, não há como calcular diária
        daily_experience = 0
    
    response = {
        "id": character.id,
        "name": character.name,
        "level": level,
        "vocation": character.vocation,
        "world": character.world,
        "guild": getattr(character, 'guild', '') or '',
        "outfit": outfit,
        "created_at": character.created_at,
        "updated_at": character.updated_at,
        "experience": experience,
        "daily_experience": daily_experience,
        "last_updated": latest_history.timestamp if latest_history else character.updated_at,
        "history": [
            {
                "id": h.id,
                "character_id": h.character_id,
                "level": h.level,
                "experience": h.total_experience if h.total_experience is not None else h.experience,
                "total_experience": h.total_experience,
                "daily_experience": h.daily_experience,
                "deaths": h.deaths,
                "timestamp": h.timestamp
            }
            for h in sorted_history
        ]
    }
    return response

@router.post("/", response_model=CharacterResponse)
async def create_character(character: CharacterCreate, db: Session = Depends(get_db)):
    try:
        # Verifica se o personagem já existe
        existing_character = db.query(Character).filter(Character.name == character.name).first()
        if existing_character:
            raise HTTPException(status_code=400, detail="Personagem já existe")

        # Cria o novo personagem
        db_character = Character(
            name=character.name,
            level=0,  # Será atualizado pelo scraper
            vocation="",  # Será atualizado pelo scraper
            world=""  # Será atualizado pelo scraper
        )
        db.add(db_character)
        db.commit()
        db.refresh(db_character)

        # Tenta obter os dados do personagem
        try:
            await scrape_character_data(character.name, db)
        except Exception as e:
            # Se falhar ao obter os dados, pelo menos o personagem foi criado
            logger.error(f"Erro ao obter dados do personagem: {str(e)}")

        db.refresh(db_character)
        # Recarrega com histórico
        db_character = db.query(Character).options(joinedload(Character.history)).filter(Character.id == db_character.id).first()
        return enrich_character_response(db_character, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar personagem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
@router.get("/")
async def list_characters(db: Session = Depends(get_db)):
    """
    Lista todos os personagens com dados enriquecidos do histórico
    Complexidade: O(n*m) onde n é número de personagens e m é histórico médio
    """
    characters = db.query(Character).options(joinedload(Character.history)).all()
    return [enrich_character_response(char, db) for char in characters]

@router.get("/{character_id}")
async def get_character(character_id: int, days: int = 0, db: Session = Depends(get_db)):
    """
    Obtém um personagem específico com dados enriquecidos
    days: filtra histórico pelos últimos N dias (0 = todos)
    Complexidade: O(m) onde m é o histórico do personagem
    """
    character = db.query(Character).options(joinedload(Character.history)).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Personagem não encontrado")
    
    # Se days > 0, filtra o histórico antes de enriquecer
    if days > 0:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        # Filtra histórico no Python (mais simples que fazer na query)
        character.history = [h for h in character.history if h.timestamp >= cutoff_date]
    
    response = enrich_character_response(character, db)
    
    # Preenche dias faltantes no histórico para garantir que vá até hoje
    # Sempre preenche, mesmo quando days=0 (usa o último registro como referência)
    if response.get('history'):
        history = response['history']
        if history:
            # Ordena por data
            history.sort(key=lambda h: h['timestamp'])
            
            # Separa registros reais (id > 0) dos preenchidos (id = 0)
            real_history = [h for h in history if h.get('id', 0) > 0]
            
            # Cria dicionário de datas existentes (apenas registros reais)
            history_dict = {}
            for h in real_history:
                # Converte timestamp para date
                try:
                    if isinstance(h['timestamp'], str):
                        date_key = datetime.fromisoformat(h['timestamp'].replace('Z', '+00:00')).date()
                    else:
                        date_key = h['timestamp'].date()
                    history_dict[date_key] = h
                except Exception as e:
                    logger.warning(f"Erro ao processar timestamp {h['timestamp']}: {str(e)}")
                    continue
            
            # Determina período para preencher
            if days > 0:
                start_date = datetime.utcnow().date() - timedelta(days=days)
            else:
                # Se days=0, usa a primeira data do histórico real como início
                first_date = min(history_dict.keys()) if history_dict else datetime.utcnow().date()
                start_date = first_date
            
            # Encontra a última data com registro real
            last_real_date = max(history_dict.keys()) if history_dict else None
            today = datetime.utcnow().date()
            
            # Só preenche até a última data real, não até hoje
            # Isso evita criar registros com experiência 0 que afetam os cálculos
            end_date = last_real_date if last_real_date else today
            
            current_date = start_date
            filled_history = []
            
            # Busca último histórico real para usar como base
            last_level = character.level or 0
            last_total_experience = None
            if real_history:
                # Usa o último registro real como base
                last_real = real_history[-1]
                last_level = last_real.get('level', character.level or 0)
                # Prefere total_experience, senão usa experience
                last_total_experience = last_real.get('total_experience')
                if last_total_experience is None:
                    last_total_experience = last_real.get('experience', 0)
            
            # Importa função para calcular experiência baseada no level
            from services.experience_lookup import get_experience_from_level_table
            
            while current_date <= end_date:
                if current_date in history_dict:
                    # Usa o valor existente (registro real)
                    h = history_dict[current_date]
                    last_level = h.get('level', last_level)
                    # Atualiza last_total_experience com total_experience ou experience
                    if h.get('total_experience') is not None:
                        last_total_experience = h.get('total_experience')
                    elif h.get('experience'):
                        last_total_experience = h.get('experience')
                    filled_history.append(h)
                else:
                    # Quando não houver dados, calcula experiência baseada no level do dia
                    # usando a tabela do Tibia
                    calculated_exp = get_experience_from_level_table(last_level)
                    filled_history.append({
                        'id': 0,
                        'character_id': character_id,
                        'level': last_level,  # Mantém level do último registro
                        'experience': calculated_exp,  # Calcula baseado no level usando tabela Tibia
                        'total_experience': calculated_exp,
                        'daily_experience': 0,  # 0 de experiência no dia
                        'deaths': 0,
                        'timestamp': datetime.combine(current_date, datetime.min.time()).isoformat()
                    })
                
                current_date += timedelta(days=1)
            
            response['history'] = filled_history
    
    return response

@router.post("/{character_id}/update", response_model=CharacterResponse)
async def update_character(character_id: int, db: Session = Depends(get_db)):
    try:
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise HTTPException(status_code=404, detail="Personagem não encontrado")
        
        logger.info(f"Atualizando personagem: {character.name}")
        
        if not await scrape_character_data(character.name, db, use_cache=True):
            logger.error(f"Falha ao atualizar dados do personagem {character.name}")
            raise HTTPException(status_code=500, detail="Erro ao atualizar dados do personagem")
        
        db.refresh(character)
        # Recarrega o histórico
        db.refresh(character)
        character = db.query(Character).options(joinedload(Character.history)).filter(Character.id == character_id).first()
        logger.info(f"Personagem {character.name} atualizado com sucesso")
        return enrich_character_response(character, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar personagem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{character_id}")
async def delete_character(character_id: int, db: Session = Depends(get_db)):
    try:
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise HTTPException(status_code=404, detail="Personagem não encontrado")
        
        logger.info(f"Excluindo personagem: {character.name}")
        db.delete(character)
        db.commit()
        logger.info(f"Personagem {character.name} excluído com sucesso")
        return {"message": "Personagem excluído com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir personagem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-all")
async def update_all_characters_endpoint():
    """
    Atualiza todos os personagens cadastrados.
    Executa o scraper completo para buscar as últimas atualizações.
    """
    try:
        import asyncio
        logger.info("Iniciando atualização completa de todos os personagens")
        # Executa em background para não bloquear a resposta
        asyncio.create_task(update_all_characters())
        return {"message": "Atualização de todos os personagens iniciada em background"}
    except Exception as e:
        logger.error(f"Erro ao iniciar atualização completa: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/discover")
async def discover_characters_endpoint(db: Session = Depends(get_db)):
    """
    Descobre e adiciona automaticamente personagens dos rankings e mortes do Taleon.
    Extrai personagens de:
    - Powergamers (Aura e San)
    - Deaths (Aura e San)
    """
    try:
        import asyncio
        logger.info("Iniciando descoberta de personagens")
        # Executa em background para não bloquear a resposta
        stats = await discover_and_add_characters(db)
        return {
            "message": "Descoberta de personagens concluída",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Erro ao descobrir personagens: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
