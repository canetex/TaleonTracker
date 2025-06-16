from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import requests
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/taleon/{path:path}")
async def proxy_taleon(path: str):
    try:
        url = f"https://san.taleon.online/{path}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://san.taleon.online/'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return Response(
            content=response.content,
            media_type=response.headers.get('content-type', 'text/html'),
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': '*',
            }
        )
    except Exception as e:
        logger.error(f"Erro no proxy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 