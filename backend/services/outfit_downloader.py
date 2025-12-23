"""
Serviço para download e salvamento de outfits de personagens
Complexidade: O(1) - download de arquivo único
"""
import aiohttp
import os
from pathlib import Path
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

# Diretório para salvar outfits
OUTFITS_DIR = Path("/app/static/outfits")
OUTFITS_DIR.mkdir(parents=True, exist_ok=True)

async def download_outfit(outfit_url: str, character_id: int, world: str) -> str:
    """
    Baixa e salva a imagem do outfit localmente
    Retorna o caminho relativo do arquivo salvo
    """
    try:
        if not outfit_url:
            return ""
        
        # Se já é um caminho local, retorna como está
        if outfit_url.startswith("/static/outfits/") or outfit_url.startswith("static/outfits/"):
            return outfit_url
        
        # Extrai o nome do arquivo da URL
        parsed_url = urlparse(outfit_url)
        filename = os.path.basename(parsed_url.path)
        
        # Se não tem extensão, adiciona .png
        if not filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            filename = f"{filename}.png"
        
        # Cria nome único: character_id_world_filename
        local_filename = f"{character_id}_{world}_{filename}"
        local_path = OUTFITS_DIR / local_filename
        
        # Se o arquivo já existe, retorna o caminho
        if local_path.exists():
            return f"/static/outfits/{local_filename}"
        
        # Faz o download da imagem
        async with aiohttp.ClientSession() as session:
            # Se a URL é relativa, precisa construir a URL completa
            if outfit_url.startswith("/"):
                base_url = "https://san.taleon.online" if world.lower() == "san" else "https://aura.taleon.online"
                full_url = f"{base_url}{outfit_url}"
            elif not outfit_url.startswith("http"):
                base_url = "https://san.taleon.online" if world.lower() == "san" else "https://aura.taleon.online"
                full_url = f"{base_url}/{outfit_url.lstrip('/')}"
            else:
                full_url = outfit_url
            
            logger.info(f"Baixando outfit de {full_url} para {local_path}")
            
            async with session.get(full_url, timeout=10) as response:
                response.raise_for_status()
                content = await response.read()
                
                # Salva o arquivo (usa modo síncrono para compatibilidade)
                with open(local_path, 'wb') as f:
                    f.write(content)
                
                logger.info(f"Outfit salvo em {local_path}")
                return f"/static/outfits/{local_filename}"
    
    except Exception as e:
        logger.error(f"Erro ao baixar outfit {outfit_url}: {str(e)}")
        # Retorna a URL original em caso de erro
        return outfit_url

