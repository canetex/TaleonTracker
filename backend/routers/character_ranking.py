from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta
from database import get_db
from models.character import Character
from models.character_history import CharacterHistory
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/ranking/experience")
async def get_experience_ranking(
    days: int = 30,
    limit: int = 20,
    world: str = None,
    db: Session = Depends(get_db)
):
    """
    Retorna ranking dos personagens com maior experiência histórica
    Complexidade: O(n*m) onde n é número de personagens e m é histórico médio
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days) if days > 0 else None
        
        # Query base para buscar experiência máxima por personagem
        query = db.query(
            Character.id,
            Character.name,
            Character.world,
            Character.vocation,
            func.max(CharacterHistory.experience).label('max_experience'),
            func.max(CharacterHistory.timestamp).label('last_update')
        ).join(
            CharacterHistory, Character.id == CharacterHistory.character_id
        )
        
        # Filtra por data se especificado
        if cutoff_date:
            query = query.filter(CharacterHistory.timestamp >= cutoff_date)
        
        # Filtra por mundo se especificado
        if world:
            world_lower = world.lower()
            if world_lower not in ['san', 'aura']:
                raise HTTPException(status_code=400, detail="Mundo inválido. Apenas 'san' e 'aura' são permitidos.")
            query = query.filter(Character.world == world_lower)
        else:
            # Filtra apenas mundos válidos
            query = query.filter(Character.world.in_(['san', 'aura']))
        
        # Agrupa por personagem e ordena por experiência máxima
        results = query.group_by(
            Character.id,
            Character.name,
            Character.world,
            Character.vocation
        ).order_by(
            desc('max_experience')
        ).limit(limit).all()
        
        # Formata resultado
        ranking = []
        for idx, row in enumerate(results, 1):
            ranking.append({
                "rank": idx,
                "character_id": row.id,
                "name": row.name,
                "world": row.world,
                "vocation": row.vocation,
                "max_experience": float(row.max_experience) if row.max_experience else 0,
                "last_update": row.last_update.isoformat() if row.last_update else None
            })
        
        return ranking
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar ranking de experiência: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

