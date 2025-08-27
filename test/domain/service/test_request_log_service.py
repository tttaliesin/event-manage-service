import pytest
from datetime import datetime
from event_manage_service.domain.service.request_log_service import RequestLogService
from event_manage_service.domain.model.request_log import RequestLog


class TestRequestLogService:
    """RequestLogService 테스트 케이스"""

    def test_create_request_log_with_all_parameters(self, request_log_service) -> None:
        """모든 매개변수로 요청 로그 생성 테스트"""
        metadata = {"session_id": "abc123", "user_agent": "test"}
        
        log = request_log_service.create_request_log(
            event_type="user_login",
            client_ip="192.168.1.100",
            metadata=metadata
        )
        
        assert isinstance(log, RequestLog)
        assert log.event_type == "user_login"
        assert log.client_ip == "192.168.1.100"
        assert log.metadata == metadata
        assert isinstance(log.timestamp, datetime)

    def test_create_request_log_minimal_parameters(self, request_log_service) -> None:
        """최소 매개변수로 요청 로그 생성 테스트"""
        log = request_log_service.create_request_log(
            event_type="minimal_event"
        )
        
        assert isinstance(log, RequestLog)
        assert log.event_type == "minimal_event"
        assert log.client_ip is None
        assert log.metadata == {}
        assert isinstance(log.timestamp, datetime)

    def test_create_request_log_with_none_metadata(self, request_log_service) -> None:
        """None 메타데이터로 요청 로그 생성 테스트 (기본값은 빈 딕셔너리)"""
        log = request_log_service.create_request_log(
            event_type="test_event",
            client_ip="10.0.0.1",
            metadata=None
        )
        
        assert log.metadata == {}

    def test_create_request_log_with_empty_metadata(self, request_log_service) -> None:
        """명시적으로 빈 메타데이터로 요청 로그 생성 테스트"""
        log = request_log_service.create_request_log(
            event_type="test_event",
            client_ip="10.0.0.1",
            metadata={}
        )
        
        assert log.metadata == {}

    def test_validate_log_entry_valid_log(self, request_log_service) -> None:
        """유효한 로그 엔트리 유효성 검사 테스트"""
        log = RequestLog(
            event_type="valid_event",
            client_ip="192.168.1.1"
        )
        
        assert request_log_service.validate_log_entry(log) is True

    def test_validate_log_entry_missing_event_type(self, request_log_service) -> None:
        """event_type이 누락된 경우 유효성 검사 실패 테스트"""
        log = RequestLog(
            event_type="",
            client_ip="192.168.1.1"
        )
        
        assert request_log_service.validate_log_entry(log) is False

    def test_validate_log_entry_missing_client_ip(self, request_log_service) -> None:
        """client_ip가 누락된 경우 유효성 검사 실패 테스트"""
        log = RequestLog(
            event_type="test_event",
            client_ip=None
        )
        
        assert request_log_service.validate_log_entry(log) is False

    def test_validate_log_entry_both_missing(self, request_log_service) -> None:
        """필수 필드 둘 다 누락된 경우 유효성 검사 실패 테스트"""
        log = RequestLog(
            event_type="",
            client_ip=None
        )
        
        assert request_log_service.validate_log_entry(log) is False

    def test_validate_log_entry_with_whitespace_event_type(self, request_log_service) -> None:
        """공백만 있는 event_type으로 유효성 검사 테스트"""
        log = RequestLog(
            event_type="   ",
            client_ip="192.168.1.1"
        )
        
        # bool("   ")는 True이지만, 비즈니스 규칙에따라 고려해야 할 수 있음
        assert request_log_service.validate_log_entry(log) is True

    def test_filter_logs_by_event_type_single_match(self, request_log_service) -> None:
        """단일 매치로 이벤트 타입별 로그 필터링 테스트"""
        logs = [
            RequestLog(event_type="login", client_ip="192.168.1.1"),
            RequestLog(event_type="logout", client_ip="192.168.1.2"),
            RequestLog(event_type="view", client_ip="192.168.1.3")
        ]
        
        filtered = request_log_service.filter_logs_by_event_type(logs, "login")
        
        assert len(filtered) == 1
        assert filtered[0].event_type == "login"
        assert filtered[0].client_ip == "192.168.1.1"

    def test_filter_logs_by_event_type_multiple_matches(self, request_log_service) -> None:
        """다중 매치로 이벤트 타입별 로그 필터링 테스트"""
        logs = [
            RequestLog(event_type="login", client_ip="192.168.1.1"),
            RequestLog(event_type="login", client_ip="192.168.1.2"),
            RequestLog(event_type="logout", client_ip="192.168.1.3")
        ]
        
        filtered = request_log_service.filter_logs_by_event_type(logs, "login")
        
        assert len(filtered) == 2
        assert all(log.event_type == "login" for log in filtered)

    def test_filter_logs_by_event_type_no_matches(self, request_log_service) -> None:
        """매치 없는 이벤트 타입별 로그 필터링 테스트"""
        logs = [
            RequestLog(event_type="login", client_ip="192.168.1.1"),
            RequestLog(event_type="logout", client_ip="192.168.1.2")
        ]
        
        filtered = request_log_service.filter_logs_by_event_type(logs, "register")
        
        assert len(filtered) == 0
        assert filtered == []

    def test_filter_logs_by_event_type_empty_list(self, request_log_service) -> None:
        """빈 로그 리스트 필터링 테스트"""
        logs = []
        
        filtered = request_log_service.filter_logs_by_event_type(logs, "any_event")
        
        assert len(filtered) == 0
        assert filtered == []

    def test_filter_logs_by_event_type_case_sensitive(self, request_log_service) -> None:
        """필터링이 대소문자를 구분하는지 테스트"""
        logs = [
            RequestLog(event_type="Login", client_ip="192.168.1.1"),
            RequestLog(event_type="login", client_ip="192.168.1.2")
        ]
        
        filtered_upper = request_log_service.filter_logs_by_event_type(logs, "Login")
        filtered_lower = request_log_service.filter_logs_by_event_type(logs, "login")
        
        assert len(filtered_upper) == 1
        assert len(filtered_lower) == 1
        assert filtered_upper[0].event_type == "Login"
        assert filtered_lower[0].event_type == "login"