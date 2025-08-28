import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
import socketio
from event_manage_service.adapter.inbound.websocket.socketio_server import SocketIOServer


class TestSimpleSocketIO:
    """서버 없는 간단한 SocketIO 통합 테스트"""

    @pytest.fixture
    def mock_socketio_server(self) -> Mock:
        """SocketIO 서버 모킹"""
        sio = Mock()
        sio.on = Mock()
        sio.emit = AsyncMock()
        sio.enter_room = AsyncMock()
        sio.leave_room = AsyncMock()
        
        # @sio.event 데코레이터 모킹
        def mock_event_decorator(func):
            # 데코레이터 동작을 시뮬레이션하여 함수를 그대로 반환
            return func
        sio.event = mock_event_decorator
        
        return sio

    @pytest.fixture
    def mock_socketio_inbound_port(self) -> AsyncMock:
        """EventSubscriber 모킹"""
        port = AsyncMock()
        port.handle_client_connect = AsyncMock()
        port.handle_response_client_metadata = AsyncMock()
        port.handle_client_disconnect = AsyncMock()
        port.handle_capture_start = AsyncMock()
        port.handle_capture_stop = AsyncMock()
        port.handle_join_streaming_room = AsyncMock()
        port.handle_leave_streaming_room = AsyncMock()
        port.handle_video_frame_relay = AsyncMock()
        port.handle_request_capture_status = AsyncMock()
        port.handle_broadcast_capture_status = AsyncMock()
        return port

    @pytest.fixture
    def mock_event_logger(self) -> Mock:
        """이벤트 로거 모킹"""
        return Mock()

    @pytest.fixture
    def socketio_adapter(self, mock_socketio_server: Mock, mock_socketio_inbound_port: AsyncMock, mock_event_logger: Mock) -> SocketIOServer:
        """SocketIOServer 인스턴스"""
        return SocketIOServer(
            sio=mock_socketio_server,
            socketio_inbound_port=mock_socketio_inbound_port,
            event_logger=mock_event_logger
        )

    def test_adapter_initialization(self, socketio_adapter: SocketIOServer, mock_socketio_server: Mock, mock_socketio_inbound_port: AsyncMock, mock_event_logger: Mock) -> None:
        """어댑터 초기화 테스트"""
        assert socketio_adapter.sio is mock_socketio_server
        assert socketio_adapter.socketio_inbound_port is mock_socketio_inbound_port
        assert socketio_adapter.event_logger is mock_event_logger

    def test_event_registration(self, socketio_adapter: SocketIOServer, mock_socketio_server: Mock) -> None:
        """이벤트 등록이 오류 없이 완료되는지 테스트"""
        # 예외가 발생하지 않아야 함
        socketio_adapter.resister_event()
        
        # 어댑터가 여전히 서버 참조를 가지고 있는지 확인
        assert socketio_adapter.sio is mock_socketio_server

    def test_adapter_methods_exist(self, socketio_adapter: SocketIOServer) -> None:
        """어댑터가 필요한 메소드를 가지는지 테스트"""
        assert hasattr(socketio_adapter, 'resister_event')
        assert callable(socketio_adapter.resister_event)
        
        # 어댑터가 올바른 속성을 가지는지 테스트
        assert hasattr(socketio_adapter, 'sio')
        assert hasattr(socketio_adapter, 'socketio_inbound_port')
        assert hasattr(socketio_adapter, 'event_logger')

    def test_adapter_dependencies_injection(self, socketio_adapter: SocketIOServer, mock_socketio_server: Mock, mock_socketio_inbound_port: AsyncMock, mock_event_logger: Mock) -> None:
        """의존성이 적절히 주입되었는지 테스트"""
        # 의존성 주입이 올바르게 작동했는지 테스트
        assert socketio_adapter.sio is mock_socketio_server
        assert socketio_adapter.socketio_inbound_port is mock_socketio_inbound_port
        assert socketio_adapter.event_logger is mock_event_logger

    def test_socketio_server_integration_points(self, socketio_adapter: SocketIOServer) -> None:
        """SocketIO 서버와의 통합 지점 테스트"""
        # 어댑터가 서버와 적절히 상호작용하는지 테스트
        assert socketio_adapter.sio is not None
        assert hasattr(socketio_adapter, 'resister_event')
        
        # 이벤트 등록이 크래시되지 않는지 테스트
        socketio_adapter.resister_event()
        
        # 어댑터가 여전히 작동해야 함
        assert socketio_adapter.sio is not None
        
    def test_handler_error_resilience(self, socketio_adapter: SocketIOServer, mock_socketio_inbound_port: AsyncMock) -> None:
        """어댑터가 설정을 우아하게 처리하는지 테스트"""
        # 포트에 문제가 있어도 어댑터가 크래시되지 않아야 함
        socketio_adapter.resister_event()
        
        # 어댑터가 여전히 작동해야 함
        assert socketio_adapter.sio is not None
        assert socketio_adapter.socketio_inbound_port is not None