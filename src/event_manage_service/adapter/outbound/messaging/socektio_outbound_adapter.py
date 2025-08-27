import logging

from typing import Dict, Any, Set
import socketio

from event_manage_service.config.constants import (
    EmitEvent,
    Rooms
)
from event_manage_service.application.port.outbound.socketio_outbound_port import SocketIOOutboundPort
from event_manage_service.application.dto.socketio_dto import (
    VideoFrameFromServiceDTO,
    CaptureStatusResponseDTO
)
from event_manage_service.domain.service.stream_management_service import StreamManagementService

logger = logging.getLogger(__name__)

class SocketioOutboundAdapter(SocketIOOutboundPort):
    def __init__(self, sio: socketio.AsyncServer, emit_event: EmitEvent, rooms: Rooms, stream_management_service: StreamManagementService):
        self.sio = sio
        self.rooms = rooms
        self.emit_event = emit_event
        self.stream_management_service = stream_management_service
        
    def set_stream_service(self, sid):
        self.stream_management_service.set_stream_service(sid)
        
    # 요청
    async def request_client_metadata(self, sid: str):
        await self.sio.emit(
            self.emit_event.REQUEST_CLIENT_METADATA, 
            to=sid
        )
        
    async def send_capture_start_command(self) -> None:
        stream_service = self.stream_management_service.get_stream_service()
        await self.sio.emit(
            self.emit_event.CAPURE_START_REQUEST, 
            to=stream_service
        )
    
    async def send_capture_stop_command(self) -> None:
        stream_service = self.stream_management_service.get_stream_service()
        await self.sio.emit(
            self.emit_event.CAPURE_STOP_REQUEST, 
            to=stream_service
        )
    
    async def request_capure_status(self) -> None:
        stream_service = self.stream_management_service.get_stream_service()
        await self.sio.emit(
            self.emit_event.REQUEST_CAPURE_STATUS, 
            to=stream_service
        )
        
    # boradcast
    async def broadcast_capture_status(self, dto:CaptureStatusResponseDTO) -> None:
        data = dto.model_dump()
        await self.sio.emit(
            self.emit_event.BROADCAST_CAPTURE_STATUS, 
            data, 
            room=self.rooms.USER_ROOM, 
        )
    
    async def broadcast_video_frame(self, dto:VideoFrameFromServiceDTO) -> None:
        data = dto.model_dump()
        await self.sio.emit(self.emit_event.BROADCAST_VIDEO_FRAME, data, room=self.rooms.STREAMING_ROOM)
    
    # room manage
    async def add_client_to_room(self, sid: str, room: str) -> None:
        await self.sio.enter_room(sid, room)
        if room == self.rooms.STREAMING_ROOM:
            self.stream_management_service.add_client_to_streaming_room(sid)
        elif room == self.rooms.USER_ROOM:
            self.stream_management_service.add_client_to_user_room(sid)
    
    async def remove_client_from_room(self, sid: str, room: str) -> None:
        await self.sio.leave_room(sid, room)
        if room == self.rooms.STREAMING_ROOM:
            self.stream_management_service.remove_client_from_streaming_room(sid)
        elif room == self.rooms.USER_ROOM:
            self.stream_management_service.remove_client_from_user_room(sid)
    
    async def remove_client_from_all_rooms(self, sid: str) -> None:
        removed_from = self.stream_management_service.remove_client_from_all_rooms(sid)
        
        for room_type in removed_from:
            if room_type == "streaming_room":
                await self.sio.leave_room(sid, self.rooms.STREAMING_ROOM)
            elif room_type == "user_room":
                await self.sio.leave_room(sid, self.rooms.USER_ROOM)
            
    def get_sid_ip(self, sid: str) -> str:
        environ: dict[str, any] = self.sio.get_environ(sid)
        client_ip:str = environ.get('REMOTE_ADDR')
        return client_ip