from datetime import datetime
from typing import Optional
from dataclasses import dataclass

@dataclass
class RequestLog:
    id: Optional[int] = None
    event_type: str = ""
    client_ip: Optional[str] = None
    timestamp: datetime = None
    metadata: Optional[dict] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()