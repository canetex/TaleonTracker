"""
Serviço para fazer scraping de mortes de personagens
Complexidade: O(n) onde n é o número de mortes na página
"""
import aiohttp
from bs4 import BeautifulSoup
import re
import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from models.death import Death
from models.character import Character

logger = logging.getLogger(__name__)

async def scrape_deaths(world: str, db: Session) -> List[Dict]:
    """
    Faz scraping da página de mortes e retorna lista de mortes encontradas
    Complexidade: O(n) onde n é o número de mortes na página
    """
    try:
        world_url = f"https://{world}.taleon.online"
        url = f"{world_url}/deaths.php"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        timeout = aiohttp.ClientTimeout(total=20, connect=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    logger.warning(f"Erro ao acessar deaths.php: status {response.status}")
                    return []
                
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                deaths = []
                
                # Procura pela tabela de mortes (geralmente tem id="deathsTable" ou classe específica)
                table = soup.find('table', {'id': 'deathsTable'})
                if not table:
                    # Tenta encontrar qualquer tabela que contenha informações de mortes
                    tables = soup.find_all('table')
                    for t in tables:
                        if 'death' in t.get_text().lower() or 'killed' in t.get_text().lower():
                            table = t
                            break
                
                if not table:
                    logger.warning(f"Tabela de mortes não encontrada em {url}")
                    return []
                
                rows = table.find_all('tr')
                for row in rows[1:]:  # Pula o cabeçalho
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 3:
                        continue
                    
                    try:
                        # Extrai informações da morte
                        # Formato típico: [Data, Personagem, Level, ...]
                        death_data = {}
                        
                        # Procura por link do personagem
                        character_link = row.find('a', href=re.compile(r'characterprofile\.php'))
                        if character_link:
                            href = character_link.get('href', '')
                            # Extrai nome da URL
                            match = re.search(r'name=([^&]+)', href)
                            if match:
                                from urllib.parse import unquote
                                character_name = unquote(match.group(1))
                                death_data['character_name'] = character_name
                        
                        # Se não encontrou no link, tenta pegar do texto
                        if 'character_name' not in death_data:
                            for cell in cells:
                                cell_text = cell.get_text(strip=True)
                                # Verifica se parece um nome de personagem (não é data, não é número puro)
                                if cell_text and len(cell_text) > 2 and len(cell_text) < 50:
                                    if not re.match(r'^\d+[/-]\d+[/-]\d+', cell_text):  # Não é data
                                        if not re.match(r'^\d+$', cell_text):  # Não é apenas número
                                            death_data['character_name'] = cell_text
                                            break
                        
                        # Extrai level
                        for cell in cells:
                            cell_text = cell.get_text(strip=True)
                            # Procura por número que pode ser level (geralmente entre 1 e 2000)
                            if re.match(r'^\d+$', cell_text):
                                level = int(cell_text)
                                if 1 <= level <= 2000:
                                    death_data['level'] = level
                                    break
                        
                        # Extrai data
                        for cell in cells:
                            cell_text = cell.get_text(strip=True)
                            # Procura por formato de data
                            date_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', cell_text)
                            if date_match:
                                try:
                                    day, month, year = date_match.groups()
                                    if len(year) == 2:
                                        year = '20' + year
                                    # Tenta parsear a data
                                    death_data['death_date'] = datetime.strptime(
                                        f"{day}/{month}/{year}", "%d/%m/%Y"
                                    )
                                    break
                                except ValueError:
                                    continue
                        
                        # Se não encontrou data específica, usa data atual
                        if 'death_date' not in death_data:
                            death_data['death_date'] = datetime.utcnow()
                        
                        # Valida se tem informações mínimas
                        if 'character_name' in death_data and 'level' in death_data:
                            death_data['world'] = world
                            deaths.append(death_data)
                            logger.info(f"Morte encontrada: {death_data['character_name']} (level {death_data['level']}) em {world}")
                    except Exception as e:
                        logger.warning(f"Erro ao processar linha de morte: {str(e)}")
                        continue
                
                logger.info(f"Total de {len(deaths)} mortes encontradas em {world}")
                return deaths
    except Exception as e:
        logger.error(f"Erro ao fazer scraping de mortes em {world}: {str(e)}")
        return []

async def save_deaths(deaths: List[Dict], db: Session) -> int:
    """
    Salva mortes no banco de dados, evitando duplicatas
    Complexidade: O(n) onde n é o número de mortes
    """
    saved_count = 0
    for death_data in deaths:
        try:
            # Verifica se já existe (evita duplicatas)
            existing = db.query(Death).filter(
                Death.character_name == death_data['character_name'],
                Death.death_date == death_data['death_date'],
                Death.world == death_data['world']
            ).first()
            
            if existing:
                continue
            
            # Tenta encontrar o character_id se o personagem existir
            character = db.query(Character).filter(
                Character.name == death_data['character_name']
            ).first()
            
            character_id = character.id if character else None
            
            # Cria novo registro de morte
            death = Death(
                character_name=death_data['character_name'],
                character_id=character_id,
                level=death_data['level'],
                world=death_data['world'],
                death_date=death_data['death_date']
            )
            
            db.add(death)
            saved_count += 1
        except Exception as e:
            logger.error(f"Erro ao salvar morte: {str(e)}")
            db.rollback()
            continue
    
    try:
        db.commit()
        logger.info(f"{saved_count} mortes salvas no banco de dados")
    except Exception as e:
        logger.error(f"Erro ao commitar mortes: {str(e)}")
        db.rollback()
    
    return saved_count

