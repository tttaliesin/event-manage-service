import pytest
from unittest.mock import patch
from event_manage_service.domain.service.stream_management_service import StreamManagementService


class TestStreamManagementService:
    """StreamManagementService에 대한 테스트 케이스"""

    def test_initial_state(self, stream_management_service):
        """StreamManagementService의 초기 상태 테스트"""
        assert len(stream_management_service.streaming_room_clients) == 0
        assert len(stream_management_service.user_room_clients) == 0
        assert stream_management_service.stream_service is None

    def test_set_and_get_stream_service(self, stream_management_service):
        """스트림 서비스 설정 및 조회 테스트"""
        sid = "stream_service_123"
        
        with patch('event_manage_service.domain.service.stream_management_service.logger') as mock_logger:
            stream_management_service.set_stream_service(sid)
            mock_logger.info.assert_called_once_with(f"stream service 등록: {sid}")
        
        assert stream_management_service.get_stream_service() == sid

    def test_set_stream_service_overwrites_existing(self, stream_management_service):
        """스트림 서비스 설정 시 기존 것을 덮어쓰는지 테스트"""
        old_sid = "old_stream_service"
        new_sid = "new_stream_service"
        
        stream_management_service.set_stream_service(old_sid)
        stream_management_service.set_stream_service(new_sid)
        
        assert stream_management_service.get_stream_service() == new_sid

    def test_add_client_to_streaming_room(self, stream_management_service):
        """스트리밍 룸에 클라이언트 추가 테스트"""
        sid = "client_123"
        
        with patch('event_manage_service.domain.service.stream_management_service.logger') as mock_logger:
            stream_management_service.add_client_to_streaming_room(sid)
            mock_logger.info.assert_called_once_with(f"client {sid} streaming 룸 추가")
        
        assert sid in stream_management_service.streaming_room_clients
        assert stream_management_service.is_client_in_streaming_room(sid) is True

    def test_add_client_to_user_room(self, stream_management_service):
        """사용자 룸에 클라이언트 추가 테스트"""
        sid = "user_123"
        
        with patch('event_manage_service.domain.service.stream_management_service.logger') as mock_logger:
            stream_management_service.add_client_to_user_room(sid)
            mock_logger.info.assert_called_once_with(f"client {sid} user 룸 추가")
        
        assert sid in stream_management_service.user_room_clients
        assert stream_management_service.is_client_in_user_room(sid) is True

    def test_add_same_client_to_both_rooms(self, stream_management_service):
        """동일한 클라이언트를 두 룸에 모두 추가하는 테스트"""
        sid = "client_both"
        
        stream_management_service.add_client_to_streaming_room(sid)
        stream_management_service.add_client_to_user_room(sid)
        
        assert stream_management_service.is_client_in_streaming_room(sid) is True
        assert stream_management_service.is_client_in_user_room(sid) is True

    def test_remove_client_from_streaming_room(self, stream_management_service):
        """스트리밍 룸에서 클라이언트 제거 테스트"""
        sid = "client_to_remove"
        
        # Add client first
        stream_management_service.add_client_to_streaming_room(sid)
        assert stream_management_service.is_client_in_streaming_room(sid) is True
        
        # Remove client
        with patch('event_manage_service.domain.service.stream_management_service.logger') as mock_logger:
            stream_management_service.remove_client_from_streaming_room(sid)
            mock_logger.info.assert_called_once_with(f"client {sid} streaming 룸에서 제거")
        
        assert stream_management_service.is_client_in_streaming_room(sid) is False

    def test_remove_client_from_user_room(self, stream_management_service):
        """사용자 룸에서 클라이언트 제거 테스트"""
        sid = "user_to_remove"
        
        # Add client first
        stream_management_service.add_client_to_user_room(sid)
        assert stream_management_service.is_client_in_user_room(sid) is True
        
        # Remove client
        with patch('event_manage_service.domain.service.stream_management_service.logger') as mock_logger:
            stream_management_service.remove_client_from_user_room(sid)
            mock_logger.info.assert_called_once_with(f"client {sid} user 룸에서 제거")
        
        assert stream_management_service.is_client_in_user_room(sid) is False

    def test_remove_nonexistent_client_from_rooms(self, stream_management_service):
        """존재하지 않는 클라이언트를 룸에서 제거 테스트 (에러를 발생시키지 않아야 함)"""
        sid = "nonexistent_client"
        
        # Should not raise any errors
        stream_management_service.remove_client_from_streaming_room(sid)
        stream_management_service.remove_client_from_user_room(sid)

    def test_remove_client_from_all_rooms_streaming_only(self, stream_management_service):
        """스트리밍 룸에만 있는 클라이언트를 모든 룸에서 제거 테스트"""
        sid = "streaming_only_client"
        
        stream_management_service.add_client_to_streaming_room(sid)
        
        removed_from = stream_management_service.remove_client_from_all_rooms(sid)
        
        assert "streaming_room" in removed_from
        assert "user_room" not in removed_from
        assert "stream_service" not in removed_from
        assert stream_management_service.is_client_in_streaming_room(sid) is False

    def test_remove_client_from_all_rooms_user_only(self, stream_management_service):
        """사용자 룸에만 있는 클라이언트를 모든 룸에서 제거 테스트"""
        sid = "user_only_client"
        
        stream_management_service.add_client_to_user_room(sid)
        
        removed_from = stream_management_service.remove_client_from_all_rooms(sid)
        
        assert "user_room" in removed_from
        assert "streaming_room" not in removed_from
        assert "stream_service" not in removed_from
        assert stream_management_service.is_client_in_user_room(sid) is False

    def test_remove_client_from_all_rooms_stream_service(self, stream_management_service):
        """모든 룸에서 스트림 서비스 제거 테스트"""
        sid = "stream_service_client"
        
        stream_management_service.set_stream_service(sid)
        
        with patch('event_manage_service.domain.service.stream_management_service.logger') as mock_logger:
            removed_from = stream_management_service.remove_client_from_all_rooms(sid)
            mock_logger.warning.assert_called_once_with("stream service 연결 해제")
        
        assert "stream_service" in removed_from
        assert stream_management_service.get_stream_service() is None

    def test_remove_client_from_all_rooms_multiple(self, stream_management_service):
        """여러 룸에 있는 클라이언트를 모든 룸에서 제거 테스트"""
        sid = "multi_room_client"
        
        stream_management_service.add_client_to_streaming_room(sid)
        stream_management_service.add_client_to_user_room(sid)
        stream_management_service.set_stream_service(sid)
        
        removed_from = stream_management_service.remove_client_from_all_rooms(sid)
        
        assert "streaming_room" in removed_from
        assert "user_room" in removed_from
        assert "stream_service" in removed_from
        assert len(removed_from) == 3

    def test_remove_client_from_all_rooms_nonexistent(self, stream_management_service):
        """존재하지 않는 클라이언트를 모든 룸에서 제거 테스트"""
        sid = "nonexistent_client"
        
        removed_from = stream_management_service.remove_client_from_all_rooms(sid)
        
        assert removed_from == []

    def test_get_streaming_room_clients_copy(self, stream_management_service):
        """get_streaming_room_clients가 복사본을 반환하는지 테스트"""
        sid1, sid2 = "client1", "client2"
        
        stream_management_service.add_client_to_streaming_room(sid1)
        stream_management_service.add_client_to_streaming_room(sid2)
        
        clients = stream_management_service.get_streaming_room_clients()
        
        # Modify returned set
        clients.add("external_client")
        
        # Original set should be unchanged
        original_clients = stream_management_service.get_streaming_room_clients()
        assert "external_client" not in original_clients
        assert len(original_clients) == 2

    def test_get_user_room_clients_copy(self, stream_management_service):
        """get_user_room_clients가 복사본을 반환하는지 테스트"""
        sid1, sid2 = "user1", "user2"
        
        stream_management_service.add_client_to_user_room(sid1)
        stream_management_service.add_client_to_user_room(sid2)
        
        clients = stream_management_service.get_user_room_clients()
        
        # Modify returned set
        clients.add("external_user")
        
        # Original set should be unchanged
        original_clients = stream_management_service.get_user_room_clients()
        assert "external_user" not in original_clients
        assert len(original_clients) == 2

    def test_multiple_clients_in_same_room(self, stream_management_service):
        """동일한 룸에 여러 클라이언트가 있는 경우 테스트"""
        sids = ["client1", "client2", "client3"]
        
        for sid in sids:
            stream_management_service.add_client_to_streaming_room(sid)
        
        clients = stream_management_service.get_streaming_room_clients()
        assert len(clients) == 3
        assert all(sid in clients for sid in sids)

    def test_is_client_in_room_false_cases(self, stream_management_service):
        """is_client_in_room 메서드가 존재하지 않는 클라이언트에 대해 False를 반환하는지 테스트"""
        sid = "nonexistent_client"
        
        assert stream_management_service.is_client_in_streaming_room(sid) is False
        assert stream_management_service.is_client_in_user_room(sid) is False