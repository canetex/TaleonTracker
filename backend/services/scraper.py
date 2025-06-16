import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from models.character import Character
from datetime import datetime

def scrape_character_data(character_name: str, db: Session) -> bool:
    try:
        # URL do site do Taleon
        url = f"https://taleon.com.br/character/{character_name}"
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extrair dados do personagem
        level = int(soup.find('div', {'class': 'level'}).text.strip())
        vocation = soup.find('div', {'class': 'vocation'}).text.strip()
        world = soup.find('div', {'class': 'world'}).text.strip()
        
        # Atualizar ou criar o personagem no banco
        character = db.query(Character).filter(Character.name == character_name).first()
        if not character:
            character = Character(name=character_name)
        
        character.level = level
        character.vocation = vocation
        character.world = world
        character.last_updated = datetime.utcnow()
        
        db.add(character)
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