from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class CharacterHistory(Base):
    __tablename__ = "character_history"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    level = Column(Integer)
    experience = Column(Integer)
    timestamp = Column(DateTime)
    
    character = relationship("Character", back_populates="history") 