from abc import ABC, abstractmethod

from event_manage_service.application.dto.socketio_dto import (
    CaptureStatusResponseDTO,
    VideoFrameFromServiceDTO,
    ResponseClientMetadataDTO
)

class EventSubscriber(ABC):
    
    @abstractmethod
    async def handle_client_connect(self, sid) -> None:
        """client connection 제어함수"""
        pass
    
    @abstractmethod
    async def handle_response_client_metadata(self, sid, dto:ResponseClientMetadataDTO) -> None:
        """client의 metadata 응답에대한 제어함수"""
    
    @abstractmethod
    async def handle_client_disconnect(self, sid: str) -> None:
        """client disconnection 제어함수"""
        pass
    
    @abstractmethod
    async def handle_capture_start(self, sid: str) -> None:
        """Handle capture start request"""
        pass
    
    @abstractmethod
    async def handle_capture_stop(self, sid: str) -> None:
        """Handle capture stop request"""
        pass
    
    @abstractmethod
    async def handle_join_streaming_room(self, sid: str) -> None:
        """Handle streaming room join"""
        pass
    
    @abstractmethod
    async def handle_leave_streaming_room(self, sid: str) -> None:
        """Handle streaming room leave"""
        pass
    
    @abstractmethod
    async def handle_video_frame_relay(self, dto: VideoFrameFromServiceDTO) -> None:
        """Handle video frame broadcast"""
        pass
    
    @abstractmethod
    async def handle_request_capture_status(self) -> None:
        pass
    
    @abstractmethod
    async def handle_broadcast_capture_status(self, dto: CaptureStatusResponseDTO) -> None:
        """Broadcast capture status to client room"""
        pass