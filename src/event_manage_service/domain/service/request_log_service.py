from typing import Dict, Any, List, Optional
from event_manage_service.domain.model.request_log import RequestLog

class RequestLogService:
    def create_request_log(self, event_type: str, metadata: Dict[str, Any] = None, client_ip: str = None) -> RequestLog:
        """Create a new request log with business rules"""
        return RequestLog(
            event_type=event_type,
            client_ip=client_ip,
            metadata=metadata or {}
        )
    
    def validate_log_entry(self, log: RequestLog) -> bool:
        """Validate log entry before saving"""
        return bool(log.event_type and log.client_ip)
    
    def filter_logs_by_event_type(self, logs: List[RequestLog], event_type: str) -> List[RequestLog]:
        """Filter logs by event type"""
        return [log for log in logs if log.event_type == event_type]