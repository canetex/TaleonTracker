from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from database import get_db
from models import Character, CharacterHistory
from services.scraper import scrape_character_data
from schemas.character import CharacterCreate, CharacterResponse, CharacterHistoryResponse

router = APIRouter()

@router.post("/", response_model=CharacterResponse)
def create_character(character: CharacterCreate, db: Session = Depends(get_db)):
    """
    Adiciona um novo personagem para monitoramento.
    """
    # Verifica se o personagem já existe
    db_character = db.query(Character).filter(Character.name == character.name).first()
    if db_character:
        raise HTTPException(status_code=400, detail="Personagem já cadastrado")
    
    # Cria o personagem
    new_character = Character(name=character.name)
    db.add(new_character)
    db.commit()
    db.refresh(new_character)
    
    # Faz o primeiro scraping
    if not scrape_character_data(character.name, db):
        raise HTTPException(status_code=500, detail="Erro ao obter dados do personagem")
    
    return new_character

@router.get("/", response_model=List[CharacterResponse])
def get_characters(db: Session = Depends(get_db)):
    """
    Retorna a lista de todos os personagens cadastrados.
    """
    return db.query(Character).all()

@router.get("/{character_id}/history", response_model=List[CharacterHistoryResponse])
def get_character_history(
    character_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Retorna o histórico de um personagem nos últimos N dias.
    """
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Personagem não encontrado")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    history = db.query(CharacterHistory)\
        .filter(CharacterHistory.character_id == character_id)\
        .filter(CharacterHistory.timestamp >= start_date)\
        .order_by(CharacterHistory.timestamp.desc())\
        .all()
    
    return history

@router.post("/{character_id}/update")
def update_character(character_id: int, db: Session = Depends(get_db)):
    """
    Força uma atualização manual dos dados do personagem.
    """
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Personagem não encontrado")
    
    if not scrape_character_data(character.name, db):
        raise HTTPException(status_code=500, detail="Erro ao atualizar dados do personagem")
    
    return {"message": "Dados atualizados com sucesso"}

@router.delete("/{character_id}")
def delete_character(character_id: int, db: Session = Depends(get_db)):
    """
    Remove um personagem do monitoramento.
    """
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Personagem não encontrado")
    
    db.delete(character)
    db.commit()
    
    return {"message": "Personagem removido com sucesso"} 