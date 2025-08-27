import logging
from typing import Set, Optional


logger = logging.getLogger(__name__)

class StreamManagementService:
    def __init__(self):
        self.streaming_room_clients: Set[str] = set()
        self.user_room_clients: Set[str] = set()
        self.stream_service: Optional[str] = None
        
    def set_stream_service(self, sid: str) -> None:
        """stream service client 저장"""
        self.stream_service = sid
        logger.info(f"stream service 등록: {sid}")
        
    def get_stream_service(self) -> Optional[str]:
        """stream service sid 추출"""
        return self.stream_service
        
    def add_client_to_streaming_room(self, sid: str) -> None:
        """streaming room에 user 등록"""
        self.streaming_room_clients.add(sid)
        logger.info(f"client {sid} streaming 룸 추가")
        
    def add_client_to_user_room(self, sid: str) -> None:
        """user room에 user 등록"""
        self.user_room_clients.add(sid)
        logger.info(f"client {sid} user 룸 추가")
        
    def remove_client_from_streaming_room(self, sid: str) -> None:
        """streaming room에 user 제거"""
        self.streaming_room_clients.discard(sid)
        logger.info(f"client {sid} streaming 룸에서 제거")
        
    def remove_client_from_user_room(self, sid: str) -> None:
        """user room에 user 제거"""
        self.user_room_clients.discard(sid)
        logger.info(f"client {sid} user 룸에서 제거")
        
    def remove_client_from_all_rooms(self, sid: str) -> list[str]:
        """모든 room에서 user 제거"""
        removed_from = []
        
        if sid in self.streaming_room_clients:
            self.remove_client_from_streaming_room(sid)
            removed_from.append("streaming_room")
            
        if sid in self.user_room_clients:
            self.remove_client_from_user_room(sid)
            removed_from.append("user_room")
            
        if sid == self.stream_service:
            self.stream_service = None
            removed_from.append("stream_service")
            logger.warning("stream service 연결 해제")
            
        return removed_from
        
    def get_streaming_room_clients(self) -> Set[str]:
        """streaming room의 clients 추출"""
        return self.streaming_room_clients.copy()
        
    def get_user_room_clients(self) -> Set[str]:
        """user room의 clients 추출"""
        return self.user_room_clients.copy()
        
    def is_client_in_streaming_room(self, sid: str) -> bool:
        """sid가 streaming room에 등록되어있는지 확인"""
        return sid in self.streaming_room_clients
        
    def is_client_in_user_room(self, sid: str) -> bool:
        """sid가 user room에 등록되어있는지 확인"""
        return sid in self.user_room_clients