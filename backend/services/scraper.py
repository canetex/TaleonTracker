import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from models.character import Character
from models.character_history import CharacterHistory
from datetime import datetime
from urllib.parse import quote
import re
import logging
import time
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
import asyncio

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@cache(expire=300)  # Cache por 5 minutos
async def get_character_html(character_name: str) -> str:
    """Obtém o HTML do perfil do personagem com cache"""
    encoded_name = quote(character_name)
    url = f"http://localhost:8000/api/proxy/taleon/characterprofile.php?name={encoded_name}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=10) as response:
            response.raise_for_status()
            return await response.text()

async def scrape_character_data(character_name: str, db: Session) -> bool:
    try:
        logger.info(f"Scraping character: {character_name}")
        
        # Obtém o HTML com cache
        html_content = await get_character_html(character_name)
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Encontra a tabela com as informações do personagem
        character_table = soup.find('table', {'class': 'table'})
        if not character_table:
            logger.error(f"Tabela de personagem não encontrada para: {character_name}")
            return False
        
        # Extrai as informações
        rows = character_table.find_all('tr')
        character_data = {}
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                key = cols[0].text.strip().lower()
                value = cols[1].text.strip()
                character_data[key] = value
        
        # Atualiza o personagem no banco de dados
        character = db.query(Character).filter(Character.name == character_name).first()
        if character:
            character.level = int(character_data.get('level', 0))
            character.vocation = character_data.get('vocation', '')
            character.world = character_data.get('world', '')
            db.commit()
            logger.info(f"Character {character_name} updated successfully")
            return True
        else:
            logger.error(f"Character {character_name} not found in database")
            return False
            
    except Exception as e:
        logger.error(f"Error scraping character {character_name}: {str(e)}")
        return False

async def update_all_characters():
    """
    Atualiza todos os personagens cadastrados.
    """
    from database import SessionLocal
    db = SessionLocal()
    try:
        characters = db.query(Character).all()
        for character in characters:
            logger.info(f"Atualizando personagem: {character.name}")
            await scrape_character_data(character.name, db)
            # Adiciona um delay entre as requisições
            await asyncio.sleep(2)
    finally:
        db.close()
