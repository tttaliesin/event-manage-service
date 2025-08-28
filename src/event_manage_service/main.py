import logging
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from event_manage_service.config.settings import settings
from event_manage_service.config.container import Container
from event_manage_service.adapter.outbound.persistence.entity import Base
from sqlalchemy import select
from event_manage_service.adapter.inbound.websocket.socketio_server import SocektIOServer
from event_manage_service.adapter.inbound.http.service_log_router import router as log_router

def setup_socketio_handlers(sio, stream_handler, event_logger):
    adapter = SocektIOServer(sio, stream_handler, event_logger)
    adapter.resister_event()


logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def create_app() -> FastAPI:

    container = Container()

    # Create tables and warm up connection pool
    if settings.env == "DEV" :
        engine = container.db_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    # Connection pool 워밍업
    try:
        session_factory = container.session_maker()
        async with session_factory() as session:
            await session.execute(select(1))
        print("Database connection pool warmed up successfully")
    except Exception as e:
        print(f"Warning: Could not warm up database connection pool: {e}")

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description=settings.description
    )

    # CORS 설정 추가
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.container = container
    container.wire(modules=[__name__, "event_manage_service.adapter.inbound.http.service_log_router"])

    app.include_router(log_router)

    sio = container.socketio_server()
    stream_handler = container.stream_handler()
    event_logger = container.event_logger()
    
    setup_socketio_handlers(sio, stream_handler, event_logger)

    socketio_asgi_app = socketio.ASGIApp(sio, other_asgi_app=app)

    return socketio_asgi_app

import asyncio

async def main():
    return await create_app()

app = asyncio.run(main())

if __name__ == "__main__":
    import uvicorn
    import signal
    
    def signal_handler(signum, frame):
        print("Shutting down gracefully...")
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        uvicorn.run(app, host=settings.host, port=settings.port)
    except KeyboardInterrupt:
        print("Server stopped.")    
