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
            # Experiência acumulada: diferença entre experiência ANTES do período e última experiência no período
            # Primeiro, busca os personagens com histórico no período
            history_query = db.query(
                CharacterHistory.character_id,
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
            
            # Para cada personagem, busca a experiência ANTES do período (se houver)
            char_ids = [row.character_id for row in history_results]
            if not char_ids:
                return []
            
            # Busca experiência antes do período para cada personagem
            initial_exp_query = db.query(
                CharacterHistory.character_id,
                func.max(CharacterHistory.timestamp).label('max_timestamp')
            ).filter(
                CharacterHistory.character_id.in_(char_ids)
            )
            
            if cutoff_date:
                initial_exp_query = initial_exp_query.filter(CharacterHistory.timestamp < cutoff_date)
            
            initial_exp_query = initial_exp_query.group_by(CharacterHistory.character_id).subquery()
            
            initial_exp_data = db.query(
                CharacterHistory.character_id,
                CharacterHistory.experience
            ).join(
                initial_exp_query,
                (CharacterHistory.character_id == initial_exp_query.c.character_id) &
                (CharacterHistory.timestamp == initial_exp_query.c.max_timestamp)
            ).all()
            
            initial_exp_dict = {row.character_id: float(row.experience) for row in initial_exp_data}
            
            # Calcula experiência acumulada e ordena
            character_data = {}
            for row in history_results:
                char_id = row.character_id
                max_exp = float(row.max_exp) if row.max_exp else 0
                # Se não há experiência inicial (antes do período), usa 0 como base
                initial_exp = initial_exp_dict.get(char_id, 0)
                accumulated = max_exp - initial_exp
                # Só adiciona se a experiência acumulada for maior que 0
                if accumulated > 0:
                    if char_id not in character_data or accumulated > character_data[char_id]['accumulated']:
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
            # Experiência média: SOMA(EXP_POR_DIA) / INTERVALO_DIAS
            # Calcula a diferença total de experiência no período e divide pelo intervalo
            history_query = db.query(
                CharacterHistory.character_id,
                func.min(CharacterHistory.experience).label('first_exp'),
                func.max(CharacterHistory.experience).label('last_exp'),
                func.min(CharacterHistory.timestamp).label('first_date'),
                func.max(CharacterHistory.timestamp).label('last_date')
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
            
            # Calcula experiência média: (ÚLTIMA_EXP - PRIMEIRA_EXP) / INTERVALO_DIAS
            character_avg = {}
            interval_days = days if days > 0 else 1
            
            for row in history_results:
                char_id = row.character_id
                first_exp = float(row.first_exp) if row.first_exp else 0
                last_exp = float(row.last_exp) if row.last_exp else 0
                
                # Calcula experiência total ganha no período
                total_exp_gained = last_exp - first_exp
                if total_exp_gained < 0:
                    total_exp_gained = 0  # Se a experiência diminuiu (morte), considera 0
                
                # Calcula média: experiência total / intervalo de dias
                avg_exp = total_exp_gained / interval_days
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

