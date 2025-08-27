from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from event_manage_service.domain.model.request_log import RequestLog

class ServiceLogInboundPort(ABC):
    @abstractmethod
    async def get_logs_by_event_type(self, event_type: str) -> List[RequestLog]:
        """Get logs by event type"""
        pass
    
    @abstractmethod
    async def get_all_logs(self) -> List[RequestLog]:
        """Get all logs"""
        pass