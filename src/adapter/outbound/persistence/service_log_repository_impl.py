from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

import json
import logging

from application.port.outbound.service_log_repository import ServiceLogRepository
from domain.model.request_log import RequestLog
from .entity import RequestLogEntity

logger = logging.getLogger(__name__)

class ServiceLogRepositoryImpl(ServiceLogRepository):
    def __init__(self, session_maker: sessionmaker[AsyncSession]):
        self.session_maker = session_maker
    
    def _to_entity(self, domain_log: RequestLog) -> RequestLogEntity:
        """Convert domain model to entity"""
        return RequestLogEntity(
            id=domain_log.id,
            event_type=domain_log.event_type,
            client_ip=domain_log.client_ip,
            timestamp=domain_log.timestamp,
            request_metadata=json.dumps(domain_log.metadata) if domain_log.metadata else None
        )
    
    def _to_domain(self, entity: RequestLogEntity) -> RequestLog:
        """Convert entity to domain model"""
        metadata = json.loads(entity.request_metadata) if entity.request_metadata else None
        return RequestLog(
            id=entity.id,
            event_type=entity.event_type,
            client_ip=entity.client_ip,
            timestamp=entity.timestamp,
            metadata=metadata
        )
    
    async def save(self, log: RequestLog) -> RequestLog:
        """Save a request log"""
        try:
            async with self.session_maker() as session:
                entity = self._to_entity(log)
                session.add(entity)
                await session.commit()
                await session.refresh(entity)
                return self._to_domain(entity)
        except (DisconnectionError, SQLAlchemyError) as e:
            logger.error(f"로그 저장 실패: {e}")
            raise e
        except Exception as e:
            logger.error(f"로그 저장 중 예상치 못한 오류: {e}")
            raise e
    
    async def find_by_id(self, log_id: int) -> Optional[RequestLog]:
        """Find log by ID"""
        async with self.session_maker() as session:
            result = await session.execute(
                select(RequestLogEntity).where(RequestLogEntity.id == log_id)
            )
            entity = result.scalar_one_or_none()
            return self._to_domain(entity) if entity else None
    
    async def find_by_event_type(self, event_type: str) -> List[RequestLog]:
        """Find logs by event type"""
        async with self.session_maker() as session:
            result = await session.execute(
                select(RequestLogEntity).where(RequestLogEntity.event_type == event_type)
            )
            entities = result.scalars().all()
            return [self._to_domain(entity) for entity in entities]
    
    async def find_all(self) -> List[RequestLog]:
        try:
            async with self.session_maker() as session:
                result = await session.execute(select(RequestLogEntity))
                entities = result.scalars().all()
                return [self._to_domain(entity) for entity in entities]
        except (DisconnectionError, SQLAlchemyError) as e:
            logger.error(f"모든 로그 조회 실패: {e}")
            return []  # 빈 목록 반환
        except Exception as e:
            logger.error(f"find_all에서 예상치 못한 오류: {e}")
            return []  # 빈 목록 반환