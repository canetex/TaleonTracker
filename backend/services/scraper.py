import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from models.character import Character
from models.character_history import CharacterHistory
from datetime import datetime
from urllib.parse import quote
from typing import Tuple
import re
import logging
import time
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
import asyncio
from services.outfit_downloader import download_outfit

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL base do Taleon
# Mundos disponíveis: San, Aura
# Mundo Gaia desativado conforme solicitação
TALEON_WORLDS = {
    "San": "https://san.taleon.online",
    "Aura": "https://aura.taleon.online",
    # "Gaia": "https://gaia.taleon.online"  # Desativado
}
TALEON_BASE_URL = TALEON_WORLDS["San"]  # Padrão: San

async def get_character_html(character_name: str, world: str = None, use_cache: bool = True) -> Tuple[str, str]:
    """
    Obtém o HTML do perfil do personagem com cache
    Retorna (html_content, world_detected)
    """
    encoded_name = quote(character_name)
    
    # Se não especificado, tenta ambos os mundos
    worlds_to_try = [world] if world else ["San", "Aura"]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    for world_name in worlds_to_try:
        try:
            base_url = TALEON_WORLDS.get(world_name, TALEON_BASE_URL)
            url = f"{base_url}/characterprofile.php?name={encoded_name}"
            
            logger.info(f"Fazendo requisição para: {url}")
            logger.info(f"Headers da requisição: {headers}")
            
            # Timeout mais robusto: 15 segundos para conexão, 20 segundos total
            timeout = aiohttp.ClientTimeout(total=20, connect=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    logger.info(f"Status da resposta: {response.status}")
                    logger.info(f"Headers da resposta: {response.headers}")
                    
                    html_content = await response.text()
                    logger.info(f"HTML recebido para {character_name} (tamanho: {len(html_content)})")
                    logger.info(f"Primeiros 1000 caracteres do HTML: {html_content[:1000]}")
                    
                    if len(html_content) < 100:
                        logger.error(f"HTML muito curto, possivel erro na resposta: {html_content}")
                        continue  # Tenta próximo mundo
                    
                    # Detecta o mundo pela URL
                    world_detected = world_name.lower() if world_name else "san"
                    if "san.taleon.online" in url:
                        world_detected = "san"
                    elif "aura.taleon.online" in url:
                        world_detected = "aura"
                    
                    return html_content, world_detected
        except Exception as e:
            logger.warning(f"Erro ao obter HTML de {world_name} para {character_name}: {str(e)}")
            continue  # Tenta próximo mundo
    
    # Se nenhum mundo funcionou, tenta com o padrão
    try:
        url = f"{TALEON_BASE_URL}/characterprofile.php?name={encoded_name}"
        timeout = aiohttp.ClientTimeout(total=20, connect=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                html_content = await response.text()
                world_detected = "san"  # Padrão
                return html_content, world_detected
    except Exception as e:
        logger.error(f"Erro ao obter HTML para {character_name}: {str(e)}")
        raise

async def scrape_character_data(character_name: str, db: Session, world: str = None, use_cache: bool = True) -> bool:
    """
    Scrapes character data from Taleon website
    Complexidade: O(1) - requisição HTTP única
    """
    try:
        logger.info(f"Iniciando scraping do personagem: {character_name} (mundo: {world})")
        
        # Obtém o HTML (com cache se disponível)
        # Adiciona timeout adicional aqui também
        html_content, world_detected = await asyncio.wait_for(
            get_character_html(character_name, world, use_cache=use_cache),
            timeout=25  # Timeout de 25 segundos para obter HTML
        )
        logger.info(f"HTML obtido com sucesso para {character_name} no mundo {world_detected}")
        logger.info(f"Primeiros 1000 caracteres do HTML: {html_content[:1000]}")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        logger.info(f"HTML parseado para {character_name}")
        
        # Verifica se a página é uma página de erro (personagem não encontrado)
        # A página de erro contém "Could not find any player" ou "Could not find any guild"
        page_text = soup.get_text().lower()
        if 'could not find any player' in page_text or 'could not find any guild' in page_text:
            logger.warning(f"Personagem {character_name} não encontrado no servidor Taleon (página de erro detectada)")
            return False
        
        # Verifica se há uma tabela de busca (indicando que o personagem não foi encontrado)
        search_table = soup.find('table', {'class': 'table table-striped'})
        if search_table:
            # Verifica se contém mensagem de erro
            search_text = search_table.get_text().lower()
            if 'could not find any player' in search_text:
                logger.warning(f"Personagem {character_name} não encontrado (tabela de busca detectada)")
                return False
        
        # Encontra a tabela com as informações do personagem
        character_table = soup.find('table', {'class': 'table'})
        if not character_table:
            # Tenta encontrar a tabela sem especificar a classe
            character_table = soup.find('table')
            if not character_table:
                logger.error(f"Nenhuma tabela encontrada para: {character_name}")
                logger.error(f"HTML recebido: {html_content[:500]}...")  # Log dos primeiros 500 caracteres
                return False
        
        # Verifica se a tabela encontrada é realmente uma tabela de perfil de personagem
        # Tabelas de perfil têm campos como "Name:", "Level:", "Vocation:", etc.
        table_text = character_table.get_text().lower()
        if 'could not find' in table_text or 'players' in table_text and 'guilds' in table_text:
            logger.warning(f"Tabela encontrada é uma tabela de busca, não um perfil de personagem: {character_name}")
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
                # Se for a linha do nome, pega o nome formatado e o outfit
                if key == 'name':
                    outfit_img = cols[1].find('img', {'class': 'outfitImgTable'})
                    if outfit_img:
                        character_data['outfit'] = outfit_img.get('src', '')
                    # Pega o nome formatado (sem o outfit)
                    value = cols[1].get_text(strip=True)
                else:
                    value = cols[1].text.strip()
                character_data[key] = value
                logger.info(f"Encontrado: {key} = {value}")
        
        # Procura por informações de guild (pode estar em uma seção separada ou link)
        guild_link = soup.find('a', href=re.compile(r'guildprofile\.php'))
        if guild_link:
            guild_name = guild_link.get_text(strip=True)
            if guild_name:
                character_data['guild'] = guild_name
                logger.info(f"Guild encontrada: {guild_name}")
        
        # Log dos dados encontrados
        logger.info(f"Dados encontrados para {character_name}: {character_data}")
        
        # Procura pela tabela "Experience History" para extrair experiência diária
        daily_experience = 0
        # Procura por todas as tabelas e verifica se alguma tem "Experience History" como cabeçalho
        all_tables = soup.find_all('table')
        for table in all_tables:
            # Verifica se a tabela anterior ou um heading próximo menciona "Experience History"
            prev_elements = table.find_all_previous(['h3', 'h4', 'h5', 'strong', 'b'])
            for elem in prev_elements[:5]:  # Verifica os 5 elementos anteriores mais próximos
                if elem and re.search('Experience History', elem.get_text(), re.I):
                    # Encontrou a tabela de Experience History
                    rows = table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            date_col = cols[0].text.strip()
                            exp_col = cols[1].text.strip()
                            # Procura pela linha "Today"
                            if date_col.lower() == 'today':
                                # Remove pontos e vírgulas, mantém apenas números
                                exp_text = re.sub(r'[^\d]', '', exp_col)
                                daily_experience = float(exp_text) if exp_text else 0
                                logger.info(f"Experiência diária (Today) extraída: {daily_experience} de '{exp_col}'")
                                break
                    if daily_experience > 0:
                        break
            if daily_experience > 0:
                break
        
        # Se não encontrou, tenta procurar diretamente por "Today" em qualquer tabela
        if daily_experience == 0:
            for table in all_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        date_col = cols[0].text.strip().lower()
                        if 'today' in date_col:
                            exp_col = cols[1].text.strip()
                            exp_text = re.sub(r'[^\d]', '', exp_col)
                            daily_experience = float(exp_text) if exp_text else 0
                            logger.info(f"Experiência diária (Today) extraída (método alternativo): {daily_experience} de '{exp_col}'")
                            break
                if daily_experience > 0:
                    break
        
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
                character.world = world_detected  # Usa o mundo detectado pela URL
                character.guild = character_data.get('guild', '')  # Extrai guild se disponível
                
                # Baixa e salva o outfit localmente
                outfit_url = character_data.get('outfit', '')
                if outfit_url:
                    try:
                        local_outfit_path = await download_outfit(outfit_url, character.id, world_detected)
                        character.outfit = local_outfit_path
                        logger.info(f"Outfit salvo localmente: {local_outfit_path}")
                    except Exception as e:
                        logger.error(f"Erro ao baixar outfit: {str(e)}")
                        character.outfit = outfit_url  # Mantém URL original em caso de erro
                else:
                    character.outfit = ''
                
                character.name = character_data.get('name', character_name)  # Atualiza o nome formatado
                
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
                        daily_experience=daily_experience,
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
        total = len(characters)
        logger.info(f"Iniciando atualização de {total} personagens")
        success_count = 0
        error_count = 0
        
        timeout_seconds = 30  # Timeout de 30 segundos por personagem
        
        for idx, character in enumerate(characters, 1):
            logger.info(f"[{idx}/{total}] Atualizando personagem: {character.name}")
            try:
                # Adiciona timeout para evitar travar em um personagem
                try:
                    result = await asyncio.wait_for(
                        scrape_character_data(character.name, db, character.world, use_cache=False),
                        timeout=timeout_seconds
                    )
                    if result:
                        success_count += 1
                        logger.info(f"[{idx}/{total}] Personagem {character.name} atualizado com sucesso")
                    else:
                        error_count += 1
                        logger.warning(f"[{idx}/{total}] Falha ao atualizar {character.name}")
                except asyncio.TimeoutError:
                    error_count += 1
                    logger.error(f"[{idx}/{total}] Timeout ao atualizar {character.name} (>{timeout_seconds}s)")
                except Exception as e:
                    error_count += 1
                    logger.error(f"[{idx}/{total}] Erro ao atualizar {character.name}: {str(e)}")
            except Exception as e:
                error_count += 1
                logger.error(f"[{idx}/{total}] Erro inesperado ao processar {character.name}: {str(e)}")
            
            # Adiciona um delay entre as requisições para não sobrecarregar o servidor
            await asyncio.sleep(2)
        
        logger.info(f"Atualização completa finalizada. Total: {total}, Sucesso: {success_count}, Erros: {error_count}")
    finally:
        db.close()
