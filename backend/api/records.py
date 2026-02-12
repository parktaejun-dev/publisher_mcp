from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

from backend.db.session import get_db
from backend.db.models import MediaRecordDraft, MediaRecord, Evidence, Document

router = APIRouter()

@router.get("/")
def list_records(
    kind: str = Query(..., regex="^(draft|approved)$"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    if kind == "draft":
        records = db.query(MediaRecordDraft).order_by(MediaRecordDraft.created_at.desc()).offset(skip).limit(limit).all()
        return records
    else:
        records = db.query(MediaRecord).order_by(MediaRecord.created_at.desc()).offset(skip).limit(limit).all()
        return records

@router.get("/draft/{draft_id}")
def get_draft(draft_id: str, db: Session = Depends(get_db)):
    draft = db.query(MediaRecordDraft).filter(MediaRecordDraft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft

@router.patch("/draft/{draft_id}")
def update_draft(
    draft_id: str,
    raw_json: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    draft = db.query(MediaRecordDraft).filter(MediaRecordDraft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    # TODO: We should re-validate the JSON here against the schema and update validation_report
    # For now, just update the JSON
    draft.raw_json = raw_json
    # Reset status to draft_saved or keep as is?
    # If edited, maybe it needs review again?
    # Prompt says: "PATCH /api/records/draft/{id} (raw_json 수정 저장)"

    db.commit()
    db.refresh(draft)
    return draft

@router.post("/draft/{draft_id}/approve")
def approve_draft(draft_id: str, db: Session = Depends(get_db)):
    draft = db.query(MediaRecordDraft).filter(MediaRecordDraft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    # Extract fields from raw_json
    data = draft.raw_json

    # Create Approved Record
    new_record = MediaRecord(
        draft_id=draft.id,
        document_id=draft.document_id,
        media_owner=data.get("media_owner"),
        media_name=data.get("media_name"),
        media_type=data.get("media_type"),
        product_name=data.get("product_name"),
        pricing_model=data.get("pricing_model"),
        price_text=data.get("price_text"),
        min_budget_text=data.get("min_budget_text"),
        targeting_text=data.get("targeting_text"),
        specs_text=data.get("specs_text"),
        kpi_text=data.get("kpi_text"),
        sales_contact=data.get("sales_contact"),
        # valid_until might need parsing if it's a date string, or schema handles it.
        # Schema says string or null. Model says Date.
        # If it's a string, we might need to parse it.
        # For MVP, if parsing fails, we might leave it null or handle error.
        # Let's assume for now it comes as YYYY-MM-DD or we leave it null if format wrong.
        valid_until=None
    )

    # Try parsing valid_until
    if data.get("valid_until"):
        try:
            new_record.valid_until = datetime.strptime(data.get("valid_until"), "%Y-%m-%d").date()
        except ValueError:
            pass # Log warning?

    db.add(new_record)
    db.flush() # Get ID

    # Copy Evidence
    evidence_list = data.get("evidence", [])
    for ev in evidence_list:
        new_ev = Evidence(
            record_kind="approved",
            record_id=new_record.id,
            field=ev.get("field"),
            quote=ev.get("quote"),
            page=ev.get("page")
        )
        db.add(new_ev)

    db.commit()
    db.refresh(new_record)

    return new_record
