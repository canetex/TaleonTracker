from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.character import Character
from schemas.character import CharacterCreate, CharacterResponse
from services.scraper import scrape_character_data

router = APIRouter()

@router.post("/scrape", response_model=CharacterResponse)
def scrape_character(character_name: str, db: Session = Depends(get_db)):
    try:
        if not scrape_character_data(character_name, db):
            raise HTTPException(status_code=500, detail="Erro ao obter dados do personagem")
        character = db.query(Character).filter(Character.name == character_name).first()
        return character
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{character_name}", response_model=CharacterResponse)
def get_character(character_name: str, db: Session = Depends(get_db)):
    character = db.query(Character).filter(Character.name == character_name).first()
    if not character:
        raise HTTPException(status_code=404, detail="Personagem não encontrado")
    return character

@router.get("/", response_model=List[CharacterResponse])
def list_characters(db: Session = Depends(get_db)):
    return db.query(Character).all()
