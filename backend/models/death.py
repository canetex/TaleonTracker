from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Death(Base):
    """
    Modelo para armazenar informações de mortes de personagens
    Complexidade: O(1) - operações CRUD simples
    """
    __tablename__ = "deaths"

    id = Column(Integer, primary_key=True, index=True)
    character_name = Column(String, index=True)  # Nome do personagem (pode não estar no banco ainda)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=True)  # Relacionamento opcional
    level = Column(Integer)  # Level no momento da morte
    world = Column(String)  # Mundo onde ocorreu a morte
    death_date = Column(DateTime)  # Data/hora da morte
    timestamp = Column(DateTime, default=datetime.utcnow)  # Quando foi registrado no sistema
    
    # Relacionamento opcional com Character
    character = relationship("Character", foreign_keys=[character_id])

