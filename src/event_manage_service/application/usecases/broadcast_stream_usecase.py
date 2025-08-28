import logging

from event_manage_service.application.port.inbound.event_subscriber import EventSubscriber
from event_manage_service.application.port.outbound.event_publisher import EventPublisher
from event_manage_service.application.port.outbound.service_log_repository import ServiceLogRepository
from event_manage_service.application.dto.socketio_dto import (
    CaptureStatusResponseDTO,
    VideoFrameFromServiceDTO,
    ResponseClientMetadataDTO
)

from event_manage_service.domain.service.stream_management_service import StreamManagementService
from event_manage_service.domain.service.request_log_service import RequestLogService

from event_manage_service.config.constants import Rooms

logger = logging.getLogger(__name__)

class BroadcastStreamUseCase(EventSubscriber):
    def __init__(
        self,
        socketio_outbound_port: EventPublisher,
        service_log_repository: ServiceLogRepository,
        stream_management_service: StreamManagementService,
        request_log_service: RequestLogService,
        rooms: Rooms
    ):
        
        self.socketio_outbound_port = socketio_outbound_port
        self.service_log_repository = service_log_repository
        self.stream_management_service = stream_management_service
        self.request_log_service = request_log_service
        self.rooms = rooms
        
    async def handle_client_connect(self, sid) -> None:
        await self.socketio_outbound_port.request_client_metadata(sid)

    async def handle_response_client_metadata(self, sid, dto:ResponseClientMetadataDTO) -> None:
        if dto.client_type == "stream-service" :
            self.stream_management_service.set_stream_service(sid)
            await self.socketio_outbound_port.set_stream_service(sid)
        elif dto.client_type == "user" :
            await self.socketio_outbound_port.add_client_to_room(sid, self.rooms.USER_ROOM)

    async def handle_client_disconnect(self, sid: str) -> None:
        await self.socketio_outbound_port.remove_client_from_all_rooms(sid)

    async def handle_capture_start(self, sid: str) -> None:
        await self.socketio_outbound_port.send_capture_start_command()
        
        client_ip = self.socketio_outbound_port.get_sid_ip(sid)
        log = self.request_log_service.create_request_log(
            event_type="capture_start",
            client_ip=client_ip,
            metadata={"sid": sid}
        )
        await self.service_log_repository.save(log)

    async def handle_capture_stop(self, sid: str) -> None:
        await self.socketio_outbound_port.send_capture_stop_command()
        
        client_ip = self.socketio_outbound_port.get_sid_ip(sid)
        log = self.request_log_service.create_request_log(
            event_type="capture_stop",
            client_ip=client_ip,
            metadata={"sid": sid}
        )
        await self.service_log_repository.save(log)

    async def handle_join_streaming_room(self, sid: str) -> None:
        await self.socketio_outbound_port.add_client_to_room(sid, self.rooms.STREAMING_ROOM)
        
        client_ip = self.socketio_outbound_port.get_sid_ip(sid)
        log = self.request_log_service.create_request_log(
            event_type="join_streaming_room",
            client_ip=client_ip,
            metadata={"sid": sid}
        )
        await self.service_log_repository.save(log)

    async def handle_leave_streaming_room(self, sid: str) -> None:
        await self.socketio_outbound_port.remove_client_from_room(sid, self.rooms.STREAMING_ROOM)
        
        client_ip = self.socketio_outbound_port.get_sid_ip(sid)
        log = self.request_log_service.create_request_log(
            event_type="leave_streaming_room",
            client_ip=client_ip,
            metadata={"sid": sid}
        )
        await self.service_log_repository.save(log)

    async def handle_video_frame_relay(self, dto: VideoFrameFromServiceDTO) -> None:
        await self.socketio_outbound_port.broadcast_video_frame(dto)

    async def handle_request_capture_status(self) -> None:
        await self.socketio_outbound_port.request_capure_status()
        
    async def handle_broadcast_capture_status(self, dto: CaptureStatusResponseDTO) -> None:
        await self.socketio_outbound_port.broadcast_caputere_status(dto)