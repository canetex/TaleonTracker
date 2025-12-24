"""
Serviço para preencher dias faltantes na tabela server_stats
Preenche com 0 de experiência e mantém o mesmo número de personagens ativos do dia anterior
Complexidade: O(d) onde d é o número de dias no período
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date
from models.server_stats import ServerStats
from models.character import Character
from models.character_history import CharacterHistory
import logging

logger = logging.getLogger(__name__)

def fill_missing_days_for_world(world: str, db: Session, start_date: date = None, end_date: date = None):
    """
    Preenche dias faltantes na tabela server_stats para um mundo específico
    Para dias sem dados, cria registros com:
    - total_experience: mesmo valor do dia anterior (ou 0 se for o primeiro dia)
    - active_characters: mesmo valor do dia anterior (ou 0 se for o primeiro dia)
    """
    try:
        world_lower = world.lower()
        if world_lower not in ['san', 'aura']:
            logger.error(f"Mundo inválido: {world}")
            return
        
        # Define período padrão se não especificado
        if end_date is None:
            end_date = datetime.utcnow().date()
        if start_date is None:
            start_date = end_date - timedelta(days=90)  # Últimos 90 dias por padrão
        
        logger.info(f"Preenchendo dias faltantes para {world_lower} de {start_date} até {end_date}")
        
        # Busca todos os registros existentes no período
        existing_stats = db.query(ServerStats).filter(
            ServerStats.world == world_lower,
            func.date(ServerStats.timestamp) >= start_date,
            func.date(ServerStats.timestamp) <= end_date
        ).order_by(ServerStats.timestamp.asc()).all()
        
        # Cria dicionário de datas existentes
        existing_dates = {stat.timestamp.date(): stat for stat in existing_stats}
        
        # Itera por todos os dias no período
        current_date = start_date
        last_total_exp = 0
        last_active_chars = 0
        new_records = []
        
        while current_date <= end_date:
            if current_date in existing_dates:
                # Atualiza valores do último dia conhecido
                stat = existing_dates[current_date]
                last_total_exp = stat.total_experience
                last_active_chars = stat.active_characters
            else:
                # Cria novo registro para o dia faltante
                new_stat = ServerStats(
                    world=world_lower,
                    total_experience=last_total_exp,  # Mantém valor do dia anterior
                    active_characters=last_active_chars,  # Mantém valor do dia anterior
                    timestamp=datetime.combine(current_date, datetime.min.time())
                )
                new_records.append(new_stat)
                logger.info(f"Criando registro para {current_date}: EXP={last_total_exp}, Ativos={last_active_chars}")
            
            current_date += timedelta(days=1)
        
        # Insere novos registros em lote
        if new_records:
            db.bulk_save_objects(new_records)
            db.commit()
            logger.info(f"Preenchidos {len(new_records)} dias faltantes para {world_lower}")
        else:
            logger.info(f"Nenhum dia faltante encontrado para {world_lower}")
    
    except Exception as e:
        logger.error(f"Erro ao preencher dias faltantes para {world}: {str(e)}")
        db.rollback()
        raise

def fill_missing_days_all_worlds(db: Session, start_date: date = None, end_date: date = None):
    """
    Preenche dias faltantes para todos os mundos (san e aura)
    """
    for world in ['san', 'aura']:
        try:
            fill_missing_days_for_world(world, db, start_date, end_date)
        except Exception as e:
            logger.error(f"Erro ao preencher dias faltantes para {world}: {str(e)}")
            continue

