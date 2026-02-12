from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import uuid
import hashlib
import json
from datetime import datetime

from backend.db.session import get_db
from backend.db.models import Document, MediaRecordDraft

router = APIRouter()

@router.post("/", status_code=201)
def import_json(
    meta: Dict[str, Any] = Body(...),
    extracted_json: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    # TODO: Validate schema here using Validator service (once created)
    # For now, assume valid.

    # Create Document Placeholder
    # We use a dummy SHA256 based on JSON content to avoid unique constraint issues if imported twice
    json_str = json.dumps(extracted_json, sort_keys=True)
    sha256_hash = hashlib.sha256(json_str.encode()).hexdigest()

    # Check if exists? Maybe just create new one with unique ID but same hash?
    # Documents table has unique index on sha256.
    existing_doc = db.query(Document).filter(Document.sha256 == sha256_hash).first()

    if existing_doc:
        doc_id = existing_doc.id
    else:
        doc_id = uuid.uuid4()
        new_doc = Document(
            id=doc_id,
            stored_filename="imported",
            original_filename=meta.get("filename", "imported_json.json"),
            content_type="application/json",
            file_size=len(json_str),
            sha256=sha256_hash,
            media_owner=meta.get("media_owner", "Unknown"),
            media_name=meta.get("media_name", "Imported Media"),
            doc_type=meta.get("doc_type", "etc"),
            doc_date=None, # or parse meta date
            tags=meta.get("tags", []),
            confidentiality=meta.get("confidentiality", "internal")
        )
        db.add(new_doc)
        db.flush()

    # Create Draft
    # Engine B: User LLM
    new_draft = MediaRecordDraft(
        document_id=doc_id,
        engine="user_llm",
        raw_json=extracted_json,
        validation_report={"status": "imported", "notes": "No server validation yet"},
        status="draft_saved"
    )
    db.add(new_draft)

    db.commit()
    db.refresh(new_draft)

    return {"draft_id": str(new_draft.id), "document_id": str(doc_id), "message": "JSON imported as draft."}
