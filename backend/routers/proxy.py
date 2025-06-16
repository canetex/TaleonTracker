from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
import requests
import logging
from urllib.parse import urlparse
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

router = APIRouter()
logger = logging.getLogger(__name__)

# Configurações
TALEON_BASE_URL = "https://san.taleon.online"
TIMEOUT = 10  # segundos
ALLOWED_PATHS = [
    "characterprofile.php",
    "guildprofile.php",
    "highscores.php",
    "online.php"
]

def is_valid_path(path: str) -> bool:
    """Verifica se o path está na lista de paths permitidos"""
    return any(allowed in path for allowed in ALLOWED_PATHS)

@router.get("/taleon/{path:path}")
@cache(expire=300)  # Cache por 5 minutos
async def proxy_taleon(path: str, request: Request):
    """
    Proxy para a API do Taleon
    """
    try:
        # Valida o path
        if not is_valid_path(path):
            raise HTTPException(status_code=400, detail="Path não permitido")

        # Constrói a URL completa
        full_url = f"{TALEON_BASE_URL}/{path}"
        
        # Obtém os parâmetros da query
        query_params = dict(request.query_params)
        
        # Log da requisição
        logger.info(f"Proxy request: {full_url} with params: {query_params}")
        
        # Faz a requisição com timeout
        response = requests.get(
            full_url,
            params=query_params,
            timeout=TIMEOUT,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )
        
        # Log do status da resposta
        logger.info(f"Proxy response status: {response.status_code}")
        
        # Verifica o status da resposta
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Erro ao acessar o servidor Taleon")
        
        # Retorna o conteúdo HTML
        return HTMLResponse(
            content=response.text,
            headers={
                "Content-Type": "text/html; charset=utf-8",
                "Cache-Control": "public, max-age=300"
            }
        )
        
    except requests.Timeout:
        logger.error("Timeout ao acessar o servidor Taleon")
        raise HTTPException(status_code=504, detail="Timeout ao acessar o servidor Taleon")
    except requests.RequestException as e:
        logger.error(f"Erro ao acessar o servidor Taleon: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao acessar o servidor Taleon") 