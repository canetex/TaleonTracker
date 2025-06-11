from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging

from services.scraper import update_all_characters

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
            replace_existing=True
        )
        logger.info("Agendamento diário configurado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao configurar agendamento: {str(e)}") 