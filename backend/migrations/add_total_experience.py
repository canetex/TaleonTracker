"""
Migration para adicionar coluna total_experience à tabela character_history
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

def add_total_experience_column():
    """
    Adiciona a coluna total_experience à tabela character_history
    """
    try:
        with engine.connect() as conn:
            # Verifica se a coluna já existe
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'character_history' AND column_name = 'total_experience'
            """))
            
            if result.fetchone():
                logger.info("Coluna total_experience já existe na tabela character_history")
                return
            
            # Adiciona a coluna
            conn.execute(text("""
                ALTER TABLE character_history 
                ADD COLUMN total_experience FLOAT
            """))
            conn.commit()
            logger.info("Coluna total_experience adicionada com sucesso à tabela character_history")
    except Exception as e:
        logger.error(f"Erro ao adicionar coluna total_experience: {str(e)}")
        raise

if __name__ == "__main__":
    add_total_experience_column()

