"""
Serviço para buscar experiência total de personagens
Complexidade: O(1) - requisições HTTP únicas
"""
import aiohttp
from bs4 import BeautifulSoup
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Tabela de experiência por level (baseada em https://www.tibia.com/library/?subtopic=experiencetable)
# Valores aproximados para os primeiros níveis
EXPERIENCE_TABLE = {
    1: 0,
    2: 100,
    3: 185,
    4: 274,
    5: 368,
    6: 466,
    7: 568,
    8: 674,
    9: 784,
    10: 897,
    11: 1014,
    12: 1135,
    13: 1260,
    14: 1389,
    15: 1522,
    16: 1659,
    17: 1800,
    18: 1945,
    19: 2094,
    20: 2247,
    21: 2404,
    22: 2565,
    23: 2730,
    24: 2899,
    25: 3072,
    26: 3249,
    27: 3430,
    28: 3615,
    29: 3804,
    30: 3997,
    31: 4194,
    32: 4395,
    33: 4600,
    34: 4809,
    35: 5022,
    36: 5239,
    37: 5460,
    38: 5685,
    39: 5914,
    40: 6147,
    41: 6384,
    42: 6625,
    43: 6870,
    44: 7119,
    45: 7372,
    46: 7629,
    47: 7890,
    48: 8155,
    49: 8424,
    50: 8697,
}

def calculate_experience_for_level(level: int) -> float:
    """
    Calcula a experiência mínima necessária para um determinado level
    Fórmula aproximada baseada na tabela do Tibia
    Complexidade: O(1)
    """
    if level <= 0:
        return 0.0
    
    if level <= 50:
        return float(EXPERIENCE_TABLE.get(level, 0))
    
    # Para levels acima de 50, usa fórmula aproximada
    # Fórmula: exp = 50 * level^3 - 150 * level^2 + 400 * level
    if level <= 100:
        return float(50 * level**3 - 150 * level**2 + 400 * level)
    
    # Para levels acima de 100, usa fórmula mais precisa
    # Fórmula aproximada: exp = 50 * level^3 - 150 * level^2 + 400 * level
    return float(50 * level**3 - 150 * level**2 + 400 * level)

async def get_experience_from_highscores(character_name: str, world: str) -> Optional[float]:
    """
    Busca experiência total do personagem na página de highscores
    Retorna None se não encontrar
    Complexidade: O(1) - requisição HTTP única
    """
    try:
        world_url = f"https://{world}.taleon.online" if world else "https://san.taleon.online"
        url = f"{world_url}/highscores.php"
        
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
                    logger.warning(f"Erro ao acessar highscores: status {response.status}")
                    return None
                
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Procura pela tabela de highscores
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            # Procura pelo nome do personagem
                            cell_text = ' '.join([cell.get_text(strip=True) for cell in cells])
                            if character_name.lower() in cell_text.lower():
                                # Tenta extrair a experiência (geralmente está em uma das colunas)
                                for cell in cells:
                                    cell_text = cell.get_text(strip=True)
                                    # Remove pontos e vírgulas, mantém apenas números
                                    exp_text = re.sub(r'[^\d]', '', cell_text)
                                    if exp_text and len(exp_text) > 3:  # Experiência geralmente tem mais de 3 dígitos
                                        try:
                                            experience = float(exp_text)
                                            logger.info(f"Experiência encontrada no highscores para {character_name}: {experience}")
                                            return experience
                                        except ValueError:
                                            continue
                
                logger.warning(f"Personagem {character_name} não encontrado no highscores")
                return None
    except Exception as e:
        logger.error(f"Erro ao buscar experiência no highscores para {character_name}: {str(e)}")
        return None

def get_experience_from_level_table(level: int) -> float:
    """
    Retorna a experiência mínima esperada para um determinado level
    baseado na tabela de experiência do Tibia
    Complexidade: O(1)
    """
    return calculate_experience_for_level(level)

