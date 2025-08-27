from abc import ABC, abstractmethod
from typing import List, Optional
from domain.model.request_log import RequestLog

class ServiceLogRepository(ABC):
    @abstractmethod
    async def save(self, log: RequestLog) -> RequestLog:
        """Save a request log"""
        pass
    
    @abstractmethod
    async def find_by_id(self, log_id: int) -> Optional[RequestLog]:
        """Find log by ID"""
        pass
    
    @abstractmethod
    async def find_by_event_type(self, event_type: str) -> List[RequestLog]:
        """Find logs by event type"""
        pass
    
    @abstractmethod
    async def find_all(self) -> List[RequestLog]:
        """Find all logs"""
        pass