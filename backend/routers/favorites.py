from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.character_favorite import CharacterFavorite
from models.character import Character
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/{character_id}")
async def add_favorite(character_id: int, db: Session = Depends(get_db)):
    """
    Adiciona um personagem aos favoritos
    Complexidade: O(1)
    """
    try:
        # Verifica se o personagem existe
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise HTTPException(status_code=404, detail="Personagem não encontrado")
        
        # Verifica se já é favorito
        existing = db.query(CharacterFavorite).filter(CharacterFavorite.character_id == character_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Personagem já está nos favoritos")
        
        favorite = CharacterFavorite(character_id=character_id)
        db.add(favorite)
        db.commit()
        return {"message": "Personagem adicionado aos favoritos"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao adicionar favorito: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{character_id}")
async def remove_favorite(character_id: int, db: Session = Depends(get_db)):
    """
    Remove um personagem dos favoritos
    Complexidade: O(1)
    """
    try:
        favorite = db.query(CharacterFavorite).filter(CharacterFavorite.character_id == character_id).first()
        if not favorite:
            raise HTTPException(status_code=404, detail="Personagem não está nos favoritos")
        
        db.delete(favorite)
        db.commit()
        return {"message": "Personagem removido dos favoritos"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover favorito: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_favorites(db: Session = Depends(get_db)):
    """
    Lista todos os personagens favoritos
    Complexidade: O(n) onde n é o número de favoritos
    """
    try:
        favorites = db.query(CharacterFavorite).all()
        return [{"character_id": fav.character_id, "created_at": fav.created_at} for fav in favorites]
    except Exception as e:
        logger.error(f"Erro ao listar favoritos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

