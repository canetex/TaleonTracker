from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
import asyncio

from services.scraper import update_all_characters
from services.character_discovery import discover_and_add_characters
from database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def schedule_daily_scrape(scheduler: BackgroundScheduler):
    """
    Agenda a execução do scraping diariamente às 00h01.
    """
    try:
        # Agenda a execução para 00h01 todos os dias
        scheduler.add_job(
            update_all_characters,
            'cron',
            hour=0,
            minute=1,
            id='daily_scrape',
            name='Atualização diária dos personagens',
            replace_existing=True,
            timezone='America/Sao_Paulo'  # Definindo o timezone para Brasil
        )
        logger.info("Agendamento diário configurado com sucesso para 00:01 (Brasília)")
    except Exception as e:
        logger.error(f"Erro ao configurar agendamento: {str(e)}")

def schedule_character_discovery(scheduler: BackgroundScheduler):
    """
    Agenda a descoberta de novos personagens diariamente às 23h00.
    """
    try:
        def run_discovery():
            """Wrapper síncrono para executar a função assíncrona"""
            db = SessionLocal()
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                stats = loop.run_until_complete(discover_and_add_characters(db))
                logger.info(f"Descoberta de personagens concluída: {stats}")
            finally:
                db.close()
                loop.close()
        
        # Agenda a execução para 23h00 todos os dias
        scheduler.add_job(
            run_discovery,
            'cron',
            hour=23,
            minute=0,
            id='character_discovery',
            name='Descoberta automática de personagens',
            replace_existing=True,
            timezone='America/Sao_Paulo'
        )
        logger.info("Agendamento de descoberta de personagens configurado para 23:00 (Brasília)")
    except Exception as e:
        logger.error(f"Erro ao configurar agendamento de descoberta: {str(e)}") 