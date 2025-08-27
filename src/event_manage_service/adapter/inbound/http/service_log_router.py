from fastapi import APIRouter, Depends
from typing import List
from dependency_injector.wiring import inject, Provide

from event_manage_service.application.port.inbound.sevice_log_inbound_port import ServiceLogInboundPort
from event_manage_service.application.dto.service_log_dto import RequestLogResponseDTO
from event_manage_service.config.container import Container

router = APIRouter(prefix="/logs", tags=["logs"])

@router.get("/", response_model=List[RequestLogResponseDTO])
@inject
async def get_all_logs(
    event_logger: ServiceLogInboundPort = Depends(Provide[Container.event_logger])
):
    logs = await event_logger.get_all_logs()
    return [RequestLogResponseDTO(
        id=log.id,
        event_type=log.event_type,
        client_ip=log.client_ip,
        timestamp=log.timestamp,
        metadata=log.metadata
    ) for log in logs]

@router.get("/event/{event_type}", response_model=List[RequestLogResponseDTO])
@inject
async def get_logs_by_event_type(
    event_type: str,
    event_logger: ServiceLogInboundPort = Depends(Provide[Container.event_logger])
):
    logs = await event_logger.get_logs_by_event_type(event_type)
    return [RequestLogResponseDTO(
        id=log.id,
        event_type=log.event_type,
        client_ip=log.client_ip,
        timestamp=log.timestamp,
        metadata=log.metadata
    ) for log in logs]