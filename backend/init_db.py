import sys
import os

# Adiciona o diretório atual ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, Base
from backend.models.character import Character
from backend.models.character_history import CharacterHistory

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Banco de dados inicializado com sucesso!")
