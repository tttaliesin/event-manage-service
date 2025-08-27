from typing import List, Dict, Any
from application.port.inbound.sevice_log_inbound_port import ServiceLogInboundPort
from application.port.outbound.service_log_repository import ServiceLogRepository
from domain.service.request_log_service import RequestLogService
from domain.model.request_log import RequestLog

class RequestLogUseCase(ServiceLogInboundPort):
    def __init__(self, repository: ServiceLogRepository, domain_service: RequestLogService):
        self.repository = repository
        self.domain_service = domain_service
    
    async def get_logs_by_event_type(self, event_type: str) -> List[RequestLog]:
        """이벤트 타입으로 로그 조회"""
        return await self.repository.find_by_event_type(event_type)
    
    async def get_all_logs(self) -> List[RequestLog]:
        """모든 로그 조회"""
        return await self.repository.find_all()