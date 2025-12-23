from sqlalchemy import Column, Integer, String, DateTime, Float
from database import Base
from datetime import datetime

class ServerStats(Base):
    __tablename__ = "server_stats"

    id = Column(Integer, primary_key=True, index=True)
    world = Column(String, index=True)
    total_experience = Column(Float, default=0)
    active_characters = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<ServerStats(world={self.world}, exp={self.total_experience}, active={self.active_characters}, timestamp={self.timestamp})>"

