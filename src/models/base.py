from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.sql import func, expression
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime
from config.database import Base
from typing import Optional

class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())