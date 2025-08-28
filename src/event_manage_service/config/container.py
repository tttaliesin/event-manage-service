import socketio
import logging
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from event_manage_service.config.settings import Settings

from event_manage_service.domain.service.request_log_service import RequestLogService
from event_manage_service.domain.service.stream_management_service import StreamManagementService

from event_manage_service.application.usecases.request_log_usecase import RequestLogUseCase
from event_manage_service.application.usecases.broadcast_stream_usecase import BroadcastStreamUseCase

from event_manage_service.adapter.outbound.persistence.service_log_repository_impl import ServiceLogRepositoryImpl
from event_manage_service.adapter.outbound.messaging.socketio_publisher import SocketIOPublisher

from event_manage_service.config.constants import EmitEvent, Rooms

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    settings = Settings()
    
    # Engine.IO 로거 레벨 설정
    logging.getLogger('engineio.server').setLevel(logging.DEBUG)
    logging.getLogger('socketio.server').setLevel(logging.DEBUG)
    
    # Constants
    emit_event = providers.Factory(EmitEvent)
    rooms = providers.Factory(Rooms)
    
    # Domain services
    request_log_domain_service = providers.Factory(
        RequestLogService
    )
    stream_management_domain_service = providers.Singleton(
        StreamManagementService
    )
    
    # adapter
    db_engine = providers.Singleton(
        create_async_engine,
        settings.database_url,
    )
    session_maker = providers.Singleton(
        sessionmaker,
        db_engine,
        class_=AsyncSession,
        expire_on_commit=True
    )
    service_log_repository_impl = providers.Factory(
        ServiceLogRepositoryImpl,
        session_maker=session_maker
    )
    
    sio = providers.Singleton(
        socketio.AsyncServer,
        async_mode='asgi',
        cors_allowed_origins="*",
        logger=True,
        engineio_logger=False
    )
    
    socketio_publisher = providers.Factory(
        SocketIOPublisher,
        sio=sio,
        emit_event=emit_event,
        rooms=rooms,
        stream_management_service=stream_management_domain_service
    )
    
    # Use cases
    event_logger = providers.Factory(
        RequestLogUseCase,
        repository=service_log_repository_impl,
        domain_service=request_log_domain_service
    )
    
    broadcast_stream_usecase = providers.Factory(
        BroadcastStreamUseCase,
        event_publisher=socketio_publisher,
        service_log_repository=service_log_repository_impl,
        stream_management_service=stream_management_domain_service,
        request_log_service=request_log_domain_service,
        rooms=rooms
    )


