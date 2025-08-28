import pytest
from typing import Any, Dict
from unittest.mock import Mock, AsyncMock, patch
import socketio
from event_manage_service.adapter.inbound.websocket.socketio_server import SocektIOServer
from event_manage_service.application.dto.socketio_dto import (
    ResponseClientMetadataDTO,
    VideoFrameFromServiceDTO,
    CaptureStatusResponseDTO
)


class TestSocektIOServer:
    """SocektIOServer 테스트 케이스"""

    @pytest.fixture
    def mock_socketio_inbound_port(self) -> Mock:
        """EventSubscriber 모킹"""
        port = Mock()
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
        """이벤트 로거(ServiceLogController) 모킹"""
        logger = Mock()
        return logger

    @pytest.fixture
    def socketio_adapter(self, mock_socketio_server: Mock, mock_socketio_inbound_port: Mock, mock_event_logger: Mock) -> SocektIOServer:
        """모킹된 의존성을 가진 SocektIOServer 인스턴스"""
        return SocektIOServer(
            sio=mock_socketio_server,
            socketio_inbound_port=mock_socketio_inbound_port,
            event_logger=mock_event_logger
        )

    def test_adapter_initialization(self, socketio_adapter: SocektIOServer, mock_socketio_server: Mock, mock_socketio_inbound_port: Mock, mock_event_logger: Mock) -> None:
        """어댑터 초기화 테스트"""
        assert socketio_adapter.sio is mock_socketio_server
        assert socketio_adapter.socketio_inbound_port is mock_socketio_inbound_port
        assert socketio_adapter.event_logger is mock_event_logger

    @patch('event_manage_service.adapter.inbound.websocket.socketio_inbound_adapter.logger')
    def test_register_event_decorates_handlers(self, mock_logger: Mock, socketio_adapter: SocektIOServer, mock_socketio_server: Mock) -> None:
        """이벤트 등록이 핸들러를 적절히 데코레이트하는지 테스트"""
        socketio_adapter.resister_event()
        
        # Verify that event decorators were called
        assert mock_socketio_server.event.call_count >= 8  # At least 8 events should be registered

    @pytest.mark.asyncio
    @patch('event_manage_service.adapter.inbound.websocket.socketio_inbound_adapter.logger')
    async def test_connect_event_handler(self, mock_logger: Mock, socketio_adapter: SocektIOServer, mock_socketio_inbound_port: Mock) -> None:
        """연결 이벤트 핸들러 테스트"""
        socketio_adapter.resister_event()
        
        # Get the decorated connect function
        connect_handler = None
        for call in socketio_adapter.sio.event.call_args_list:
            if call[0][0].__name__ == 'connect':
                connect_handler = call[0][0]
                break
        
        assert connect_handler is not None
        
        sid = "test_client_123"
        environ = {}
        
        await connect_handler(sid, environ)
        
        mock_socketio_inbound_port.handle_client_connect.assert_called_once_with(sid)
        mock_logger.info.assert_called_once_with(f"{sid}client가 connect 되었습니다.")

    @pytest.mark.asyncio
    @patch('event_manage_service.adapter.inbound.websocket.socketio_inbound_adapter.logger')
    async def test_response_client_metadata_valid_data(self, mock_logger: Mock, socketio_adapter: SocektIOServer, mock_socketio_inbound_port: Mock) -> None:
        """유효한 데이터로 클라이언트 메타데이터 응답 이벤트 핸들러 테스트"""
        socketio_adapter.resister_event()
        
        # Get the decorated function
        handler = None
        for call in socketio_adapter.sio.event.call_args_list:
            if call[0][0].__name__ == 'response_client_metadata':
                handler = call[0][0]
                break
        
        assert handler is not None
        
        sid = "test_client"
        data = {"client_type": "user"}
        
        await handler(sid, data)
        
        mock_socketio_inbound_port.handle_response_client_metadata.assert_called_once()
        call_args = mock_socketio_inbound_port.handle_response_client_metadata.call_args
        assert call_args[0][0] == sid
        assert isinstance(call_args[0][1], ResponseClientMetadataDTO)
        assert call_args[0][1].client_type == "user"

    @pytest.mark.asyncio
    @patch('event_manage_service.adapter.inbound.websocket.socketio_inbound_adapter.logger')
    async def test_response_client_metadata_invalid_data(self, mock_logger: Mock, socketio_adapter: SocektIOServer, mock_socketio_inbound_port: Mock) -> None:
        """잘못된 데이터로 클라이언트 메타데이터 응답 이벤트 핸들러 테스트"""
        socketio_adapter.resister_event()
        
        # Get the decorated function
        handler = None
        for call in socketio_adapter.sio.event.call_args_list:
            if call[0][0].__name__ == 'response_client_metadata':
                handler = call[0][0]
                break
        
        sid = "test_client"
        invalid_data = {"invalid_field": "invalid_value"}
        
        await handler(sid, invalid_data)
        
        # Handler should not be called due to validation error
        mock_socketio_inbound_port.handle_response_client_metadata.assert_not_called()
        mock_logger.error.assert_called()

    @pytest.mark.asyncio
    @patch('event_manage_service.adapter.inbound.websocket.socketio_inbound_adapter.logger')
    async def test_disconnect_event_handler(self, mock_logger: Mock, socketio_adapter: SocektIOServer, mock_socketio_inbound_port: Mock) -> None:
        """연결 끊기 이벤트 핸들러 테스트"""
        socketio_adapter.resister_event()
        
        # Get the decorated function
        handler = None
        for call in socketio_adapter.sio.event.call_args_list:
            if call[0][0].__name__ == 'disconnect':
                handler = call[0][0]
                break
        
        assert handler is not None
        
        sid = "disconnecting_client"
        reason = "client_disconnect"
        
        await handler(sid, reason)
        
        mock_socketio_inbound_port.handle_client_disconnect.assert_called_once_with(sid)
        mock_logger.info.assert_called_once_with(f"{sid} client가 disconnect 되었습니다.")

    @pytest.mark.asyncio
    @patch('event_manage_service.adapter.inbound.websocket.socketio_inbound_adapter.logger')
    async def test_start_capture_event_handler(self, mock_logger: Mock, socketio_adapter: SocektIOServer, mock_socketio_inbound_port: Mock) -> None:
        """캐처 시작 이벤트 핸들러 테스트"""
        socketio_adapter.resister_event()
        
        # Get the decorated function
        handler = None
        for call in socketio_adapter.sio.event.call_args_list:
            if call[0][0].__name__ == 'start_capture':
                handler = call[0][0]
                break
        
        assert handler is not None
        
        sid = "capture_client"
        
        await handler(sid)
        
        mock_socketio_inbound_port.handle_capture_start.assert_called_once_with(sid)
        mock_logger.info.assert_called_once()

    @pytest.mark.asyncio
    @patch('event_manage_service.adapter.inbound.websocket.socketio_inbound_adapter.logger')
    async def test_video_frame_relay_valid_data(self, mock_logger: Mock, socketio_adapter: SocektIOServer, mock_socketio_inbound_port: Mock) -> None:
        """유효한 데이터로 비디오 프레임 릴레이 이벤트 핸들러 테스트"""
        socketio_adapter.resister_event()
        
        # Get the decorated function
        handler = None
        for call in socketio_adapter.sio.event.call_args_list:
            if call[0][0].__name__ == 'video_frame_relay':
                handler = call[0][0]
                break
        
        assert handler is not None
        
        sid = "stream_service"
        data = {"frame_data": b"fake_video_data"}
        
        await handler(sid, data)
        
        mock_socketio_inbound_port.handle_video_frame_relay.assert_called_once()
        call_args = mock_socketio_inbound_port.handle_video_frame_relay.call_args
        assert call_args[0][0] == sid
        assert isinstance(call_args[0][1], VideoFrameFromServiceDTO)

    @pytest.mark.asyncio
    @patch('event_manage_service.adapter.inbound.websocket.socketio_inbound_adapter.logger')
    async def test_video_frame_relay_invalid_data(self, mock_logger: Mock, socketio_adapter: SocektIOServer, mock_socketio_inbound_port: Mock) -> None:
        """잘못된 데이터로 비디오 프레임 릴레이 이벤트 핸들러 테스트"""
        socketio_adapter.resister_event()
        
        # Get the decorated function
        handler = None
        for call in socketio_adapter.sio.event.call_args_list:
            if call[0][0].__name__ == 'video_frame_relay':
                handler = call[0][0]
                break
        
        sid = "stream_service"
        invalid_data = {"wrong_field": "wrong_value"}
        
        await handler(sid, invalid_data)
        
        # Handler should not be called due to validation error
        mock_socketio_inbound_port.handle_video_frame_relay.assert_not_called()
        mock_logger.error.assert_called()

    @pytest.mark.asyncio
    @patch('event_manage_service.adapter.inbound.websocket.socketio_inbound_adapter.logger')
    async def test_broadcast_capture_status_valid_data(self, mock_logger: Mock, socketio_adapter: SocektIOServer, mock_socketio_inbound_port: Mock) -> None:
        """유효한 데이터로 캐처 상태 브로드캐스트 이벤트 핸들러 테스트"""
        socketio_adapter.resister_event()
        
        # Get the decorated function
        handler = None
        for call in socketio_adapter.sio.event.call_args_list:
            if call[0][0].__name__ == 'broadcast_capture_status':
                handler = call[0][0]
                break
        
        assert handler is not None
        
        sid = "stream_service"
        data = {"rtsp_url": "rtsp://example.com/stream", "is_active": True}
        
        await handler(sid, data)
        
        mock_socketio_inbound_port.handle_broadcast_capture_status.assert_called_once()
        call_args = mock_socketio_inbound_port.handle_broadcast_capture_status.call_args
        assert call_args[0][0] == sid
        assert isinstance(call_args[0][1], CaptureStatusResponseDTO)
        assert call_args[0][1].rtsp_url == "rtsp://example.com/stream"
        assert call_args[0][1].is_active is True

    @pytest.mark.asyncio
    async def test_all_basic_events_registered(self, socketio_adapter: SocektIOServer, mock_socketio_server: Mock) -> None:
        """모든 기본 이벤트가 등록되었는지 테스트"""
        socketio_adapter.resister_event()
        
        # Get all registered event names
        registered_events = []
        for call in mock_socketio_server.event.call_args_list:
            if hasattr(call[0][0], '__name__'):
                registered_events.append(call[0][0].__name__)
        
        expected_events = [
            'connect',
            'response_client_metadata', 
            'disconnect',
            'start_capture',
            'stop_capture',
            'join_streaming_room',
            'leave_streaming_room',
            'video_frame_relay',
            'request_capture_status',
            'broadcast_capture_status'
        ]
        
        for event in expected_events:
            assert event in registered_events

    @pytest.mark.asyncio
    @patch('event_manage_service.adapter.inbound.websocket.socketio_inbound_adapter.logger')
    async def test_error_handling_preserves_logging(self, mock_logger: Mock, socketio_adapter: SocektIOServer, mock_socketio_inbound_port: Mock) -> None:
        """에러 처리가 디버그 정보를 로깅하는지 테스트"""
        socketio_adapter.resister_event()
        
        # Get video frame relay handler for testing
        handler = None
        for call in socketio_adapter.sio.event.call_args_list:
            if call[0][0].__name__ == 'video_frame_relay':
                handler = call[0][0]
                break
        
        sid = "test_service"
        data = {"frame_data": b"test_data"}
        
        await handler(sid, data)
        
        # Should log debug message regardless of validation success/failure
        mock_logger.debug.assert_called_once()