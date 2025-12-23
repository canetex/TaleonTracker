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
    type: str = "accumulated",
    db: Session = Depends(get_db)
):
    """
    Retorna ranking dos personagens com maior experiência histórica
    type: 'accumulated' (experiência acumulada no período) ou 'average' (experiência média no período)
    Complexidade: O(n*m) onde n é número de personagens e m é histórico médio
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days) if days > 0 else None
        
        # Filtra por mundo se especificado
        world_filter = None
        if world:
            world_lower = world.lower()
            if world_lower not in ['san', 'aura']:
                raise HTTPException(status_code=400, detail="Mundo inválido. Apenas 'san' e 'aura' são permitidos.")
            world_filter = world_lower
        else:
            world_filter = ['san', 'aura']
        
        if type == "accumulated":
            # Experiência acumulada: diferença entre primeira e última experiência no período
            subquery = db.query(
                CharacterHistory.character_id,
                func.min(CharacterHistory.experience).label('min_exp'),
                func.max(CharacterHistory.experience).label('max_exp')
            )
            
            if cutoff_date:
                subquery = subquery.filter(CharacterHistory.timestamp >= cutoff_date)
            
            subquery = subquery.group_by(CharacterHistory.character_id).subquery()
            
            query = db.query(
                Character.id,
                Character.name,
                Character.world,
                Character.vocation,
                (func.coalesce(subquery.c.max_exp, 0) - func.coalesce(subquery.c.min_exp, 0)).label('accumulated_experience'),
                func.max(CharacterHistory.timestamp).label('last_update')
            ).join(
                subquery, Character.id == subquery.c.character_id
            ).outerjoin(
                CharacterHistory, Character.id == CharacterHistory.character_id
            )
            
            if isinstance(world_filter, list):
                query = query.filter(Character.world.in_(world_filter))
            else:
                query = query.filter(Character.world == world_filter)
            
            if cutoff_date:
                query = query.filter(CharacterHistory.timestamp >= cutoff_date)
            
            results = query.group_by(
                Character.id,
                Character.name,
                Character.world,
                Character.vocation,
                subquery.c.min_exp,
                subquery.c.max_exp
            ).order_by(
                desc('accumulated_experience')
            ).limit(limit).all()
            
            ranking = []
            for idx, row in enumerate(results, 1):
                ranking.append({
                    "rank": idx,
                    "character_id": row.id,
                    "name": row.name,
                    "world": row.world,
                    "vocation": row.vocation,
                    "accumulated_experience": float(row.accumulated_experience) if row.accumulated_experience else 0,
                    "max_experience": float(row.accumulated_experience) if row.accumulated_experience else 0,
                    "last_update": row.last_update.isoformat() if row.last_update else None
                })
        else:
            # Experiência média: média de todas as experiências no período
            query = db.query(
                Character.id,
                Character.name,
                Character.world,
                Character.vocation,
                func.avg(CharacterHistory.experience).label('average_experience'),
                func.max(CharacterHistory.timestamp).label('last_update')
            ).join(
                CharacterHistory, Character.id == CharacterHistory.character_id
            )
            
            if cutoff_date:
                query = query.filter(CharacterHistory.timestamp >= cutoff_date)
            
            if isinstance(world_filter, list):
                query = query.filter(Character.world.in_(world_filter))
            else:
                query = query.filter(Character.world == world_filter)
            
            results = query.group_by(
                Character.id,
                Character.name,
                Character.world,
                Character.vocation
            ).order_by(
                desc('average_experience')
            ).limit(limit).all()
            
            ranking = []
            for idx, row in enumerate(results, 1):
                ranking.append({
                    "rank": idx,
                    "character_id": row.id,
                    "name": row.name,
                    "world": row.world,
                    "vocation": row.vocation,
                    "average_experience": float(row.average_experience) if row.average_experience else 0,
                    "max_experience": float(row.average_experience) if row.average_experience else 0,
                    "last_update": row.last_update.isoformat() if row.last_update else None
                })
        
        return ranking
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar ranking de experiência: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

