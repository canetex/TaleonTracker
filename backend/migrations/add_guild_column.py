"""
Migração para adicionar coluna 'guild' à tabela 'characters'
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, create_engine
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_guild_column():
    """
    Adiciona a coluna 'guild' à tabela 'characters' se ela não existir
    """
    try:
        # Conecta ao banco usando a mesma configuração do projeto
        database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@tibia-tracker-postgres:5432/tibia_tracker')
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Verifica se a coluna já existe
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'characters' AND column_name = 'guild'
            """))
            
            if result.fetchone() is None:
                # Adiciona a coluna
                conn.execute(text("""
                    ALTER TABLE characters 
                    ADD COLUMN guild VARCHAR DEFAULT ''
                """))
                conn.commit()
                logger.info("Coluna 'guild' adicionada à tabela 'characters' com sucesso")
            else:
                logger.info("Coluna 'guild' já existe na tabela 'characters'")
    except Exception as e:
        logger.error(f"Erro ao adicionar coluna 'guild': {str(e)}")
        raise

if __name__ == "__main__":
    add_guild_column()

