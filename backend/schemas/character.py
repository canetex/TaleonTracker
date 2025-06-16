from pydantic import BaseModel
from datetime import datetime

class CharacterBase(BaseModel):
    name: str
    level: int
    vocation: str
    world: str

class CharacterCreate(CharacterBase):
    pass

class CharacterResponse(CharacterBase):
    id: int
    last_updated: datetime

    class Config:
        from_attributes = True
