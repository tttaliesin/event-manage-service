import pytest
from unittest.mock import AsyncMock
from event_manage_service.application.usecases.request_log_usecase import RequestLogUseCase
from event_manage_service.domain.model.request_log import RequestLog


class TestRequestLogUseCase:
    """RequestLogUseCase에 대한 테스트 케이스"""

    @pytest.mark.asyncio
    async def test_get_logs_by_event_type(self, request_log_usecase, mock_service_log_repository):
        """이벤트 타입별 로그 조회 테스트"""
        event_type = "user_login"
        expected_logs = [
            RequestLog(event_type="user_login", client_ip="192.168.1.1"),
            RequestLog(event_type="user_login", client_ip="192.168.1.2")
        ]
        
        mock_service_log_repository.find_by_event_type.return_value = expected_logs
        
        result = await request_log_usecase.get_logs_by_event_type(event_type)
        
        mock_service_log_repository.find_by_event_type.assert_called_once_with(event_type)
        assert result == expected_logs
        assert len(result) == 2
        assert all(log.event_type == "user_login" for log in result)

    @pytest.mark.asyncio
    async def test_get_logs_by_event_type_empty_result(self, request_log_usecase, mock_service_log_repository):
        """빈 결과로 이벤트 타입별 로그 조회 테스트"""
        event_type = "nonexistent_event"
        expected_logs = []
        
        mock_service_log_repository.find_by_event_type.return_value = expected_logs
        
        result = await request_log_usecase.get_logs_by_event_type(event_type)
        
        mock_service_log_repository.find_by_event_type.assert_called_once_with(event_type)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_logs_by_event_type_repository_error(self, request_log_usecase, mock_service_log_repository):
        """get_logs_by_event_type에서 리포지토리 에러 처리 테스트"""
        event_type = "test_event"
        mock_service_log_repository.find_by_event_type.side_effect = Exception("Database error")
        
        with pytest.raises(Exception, match="Database error"):
            await request_log_usecase.get_logs_by_event_type(event_type)
        
        mock_service_log_repository.find_by_event_type.assert_called_once_with(event_type)

    @pytest.mark.asyncio
    async def test_get_all_logs(self, request_log_usecase, mock_service_log_repository):
        """모든 로그 조회 테스트"""
        expected_logs = [
            RequestLog(event_type="login", client_ip="192.168.1.1"),
            RequestLog(event_type="logout", client_ip="192.168.1.2"),
            RequestLog(event_type="view_page", client_ip="192.168.1.3")
        ]
        
        mock_service_log_repository.find_all.return_value = expected_logs
        
        result = await request_log_usecase.get_all_logs()
        
        mock_service_log_repository.find_all.assert_called_once()
        assert result == expected_logs
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_get_all_logs_empty_result(self, request_log_usecase, mock_service_log_repository):
        """빈 결과로 모든 로그 조회 테스트"""
        expected_logs = []
        
        mock_service_log_repository.find_all.return_value = expected_logs
        
        result = await request_log_usecase.get_all_logs()
        
        mock_service_log_repository.find_all.assert_called_once()
        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_logs_repository_error(self, request_log_usecase, mock_service_log_repository):
        """get_all_logs에서 리포지토리 에러 처리 테스트"""
        mock_service_log_repository.find_all.side_effect = Exception("Connection timeout")
        
        with pytest.raises(Exception, match="Connection timeout"):
            await request_log_usecase.get_all_logs()
        
        mock_service_log_repository.find_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_dependency_injection(self, mock_service_log_repository, request_log_service):
        """의존성이 올바르게 주입되는지 테스트"""
        usecase = RequestLogUseCase(
            repository=mock_service_log_repository,
            domain_service=request_log_service
        )
        
        assert usecase.repository is mock_service_log_repository
        assert usecase.domain_service is request_log_service

    @pytest.mark.asyncio
    async def test_multiple_calls_independence(self, request_log_usecase, mock_service_log_repository):
        """여러 호출이 독립적인지 테스트"""
        # First call
        event_type_1 = "event_1"
        logs_1 = [RequestLog(event_type="event_1", client_ip="192.168.1.1")]
        mock_service_log_repository.find_by_event_type.return_value = logs_1
        
        result_1 = await request_log_usecase.get_logs_by_event_type(event_type_1)
        
        # Second call
        event_type_2 = "event_2"
        logs_2 = [RequestLog(event_type="event_2", client_ip="192.168.1.2")]
        mock_service_log_repository.find_by_event_type.return_value = logs_2
        
        result_2 = await request_log_usecase.get_logs_by_event_type(event_type_2)
        
        # Verify calls
        assert mock_service_log_repository.find_by_event_type.call_count == 2
        assert result_1 != result_2
        assert result_1[0].event_type == "event_1"
        assert result_2[0].event_type == "event_2"