import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from typing import Optional, Dict, Any

from models import Character, CharacterHistory
from database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://san.taleon.online/characterprofile.php"

def extract_character_data(html_content: str) -> Optional[Dict[str, Any]]:
    """
    Extrai os dados do personagem do HTML da página.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Encontra o nível
        level_element = soup.find('div', string=lambda text: text and 'Level:' in text)
        level = int(level_element.find_next('div').text.strip()) if level_element else None
        
        # Encontra a experiência
        exp_element = soup.find('div', string=lambda text: text and 'Experience:' in text)
        exp = float(exp_element.find_next('div').text.strip().replace(',', '')) if exp_element else None
        
        # Encontra as mortes
        deaths_element = soup.find('div', string=lambda text: text and 'Deaths:' in text)
        deaths = int(deaths_element.find_next('div').text.strip()) if deaths_element else 0
        
        if level is None or exp is None:
            logger.error("Não foi possível extrair todos os dados do personagem")
            return None
            
        return {
            "level": level,
            "experience": exp,
            "deaths": deaths
        }
    except Exception as e:
        logger.error(f"Erro ao extrair dados do personagem: {str(e)}")
        return None

def scrape_character_data(character_name: str, db: Session) -> bool:
    """
    Faz o scraping dos dados do personagem e salva no banco de dados.
    """
    try:
        # Faz a requisição para a página do personagem
        params = {"name": character_name}
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        # Extrai os dados do HTML
        data = extract_character_data(response.text)
        if not data:
            return False
            
        # Busca ou cria o personagem no banco
        character = db.query(Character).filter(Character.name == character_name).first()
        if not character:
            character = Character(name=character_name)
            db.add(character)
            db.commit()
            db.refresh(character)
        
        # Cria o registro histórico
        history = CharacterHistory(
            character_id=character.id,
            level=data["level"],
            experience=data["experience"],
            deaths=data["deaths"]
        )
        
        db.add(history)
        db.commit()
        
        logger.info(f"Dados do personagem {character_name} atualizados com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao fazer scraping do personagem {character_name}: {str(e)}")
        return False

def update_all_characters():
    """
    Atualiza os dados de todos os personagens cadastrados.
    """
    db = SessionLocal()
    try:
        characters = db.query(Character).all()
        for character in characters:
            scrape_character_data(character.name, db)
    finally:
        db.close() 