import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from models.character import Character
from models.character_history import CharacterHistory
from datetime import datetime

def scrape_character_data(character_name: str, db: Session) -> bool:
    try:
        # URL da API do Taleon
        url = f"http://192.168.1.178:8001/characters/{character_name}"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Atualizar ou criar o personagem no banco
        character = db.query(Character).filter(Character.name == character_name).first()
        if not character:
            character = Character(
                name=character_name,
                level=data.get('level', 0),
                vocation=data.get('vocation', ''),
                world=data.get('world', '')
            )
            db.add(character)
            db.commit()
            db.refresh(character)
        
        # Criar histórico
        history = CharacterHistory(
            character_id=character.id,
            level=data.get('level', 0),
            experience=data.get('experience', 0),
            deaths=data.get('deaths', 0),
            timestamp=datetime.utcnow()
        )
        
        db.add(history)
        db.commit()
        return True
        
    except Exception as e:
        print(f"Erro ao fazer scraping: {str(e)}")
        return False

def update_all_characters():
    """
    Atualiza todos os personagens cadastrados.
    """
    from database import SessionLocal
    db = SessionLocal()
    try:
        characters = db.query(Character).all()
        for character in characters:
            scrape_character_data(character.name, db)
    finally:
        db.close()
