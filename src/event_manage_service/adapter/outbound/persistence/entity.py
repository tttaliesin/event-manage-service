from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import JSON
from datetime import datetime

Base = declarative_base()

class RequestLogEntity(Base):
    __tablename__ = "request_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(100), nullable=False)
    client_ip = Column(String(45), nullable=True)  # IPv6 지원을 위해 45자
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    request_metadata = Column(Text, nullable=True)
