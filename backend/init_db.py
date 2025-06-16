import sys
import os

# Adiciona o diretório atual ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, Base
from backend.models.character import Character
from backend.models.character_history import CharacterHistory
from sqlalchemy import text

def init_db():
    # Primeiro, vamos verificar se a tabela characters existe
    with engine.connect() as conn:
        result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'characters')"))
        table_exists = result.scalar()

        if table_exists:
            # Se a tabela existe, vamos verificar se precisamos adicionar as novas colunas
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'characters'
            """))
            existing_columns = [row[0] for row in result]

            # Adicionar colunas que não existem
            if 'level' not in existing_columns:
                conn.execute(text("ALTER TABLE characters ADD COLUMN level INTEGER"))
            if 'vocation' not in existing_columns:
                conn.execute(text("ALTER TABLE characters ADD COLUMN vocation VARCHAR"))
            if 'world' not in existing_columns:
                conn.execute(text("ALTER TABLE characters ADD COLUMN world VARCHAR"))
            if 'last_updated' not in existing_columns:
                conn.execute(text("ALTER TABLE characters ADD COLUMN last_updated TIMESTAMP"))

            conn.commit()

    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Banco de dados inicializado com sucesso!")
