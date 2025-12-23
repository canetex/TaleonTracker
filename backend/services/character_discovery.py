"""
Serviço para descobrir e adicionar automaticamente personagens de rankings e mortes
Complexidade: O(n) onde n é o número de personagens encontrados nas páginas
"""
import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from models.character import Character
from database import SessionLocal
import logging
import re
from typing import List, Set
import asyncio

logger = logging.getLogger(__name__)

# URLs dos portais para extrair personagens
DISCOVERY_URLS = {
    "aura_powergamers": "https://aura.taleon.online/powergamers.php",
    "san_powergamers": "https://san.taleon.online/powergamers.php",
    "aura_deaths": "https://aura.taleon.online/deaths.php",
    "san_deaths": "https://san.taleon.online/deaths.php",
}

async def extract_characters_from_table(html_content: str, table_selector: str = None, table_id: str = None) -> Set[str]:
    """
    Extrai nomes de personagens de uma tabela HTML
    Retorna um conjunto de nomes únicos
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    character_names = set()
    
    # Encontra a tabela
    table = None
    if table_id:
        table = soup.find('table', {'id': table_id})
    elif table_selector:
        table = soup.find('table', {'class': table_selector})
    else:
        # Tenta encontrar qualquer tabela
        table = soup.find('table')
    
    if not table:
        logger.warning(f"Tabela não encontrada (selector: {table_selector}, id: {table_id})")
        return character_names
    
    # Extrai nomes das células da tabela
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        for cell in cells:
            # Procura por links que podem conter nomes de personagens
            links = cell.find_all('a', href=re.compile(r'characterprofile\.php'))
            for link in links:
                # Extrai o nome do link ou do texto
                name = link.get('href', '')
                if 'name=' in name:
                    # Extrai o nome do parâmetro name= na URL
                    match = re.search(r'name=([^&]+)', name)
                    if match:
                        character_name = match.group(1)
                        # Decodifica URL encoding
                        from urllib.parse import unquote
                        character_name = unquote(character_name)
                        if character_name:
                            character_names.add(character_name)
                else:
                    # Tenta pegar o texto do link
                    text = link.get_text(strip=True)
                    if text and len(text) > 2:  # Nome válido
                        character_names.add(text)
            
            # Também verifica se há texto direto que possa ser um nome
            text = cell.get_text(strip=True)
            # Se o texto parece um nome de personagem (sem números excessivos, sem caracteres especiais demais)
            if text and len(text) > 2 and len(text) < 50:
                # Verifica se não é apenas números ou datas
                if not re.match(r'^\d+[/-]\d+[/-]\d+', text):  # Não é data
                    if not re.match(r'^\d+$', text):  # Não é apenas número
                        # Pode ser um nome, mas vamos ser conservadores
                        # Só adiciona se estiver em uma célula próxima a um link de personagem
                        pass
    
    return character_names

async def fetch_and_extract_characters(url: str, table_selector: str = None, table_id: str = None) -> Set[str]:
    """
    Busca uma URL e extrai nomes de personagens da tabela
    """
    try:
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
                html_content = await response.text()
                logger.info(f"HTML obtido de {url} (tamanho: {len(html_content)})")
                
                character_names = await extract_characters_from_table(html_content, table_selector, table_id)
                logger.info(f"Extraídos {len(character_names)} personagens únicos de {url}")
                return character_names
    except Exception as e:
        logger.error(f"Erro ao buscar {url}: {str(e)}")
        return set()

async def discover_and_add_characters(db: Session = None) -> dict:
    """
    Descobre personagens de todas as fontes e adiciona ao banco de dados
    Retorna estatísticas do processo
    """
    if db is None:
        db = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        all_characters = set()
        
        # Extrai personagens de cada fonte
        logger.info("Iniciando descoberta de personagens...")
        
        # Powergamers Aura
        aura_powergamers = await fetch_and_extract_characters(
            DISCOVERY_URLS["aura_powergamers"],
            table_selector="table"
        )
        all_characters.update(aura_powergamers)
        logger.info(f"Powergamers Aura: {len(aura_powergamers)} personagens encontrados")
        
        # Powergamers San
        san_powergamers = await fetch_and_extract_characters(
            DISCOVERY_URLS["san_powergamers"],
            table_selector="table"
        )
        all_characters.update(san_powergamers)
        logger.info(f"Powergamers San: {len(san_powergamers)} personagens encontrados")
        
        # Deaths Aura
        aura_deaths = await fetch_and_extract_characters(
            DISCOVERY_URLS["aura_deaths"],
            table_id="deathsTable"
        )
        all_characters.update(aura_deaths)
        logger.info(f"Deaths Aura: {len(aura_deaths)} personagens encontrados")
        
        # Deaths San
        san_deaths = await fetch_and_extract_characters(
            DISCOVERY_URLS["san_deaths"],
            table_id="deathsTable"
        )
        all_characters.update(san_deaths)
        logger.info(f"Deaths San: {len(san_deaths)} personagens encontrados")
        
        logger.info(f"Total de personagens únicos encontrados: {len(all_characters)}")
        
        # Adiciona personagens ao banco de dados
        added_count = 0
        existing_count = 0
        error_count = 0
        
        for character_name in all_characters:
            try:
                # Verifica se já existe
                existing = db.query(Character).filter(Character.name == character_name).first()
                if existing:
                    existing_count += 1
                    continue
                
                # Cria novo personagem
                new_character = Character(
                    name=character_name,
                    level=0,
                    vocation="",
                    world=""  # Será detectado pelo scraper
                )
                db.add(new_character)
                added_count += 1
                logger.info(f"Personagem adicionado: {character_name}")
            except Exception as e:
                error_count += 1
                logger.error(f"Erro ao adicionar personagem {character_name}: {str(e)}")
        
        db.commit()
        
        stats = {
            "total_found": len(all_characters),
            "added": added_count,
            "existing": existing_count,
            "errors": error_count,
            "sources": {
                "aura_powergamers": len(aura_powergamers),
                "san_powergamers": len(san_powergamers),
                "aura_deaths": len(aura_deaths),
                "san_deaths": len(san_deaths),
            }
        }
        
        logger.info(f"Descoberta concluída: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Erro na descoberta de personagens: {str(e)}")
        if should_close:
            db.rollback()
        raise
    finally:
        if should_close:
            db.close()

async def run_discovery():
    """
    Executa a descoberta de personagens (para uso standalone)
    """
    db = SessionLocal()
    try:
        stats = await discover_and_add_characters(db)
        print(f"Descoberta concluída: {stats}")
        return stats
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_discovery())

