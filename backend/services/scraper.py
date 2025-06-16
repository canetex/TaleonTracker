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

# URL base do Taleon
TALEON_BASE_URL = "https://san.taleon.online"

@cache(expire=300)  # Cache por 5 minutos
async def get_character_html(character_name: str) -> str:
    """Obtém o HTML do perfil do personagem com cache"""
    encoded_name = quote(character_name)
    url = f"{TALEON_BASE_URL}/characterprofile.php?name={encoded_name}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        logger.info(f"Fazendo requisição para: {url}")
        logger.info(f"Headers da requisição: {headers}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                response.raise_for_status()
                logger.info(f"Status da resposta: {response.status}")
                logger.info(f"Headers da resposta: {response.headers}")
                
                html_content = await response.text()
                logger.info(f"HTML recebido para {character_name} (tamanho: {len(html_content)})")
                logger.info(f"Primeiros 1000 caracteres do HTML: {html_content[:1000]}")
                
                if len(html_content) < 100:
                    logger.error(f"HTML muito curto, possivel erro na resposta: {html_content}")
                    raise Exception("HTML muito curto, possivel erro na resposta")
                
                return html_content
    except Exception as e:
        logger.error(f"Erro ao obter HTML para {character_name}: {str(e)}")
        raise

async def scrape_character_data(character_name: str, db: Session) -> bool:
    try:
        logger.info(f"Iniciando scraping do personagem: {character_name}")
        
        # Obtém o HTML com cache
        html_content = await get_character_html(character_name)
        logger.info(f"HTML obtido com sucesso para {character_name}")
        logger.info(f"Primeiros 1000 caracteres do HTML: {html_content[:1000]}")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        logger.info(f"HTML parseado para {character_name}")
        
        # Encontra a tabela com as informações do personagem
        character_table = soup.find('table', {'class': 'table'})
        if not character_table:
            # Tenta encontrar a tabela sem especificar a classe
            character_table = soup.find('table')
            if not character_table:
                logger.error(f"Nenhuma tabela encontrada para: {character_name}")
                logger.error(f"HTML recebido: {html_content[:500]}...")  # Log dos primeiros 500 caracteres
                return False
        
        # Log da estrutura da tabela
        logger.info(f"Estrutura da tabela encontrada: {character_table.prettify()[:500]}")
        
        # Extrai as informações
        rows = character_table.find_all('tr')
        character_data = {}
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                key = cols[0].text.strip().lower().replace(':', '')
                value = cols[1].text.strip()
                character_data[key] = value
                logger.info(f"Encontrado: {key} = {value}")
        
        # Log dos dados encontrados
        logger.info(f"Dados encontrados para {character_name}: {character_data}")
        
        # Atualiza o personagem no banco de dados
        character = db.query(Character).filter(Character.name == character_name).first()
        if character:
            try:
                # Atualiza os dados básicos do personagem
                level_text = character_data.get('level', '0')
                # Remove caracteres não numéricos exceto ponto
                level_text = re.sub(r'[^\d.]', '', level_text)
                # Converte para float e depois para inteiro, removendo o ponto
                level = int(level_text.replace('.', ''))
                character.level = level
                character.vocation = character_data.get('vocation', '')
                character.world = character_data.get('residence', '')  # Usando residence como world
                
                # Extrai experiência e mortes
                experience = 0
                deaths = 0
                
                # Tenta extrair experiência
                exp_text = character_data.get('experience', '0')
                if exp_text:
                    # Remove caracteres não numéricos
                    exp_text = re.sub(r'[^\d]', '', exp_text)
                    experience = float(exp_text) if exp_text else 0
                    logger.info(f"Experiência extraída de '{exp_text}' para {experience}")
                
                # Tenta extrair mortes
                deaths_text = character_data.get('deaths', '0')
                if deaths_text:
                    # Remove caracteres não numéricos
                    deaths_text = re.sub(r'[^\d]', '', deaths_text)
                    deaths = int(deaths_text) if deaths_text else 0
                    logger.info(f"Mortes extraídas de '{deaths_text}' para {deaths}")
                
                # Cria um novo registro de histórico
                try:
                    history = CharacterHistory(
                        character_id=character.id,
                        level=level,  # Usando o mesmo nível já processado
                        experience=experience,
                        deaths=deaths,
                        timestamp=datetime.utcnow()
                    )
                    db.add(history)
                    logger.info(f"Registro de histórico criado para {character_name}")
                except Exception as e:
                    logger.error(f"Erro ao criar registro de histórico: {str(e)}")
                    raise
                
                db.commit()
                logger.info(f"Character {character_name} updated successfully")
                return True
            except Exception as e:
                logger.error(f"Erro ao atualizar personagem {character_name}: {str(e)}")
                db.rollback()
                return False
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
