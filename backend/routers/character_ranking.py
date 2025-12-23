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
            # Primeiro, busca os personagens com histórico no período
            history_query = db.query(
                CharacterHistory.character_id,
                func.min(CharacterHistory.experience).label('min_exp'),
                func.max(CharacterHistory.experience).label('max_exp'),
                func.max(CharacterHistory.timestamp).label('last_update')
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
            
            # Calcula experiência acumulada e ordena
            character_data = {}
            for row in history_results:
                char_id = row.character_id
                accumulated = float(row.max_exp) - float(row.min_exp) if row.max_exp and row.min_exp else 0
                if char_id not in character_data or accumulated > character_data[char_id]['accumulated']:
                    character_data[char_id] = {
                        'accumulated': accumulated,
                        'last_update': row.last_update
                    }
            
            # Busca informações dos personagens
            char_ids = list(character_data.keys())
            if not char_ids:
                return []
            
            characters = db.query(Character).filter(Character.id.in_(char_ids)).all()
            char_info = {char.id: char for char in characters}
            
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
                        'accumulated_experience': data['accumulated'],
                        'last_update': data['last_update']
                    })
            
            # Ordena por experiência acumulada
            ranking_data.sort(key=lambda x: x['accumulated_experience'], reverse=True)
            ranking_data = ranking_data[:limit]
            
            ranking = []
            for idx, data in enumerate(ranking_data, 1):
                ranking.append({
                    "rank": idx,
                    "character_id": data['id'],
                    "name": data['name'],
                    "world": data['world'],
                    "vocation": data['vocation'],
                    "accumulated_experience": data['accumulated_experience'],
                    "max_experience": data['accumulated_experience'],
                    "last_update": data['last_update'].isoformat() if data['last_update'] else None
                })
        else:
            # Experiência média: SOMA(EXP_POR_DIA) / INTERVALO_DIAS
            # Calcula experiência ganha por dia e depois faz a média
            history_query = db.query(
                CharacterHistory.character_id,
                func.date(CharacterHistory.timestamp).label('date'),
                func.max(CharacterHistory.experience).label('max_exp'),
                func.min(CharacterHistory.experience).label('min_exp')
            )
            
            if cutoff_date:
                history_query = history_query.filter(CharacterHistory.timestamp >= cutoff_date)
            
            history_query = history_query.group_by(
                CharacterHistory.character_id,
                func.date(CharacterHistory.timestamp)
            )
            
            # Filtra por mundo através do Character
            if isinstance(world_filter, list):
                history_query = history_query.join(Character).filter(Character.world.in_(world_filter))
            else:
                history_query = history_query.join(Character).filter(Character.world == world_filter)
            
            history_results = history_query.all()
            
            # Agrupa por personagem e calcula experiência média diária
            character_daily_exp = {}
            for row in history_results:
                char_id = row.character_id
                daily_exp = float(row.max_exp) - float(row.min_exp) if row.max_exp and row.min_exp else 0
                if char_id not in character_daily_exp:
                    character_daily_exp[char_id] = []
                character_daily_exp[char_id].append(daily_exp)
            
            # Calcula média: soma de exp por dia / número de dias
            character_avg = {}
            interval_days = days if days > 0 else 1
            for char_id, daily_exps in character_daily_exp.items():
                total_exp = sum(daily_exps)
                avg_exp = total_exp / interval_days
                character_avg[char_id] = avg_exp
            
            # Busca informações dos personagens
            char_ids = list(character_avg.keys())
            if not char_ids:
                return []
            
            characters = db.query(Character).filter(Character.id.in_(char_ids)).all()
            char_info = {char.id: char for char in characters}
            
            # Busca última atualização
            last_updates = {}
            for char_id in char_ids:
                last_history = db.query(CharacterHistory).filter(
                    CharacterHistory.character_id == char_id
                ).order_by(CharacterHistory.timestamp.desc()).first()
                if last_history:
                    last_updates[char_id] = last_history.timestamp
            
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
                        'average_experience': avg_exp,
                        'last_update': last_updates.get(char_id)
                    })
            
            # Ordena por experiência média
            ranking_data.sort(key=lambda x: x['average_experience'], reverse=True)
            ranking_data = ranking_data[:limit]
            
            ranking = []
            for idx, data in enumerate(ranking_data, 1):
                ranking.append({
                    "rank": idx,
                    "character_id": data['id'],
                    "name": data['name'],
                    "world": data['world'],
                    "vocation": data['vocation'],
                    "average_experience": data['average_experience'],
                    "max_experience": data['average_experience'],
                    "last_update": data['last_update'].isoformat() if data['last_update'] else None
                })
        
        return ranking
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar ranking de experiência: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

