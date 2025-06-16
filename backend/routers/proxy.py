from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
import requests
import logging
from urllib.parse import urljoin

router = APIRouter()
logger = logging.getLogger(__name__)

BASE_URL = "https://san.taleon.online"

@router.get("/taleon/{path:path}")
async def proxy_taleon(path: str, request: Request):
    try:
        # Constrói a URL completa
        url = urljoin(BASE_URL, path)
        
        # Obtém os parâmetros de query da requisição original
        query_params = str(request.query_params)
        if query_params:
            url = f"{url}?{query_params}"
        
        logger.info(f"Proxy: Requisição para {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': BASE_URL
        }
        
        # Faz a requisição
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Prepara os headers da resposta
        response_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Expose-Headers': '*',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
        
        # Adiciona os headers originais da resposta
        for key, value in response.headers.items():
            if key.lower() not in ['content-encoding', 'content-length', 'transfer-encoding']:
                response_headers[key] = value
        
        logger.info(f"Proxy: Resposta recebida com status {response.status_code}")
        
        return Response(
            content=response.content,
            media_type=response.headers.get('content-type', 'text/html'),
            headers=response_headers
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição proxy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao acessar o site do Taleon: {str(e)}")
    except Exception as e:
        logger.error(f"Erro inesperado no proxy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 