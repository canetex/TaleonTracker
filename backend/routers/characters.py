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
    latest_history = sorted_history[0] if sorted_history else None
    previous_history = sorted_history[1] if len(sorted_history) > 1 else None
    
    # Se não há histórico, tenta buscar do character_snapshots
    experience = 0
    level = character.level
    outfit = getattr(character, 'outfit', '') or ''
    
    if latest_history:
        experience = latest_history.experience
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
    
    # Calcula experiência diária se houver histórico anterior
    daily_experience = 0
    if latest_history and previous_history:
        # Diferença entre a experiência mais recente e a anterior
        daily_experience = latest_history.experience - previous_history.experience
        if daily_experience < 0:
            daily_experience = 0
    elif latest_history:
        # Se não há histórico anterior, usa o valor salvo
        daily_experience = latest_history.daily_experience or 0
    elif db and sorted_history:
        # Se há apenas um registro, não há como calcular diária
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
                "experience": h.experience,
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
            
            # Cria dicionário de datas existentes
            history_dict = {}
            for h in history:
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
                # Se days=0, usa a primeira data do histórico como início
                first_date = min(history_dict.keys()) if history_dict else datetime.utcnow().date()
                start_date = first_date
            
            today = datetime.utcnow().date()
            current_date = start_date
            filled_history = []
            
            # Busca último histórico antes de start_date para usar como base
            last_level = character.level or 0
            last_experience = 0
            if history:
                # Usa o primeiro registro como base inicial
                first_h = history[0]
                last_level = first_h.get('level', character.level or 0)
                last_experience = first_h.get('experience', 0)
            
            while current_date <= today:
                if current_date in history_dict:
                    # Usa o valor existente
                    h = history_dict[current_date]
                    last_level = h.get('level', last_level)
                    last_experience = h.get('experience', last_experience)
                    filled_history.append(h)
                else:
                    # Cria registro com experiência 0 quando não houver dados
                    # Level mantém do último registro conhecido, mas experiência é 0
                    filled_history.append({
                        'id': 0,
                        'character_id': character_id,
                        'level': last_level,  # Mantém level do último registro
                        'experience': 0,  # Experiência sempre 0 quando não houver dados
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
