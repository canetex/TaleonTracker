from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class CharacterFavorite(Base):
    __tablename__ = "character_favorites"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    character = relationship("Character", backref="favorite")

