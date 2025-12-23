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
        cells = row.find_all(['td', 'th'])
        for cell in cells:
            # Procura por links que podem conter nomes de personagens
            links = cell.find_all('a', href=re.compile(r'characterprofile\.php'))
            for link in links:
                # Extrai o nome do link ou do texto
                href = link.get('href', '')
                # Tenta extrair do parâmetro name= na URL
                if 'name=' in href:
                    match = re.search(r'name=([^&]+)', href)
                    if match:
                        character_name = match.group(1)
                        # Decodifica URL encoding
                        from urllib.parse import unquote
                        character_name = unquote(character_name)
                        if character_name and len(character_name) > 2:
                            character_names.add(character_name)
                            continue
                
                # Se não encontrou na URL, tenta pegar o texto do link
                text = link.get_text(strip=True)
                if text and len(text) > 2 and len(text) < 50:
                    # Verifica se não é apenas números ou datas
                    if not re.match(r'^\d+[/-]\d+[/-]\d+', text):  # Não é data
                        if not re.match(r'^\d+$', text):  # Não é apenas número
                            character_names.add(text)
            
            # Também verifica se há texto direto que possa ser um nome (apenas se não encontrou link)
            if not links:
                text = cell.get_text(strip=True)
                # Se o texto parece um nome de personagem
                if text and len(text) > 2 and len(text) < 50:
                    # Verifica se não é apenas números ou datas
                    if not re.match(r'^\d+[/-]\d+[/-]\d+', text):  # Não é data
                        if not re.match(r'^\d+$', text):  # Não é apenas número
                            # Verifica se contém apenas letras, espaços e alguns caracteres especiais comuns
                            if re.match(r'^[a-zA-Z\s\-_]+$', text):
                                character_names.add(text)
    
    return character_names

async def fetch_and_extract_characters(url: str, table_selector: str = None, table_id: str = None) -> Set[str]:
    """
    Busca uma URL e extrai nomes de personagens da tabela
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/'
        }
        
        # Configura timeout e desabilita compressão Brotli se não estiver disponível
        timeout = aiohttp.ClientTimeout(total=20, connect=15)
        connector = aiohttp.TCPConnector()
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            # Remove 'br' (Brotli) do Accept-Encoding se não estiver disponível
            headers_no_br = headers.copy()
            if 'Accept-Encoding' in headers_no_br:
                # Mantém apenas gzip e deflate
                headers_no_br['Accept-Encoding'] = 'gzip, deflate'
            else:
                headers_no_br['Accept-Encoding'] = 'gzip, deflate'
            
            async with session.get(url, headers=headers_no_br, timeout=timeout) as response:
                response.raise_for_status()
                html_content = await response.text()
                logger.info(f"HTML obtido de {url} (tamanho: {len(html_content)})")
                
                # Log uma amostra do HTML para debug
                if len(html_content) > 0:
                    logger.debug(f"Primeiros 2000 caracteres do HTML: {html_content[:2000]}")
                
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
        
        # Adiciona um pequeno delay entre requisições para evitar bloqueios
        await asyncio.sleep(1)
        
        logger.info(f"Total de personagens únicos encontrados: {len(all_characters)}")
        
        # Adiciona personagens ao banco de dados
        added_count = 0
        existing_count = 0
        error_count = 0
        
        # Agrupa personagens por fonte para detectar o mundo
        characters_by_source = {
            "aura_powergamers": list(aura_powergamers),
            "san_powergamers": list(san_powergamers),
            "aura_deaths": list(aura_deaths),
            "san_deaths": list(san_deaths),
        }
        
        for character_name in all_characters:
            try:
                # Verifica se já existe
                existing = db.query(Character).filter(Character.name == character_name).first()
                if existing:
                    existing_count += 1
                    continue
                
                # Detecta o mundo pela fonte
                world_detected = ""
                if character_name in characters_by_source["aura_powergamers"] or character_name in characters_by_source["aura_deaths"]:
                    world_detected = "aura"
                elif character_name in characters_by_source["san_powergamers"] or character_name in characters_by_source["san_deaths"]:
                    world_detected = "san"
                
                # Cria novo personagem usando SQL direto para evitar problemas com colunas extras
                try:
                    from sqlalchemy import text
                    # Verifica se a coluna 'server' existe na tabela
                    result = db.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'characters' AND column_name = 'server'
                    """))
                    has_server_column = result.fetchone() is not None
                    
                    if has_server_column:
                        # Se a coluna server existe, insere com valor padrão
                        db.execute(text("""
                            INSERT INTO characters (name, level, vocation, world, outfit, server, created_at, updated_at)
                            VALUES (:name, :level, :vocation, :world, :outfit, :server, NOW(), NOW())
                            ON CONFLICT (name) DO NOTHING
                        """), {
                            "name": character_name,
                            "level": 0,
                            "vocation": "",
                            "world": world_detected,
                            "outfit": "",
                            "server": world_detected if world_detected else "san"  # Usa o mundo como server
                        })
                    else:
                        # Se não existe, insere sem a coluna server
                        db.execute(text("""
                            INSERT INTO characters (name, level, vocation, world, outfit, created_at, updated_at)
                            VALUES (:name, :level, :vocation, :world, :outfit, NOW(), NOW())
                            ON CONFLICT (name) DO NOTHING
                        """), {
                            "name": character_name,
                            "level": 0,
                            "vocation": "",
                            "world": world_detected,
                            "outfit": ""
                        })
                    db.commit()
                    added_count += 1
                    logger.info(f"Personagem adicionado: {character_name} (mundo: {world_detected})")
                except Exception as sql_error:
                    # Se falhar com SQL direto, tenta com o modelo
                    logger.warning(f"Tentando método alternativo para {character_name}: {str(sql_error)}")
                    try:
                        new_character = Character(
                            name=character_name,
                            level=0,
                            vocation="",
                            world=world_detected
                        )
                        db.add(new_character)
                        db.commit()
                        added_count += 1
                        logger.info(f"Personagem adicionado (método alternativo): {character_name} (mundo: {world_detected})")
                    except Exception as model_error:
                        error_count += 1
                        logger.error(f"Erro ao adicionar personagem {character_name} (método alternativo também falhou): {str(model_error)}")
                        db.rollback()
            except Exception as e:
                error_count += 1
                logger.error(f"Erro ao adicionar personagem {character_name}: {str(e)}")
                db.rollback()
        
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

