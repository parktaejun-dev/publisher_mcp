from dataclasses import dataclass
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from backend.db.models import Document

@dataclass
class ParsedResult:
    raw_json: Dict[str, Any]
    validation_report: Dict[str, Any]
    status: str # 'draft_saved' | 'needs_review' | 'failed'

class BaseEngine(ABC):
    @abstractmethod
    def parse(self, document: Document) -> ParsedResult:
        pass

def get_engine(engine_name: str):
    # Lazy imports to avoid circular deps
    from .server_native import ServerNativeEngine
    from .notebooklm import NotebookLMEngine
    from .user_llm import UserLLMEngine

    if engine_name == "server_native":
        return ServerNativeEngine()
    elif engine_name == "notebooklm":
        return NotebookLMEngine()
    elif engine_name == "user_llm":
        return UserLLMEngine()
    else:
        return None
