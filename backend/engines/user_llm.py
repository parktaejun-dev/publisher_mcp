from backend.db.models import Document
from .base import BaseEngine, ParsedResult
from typing import Dict, Any

class UserLLMEngine(BaseEngine):
    def parse(self, document: Document) -> ParsedResult:
        # User LLM engine is primarily for 'import_json' API
        # If this is called by job runner, it means user selected this engine but didn't provide JSON
        # This flow might be for "User manually extracts via UI" -> saves draft
        # So job runner here just creates an empty draft for user to fill?
        # Or fails because it expects JSON?

        # Let's return a special status or just empty draft
        return ParsedResult(
            raw_json={},
            validation_report={"valid": False, "errors": ["User LLM requires manual input"]},
            status="needs_review"
        )
