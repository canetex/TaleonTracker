from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List
from datetime import datetime, timedelta
from database import get_db
from models.server_stats import ServerStats
from models.character import Character
from models.character_history import CharacterHistory
from schemas.server_stats import ServerStatsResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/worlds/{world}/exp-history", response_model=List[ServerStatsResponse])
async def get_world_exp_history(world: str, days: int = 30, db: Session = Depends(get_db)):
    """
    Obtém histórico de EXP total de um mundo específico
    Se não houver dados em server_stats, calcula dinamicamente
    Preenche dias faltantes com valores do dia anterior (ou 0 se for o primeiro)
    Complexidade: O(n*m) onde n é número de personagens e m é histórico médio
    """
    try:
        # Normaliza o nome do mundo
        world_lower = world.lower()
        if world_lower not in ['san', 'aura']:
            raise HTTPException(status_code=400, detail="Mundo inválido. Apenas 'san' e 'aura' são permitidos.")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days) if days > 0 else None
        today = datetime.utcnow().date()
        
        # Busca estatísticas da tabela server_stats
        query = db.query(ServerStats).filter(ServerStats.world == world_lower)
        if cutoff_date:
            query = query.filter(ServerStats.timestamp >= cutoff_date)
        stats = query.order_by(ServerStats.timestamp.asc()).all()
        
        # Se não houver dados, calcula dinamicamente a partir do histórico
        if not stats:
            # Busca personagens do mundo
            characters = db.query(Character).filter(Character.world == world_lower).all()
            
            if not characters:
                return []
            
            # Busca todas as datas únicas no período
            dates_query = db.query(
                func.date(CharacterHistory.timestamp).label('date')
            ).join(Character).filter(
                Character.world == world_lower
            )
            
            if cutoff_date:
                dates_query = dates_query.filter(CharacterHistory.timestamp >= cutoff_date)
            
            unique_dates = [row.date for row in dates_query.distinct().order_by(func.date(CharacterHistory.timestamp).asc()).all()]
            
            # Para cada data, calcula a experiência total (soma da experiência mais recente de cada personagem até aquela data)
            stats = []
            for date in unique_dates:
                # Busca a experiência mais recente de cada personagem até esta data
                # Filtra apenas registros reais (id > 0)
                subquery = db.query(
                    CharacterHistory.character_id,
                    func.max(CharacterHistory.timestamp).label('max_timestamp')
                ).join(Character).filter(
                    Character.world == world_lower,
                    func.date(CharacterHistory.timestamp) <= date,
                    CharacterHistory.id > 0  # Apenas registros reais
                ).group_by(CharacterHistory.character_id).subquery()
                
                # Busca a experiência correspondente a cada timestamp máximo
                # Usa total_experience quando disponível, senão usa experience
                # Filtra apenas registros reais (id > 0)
                exp_query = db.query(
                    func.sum(
                        case(
                            (CharacterHistory.total_experience.isnot(None), CharacterHistory.total_experience),
                            else_=CharacterHistory.experience
                        )
                    ).label('total_exp'),
                    func.count(func.distinct(CharacterHistory.character_id)).label('active_chars')
                ).join(
                    subquery,
                    (CharacterHistory.character_id == subquery.c.character_id) &
                    (CharacterHistory.timestamp == subquery.c.max_timestamp)
                ).filter(CharacterHistory.id > 0)  # Apenas registros reais
                
                result = exp_query.first()
                total_exp = float(result.total_exp) if result and result.total_exp else 0
                active_chars = int(result.active_chars) if result and result.active_chars else 0
                
                stats.append(ServerStats(
                    id=0,
                    world=world_lower,
                    total_experience=total_exp,
                    active_characters=active_chars,
                    timestamp=datetime.combine(date, datetime.min.time())
                ))
        
        # Preenche dias faltantes e garante que vai até hoje
        stats_dict = {stat.timestamp.date(): stat for stat in stats}
        filled_stats = []
        
        start_date = cutoff_date.date() if cutoff_date else (today - timedelta(days=30))
        current_date = start_date
        last_total_exp = 0
        last_active_chars = 0
        
        while current_date <= today:
            if current_date in stats_dict:
                # Usa o valor existente
                stat = stats_dict[current_date]
                last_total_exp = stat.total_experience
                last_active_chars = stat.active_characters
                filled_stats.append(stat)
            else:
                # Cria registro com valores do dia anterior (ou 0 se for o primeiro)
                filled_stats.append(ServerStats(
                    id=0,
                    world=world_lower,
                    total_experience=last_total_exp,  # Mantém o mesmo valor do dia anterior
                    active_characters=last_active_chars,  # Mantém o mesmo valor do dia anterior
                    timestamp=datetime.combine(current_date, datetime.min.time())
                ))
            
            current_date += timedelta(days=1)
        
        return filled_stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de EXP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/worlds/{world}/active-history", response_model=List[ServerStatsResponse])
async def get_world_active_history(world: str, days: int = 30, db: Session = Depends(get_db)):
    """
    Obtém histórico de personagens ativos de um mundo específico
    Se não houver dados em server_stats, calcula dinamicamente
    Preenche dias faltantes com valores do dia anterior (ou 0 se for o primeiro)
    Complexidade: O(n*m) onde n é número de personagens e m é histórico médio
    """
    try:
        # Normaliza o nome do mundo
        world_lower = world.lower()
        if world_lower not in ['san', 'aura']:
            raise HTTPException(status_code=400, detail="Mundo inválido. Apenas 'san' e 'aura' são permitidos.")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days) if days > 0 else None
        today = datetime.utcnow().date()
        
        # Busca estatísticas da tabela server_stats
        query = db.query(ServerStats).filter(ServerStats.world == world_lower)
        if cutoff_date:
            query = query.filter(ServerStats.timestamp >= cutoff_date)
        stats = query.order_by(ServerStats.timestamp.asc()).all()
        
        # Se não houver dados, calcula dinamicamente a partir do histórico
        if not stats:
            # Busca personagens do mundo
            characters = db.query(Character).filter(Character.world == world_lower).all()
            
            if not characters:
                return []
            
            # Busca todas as datas únicas no período
            dates_query = db.query(
                func.date(CharacterHistory.timestamp).label('date')
            ).join(Character).filter(
                Character.world == world_lower
            )
            
            if cutoff_date:
                dates_query = dates_query.filter(CharacterHistory.timestamp >= cutoff_date)
            
            unique_dates = [row.date for row in dates_query.distinct().order_by(func.date(CharacterHistory.timestamp).asc()).all()]
            
            # Para cada data, calcula personagens ativos (únicos que tiveram atualização até aquela data)
            stats = []
            for date in unique_dates:
                # Busca personagens que tiveram atualização até esta data
                # Filtra apenas registros reais (id > 0)
                subquery = db.query(
                    CharacterHistory.character_id,
                    func.max(CharacterHistory.timestamp).label('max_timestamp')
                ).join(Character).filter(
                    Character.world == world_lower,
                    func.date(CharacterHistory.timestamp) <= date,
                    CharacterHistory.id > 0  # Apenas registros reais
                ).group_by(CharacterHistory.character_id).subquery()
                
                # Conta personagens únicos ativos
                # Usa total_experience quando disponível, senão usa experience
                # Filtra apenas registros reais (id > 0)
                active_query = db.query(
                    func.count(func.distinct(CharacterHistory.character_id)).label('active_chars'),
                    func.sum(
                        case(
                            (CharacterHistory.total_experience.isnot(None), CharacterHistory.total_experience),
                            else_=CharacterHistory.experience
                        )
                    ).label('total_exp')
                ).join(
                    subquery,
                    (CharacterHistory.character_id == subquery.c.character_id) &
                    (CharacterHistory.timestamp == subquery.c.max_timestamp)
                ).filter(CharacterHistory.id > 0)  # Apenas registros reais
                
                result = active_query.first()
                active_chars = int(result.active_chars) if result and result.active_chars else 0
                total_exp = float(result.total_exp) if result and result.total_exp else 0
                
                stats.append(ServerStats(
                    id=0,
                    world=world_lower,
                    total_experience=total_exp,
                    active_characters=active_chars,
                    timestamp=datetime.combine(date, datetime.min.time())
                ))
        
        # Preenche dias faltantes e garante que vai até hoje
        stats_dict = {stat.timestamp.date(): stat for stat in stats}
        filled_stats = []
        
        start_date = cutoff_date.date() if cutoff_date else (today - timedelta(days=30))
        current_date = start_date
        last_total_exp = 0
        last_active_chars = 0
        
        while current_date <= today:
            if current_date in stats_dict:
                # Usa o valor existente
                stat = stats_dict[current_date]
                last_total_exp = stat.total_experience
                last_active_chars = stat.active_characters
                filled_stats.append(stat)
            else:
                # Cria registro com valores do dia anterior (ou 0 se for o primeiro)
                filled_stats.append(ServerStats(
                    id=0,
                    world=world_lower,
                    total_experience=last_total_exp,  # Mantém o mesmo valor do dia anterior
                    active_characters=last_active_chars,  # Mantém o mesmo valor do dia anterior
                    timestamp=datetime.combine(current_date, datetime.min.time())
                ))
            
            current_date += timedelta(days=1)
        
        return filled_stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de ativos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/worlds/{world}/calculate-stats")
async def calculate_world_stats(world: str, db: Session = Depends(get_db)):
    """
    Calcula e salva estatísticas agregadas de um mundo
    Complexidade: O(n*m) onde n é número de personagens e m é histórico médio por personagem
    """
    try:
        # Busca todos os personagens do mundo
        characters = db.query(Character).filter(Character.world == world).all()
        
        if not characters:
            raise HTTPException(status_code=404, detail=f"Nenhum personagem encontrado para o mundo {world}")
        
        # Calcula EXP total e personagens ativos
        total_experience = 0
        active_characters = 0
        
        # O(n) - itera sobre personagens
        for character in characters:
            # Busca histórico mais recente (apenas registros reais)
            latest_history = db.query(CharacterHistory).filter(
                CharacterHistory.character_id == character.id,
                CharacterHistory.id > 0  # Apenas registros reais
            ).order_by(CharacterHistory.timestamp.desc()).first()
            
            if latest_history:
                # Usa total_experience quando disponível, senão usa experience
                exp_value = latest_history.total_experience if latest_history.total_experience is not None else latest_history.experience
                total_experience += exp_value if exp_value else 0
                # Considera ativo se teve atualização nos últimos 7 dias
                days_since_update = (datetime.utcnow() - latest_history.timestamp).days
                if days_since_update <= 7:
                    active_characters += 1
        
        # Cria novo registro de estatísticas
        stats = ServerStats(
            world=world,
            total_experience=total_experience,
            active_characters=active_characters,
            timestamp=datetime.utcnow()
        )
        
        db.add(stats)
        db.commit()
        db.refresh(stats)
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao calcular estatísticas: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/worlds", response_model=List[str])
async def get_available_worlds(db: Session = Depends(get_db)):
    """
    Retorna lista de mundos disponíveis (apenas san e aura)
    Complexidade: O(n) onde n é o número de personagens únicos
    """
    try:
        # Retorna apenas os mundos válidos
        valid_worlds = ['san', 'aura']
        # Verifica quais mundos têm personagens
        worlds = db.query(Character.world).distinct().all()
        existing_worlds = [w[0].lower() for w in worlds if w[0]]
        # Filtra apenas mundos válidos que existem
        available_worlds = [w for w in valid_worlds if w in existing_worlds]
        return available_worlds if available_worlds else valid_worlds
    except Exception as e:
        logger.error(f"Erro ao buscar mundos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/worlds/{world}/fill-missing-days")
async def fill_missing_days(world: str, days: int = 90, db: Session = Depends(get_db)):
    """
    Preenche dias faltantes na tabela server_stats para um mundo específico
    Para dias sem dados, cria registros com valores do dia anterior
    """
    try:
        from services.fill_missing_days import fill_missing_days_for_world
        from datetime import date, timedelta
        
        world_lower = world.lower()
        if world_lower not in ['san', 'aura']:
            raise HTTPException(status_code=400, detail="Mundo inválido. Apenas 'san' e 'aura' são permitidos.")
        
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        fill_missing_days_for_world(world_lower, db, start_date, end_date)
        
        return {"message": f"Dias faltantes preenchidos para {world_lower}", "days": days}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao preencher dias faltantes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

