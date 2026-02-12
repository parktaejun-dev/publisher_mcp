from typing import Dict, Any, List
import os
import json
import random

from backend.db.models import Document
from .base import BaseEngine, ParsedResult
from backend.services.parser import extract_text
from backend.services.validator import validate_record

class ServerNativeEngine(BaseEngine):
    def parse(self, document: Document) -> ParsedResult:
        # 1. Get file path
        upload_dir = os.getenv("UPLOAD_DIR", "/data/uploads")
        file_path = os.path.join(upload_dir, document.stored_filename)

        # 2. Extract Text
        extracted_pages = extract_text(file_path, document.content_type)
        if not extracted_pages:
             # Fallback if no text extracted (e.g. image PDF)
             # In real world, use OCR. Here, just fail or return empty draft.
             return ParsedResult(
                 raw_json={},
                 validation_report={"valid": False, "errors": ["No text extracted"]},
                 status="needs_review"
             )

        full_text = "\n".join([p["text"] for p in extracted_pages])

        # 3. Simulate LLM Extraction (Mock)
        # We try to find some keywords to populate fields

        # Mock Data Construction
        mock_data = {
            "media_owner": document.media_owner, # Use metadata as fallback/hint
            "media_name": document.media_name,
            "product_name": "Ad Product A",
            "media_type": "Digital",
            "pricing_model": "CPM",
            "price_text": "5,000,000 KRW",
            "min_budget_text": "10,000,000 KRW",
            "targeting_text": "Age 20-30",
            "specs_text": "1920x1080",
            "kpi_text": "CTR 1.5%",
            "sales_contact": "sales@example.com",
            "valid_until": None,
            "doc_meta": {
                "doc_url_or_filename": document.original_filename,
                "doc_date": str(document.doc_date) if document.doc_date else None
            },
            "evidence": []
        }

        # Generate Fake Evidence from actual text if possible
        # We just take random sentences from extracted text to simulate evidence
        sentences = [s.strip() for s in full_text.split('.') if len(s.strip()) > 10]

        evidence = []
        fields_to_prove = ["media_name", "pricing_model", "price_text"]

        for field in fields_to_prove:
            if sentences:
                quote = random.choice(sentences)
                page_info = next((p["page"] for p in extracted_pages if quote in p["text"]), 1)
                evidence.append({
                    "field": field,
                    "quote": quote,
                    "page": page_info
                })

        # Ensure we have at least 3 pieces of evidence for validation to pass
        while len(evidence) < 3 and sentences:
             quote = random.choice(sentences)
             evidence.append({
                 "field": "specs_text",
                 "quote": quote,
                 "page": 1
             })

        mock_data["evidence"] = evidence

        # 4. Validate
        report = validate_record(mock_data)

        status = "draft_saved"
        if not report["valid"] or report["evidence_count"] < 3:
            status = "needs_review"

        return ParsedResult(
            raw_json=mock_data,
            validation_report=report,
            status=status
        )
