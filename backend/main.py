from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import uvicorn
import os
from dotenv import load_dotenv
from routers import characters, auth, proxy
from services.scraper import scrape_character_data
from services.scheduler import schedule_daily_scrape, setup_scheduler
import logging

# Carrega variáveis de ambiente
load_dotenv()

# Cria as tabelas do banco de dados
from database import engine, Base
Base.metadata.create_all(bind=engine)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TaleonTracker API",
    description="API para rastreamento de personagens do Taleon Online",
    version="1.0.0"
)

# Configuração CORS mais permissiva
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos
    allow_headers=["*"],  # Permite todos os headers
    expose_headers=["*"]  # Expõe todos os headers
)

# Inclui os routers
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(characters.router, prefix="/api/characters", tags=["Personagens"])
app.include_router(proxy.router, prefix="/api/proxy", tags=["Proxy"])

# Inicializa o scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Agenda o scraping diário
schedule_daily_scrape(scheduler)

# Configurar o scheduler
setup_scheduler()

@app.get("/")
async def root():
    return {
        "message": "Bem-vindo à API do TaleonTracker",
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
