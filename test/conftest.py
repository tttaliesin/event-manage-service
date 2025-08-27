import pytest
import asyncio
from typing import Generator, Any
from datetime import datetime
from unittest.mock import Mock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector import containers, providers

from event_manage_service.domain.model.request_log import RequestLog
from event_manage_service.domain.service.request_log_service import RequestLogService
from event_manage_service.domain.service.stream_management_service import StreamManagementService
from event_manage_service.application.usecases.request_log_usecase import RequestLogUseCase
from event_manage_service.application.usecases.broadcast_stream_usecase import BroadcastStreamUseCase
from event_manage_service.config.constants import EmitEvent, Rooms


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """테스트 세션에 대한 기본 이벤트 루프 인스턴스 생성"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_session() -> Mock:
    """SQLAlchemy 비동기 세션 모킹"""
    session = Mock(spec=AsyncSession)
    session.add = Mock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    return session


@pytest.fixture
def sample_request_log() -> RequestLog:
    """테스트용 RequestLog 인스턴스 샘플"""
    return RequestLog(
        id=1,
        event_type="test_event",
        client_ip="192.168.1.1",
        timestamp=datetime.utcnow(),
        metadata={"test": "data"}
    )


@pytest.fixture
def request_log_service():
    """RequestLogService 인스턴스"""
    return RequestLogService()


@pytest.fixture
def stream_management_service():
    """StreamManagementService 인스턴스"""
    return StreamManagementService()


@pytest.fixture
def mock_service_log_repository():
    """목 서비스 로그 리포지토리"""
    repository = Mock()
    repository.save = AsyncMock()
    repository.find_all = AsyncMock()
    repository.find_by_client_ip = AsyncMock()
    repository.find_by_event_type = AsyncMock()
    return repository


@pytest.fixture
def mock_socketio_outbound_port():
    """목 SocketIO 아웃바운드 포트"""
    port = Mock()
    port.request_client_metadata = AsyncMock()
    port.set_stream_service = AsyncMock()
    port.add_client_to_room = AsyncMock()
    port.remove_client_from_room = AsyncMock()
    port.remove_client_from_all_rooms = AsyncMock()
    port.send_capture_start_command = AsyncMock()
    port.send_capture_stop_command = AsyncMock()
    port.broadcast_video_frame = AsyncMock()
    port.request_capure_status = AsyncMock()
    port.broadcast_caputere_status = AsyncMock()
    port.get_sid_ip = Mock(return_value="192.168.1.1")
    return port


@pytest.fixture
def emit_event():
    """EmitEvent 상수"""
    return EmitEvent()


@pytest.fixture
def rooms():
    """Rooms 상수"""
    return Rooms()


@pytest.fixture
def request_log_usecase(mock_service_log_repository, request_log_service):
    """모킹된 의존성을 가진 RequestLogUseCase 인스턴스"""
    return RequestLogUseCase(
        repository=mock_service_log_repository,
        domain_service=request_log_service
    )


@pytest.fixture
def broadcast_stream_usecase(
    mock_socketio_outbound_port,
    mock_service_log_repository,
    stream_management_service,
    request_log_service,
    rooms
):
    """모킹된 의존성을 가진 BroadcastStreamUseCase 인스턴스"""
    return BroadcastStreamUseCase(
        socketio_outbound_port=mock_socketio_outbound_port,
        service_log_repository=mock_service_log_repository,
        stream_management_service=stream_management_service,
        request_log_service=request_log_service,
        rooms=rooms
    )


@pytest.fixture
def mock_socketio_server():
    """목 SocketIO 서버"""
    sio = Mock()
    sio.emit = AsyncMock()
    sio.enter_room = AsyncMock()
    sio.leave_room = AsyncMock()
    sio.get_session = Mock()
    return sio


class TestContainer(containers.DeclarativeContainer):
    """테스트 DI 컨테이너"""
    
    # 서비스
    request_log_service = providers.Factory(RequestLogService)
    stream_management_service = providers.Singleton(StreamManagementService)
    
    # 상수
    emit_event = providers.Factory(EmitEvent)
    rooms = providers.Factory(Rooms)


@pytest.fixture
def test_container():
    """테스트 의존성 주입 컨테이너"""
    return TestContainer()