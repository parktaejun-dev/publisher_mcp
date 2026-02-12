from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import hashlib
import os
import shutil
import uuid

from backend.db.session import get_db
from backend.db.models import Document, IngestJob

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/data/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", status_code=201)
async def create_document(
    file: UploadFile = File(...),
    media_owner: str = Form(...),
    media_name: str = Form(...),
    doc_type: str = Form(...),
    confidentiality: str = Form("internal"),
    doc_date: Optional[date] = Form(None),
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # Calculate SHA256
    file.file.seek(0)
    content = file.file.read()
    file.file.seek(0)
    sha256_hash = hashlib.sha256(content).hexdigest()

    # Check for duplicate
    existing_doc = db.query(Document).filter(Document.sha256 == sha256_hash).first()
    if existing_doc:
        raise HTTPException(status_code=409, detail=f"Document already exists with ID: {existing_doc.id}")

    # Save file
    file_id = uuid.uuid4()
    stored_filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)

    with open(file_path, "wb") as f:
        f.write(content)

    # Parse tags
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    # Create Document record
    new_doc = Document(
        id=file_id,
        stored_filename=stored_filename,
        original_filename=file.filename,
        content_type=file.content_type,
        file_size=len(content),
        sha256=sha256_hash,
        media_owner=media_owner,
        media_name=media_name,
        doc_type=doc_type,
        doc_date=doc_date,
        tags=tag_list,
        confidentiality=confidentiality
    )
    db.add(new_doc)

    # Create Ingest Job
    # Default engine: server_native (Phase 1)
    default_engine = os.getenv("ENGINE_DEFAULT", "server_native")
    new_job = IngestJob(
        document_id=new_doc.id,
        engine=default_engine,
        status="queued"
    )
    db.add(new_job)

    db.commit()
    db.refresh(new_doc)
    db.refresh(new_job)

    return {"document_id": str(new_doc.id), "job_id": str(new_job.id), "message": "Document uploaded and ingestion queued."}

@router.get("/")
def list_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    return docs

@router.get("/{document_id}")
def get_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
