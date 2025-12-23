from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import characters, auth, proxy, server_stats
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
import logging
import os

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialização do cache
@app.on_event("startup")
async def startup():
    try:
        redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        logger.info("Cache inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar cache: {str(e)}")
        raise

# Incluir routers
app.include_router(characters.router, prefix="/api/characters", tags=["characters"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(proxy.router, prefix="/api/proxy", tags=["proxy"])
app.include_router(server_stats.router, prefix="/api/stats", tags=["stats"])

# Importar e incluir router de favoritos
from routers import favorites
app.include_router(favorites.router, prefix="/api/favorites", tags=["favorites"])

# Importar e incluir router de ranking
from routers import character_ranking
app.include_router(character_ranking.router, prefix="/api", tags=["ranking"])

# Monta diretório estático para servir outfits
static_dir = "/app/static"
outfits_dir = "/app/static/outfits"
os.makedirs(static_dir, exist_ok=True)
os.makedirs(outfits_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    return {"message": "TaleonTracker API"}

# Rota de health check
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
