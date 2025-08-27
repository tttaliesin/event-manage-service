import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
from sqlalchemy.ext.asyncio import AsyncSession

from event_manage_service.adapter.outbound.persistence.service_log_repository_impl import ServiceLogRepositoryImpl
from event_manage_service.adapter.outbound.persistence.entity import RequestLogEntity
from event_manage_service.domain.model.request_log import RequestLog


class TestServiceLogRepositoryImpl:
    """ServiceLogRepositoryImpl에 대한 테스트 케이스"""

    @pytest.fixture
    def mock_session_maker(self, mock_session):
        """세션 메이커 모킹"""
        session_maker = Mock()
        session_maker.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        session_maker.return_value.__aexit__ = AsyncMock(return_value=None)
        return session_maker

    @pytest.fixture
    def repository(self, mock_session_maker):
        """모킹된 세션 메이커로 ServiceLogRepositoryImpl 인스턴스"""
        return ServiceLogRepositoryImpl(mock_session_maker)

    @pytest.fixture
    def sample_domain_log(self):
        """샘플 RequestLog 도메인 모델"""
        return RequestLog(
            id=1,
            event_type="test_event",
            client_ip="192.168.1.1",
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            metadata={"key": "value", "number": 42}
        )

    @pytest.fixture
    def sample_entity(self):
        """샘플 RequestLogEntity"""
        return RequestLogEntity(
            id=1,
            event_type="test_event",
            client_ip="192.168.1.1",
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            request_metadata='{"key": "value", "number": 42}'
        )

    def test_to_entity_conversion(self, repository, sample_domain_log):
        """도메인 모델을 엔티티로 변환하는 테스트"""
        entity = repository._to_entity(sample_domain_log)
        
        assert isinstance(entity, RequestLogEntity)
        assert entity.id == sample_domain_log.id
        assert entity.event_type == sample_domain_log.event_type
        assert entity.client_ip == sample_domain_log.client_ip
        assert entity.timestamp == sample_domain_log.timestamp
        assert entity.request_metadata == '{"key": "value", "number": 42}'

    def test_to_entity_with_none_metadata(self, repository):
        """None 메타데이터를 가진 도메인 모델을 엔티티로 변환하는 테스트"""
        log = RequestLog(
            event_type="test_event",
            client_ip="192.168.1.1",
            metadata=None
        )
        
        entity = repository._to_entity(log)
        
        assert entity.request_metadata is None

    def test_to_entity_with_empty_metadata(self, repository):
        """빈 메타데이터를 가진 도메인 모델을 엔티티로 변환하는 테스트"""
        log = RequestLog(
            event_type="test_event",
            client_ip="192.168.1.1",
            metadata={}
        )
        
        entity = repository._to_entity(log)
        
        assert entity.request_metadata == "{}"

    def test_to_domain_conversion(self, repository, sample_entity):
        """엔티티를 도메인 모델로 변환하는 테스트"""
        domain_log = repository._to_domain(sample_entity)
        
        assert isinstance(domain_log, RequestLog)
        assert domain_log.id == sample_entity.id
        assert domain_log.event_type == sample_entity.event_type
        assert domain_log.client_ip == sample_entity.client_ip
        assert domain_log.timestamp == sample_entity.timestamp
        assert domain_log.metadata == {"key": "value", "number": 42}

    def test_to_domain_with_none_metadata(self, repository):
        """None 메타데이터를 가진 엔티티를 도메인 모델로 변환하는 테스트"""
        entity = RequestLogEntity(
            id=1,
            event_type="test_event",
            client_ip="192.168.1.1",
            timestamp=datetime.utcnow(),
            request_metadata=None
        )
        
        domain_log = repository._to_domain(entity)
        
        assert domain_log.metadata is None

    @pytest.mark.asyncio
    async def test_save_success(self, repository, mock_session, sample_domain_log):
        """성공적인 저장 작업 테스트"""
        # Mock entity after save with ID
        saved_entity = RequestLogEntity(
            id=1,
            event_type="test_event",
            client_ip="192.168.1.1",
            timestamp=sample_domain_log.timestamp,
            request_metadata='{"key": "value", "number": 42}'
        )
        
        mock_session.refresh = AsyncMock()
        
        result = await repository.save(sample_domain_log)
        
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        
        assert isinstance(result, RequestLog)

    @pytest.mark.asyncio
    async def test_save_sqlalchemy_error(self, repository, mock_session, sample_domain_log):
        """SQLAlchemy 에러가 있는 저장 작업 테스트"""
        mock_session.commit.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(SQLAlchemyError):
            await repository.save(sample_domain_log)

    @pytest.mark.asyncio
    async def test_save_disconnection_error(self, repository, mock_session, sample_domain_log):
        """연결 단절 에러가 있는 저장 작업 테스트"""
        mock_session.commit.side_effect = DisconnectionError("Connection lost")
        
        with pytest.raises(DisconnectionError):
            await repository.save(sample_domain_log)

    @pytest.mark.asyncio
    async def test_save_unexpected_error(self, repository, mock_session, sample_domain_log):
        """예상치 못한 에러가 있는 저장 작업 테스트"""
        mock_session.commit.side_effect = Exception("Unexpected error")
        
        with pytest.raises(Exception, match="Unexpected error"):
            await repository.save(sample_domain_log)

    @pytest.mark.asyncio
    async def test_find_by_id_found(self, repository, mock_session, sample_entity):
        """로그가 존재할 때 ID로 찾기 테스트"""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_entity
        mock_session.execute.return_value = mock_result
        
        result = await repository.find_by_id(1)
        
        assert isinstance(result, RequestLog)
        assert result.id == 1
        assert result.event_type == "test_event"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self, repository, mock_session):
        """로그가 존재하지 않을 때 ID로 찾기 테스트"""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        result = await repository.find_by_id(999)
        
        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_by_event_type(self, repository, mock_session, sample_entity):
        """이벤트 타입별 로그 찾기 테스트"""
        entities = [sample_entity, sample_entity]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = entities
        mock_session.execute.return_value = mock_result
        
        result = await repository.find_by_event_type("test_event")
        
        assert len(result) == 2
        assert all(isinstance(log, RequestLog) for log in result)
        assert all(log.event_type == "test_event" for log in result)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_by_event_type_empty(self, repository, mock_session):
        """결과가 없을 때 이벤트 타입별 로그 찾기 테스트"""
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result
        
        result = await repository.find_by_event_type("nonexistent_event")
        
        assert result == []
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_all_success(self, repository, mock_session, sample_entity):
        """모든 로그 성공적으로 찾기 테스트"""
        entities = [sample_entity, sample_entity, sample_entity]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = entities
        mock_session.execute.return_value = mock_result
        
        result = await repository.find_all()
        
        assert len(result) == 3
        assert all(isinstance(log, RequestLog) for log in result)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_all_empty(self, repository, mock_session):
        """븈 결과로 모든 로그 찾기 테스트"""
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result
        
        result = await repository.find_all()
        
        assert result == []
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    @patch('event_manage_service.adapter.outbound.persistence.service_log_repository_impl.logger')
    async def test_find_all_sqlalchemy_error(self, mock_logger, repository, mock_session):
        """SQLAlchemy 에러 시 find_all이 빈 리스트를 반환하는지 테스트"""
        mock_session.execute.side_effect = SQLAlchemyError("Database error")
        
        result = await repository.find_all()
        
        assert result == []
        mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    @patch('event_manage_service.adapter.outbound.persistence.service_log_repository_impl.logger')
    async def test_find_all_disconnection_error(self, mock_logger, repository, mock_session):
        """연결 단절 에러 시 find_all이 빈 리스트를 반환하는지 테스트"""
        mock_session.execute.side_effect = DisconnectionError("Connection lost")
        
        result = await repository.find_all()
        
        assert result == []
        mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    @patch('event_manage_service.adapter.outbound.persistence.service_log_repository_impl.logger')
    async def test_find_all_unexpected_error(self, mock_logger, repository, mock_session):
        """예상치 못한 에러 시 find_all이 빈 리스트를 반환하는지 테스트"""
        mock_session.execute.side_effect = Exception("Unexpected error")
        
        result = await repository.find_all()
        
        assert result == []
        mock_logger.error.assert_called_once()

    def test_json_serialization_complex_metadata(self, repository):
        """복잡한 메타데이터의 JSON 직렬화 테스트"""
        complex_metadata = {
            "nested": {"key": "value"},
            "list": [1, 2, 3],
            "boolean": True,
            "null": None
        }
        
        log = RequestLog(
            event_type="complex_test",
            client_ip="192.168.1.1",
            metadata=complex_metadata
        )
        
        entity = repository._to_entity(log)
        reconstructed_log = repository._to_domain(entity)
        
        assert reconstructed_log.metadata == complex_metadata

    def test_round_trip_conversion(self, repository, sample_domain_log):
        """도메인 -> 엔티티 -> 도메인 순환 변환 테스트"""
        entity = repository._to_entity(sample_domain_log)
        reconstructed_log = repository._to_domain(entity)
        
        assert reconstructed_log.id == sample_domain_log.id
        assert reconstructed_log.event_type == sample_domain_log.event_type
        assert reconstructed_log.client_ip == sample_domain_log.client_ip
        assert reconstructed_log.timestamp == sample_domain_log.timestamp
        assert reconstructed_log.metadata == sample_domain_log.metadata