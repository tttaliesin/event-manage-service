# Event Management Service
실시간 이벤트 관리 및 스트림 중개 서비스입니다. WebSocket을 통한 실시간 통신과 비디오 스트리밍을 지원합니다.

## 아키텍처
```
src/
├── adapter/          # 외부 시스템과의 인터페이스
│   ├── inbound/      # 외부 → 애플리케이션
│   │   ├── http/     # REST API 엔드포인트
│   │   └── websocket/ # SocketIO 이벤트 핸들러
│   └── outbound/     # 애플리케이션 → 외부
│       ├── messaging/ # SocketIO 메시징
│       └── persistence/ # 데이터베이스 액세스
├── application/      # 애플리케이션 계층
│   ├── dto/          # 데이터 전송 객체
│   ├── port/         # 인터페이스 정의
│   └── usecases/     # 비즈니스 로직 조율
├── domain/           # 도메인 계층
│   ├── model/        # 도메인 모델
│   └── service/      # 도메인 서비스
└── config/           # 설정 및 의존성 주입
```

## 주요 기능
- **실시간 통신**: SocketIO 기반 WebSocket 통신
- **비디오 스트리밍**: 실시간 비디오 프레임 중계
- **이벤트 로깅**: 클라이언트 활동 추적 및 기록
- **룸 관리**: 사용자별 스트리밍 룸 관리
- **스트림 상태 관리**: 캡처 상태 실시간 모니터링

## 기술 스택
- **Framework**: FastAPI
- **WebSocket**: python-socketio
- **Database**: MySQL (aiomysql)
- **ORM**: SQLAlchemy (Async)
- **DI Container**: dependency-injector
- **Settings**: pydantic-settings

## 시작하기

### 요구사항

- Python 3.13+
- MySQL Database
- uv (권장 패키지 관리자)

### 설치
```bash
# 프로젝트 클론
git clone <repository-url>
cd event-manage-service

# 의존성 설치
uv install

# 개발 의존성 포함 설치
uv install --group dev
```

### 환경 설정
`.env` 파일을 생성하여 설정을 구성하세요:

```env
# Application Settings
APP_NAME=Event Manage Service
DEBUG=true
HOST=localhost
PORT=8001
ENV=DEV

# Database
DATABASE_URL=mysql+aiomysql://user:password@host:port/database
```

### 실행
```bash
# 개발 서버 실행
uv run python src/main.py

# 또는 uvicorn 직접 실행
uv run uvicorn src.main:app --host localhost --port 8001 --reload
```

## API 엔드포인트

### WebSocket 이벤트
| 이벤트 | 설명 | 방향 |
|-------|------|------|
| `connect` | 클라이언트 연결 | Client → Server |
| `response_client_metadata` | 클라이언트 메타데이터 응답 | Client → Server |
| `start_capture` | 비디오 캡처 시작 | Client → Server |
| `stop_capture` | 비디오 캡처 중지 | Client → Server |
| `join_streaming_room` | 스트리밍 룸 입장 | Client → Server |
| `leave_streaming_room` | 스트리밍 룸 퇴장 | Client → Server |
| `video_frame_relay` | 비디오 프레임 전송 | Stream Service → Server |
| `request_capture_status` | 캡처 상태 요청 | Client → Server |

### HTTP API
- `GET /logs` - 서비스 로그 조회
- `POST /logs` - 로그 기록

## 도메인 모델
### RequestLog
- 클라이언트 이벤트 로깅을 위한 도메인 모델
- IP 주소, 타임스탬프, 메타데이터 포함

### 서비스 계층
- **RequestLogService**: 로그 생성 및 관리
- **StreamManagementService**: 스트림 서비스 관리

## 테스트

```bash
# 테스트 실행
uv run pytest

# 커버리지와 함께 실행
uv run pytest --cov=src
```

## 개발

### 코드 포맷팅
```bash
# Black으로 포맷팅
uv run black src/

# isort로 import 정렬
uv run isort src/
```

### 의존성 관리
```bash
# 새 의존성 추가
uv add <package-name>

# 개발 의존성 추가
uv add --group dev <package-name>
```