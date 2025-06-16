from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import characters, auth, proxy
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.1.200:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(characters.router, prefix="/api/characters", tags=["characters"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(proxy.router, prefix="/api/proxy", tags=["proxy"])

@app.get("/")
async def root():
    return {"message": "TaleonTracker API"}
