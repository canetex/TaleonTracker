"""
Migration para criar tabela deaths
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

def create_deaths_table():
    """
    Cria a tabela deaths se não existir
    """
    try:
        with engine.connect() as conn:
            # Verifica se a tabela já existe
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'deaths'
            """))
            
            if result.fetchone():
                logger.info("Tabela deaths já existe")
                return
            
            # Cria a tabela
            conn.execute(text("""
                CREATE TABLE deaths (
                    id SERIAL PRIMARY KEY,
                    character_name VARCHAR(255) NOT NULL,
                    character_id INTEGER,
                    level INTEGER NOT NULL,
                    world VARCHAR(50) NOT NULL,
                    death_date TIMESTAMP NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE SET NULL,
                    CONSTRAINT idx_deaths_character_name UNIQUE (character_name, death_date, world)
                )
            """))
            
            # Cria índices
            conn.execute(text("""
                CREATE INDEX idx_deaths_character_name ON deaths(character_name)
            """))
            
            conn.execute(text("""
                CREATE INDEX idx_deaths_character_id ON deaths(character_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX idx_deaths_world ON deaths(world)
            """))
            
            conn.execute(text("""
                CREATE INDEX idx_deaths_death_date ON deaths(death_date)
            """))
            
            conn.commit()
            logger.info("Tabela deaths criada com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar tabela deaths: {str(e)}")
        raise

if __name__ == "__main__":
    create_deaths_table()

