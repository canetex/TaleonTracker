"""
Script para limpar o campo total_experience de toda a base de dados
"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_total_experience():
    """
    Limpa o campo total_experience de todos os registros em character_history
    """
    try:
        with engine.connect() as conn:
            # Limpa o campo total_experience
            result = conn.execute(text("""
                UPDATE character_history 
                SET total_experience = NULL
            """))
            conn.commit()
            logger.info(f"Campo total_experience limpo em {result.rowcount} registros")
    except Exception as e:
        logger.error(f"Erro ao limpar total_experience: {str(e)}")
        raise

if __name__ == "__main__":
    clear_total_experience()

