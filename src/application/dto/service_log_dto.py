from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class RequestLogCreateDTO(BaseModel):
    event_type: str
    client_ip: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class RequestLogResponseDTO(BaseModel):
    id: Optional[int]
    event_type: str
    client_ip: Optional[str] = None
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class LogQueryDTO(BaseModel):
    event_type: Optional[str] = None
    limit: Optional[int] = 100