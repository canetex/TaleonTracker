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
            
            # Cria índices (se não existirem)
            indexes = [
                ("idx_deaths_character_name", "CREATE INDEX idx_deaths_character_name ON deaths(character_name)"),
                ("idx_deaths_character_id", "CREATE INDEX idx_deaths_character_id ON deaths(character_id)"),
                ("idx_deaths_world", "CREATE INDEX idx_deaths_world ON deaths(world)"),
                ("idx_deaths_death_date", "CREATE INDEX idx_deaths_death_date ON deaths(death_date)")
            ]
            
            for index_name, create_sql in indexes:
                try:
                    # Verifica se o índice já existe
                    check_result = conn.execute(text("""
                        SELECT indexname 
                        FROM pg_indexes 
                        WHERE tablename = 'deaths' AND indexname = :index_name
                    """), {"index_name": index_name})
                    
                    if not check_result.fetchone():
                        conn.execute(text(create_sql))
                        logger.info(f"Índice {index_name} criado")
                    else:
                        logger.info(f"Índice {index_name} já existe")
                except Exception as idx_error:
                    logger.warning(f"Erro ao criar índice {index_name}: {str(idx_error)}")
                    # Continua mesmo se houver erro em um índice
            
            conn.commit()
            logger.info("Tabela deaths criada com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar tabela deaths: {str(e)}")
        raise

if __name__ == "__main__":
    create_deaths_table()

