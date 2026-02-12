# KOBACO Ad Data Layer (MVP)

Media Proposal Parsing System for AI-Driven Strategy Generation.

## 📌 Project Overview
This system is designed to parse media proposals (PDF/PPTX) into structured JSON data, creating a robust "Data Layer" for AI strategy generation. It follows a **Draft-First** and **Evidence-Based** approach, ensuring data accuracy through manual verification.

### Core Philosophy
1.  **Draft First:** All parsed results start as drafts. Nothing enters the approved database without human review.
2.  **Evidence Based:** Every extracted field must be backed by a quote and page number from the original document.
3.  **Engine Agnostic:** Supports multiple parsing engines (Server Native, NotebookLM, User LLM).

## 🏗 System Architecture

The MVP consists of 4 main services managed by Docker Compose:

1.  **`db` (PostgreSQL 16):** Stores documents, jobs, drafts, and approved records. Uses `pgcrypto` for UUIDs.
2.  **`backend` (FastAPI):** Handles file uploads, API requests, and data management.
3.  **`worker` (Python Background Service):** Processes ingestion jobs asynchronously (Parsing & Validation).
4.  **`frontend` (Next.js 14):** A management console for uploading documents and approving drafts.

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- (Optional) Python 3.11+ / Node.js 20+ for local development

### Installation & Run

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd kobaco-ad-data-layer
    ```

2.  **Environment Setup:**
    The project comes with a default `.env.example`. Copy it to `.env` (optional for local dev, docker-compose uses defaults):
    ```bash
    cp .env.example .env
    ```

3.  **Run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    This will start all services:
    - Frontend: http://localhost:3000
    - Backend API: http://localhost:8000
    - Backend Docs: http://localhost:8000/docs
    - Database: localhost:5432

## 📖 Usage Guide

### 1. Upload Document
- Go to **Documents** page (http://localhost:3000/documents).
- Fill in metadata (Media Owner, Name, etc.) and upload a PDF or PPTX file.
- The system will create a **Job** (status: `queued`).

### 2. Monitor Ingestion
- Go to **Jobs** page (http://localhost:3000/jobs).
- The `worker` service picks up queued jobs and processes them using the selected engine (default: `server_native`).
- Status will change from `queued` -> `processing` -> `draft_saved` (or `failed`).

### 3. Review & Approve Draft
- Go to **Records (Drafts)** page (http://localhost:3000/records).
- Click on a draft to view the extracted JSON and validation report.
- Edit the JSON if necessary.
- Click **Approve** to promote the draft to an **Approved Record**.

### 4. AI Integration (MCP)
- The system includes an MCP (Model Context Protocol) server skeleton in `mcp-server/`.
- This allows AI agents (like Claude Desktop) to query the approved database directly.

## 🛠 Development Notes

- **Backend Structure:**
    - `backend/api`: API Routers
    - `backend/db`: Database models & session
    - `backend/engines`: Parsing logic (Server Native, etc.)
    - `backend/services`: Core logic (Job Runner, Validator)
    - `backend/schema`: JSON Schemas

- **Frontend Structure:**
    - `frontend/app`: Next.js App Router pages (`documents`, `jobs`, `records`)

- **Database Schema:**
    - `documents`: Raw files metadata
    - `ingest_jobs`: Processing queue
    - `media_records_draft`: Parsed JSON (unverified)
    - `media_records`: Structured Data (verified)
    - `evidence`: Quotes supporting the data

## ⚠️ MVP Limitations
- **Server Native Engine:** Currently uses a mock implementation that generates dummy data and random evidence from text.
- **File Parsing:** Basic text extraction via `pymupdf` (PDF) and `python-pptx` (PPTX). No OCR yet.
- **Authentication:** Not implemented in MVP.

---
© 2024 KOBACO Ad Data Layer Project
