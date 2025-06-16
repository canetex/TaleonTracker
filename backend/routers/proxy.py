from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
import httpx
import logging
from urllib.parse import urljoin

router = APIRouter()
logger = logging.getLogger(__name__)

BASE_URL = "https://san.taleon.online"

@router.get("/taleon/{path:path}")
async def proxy_taleon(path: str, request: Request):
    try:
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

        async with httpx.AsyncClient() as client:
            response = await client.get(
                full_url,
                params=query_params,
                headers=headers,
                follow_redirects=True
            )
            
            logger.info(f"Proxy response status: {response.status_code}")
            
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
    except Exception as e:
        logger.error(f"Erro no proxy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 