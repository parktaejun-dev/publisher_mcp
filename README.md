# KOBACO Ad Data Layer MVP

KOBACO Ad Data Layer는 매체 제안서(PDF, PPTX 등)를 파싱하여 구조화된 JSON 데이터로 변환하고, 이를 AI 에이전트(MCP)가 활용할 수 있도록 지원하는 시스템입니다. 'Draft First' 및 'Text First' 원칙을 준수하며, 원본 데이터의 근거(Evidence: 인용구, 페이지 번호)를 추적합니다.

## 주요 기능 (Key Features)

*   **Draft First Workflow**: 파싱된 데이터는 즉시 반영되지 않고 'Draft(초안)' 상태로 저장되며, 관리자의 검토 및 승인(Approve) 과정을 거쳐야 검색 가능한 데이터가 됩니다.
*   **Evidence Tracking**: 추출된 데이터가 원본 문서의 어디에서 왔는지(필드, 인용구, 페이지 번호)를 추적하여 신뢰성을 보장합니다.
*   **MCP (Model Context Protocol) Integration**: Claude와 같은 AI 모델이 자연어로 매체 데이터를 검색하고 추천받을 수 있도록 MCP 서버를 제공합니다.
*   **Multi-Format Support**: PDF, PPTX 등의 다양한 문서 형식을 지원합니다.

## 기술 스택 (Tech Stack)

*   **Backend**: Python 3.11, FastAPI (REST API)
*   **Frontend**: Next.js 14+ (App Router), Tailwind CSS
*   **Database**: PostgreSQL 16 (pgcrypto)
*   **Worker**: Python Background Worker (비동기 작업 처리)
*   **Infrastructure**: Docker, Docker Compose
*   **AI Interface**: FastMCP (MCP Server)

## 사전 요구 사항 (Prerequisites)

*   Docker & Docker Compose
*   Python 3.11+ (MCP 서버 로컬 실행 시 필요)
*   Node.js 20+ (프론트엔드 로컬 개발 시 필요, Docker 사용 시 불필요)

## 설치 및 실행 (Installation & Setup)

이 프로젝트는 Docker Compose를 사용하여 손쉽게 실행할 수 있습니다.

1.  **레포지토리 클론 (Clone Repository)**
    ```bash
    git clone <repository-url>
    cd kobaco-ad-data-layer
    ```

2.  **환경 변수 설정 (Environment Variables)**
    `.env.example` 파일을 복사하여 `.env` 파일을 생성합니다.
    ```bash
    cp .env.example .env
    ```
    기본 설정값으로도 실행 가능하지만, 필요에 따라 `DATABASE_URL` 등을 수정할 수 있습니다.

3.  **서비스 실행 (Run with Docker Compose)**
    ```bash
    docker-compose up --build
    ```
    이 명령어는 DB, Backend, Worker, Frontend 컨테이너를 빌드하고 실행합니다.
    *   **Frontend**: http://localhost:3000
    *   **Backend API**: http://localhost:8000
    *   **API Docs**: http://localhost:8000/docs

## 사용 가이드 (Usage Guide - Smoke Test Workflow)

시스템의 전체 흐름을 확인하기 위한 'Smoke Test' 절차는 다음과 같습니다.

### 1. 문서 업로드 (Document Upload)
1.  브라우저에서 [http://localhost:3000](http://localhost:3000)으로 접속합니다.
2.  상단 메뉴 또는 `/documents` 경로로 이동하여 **Upload Document** 섹션을 찾습니다.
3.  Media Owner, Media Name 등 필수 정보를 입력하고 PDF 또는 PPTX 파일을 선택하여 **Upload** 버튼을 클릭합니다.

### 2. 작업 처리 (Job Processing)
1.  업로드가 완료되면 백그라운드 Worker가 문서를 파싱합니다.
2.  Docker 로그에서 `worker` 컨테이너의 로그를 통해 진행 상황을 확인할 수 있습니다.
    ```bash
    docker-compose logs -f worker
    ```

### 3. 검토 및 승인 (Review & Approve)
1.  파싱이 완료되면 [http://localhost:3000/records](http://localhost:3000/records)로 이동합니다.
2.  **Drafts** 탭을 클릭하여 생성된 초안을 확인합니다.
3.  **Review & Approve** 링크를 클릭하여 상세 페이지로 이동합니다.
4.  추출된 데이터와 원본 증거(Evidence)를 검토한 후, 하단의 **Approve** 버튼을 클릭하여 데이터를 승인합니다. 승인된 데이터만 검색 대상이 됩니다.

### 4. AI 검색 (MCP Search)
승인된 데이터는 MCP 서버를 통해 AI 에이전트가 검색할 수 있습니다. MCP 서버는 현재 Docker Compose에 포함되어 있지 않으므로 로컬에서 실행해야 합니다.

**MCP 서버 실행 방법:**

1.  `mcp-server` 디렉토리로 이동합니다.
    ```bash
    cd mcp-server
    ```
2.  의존성을 설치합니다. (가상환경 권장)
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  MCP 서버를 실행합니다.
    ```bash
    python main.py
    ```
    또는 Claude Desktop 설정 파일(`claude_desktop_config.json`)에 다음과 같이 추가하여 사용할 수 있습니다.

    ```json
    {
      "mcpServers": {
        "kobaco-ad-layer": {
          "command": "python",
          "args": ["/absolute/path/to/kobaco-ad-data-layer/mcp-server/main.py"]
        }
      }
    }
    ```

## 프로젝트 구조 (Project Structure)

```
.
├── backend/            # FastAPI 백엔드 및 워커 로직
│   ├── api/            # API 라우터 (documents, jobs, records 등)
│   ├── services/       # 비즈니스 로직 및 파서
│   └── ...
├── frontend/           # Next.js 프론트엔드
│   ├── app/            # App Router 페이지
│   └── ...
├── mcp-server/         # FastMCP 기반 MCP 서버 구현
├── scripts/            # DB 초기화 스크립트 등
├── docker-compose.yml  # Docker Compose 설정
└── README.md           # 프로젝트 문서
```

## 문제 해결 (Troubleshooting)

*   **DB 연결 오류**: `docker-compose up` 실행 시 DB가 완전히 뜰 때까지 잠시 기다려야 할 수 있습니다. `backend` 서비스는 `db` 서비스에 의존하므로 자동으로 재시도합니다.
*   **포트 충돌**: 3000(Frontend), 8000(Backend), 5432(Postgres) 포트가 이미 사용 중인지 확인하세요.
*   **MCP 연결 실패**: MCP 서버 실행 시 `DATABASE_URL` 환경 변수가 올바르게 설정되었는지 확인하세요. `.env` 파일의 설정을 참고하십시오.
