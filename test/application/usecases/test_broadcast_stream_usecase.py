import pytest
from typing import Any
from unittest.mock import AsyncMock, Mock
from event_manage_service.application.usecases.broadcast_stream_usecase import BroadcastStreamUseCase
from event_manage_service.application.dto.socketio_dto import (
    ResponseClientMetadataDTO,
    VideoFrameFromServiceDTO,
    CaptureStatusResponseDTO
)
from event_manage_service.domain.model.request_log import RequestLog


class TestBroadcastStreamUseCase:
    """BroadcastStreamUseCase 테스트 케이스"""

    @pytest.mark.asyncio
    async def test_handle_client_connect(self, broadcast_stream_usecase: BroadcastStreamUseCase, mock_socketio_outbound_port: Mock) -> None:
        """클라이언트 연결 처리 테스트"""
        sid = "client_123"
        
        await broadcast_stream_usecase.handle_client_connect(sid)
        
        mock_socketio_outbound_port.request_client_metadata.assert_called_once_with(sid)

    @pytest.mark.asyncio
    async def test_handle_response_client_metadata_stream_service(
        self, broadcast_stream_usecase: BroadcastStreamUseCase, mock_socketio_outbound_port: Mock, stream_management_service: Any
    ) -> None:
        """스트림 서비스에 대한 클라이언트 메타데이터 응답 처리 테스트"""
        sid = "stream_service_123"
        dto = ResponseClientMetadataDTO(client_type="stream-service")
        
        await broadcast_stream_usecase.handle_response_client_metadata(sid, dto)
        
        # Verify stream service is set
        assert stream_management_service.get_stream_service() == sid
        mock_socketio_outbound_port.set_stream_service.assert_called_once_with(sid)

    @pytest.mark.asyncio
    async def test_handle_response_client_metadata_user(
        self, broadcast_stream_usecase, mock_socketio_outbound_port, rooms
    ):
        """사용자에 대한 클라이언트 메타데이터 응답 처리 테스트"""
        sid = "user_123"
        dto = ResponseClientMetadataDTO(client_type="user")
        
        await broadcast_stream_usecase.handle_response_client_metadata(sid, dto)
        
        mock_socketio_outbound_port.add_client_to_room.assert_called_once_with(sid, rooms.USER_ROOM)

    @pytest.mark.asyncio
    async def test_handle_client_disconnect(self, broadcast_stream_usecase, mock_socketio_outbound_port):
        """클라이언트 연결 해제 처리 테스트"""
        sid = "client_to_disconnect"
        
        await broadcast_stream_usecase.handle_client_disconnect(sid)
        
        mock_socketio_outbound_port.remove_client_from_all_rooms.assert_called_once_with(sid)

    @pytest.mark.asyncio
    async def test_handle_capture_start(
        self, broadcast_stream_usecase, mock_socketio_outbound_port, mock_service_log_repository
    ):
        """캡처 시작 명령 처리 테스트"""
        sid = "client_start_capture"
        
        await broadcast_stream_usecase.handle_capture_start(sid)
        
        # Verify capture start command is sent
        mock_socketio_outbound_port.send_capture_start_command.assert_called_once()
        
        # Verify log is saved
        mock_service_log_repository.save.assert_called_once()
        saved_log = mock_service_log_repository.save.call_args[0][0]
        assert isinstance(saved_log, RequestLog)
        assert saved_log.event_type == "capture_start"
        assert saved_log.client_ip == "192.168.1.1"
        assert saved_log.metadata["sid"] == sid

    @pytest.mark.asyncio
    async def test_handle_capture_stop(
        self, broadcast_stream_usecase, mock_socketio_outbound_port, mock_service_log_repository
    ):
        """캡처 중지 명령 처리 테스트"""
        sid = "client_stop_capture"
        
        await broadcast_stream_usecase.handle_capture_stop(sid)
        
        # Verify capture stop command is sent
        mock_socketio_outbound_port.send_capture_stop_command.assert_called_once()
        
        # Verify log is saved
        mock_service_log_repository.save.assert_called_once()
        saved_log = mock_service_log_repository.save.call_args[0][0]
        assert isinstance(saved_log, RequestLog)
        assert saved_log.event_type == "capture_stop"
        assert saved_log.client_ip == "192.168.1.1"
        assert saved_log.metadata["sid"] == sid

    @pytest.mark.asyncio
    async def test_handle_join_streaming_room(
        self, broadcast_stream_usecase, mock_socketio_outbound_port, mock_service_log_repository, rooms
    ):
        """스트리밍 룸 참가 처리 테스트"""
        sid = "client_join_streaming"
        
        await broadcast_stream_usecase.handle_join_streaming_room(sid)
        
        # Verify client is added to streaming room
        mock_socketio_outbound_port.add_client_to_room.assert_called_once_with(sid, rooms.STREAMING_ROOM)
        
        # Verify log is saved
        mock_service_log_repository.save.assert_called_once()
        saved_log = mock_service_log_repository.save.call_args[0][0]
        assert saved_log.event_type == "join_streaming_room"

    @pytest.mark.asyncio
    async def test_handle_leave_streaming_room(
        self, broadcast_stream_usecase, mock_socketio_outbound_port, mock_service_log_repository, rooms
    ):
        """스트리밍 룸 떠나기 처리 테스트"""
        sid = "client_leave_streaming"
        
        await broadcast_stream_usecase.handle_leave_streaming_room(sid)
        
        # Verify client is removed from streaming room
        mock_socketio_outbound_port.remove_client_from_room.assert_called_once_with(sid, rooms.STREAMING_ROOM)
        
        # Verify log is saved
        mock_service_log_repository.save.assert_called_once()
        saved_log = mock_service_log_repository.save.call_args[0][0]
        assert saved_log.event_type == "leave_streaming_room"

    @pytest.mark.asyncio
    async def test_handle_video_frame_relay(self, broadcast_stream_usecase, mock_socketio_outbound_port):
        """비디오 프레임 중계 처리 테스트"""
        dto = VideoFrameFromServiceDTO(frame_data=b"fake_video_frame_data")
        
        await broadcast_stream_usecase.handle_video_frame_relay(dto)
        
        mock_socketio_outbound_port.broadcast_video_frame.assert_called_once_with(dto)

    @pytest.mark.asyncio
    async def test_handle_request_capture_status(self, broadcast_stream_usecase, mock_socketio_outbound_port):
        """캡처 상태 요청 처리 테스트"""
        await broadcast_stream_usecase.handle_request_capture_status()
        
        mock_socketio_outbound_port.request_capure_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_broadcast_capture_status(self, broadcast_stream_usecase, mock_socketio_outbound_port):
        """캡처 상태 브로드캐스트 처리 테스트"""
        dto = CaptureStatusResponseDTO(rtsp_url="rtsp://example.com/stream", is_active=True)
        
        await broadcast_stream_usecase.handle_broadcast_capture_status(dto)
        
        mock_socketio_outbound_port.broadcast_caputere_status.assert_called_once_with(dto)

    @pytest.mark.asyncio
    async def test_dependency_injection(
        self, mock_socketio_outbound_port, mock_service_log_repository, 
        stream_management_service, request_log_service, rooms
    ):
        """모든 의존성이 올바르게 주입되는지 테스트"""
        usecase = BroadcastStreamUseCase(
            socketio_outbound_port=mock_socketio_outbound_port,
            service_log_repository=mock_service_log_repository,
            stream_management_service=stream_management_service,
            request_log_service=request_log_service,
            rooms=rooms
        )
        
        assert usecase.socketio_outbound_port is mock_socketio_outbound_port
        assert usecase.service_log_repository is mock_service_log_repository
        assert usecase.stream_management_service is stream_management_service
        assert usecase.request_log_service is request_log_service
        assert usecase.rooms is rooms

    @pytest.mark.asyncio
    async def test_logging_includes_client_ip(
        self, broadcast_stream_usecase, mock_socketio_outbound_port, mock_service_log_repository
    ):
        """모든 로그된 이벤트가 클라이언트 IP를 포함하는지 테스트"""
        sid = "test_client"
        expected_ip = "192.168.1.1"
        
        # Test multiple events that should log client IP
        await broadcast_stream_usecase.handle_capture_start(sid)
        await broadcast_stream_usecase.handle_capture_stop(sid)
        await broadcast_stream_usecase.handle_join_streaming_room(sid)
        await broadcast_stream_usecase.handle_leave_streaming_room(sid)
        
        # Verify all calls included client IP
        assert mock_service_log_repository.save.call_count == 4
        
        for call_args in mock_service_log_repository.save.call_args_list:
            saved_log = call_args[0][0]
            assert saved_log.client_ip == expected_ip

    @pytest.mark.asyncio
    async def test_error_handling_in_repository_save(
        self, broadcast_stream_usecase, mock_service_log_repository
    ):
        """리포지토리 저장 실패 시 에러 처리 테스트"""
        sid = "error_test_client"
        mock_service_log_repository.save.side_effect = Exception("Database error")
        
        # The usecase should propagate the exception
        with pytest.raises(Exception, match="Database error"):
            await broadcast_stream_usecase.handle_capture_start(sid)

    @pytest.mark.asyncio
    async def test_stream_service_type_handling(
        self, broadcast_stream_usecase, stream_management_service
    ):
        """스트림 서비스 타입이 올바르게 처리되는지 테스트"""
        sid = "stream_service_test"
        dto = ResponseClientMetadataDTO(client_type="stream-service")
        
        # Verify initial state
        assert stream_management_service.get_stream_service() is None
        
        await broadcast_stream_usecase.handle_response_client_metadata(sid, dto)
        
        # Verify stream service is set
        assert stream_management_service.get_stream_service() == sid

    @pytest.mark.asyncio
    async def test_user_type_handling(
        self, broadcast_stream_usecase, mock_socketio_outbound_port, rooms
    ):
        """사용자 타입이 올바르게 처리되는지 테스트"""
        sid = "user_test"
        dto = ResponseClientMetadataDTO(client_type="user")
        
        await broadcast_stream_usecase.handle_response_client_metadata(sid, dto)
        
        # Verify user is added to user room
        mock_socketio_outbound_port.add_client_to_room.assert_called_once_with(sid, rooms.USER_ROOM)