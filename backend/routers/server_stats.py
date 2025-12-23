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
    Complexidade: O(n) onde n é o número de registros de histórico
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Busca estatísticas agregadas por data, ordenadas do mais antigo para o mais recente
        stats = db.query(ServerStats).filter(
            ServerStats.world == world,
            ServerStats.timestamp >= cutoff_date
        ).order_by(ServerStats.timestamp.asc()).all()
        
        return stats
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de EXP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/worlds/{world}/active-history", response_model=List[ServerStatsResponse])
async def get_world_active_history(world: str, days: int = 30, db: Session = Depends(get_db)):
    """
    Obtém histórico de personagens ativos de um mundo específico
    Complexidade: O(n) onde n é o número de registros de histórico
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Busca estatísticas agregadas por data, ordenadas do mais antigo para o mais recente
        stats = db.query(ServerStats).filter(
            ServerStats.world == world,
            ServerStats.timestamp >= cutoff_date
        ).order_by(ServerStats.timestamp.asc()).all()
        
        return stats
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
    Retorna lista de mundos disponíveis (excluindo Gaia)
    Complexidade: O(n) onde n é o número de personagens únicos
    """
    try:
        worlds = db.query(Character.world).distinct().all()
        # Filtra Gaia se existir
        available_worlds = [w[0] for w in worlds if w[0] and w[0].lower() != "gaia"]
        return available_worlds
    except Exception as e:
        logger.error(f"Erro ao buscar mundos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

