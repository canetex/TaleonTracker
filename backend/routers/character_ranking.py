from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta
from database import get_db
from models.character import Character
from models.character_history import CharacterHistory
import logging
import math

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
            # OVERALL: Experiência acumulada no período usando total_experience
            # INITIAL_EXPERIENCE = FIRST REGISTER OF TOTAL_EXPERIENCE no intervalo
            # LAST_EXPERIENCE = LAST REGISTER OF TOTAL_EXPERIENCE no intervalo
            # OVERALL = (LAST_EXPERIENCE - INITIAL_EXPERIENCE)
            
            # Busca personagens com histórico no período que tenham total_experience
            history_query = db.query(
                CharacterHistory.character_id,
                func.min(CharacterHistory.total_experience).label('first_total_exp'),
                func.max(CharacterHistory.total_experience).label('last_total_exp'),
                func.max(CharacterHistory.timestamp).label('last_update')
            ).filter(
                CharacterHistory.total_experience.isnot(None)
            )
            
            if cutoff_date:
                history_query = history_query.filter(CharacterHistory.timestamp >= cutoff_date)
            
            history_query = history_query.group_by(CharacterHistory.character_id)
            
            # Filtra por mundo através do Character
            if isinstance(world_filter, list):
                history_query = history_query.join(Character).filter(Character.world.in_(world_filter))
            else:
                history_query = history_query.join(Character).filter(Character.world == world_filter)
            
            history_results = history_query.all()
            
            # Calcula experiência acumulada (OVERALL)
            character_data = {}
            for row in history_results:
                char_id = row.character_id
                first_total_exp = float(row.first_total_exp) if row.first_total_exp else 0
                last_total_exp = float(row.last_total_exp) if row.last_total_exp else 0
                
                # OVERALL = (LAST_EXPERIENCE - INITIAL_EXPERIENCE)
                accumulated = last_total_exp - first_total_exp
                
                # Só adiciona se a experiência acumulada for maior que 0
                if accumulated > 0:
                    character_data[char_id] = {
                        'accumulated': accumulated,
                        'last_update': row.last_update
                    }
            
            # Busca informações dos personagens e level mais recente
            char_ids = list(character_data.keys())
            if not char_ids:
                return []
            
            characters = db.query(Character).filter(Character.id.in_(char_ids)).all()
            char_info = {char.id: char for char in characters}
            
            # Busca level mais recente de cada personagem
            levels_query = db.query(
                CharacterHistory.character_id,
                func.max(CharacterHistory.timestamp).label('max_timestamp')
            ).filter(
                CharacterHistory.character_id.in_(char_ids)
            ).group_by(CharacterHistory.character_id).subquery()
            
            levels_data = db.query(
                CharacterHistory.character_id,
                CharacterHistory.level
            ).join(
                levels_query,
                (CharacterHistory.character_id == levels_query.c.character_id) &
                (CharacterHistory.timestamp == levels_query.c.max_timestamp)
            ).all()
            
            char_levels = {row.character_id: row.level for row in levels_data}
            
            # Monta ranking
            ranking_data = []
            for char_id, data in character_data.items():
                if char_id in char_info:
                    char = char_info[char_id]
                    ranking_data.append({
                        'id': char_id,
                        'name': char.name,
                        'world': char.world,
                        'vocation': char.vocation,
                        'level': char_levels.get(char_id, char.level or 0),
                        'accumulated_experience': data['accumulated'],
                        'last_update': data['last_update']
                    })
            
            # Ordena por experiência acumulada (decrescente)
            ranking_data.sort(key=lambda x: float(x['accumulated_experience']), reverse=True)
            ranking_data = ranking_data[:limit]
            
            ranking = []
            for idx, data in enumerate(ranking_data, 1):
                ranking.append({
                    "rank": idx,
                    "character_id": data['id'],
                    "name": data['name'],
                    "world": data['world'],
                    "vocation": data['vocation'],
                    "level": int(data['level']) if data['level'] else 0,
                    "accumulated_experience": math.ceil(float(data['accumulated_experience'])),
                    "max_experience": math.ceil(float(data['accumulated_experience'])),
                    "last_update": data['last_update'].isoformat() if data['last_update'] else None
                })
        else:
            # AVERAGE: Experiência média no período usando total_experience
            # INITIAL_EXPERIENCE = FIRST REGISTER OF TOTAL_EXPERIENCE no intervalo
            # LAST_EXPERIENCE = LAST REGISTER OF TOTAL_EXPERIENCE no intervalo
            # AVERAGE = (LAST_EXPERIENCE - INITIAL_EXPERIENCE) / DAYS
            
            # Busca personagens com histórico no período que tenham total_experience
            history_query = db.query(
                CharacterHistory.character_id,
                func.min(CharacterHistory.total_experience).label('first_total_exp'),
                func.max(CharacterHistory.total_experience).label('last_total_exp'),
                func.min(CharacterHistory.timestamp).label('first_date'),
                func.max(CharacterHistory.timestamp).label('last_date')
            ).filter(
                CharacterHistory.total_experience.isnot(None)
            )
            
            if cutoff_date:
                history_query = history_query.filter(CharacterHistory.timestamp >= cutoff_date)
            
            # Filtra por mundo através do Character
            if isinstance(world_filter, list):
                history_query = history_query.join(Character).filter(Character.world.in_(world_filter))
            else:
                history_query = history_query.join(Character).filter(Character.world == world_filter)
            
            history_query = history_query.group_by(CharacterHistory.character_id)
            history_results = history_query.all()
            
            # Calcula experiência média: (LAST_EXPERIENCE - INITIAL_EXPERIENCE) / DAYS
            character_avg = {}
            interval_days = days if days > 0 else 1
            
            for row in history_results:
                char_id = row.character_id
                first_total_exp = float(row.first_total_exp) if row.first_total_exp else 0
                last_total_exp = float(row.last_total_exp) if row.last_total_exp else 0
                
                # Calcula experiência total ganha no período
                total_exp_gained = last_total_exp - first_total_exp
                
                # Calcula média: experiência total / intervalo de dias
                avg_exp = total_exp_gained / interval_days if interval_days > 0 else 0
                
                # Só adiciona se a média for maior que 0
                if avg_exp > 0:
                    character_avg[char_id] = avg_exp
            
            # Busca informações dos personagens, level e última atualização
            char_ids = list(character_avg.keys())
            if not char_ids:
                return []
            
            characters = db.query(Character).filter(Character.id.in_(char_ids)).all()
            char_info = {char.id: char for char in characters}
            
            # Busca level mais recente de cada personagem
            levels_query = db.query(
                CharacterHistory.character_id,
                func.max(CharacterHistory.timestamp).label('max_timestamp')
            ).filter(
                CharacterHistory.character_id.in_(char_ids)
            ).group_by(CharacterHistory.character_id).subquery()
            
            levels_data = db.query(
                CharacterHistory.character_id,
                CharacterHistory.level
            ).join(
                levels_query,
                (CharacterHistory.character_id == levels_query.c.character_id) &
                (CharacterHistory.timestamp == levels_query.c.max_timestamp)
            ).all()
            
            char_levels = {row.character_id: row.level for row in levels_data}
            
            # Busca última atualização de uma vez
            last_updates_query = db.query(
                CharacterHistory.character_id,
                func.max(CharacterHistory.timestamp).label('last_update')
            ).filter(
                CharacterHistory.character_id.in_(char_ids)
            ).group_by(CharacterHistory.character_id)
            
            last_updates = {row.character_id: row.last_update for row in last_updates_query.all()}
            
            # Monta ranking
            ranking_data = []
            for char_id, avg_exp in character_avg.items():
                if char_id in char_info:
                    char = char_info[char_id]
                    ranking_data.append({
                        'id': char_id,
                        'name': char.name,
                        'world': char.world,
                        'vocation': char.vocation,
                        'level': char_levels.get(char_id, char.level or 0),
                        'average_experience': avg_exp,
                        'last_update': last_updates.get(char_id)
                    })
            
            # Filtra personagens com experiência média > 0 e ordena (decrescente)
            ranking_data = [r for r in ranking_data if float(r['average_experience']) > 0]
            ranking_data.sort(key=lambda x: float(x['average_experience']), reverse=True)
            ranking_data = ranking_data[:limit]
            
            ranking = []
            for idx, data in enumerate(ranking_data, 1):
                ranking.append({
                    "rank": idx,
                    "character_id": data['id'],
                    "name": data['name'],
                    "world": data['world'],
                    "vocation": data['vocation'],
                    "level": int(data['level']) if data['level'] else 0,
                    "average_experience": math.ceil(float(data['average_experience'])),
                    "max_experience": math.ceil(float(data['average_experience'])),
                    "last_update": data['last_update'].isoformat() if data['last_update'] else None
                })
        
        return ranking
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar ranking de experiência: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

