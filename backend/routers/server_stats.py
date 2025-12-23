from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
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
    Complexidade: O(n*m) onde n é número de personagens e m é histórico médio
    """
    try:
        # Normaliza o nome do mundo
        world_lower = world.lower()
        if world_lower not in ['san', 'aura']:
            raise HTTPException(status_code=400, detail="Mundo inválido. Apenas 'san' e 'aura' são permitidos.")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days) if days > 0 else None
        
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
            
            # Agrupa histórico por data
            history_query = db.query(
                func.date(CharacterHistory.timestamp).label('date'),
                func.sum(CharacterHistory.experience).label('total_exp'),
                func.count(func.distinct(CharacterHistory.character_id)).label('active_chars')
            ).join(Character).filter(
                Character.world == world_lower
            )
            
            if cutoff_date:
                history_query = history_query.filter(CharacterHistory.timestamp >= cutoff_date)
            
            history_data = history_query.group_by(
                func.date(CharacterHistory.timestamp)
            ).order_by(
                func.date(CharacterHistory.timestamp).asc()
            ).all()
            
            # Converte para formato ServerStats
            stats = []
            for row in history_data:
                stats.append(ServerStats(
                    id=0,
                    world=world_lower,
                    total_experience=float(row.total_exp) if row.total_exp else 0,
                    active_characters=int(row.active_chars) if row.active_chars else 0,
                    timestamp=datetime.combine(row.date, datetime.min.time())
                ))
        
        return stats
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
    Complexidade: O(n*m) onde n é número de personagens e m é histórico médio
    """
    try:
        # Normaliza o nome do mundo
        world_lower = world.lower()
        if world_lower not in ['san', 'aura']:
            raise HTTPException(status_code=400, detail="Mundo inválido. Apenas 'san' e 'aura' são permitidos.")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days) if days > 0 else None
        
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
            
            # Agrupa histórico por data
            history_query = db.query(
                func.date(CharacterHistory.timestamp).label('date'),
                func.sum(CharacterHistory.experience).label('total_exp'),
                func.count(func.distinct(CharacterHistory.character_id)).label('active_chars')
            ).join(Character).filter(
                Character.world == world_lower
            )
            
            if cutoff_date:
                history_query = history_query.filter(CharacterHistory.timestamp >= cutoff_date)
            
            history_data = history_query.group_by(
                func.date(CharacterHistory.timestamp)
            ).order_by(
                func.date(CharacterHistory.timestamp).asc()
            ).all()
            
            # Converte para formato ServerStats
            stats = []
            for row in history_data:
                stats.append(ServerStats(
                    id=0,
                    world=world_lower,
                    total_experience=float(row.total_exp) if row.total_exp else 0,
                    active_characters=int(row.active_chars) if row.active_chars else 0,
                    timestamp=datetime.combine(row.date, datetime.min.time())
                ))
        
        return stats
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
            # Busca histórico mais recente
            latest_history = db.query(CharacterHistory).filter(
                CharacterHistory.character_id == character.id
            ).order_by(CharacterHistory.timestamp.desc()).first()
            
            if latest_history:
                total_experience += latest_history.experience
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

