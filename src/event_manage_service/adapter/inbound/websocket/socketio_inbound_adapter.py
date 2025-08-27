import logging
import socketio
from event_manage_service.application.port.inbound.socketio_inbound_port import SocketIOInboundPort
from event_manage_service.application.port.inbound.sevice_log_inbound_port import ServiceLogInboundPort
from event_manage_service.application.dto.socketio_dto import (
    CaptureStatusResponseDTO,
    VideoFrameFromServiceDTO,
    ResponseClientMetadataDTO
)

logger = logging.getLogger(__name__)



class SocketIOInboundAdapter:
    def __init__ (
        self,
        sio: socketio.AsyncServer,
        socketio_inbound_port: SocketIOInboundPort,
        event_logger: ServiceLogInboundPort
    ):
        self.sio = sio
        self.socketio_inbound_port = socketio_inbound_port
        self.event_logger = event_logger

    def resister_event(self):
        @self.sio.event
        async def connect(sid, environ):
            """client connect"""
            logger.info(f"{sid}client가 connect 되었습니다.")
            await self.socketio_inbound_port.handle_client_connect(sid)

        @self.sio.event
        async def response_client_metadata(sid, data: dict[str, any]):
            """client metadata 응답"""
            logger.info(f"{sid} client의 metadata를 응답받았습니다.")
            try:
                dto = ResponseClientMetadataDTO(**data)
                await self.socketio_inbound_port.handle_response_client_metadata(sid, dto)
            except ValueError:
                logger.error(f"{sid} client의 응답{data}의 DTO 변환 중 value error가 발생했습니다.")
            except :
                logger.error(f"{sid} client의 응답{data}의 DTO 변환에 실패했습니다.")
                
        @self.sio.event
        async def disconnect(sid, reason):
            """client disconnect"""
            logger.info(f"{sid} client가 disconnect 되었습니다.")
            await self.socketio_inbound_port.handle_client_disconnect(sid)

        @self.sio.event
        async def start_capture(sid):
            """stream-service의 video capture 동작 지시"""
            logger.info(f"client {sid}로부터 stream-service의 video capture 동작 지시를 전달 받았습니다.")
            await self.socketio_inbound_port.handle_capture_start(sid)

        @self.sio.event
        async def stop_capture(sid):
            """stream-service의 video capture 정지 지시"""
            logger.info(f"client {sid}로부터 stream-service의 video capture 정지 지시를 전달 받았습니다.")
            await self.socketio_inbound_port.handle_capture_stop(sid)

        @self.sio.event
        async def join_streaming_room(sid):
            """client의 streaming room 입장요청"""
            logger.info(f"client {sid}로부터 streaming room 입장요청을 받았습니다.")
            await self.socketio_inbound_port.handle_join_streaming_room(sid)

        @self.sio.event
        async def leave_streaming_room(sid):
            """client의 streaming room 퇴장요청"""
            logger.info(f"client {sid}로부터 streaming room 퇴장요청을 받았습니다.")
            await self.socketio_inbound_port.handle_leave_streaming_room(sid)

        @self.sio.event
        async def video_frame_relay(sid, data):
            """stream-service로 부터 captured frame 생산"""
            logger.debug(f"stream-service {sid}로부터 생산된 frame을 전달 받았습니다.")
            
            try:
                dto = VideoFrameFromServiceDTO(**data)
                await self.socketio_inbound_port.handle_video_frame_relay(sid, dto)    
            except ValueError:
                logger.error(f"{sid} client의 응답{data}의 DTO 변환 중 value error가 발생했습니다.")
            except :
                logger.error(f"{sid} client의 응답{data}의 DTO 변환에 실패했습니다.")
                
        @self.sio.event
        async def request_capture_status(sid):
            """client로 부터 현재 capture_status 요청"""
            logger.info(f"client {sid}로부터 현재 cpautre status 최신화 요청을 받았습니다.")
            await self.socketio_inbound_port.handle_request_capture_status(sid)
            
        @self.sio.event
        async def broadcast_capture_status(sid, data: dict[str, any]):
            """stream-service로 부터 caputre status 응답"""
            try:
                logger.info(f"stream-service {sid}로부터 capture status를 전달 받았습니다.")
                dto = CaptureStatusResponseDTO(**data)
                await self.socketio_inbound_port.handle_broadcast_capture_status(sid, dto)
            except ValueError:
                logger.error(f"{sid} client의 응답{data}의 DTO 변환 중 value error가 발생했습니다.")
            except :
                logger.error(f"{sid} client의 응답{data}의 DTO 변환에 실패했습니다.")