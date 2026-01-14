from sqlalchemy import Column, String, Boolean, Enum
import enum
from .base import BaseModel

class ConstructionProgress(BaseModel):
    __tablename__ = "construction_progress"

    name = Column(String(50), unique=True, index=True, nullable=False)
    type = Column(String(255), nullable=False)
    progress = Column(String(255), nullable=False)
    creator = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<ConstructionProgress(name={self.name}, type={self.type})>"