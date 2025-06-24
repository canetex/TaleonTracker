from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base

class CharacterHistory(Base):
    __tablename__ = "character_history"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    level = Column(Integer)
    experience = Column(Float)
    daily_experience = Column(Float, default=0)
    deaths = Column(Integer, default=0)
    timestamp = Column(DateTime)
    
    character = relationship("Character", back_populates="history") 