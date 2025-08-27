import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException
from typing import List
from datetime import datetime

from event_manage_service.domain.model.request_log import RequestLog
from event_manage_service.application.dto.service_log_dto import RequestLogResponseDTO


class TestSimpleHTTPAPI:
    """의존성 주입 없는 간단한 HTTP API 테스트"""

    @pytest.fixture
    def mock_event_logger(self) -> AsyncMock:
        """이벤트 로거 모킹"""
        mock_logger = AsyncMock()
        sample_logs = [
            RequestLog(
                id=1,
                event_type="user_login", 
                client_ip="192.168.1.1",
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                metadata={"user_agent": "Mozilla/5.0"}
            ),
            RequestLog(
                id=2,
                event_type="capture_start",
                client_ip="192.168.1.2", 
                timestamp=datetime(2023, 1, 1, 12, 5, 0),
                metadata={"sid": "client123"}
            ),
            RequestLog(
                id=3,
                event_type="user_login",
                client_ip="192.168.1.3",
                timestamp=datetime(2023, 1, 1, 12, 10, 0), 
                metadata={"session_id": "session456"}
            )
        ]
        mock_logger.get_all_logs.return_value = sample_logs
        mock_logger.get_logs_by_event_type.return_value = [
            log for log in sample_logs if log.event_type == "user_login"
        ]
        return mock_logger

    @pytest.fixture 
    def app(self, mock_event_logger: AsyncMock) -> FastAPI:
        """테스트 앱 생성"""
        app = FastAPI(title="Test Event Manage Service")
        
        # 의존성 주입 없는 간단한 엔드포인트
        @app.get("/logs", response_model=List[RequestLogResponseDTO])
        async def get_all_logs():
            logs = await mock_event_logger.get_all_logs()
            return [RequestLogResponseDTO(
                id=log.id,
                event_type=log.event_type,
                client_ip=log.client_ip,
                timestamp=log.timestamp,
                metadata=log.metadata
            ) for log in logs]
        
        @app.get("/logs/event/{event_type}", response_model=List[RequestLogResponseDTO])
        async def get_logs_by_event_type(event_type: str):
            logs = await mock_event_logger.get_logs_by_event_type(event_type)
            return [RequestLogResponseDTO(
                id=log.id,
                event_type=log.event_type,
                client_ip=log.client_ip,
                timestamp=log.timestamp,
                metadata=log.metadata
            ) for log in logs]
        
        @app.get("/")
        async def health_check():
            return {"status": "ok"}
            
        return app

    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        """테스트 클라이언트"""
        return TestClient(app)

    def test_health_check_endpoint(self, client: TestClient) -> None:
        """헬스 체크 엔드포인트 테스트"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_get_all_logs_endpoint(self, client: TestClient) -> None:
        """모든 로그를 반환하는 GET /logs 엔드포인트 테스트"""
        response = client.get("/logs")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 3
        
        # 로그 구조 확인
        log = data[0]
        assert "id" in log
        assert "event_type" in log
        assert "client_ip" in log
        assert "timestamp" in log
        assert log["event_type"] == "user_login"

    def test_get_logs_by_event_type_endpoint(self, client: TestClient) -> None:
        """GET /logs/event/{event_type} 엔드포인트 테스트"""
        response = client.get("/logs/event/user_login")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 2  # Only user_login events
        assert all(log["event_type"] == "user_login" for log in data)

    def test_logs_response_format(self, client: TestClient) -> None:
        """로그 응답이 올바른 형식을 가지는지 테스트"""
        response = client.get("/logs")
        
        assert response.status_code == 200
        data = response.json()
        
        if data:  # If there are logs
            log = data[0]
            
            # 필수 필드
            assert "id" in log
            assert "event_type" in log
            assert "client_ip" in log
            assert "timestamp" in log
            
            # 데이터 타입 확인
            assert isinstance(log["id"], int)
            assert isinstance(log["event_type"], str)
            assert isinstance(log["client_ip"], str)
            assert isinstance(log["timestamp"], str)  # ISO format string

    def test_content_type_headers(self, client: TestClient) -> None:
        """\uc62c\ubc14\ub978 \ucf58\ud150\uce20 \ud0c0\uc785 \ud5e4\ub354\uac00 \ubc18\ud658\ub418\ub294\uc9c0 \ud14c\uc2a4\ud2b8"""
        response = client.get("/logs")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"