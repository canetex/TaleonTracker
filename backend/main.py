from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import uvicorn
import os
from dotenv import load_dotenv

from database import engine, Base
from routers import characters, auth
from services.scraper import scrape_character_data
from services.scheduler import schedule_daily_scrape

# Carrega variáveis de ambiente
load_dotenv()

# Cria as tabelas do banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaleonTracker API",
    description="API para rastreamento de personagens do Taleon Online",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui os routers
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(characters.router, prefix="/api/characters", tags=["Personagens"])

# Inicializa o scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Agenda o scraping diário
schedule_daily_scrape(scheduler)

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
