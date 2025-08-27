import pytest
from typing import Dict, Any, Optional
from datetime import datetime
from event_manage_service.domain.model.request_log import RequestLog


class TestRequestLog:
    """RequestLog 도메인 모델 테스트 케이스"""

    def test_request_log_creation_with_all_fields(self) -> None:
        """모든 필드를 제공하여 RequestLog 생성 테스트"""
        timestamp = datetime.utcnow()
        metadata = {"key": "value", "number": 42}
        
        log = RequestLog(
            id=1,
            event_type="test_event",
            client_ip="192.168.1.1",
            timestamp=timestamp,
            metadata=metadata
        )
        
        assert log.id == 1
        assert log.event_type == "test_event"
        assert log.client_ip == "192.168.1.1"
        assert log.timestamp == timestamp
        assert log.metadata == metadata

    def test_request_log_creation_with_minimal_fields(self) -> None:
        """최소 필수 필드로 RequestLog 생성 테스트"""
        log = RequestLog(
            event_type="minimal_event",
            client_ip="10.0.0.1"
        )
        
        assert log.id is None
        assert log.event_type == "minimal_event"
        assert log.client_ip == "10.0.0.1"
        assert log.metadata is None
        assert isinstance(log.timestamp, datetime)

    def test_request_log_creation_with_defaults(self) -> None:
        """기본값으로 RequestLog 생성 테스트"""
        log = RequestLog()
        
        assert log.id is None
        assert log.event_type == ""
        assert log.client_ip is None
        assert log.metadata is None
        assert isinstance(log.timestamp, datetime)

    def test_request_log_post_init_sets_timestamp(self) -> None:
        """__post_init__가 제공되지 않은 경우 타임스탬프를 설정하는지 테스트"""
        before_creation = datetime.utcnow()
        log = RequestLog(event_type="timestamp_test")
        after_creation = datetime.utcnow()
        
        assert before_creation <= log.timestamp <= after_creation

    def test_request_log_post_init_preserves_existing_timestamp(self) -> None:
        """__post_init__가 기존 타임스탬프를 보존하는지 테스트"""
        custom_timestamp = datetime(2023, 1, 1, 12, 0, 0)
        log = RequestLog(
            event_type="preserve_timestamp_test",
            timestamp=custom_timestamp
        )
        
        assert log.timestamp == custom_timestamp

    def test_request_log_with_complex_metadata(self) -> None:
        """복잡한 메타데이터 구조로 RequestLog 테스트"""
        complex_metadata = {
            "user_agent": "Mozilla/5.0",
            "session": {
                "id": "abc123",
                "duration": 300
            },
            "features": ["streaming", "recording"],
            "stats": {
                "connection_count": 5,
                "bandwidth": 1024.5
            }
        }
        
        log = RequestLog(
            event_type="complex_event",
            client_ip="203.0.113.1",
            metadata=complex_metadata
        )
        
        assert log.metadata == complex_metadata
        assert log.metadata["session"]["id"] == "abc123"
        assert log.metadata["stats"]["bandwidth"] == 1024.5

    def test_request_log_equality(self) -> None:
        """RequestLog 인스턴스 간 동등성 비교 테스트"""
        timestamp = datetime.utcnow()
        metadata = {"test": "data"}
        
        log1 = RequestLog(
            id=1,
            event_type="test",
            client_ip="192.168.1.1",
            timestamp=timestamp,
            metadata=metadata
        )
        
        log2 = RequestLog(
            id=1,
            event_type="test",
            client_ip="192.168.1.1",
            timestamp=timestamp,
            metadata=metadata
        )
        
        # 참고: dataclass는 자동으로 __eq__ 메소드를 제공함
        assert log1 == log2

    def test_request_log_string_representation(self) -> None:
        """RequestLog의 문자열 표현 테스트"""
        log = RequestLog(
            id=1,
            event_type="test_event",
            client_ip="192.168.1.1"
        )
        
        str_repr = str(log)
        assert "RequestLog" in str_repr
        assert "test_event" in str_repr
        assert "192.168.1.1" in str_repr