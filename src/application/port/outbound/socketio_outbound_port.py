from abc import ABC, abstractmethod
from typing import Dict, Any

from application.dto.socketio_dto import (
    VideoFrameFromServiceDTO,
    CaptureStatusResponseDTO
)

class SocketIOOutboundPort(ABC):
    
    @abstractmethod
    def set_stream_service(self, sid):
        """stream service 연결시 등록"""
        pass
    
    #요청 
    
    @abstractmethod
    async def request_client_metadata(self, sid) -> None:
        """connect 시 해당 sid로 client metadata 요청"""
    
    @abstractmethod
    async def send_capture_start_command(self) -> None:
        """capture start command 수신 시 stream service로 전달"""
        pass
    
    @abstractmethod
    async def send_capture_stop_command(self) -> None:
        """capture start command 수신 시 stream service로 전달"""
        pass
    
    @abstractmethod
    async def request_capure_status(self) -> None:
        """capture status 오쳥 수신 시 stream service로 전달"""
        pass
    
    @abstractmethod
    async def broadcast_capture_status(self, dto:CaptureStatusResponseDTO) -> None:
        """stream service로부터 capture status 수신시 client_room으로 전달"""
        pass
    
    @abstractmethod
    async def broadcast_video_frame(self, dto:VideoFrameFromServiceDTO) -> None:
        """stream service로부터 video frame 수신시 streaming_room으로 전달"""
        pass
    
    @abstractmethod
    async def add_client_to_room(self, sid: str, room: str) -> None:
        """client를 특정 room에 추가"""
        pass
    
    @abstractmethod
    async def remove_client_from_room(self, sid: str, room: str) -> None:
        """client를 특정 room에서 제거"""
        pass
    
    @abstractmethod
    async def remove_client_from_all_rooms(self, sid: str) -> None:
        """클라이언트를 모든 room에서"""
        pass
    
    @abstractmethod
    def get_sid_ip(self, sid: str) -> str:
        """client ip 추출"""
        pass