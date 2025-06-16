from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from .character_history import CharacterHistory

class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    level = Column(Integer)
    vocation = Column(String)
    world = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    history = relationship("CharacterHistory", back_populates="character", cascade="all, delete-orphan")
