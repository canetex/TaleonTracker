from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
import httpx
import logging
from urllib.parse import urljoin, urlparse
from fastapi.middleware.throttling import ThrottlingMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
import time
from typing import Optional

router = APIRouter()
logger = logging.getLogger(__name__)

BASE_URL = "https://san.taleon.online"
TIMEOUT = 10.0  # timeout em segundos
ALLOWED_PATHS = [
    "characterprofile.php",
    "guilds.php",
    "highscores.php",
    "onlinelist.php"
]

def is_valid_path(path: str) -> bool:
    """Verifica se o path é válido e permitido"""
    parsed = urlparse(path)
    return any(allowed in parsed.path for allowed in ALLOWED_PATHS)

@router.get("/taleon/{path:path}")
@cache(expire=300)  # Cache por 5 minutos
async def proxy_taleon(path: str, request: Request):
    try:
        # Valida o path
        if not is_valid_path(path):
            raise HTTPException(status_code=400, detail="Path não permitido")

        # Constrói a URL completa
        full_url = urljoin(BASE_URL, path)
        logger.info(f"Proxy request to: {full_url}")

        # Obtém os parâmetros da query
        query_params = dict(request.query_params)
        
        # Configura os headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                full_url,
                params=query_params,
                headers=headers,
                follow_redirects=True
            )
            
            logger.info(f"Proxy response status: {response.status_code}")
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Erro ao acessar o servidor Taleon")
            
            # Cria a resposta com os headers apropriados
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers={
                    "Content-Type": response.headers.get("content-type", "text/html"),
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0"
                }
            )
    except httpx.TimeoutException:
        logger.error("Timeout ao acessar o servidor Taleon")
        raise HTTPException(status_code=504, detail="Timeout ao acessar o servidor Taleon")
    except httpx.RequestError as e:
        logger.error(f"Erro na requisição: {str(e)}")
        raise HTTPException(status_code=502, detail="Erro ao acessar o servidor Taleon")
    except Exception as e:
        logger.error(f"Erro no proxy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 