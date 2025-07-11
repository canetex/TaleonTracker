from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.character import Character
from schemas.character import CharacterCreate, CharacterResponse
from services.scraper import scrape_character_data
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=CharacterResponse)
async def create_character(character: CharacterCreate, db: Session = Depends(get_db)):
    try:
        # Verifica se o personagem já existe
        existing_character = db.query(Character).filter(Character.name == character.name).first()
        if existing_character:
            raise HTTPException(status_code=400, detail="Personagem já existe")

        # Cria o novo personagem
        db_character = Character(
            name=character.name,
            level=0,  # Será atualizado pelo scraper
            vocation="",  # Será atualizado pelo scraper
            world=""  # Será atualizado pelo scraper
        )
        db.add(db_character)
        db.commit()
        db.refresh(db_character)

        # Tenta obter os dados do personagem
        try:
            await scrape_character_data(character.name, db)
        except Exception as e:
            # Se falhar ao obter os dados, pelo menos o personagem foi criado
            logger.error(f"Erro ao obter dados do personagem: {str(e)}")

        return db_character
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar personagem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[CharacterResponse])
async def list_characters(db: Session = Depends(get_db)):
    return db.query(Character).all()

@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: int, db: Session = Depends(get_db)):
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Personagem não encontrado")
    return character

@router.post("/{character_id}/update", response_model=CharacterResponse)
async def update_character(character_id: int, db: Session = Depends(get_db)):
    try:
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise HTTPException(status_code=404, detail="Personagem não encontrado")
        
        logger.info(f"Atualizando personagem: {character.name}")
        
        if not await scrape_character_data(character.name, db):
            logger.error(f"Falha ao atualizar dados do personagem {character.name}")
            raise HTTPException(status_code=500, detail="Erro ao atualizar dados do personagem")
        
        db.refresh(character)
        logger.info(f"Personagem {character.name} atualizado com sucesso")
        return character
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar personagem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{character_id}")
async def delete_character(character_id: int, db: Session = Depends(get_db)):
    try:
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise HTTPException(status_code=404, detail="Personagem não encontrado")
        
        logger.info(f"Excluindo personagem: {character.name}")
        db.delete(character)
        db.commit()
        logger.info(f"Personagem {character.name} excluído com sucesso")
        return {"message": "Personagem excluído com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir personagem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
