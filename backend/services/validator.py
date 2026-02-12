import json
import os
import jsonschema
from typing import Dict, Any, List

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "schema", "media_record.schema.json")

def load_schema():
    with open(SCHEMA_PATH, "r") as f:
        return json.load(f)

MEDIA_RECORD_SCHEMA = load_schema()

def validate_record(data: Dict[str, Any]) -> Dict[str, Any]:
    report = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "evidence_count": 0
    }

    # 1. Schema Validation
    try:
        jsonschema.validate(instance=data, schema=MEDIA_RECORD_SCHEMA)
    except jsonschema.exceptions.ValidationError as e:
        report["valid"] = False
        report["errors"].append(e.message)
        # We can try to get more errors if we use a validator instance,
        # but for now one is enough to mark invalid.

    # 2. Evidence Check (even if schema passed, we double check counts for report)
    evidence = data.get("evidence", [])
    report["evidence_count"] = len(evidence)

    if len(evidence) < 3:
        # Schema should have caught this, but we add explicit warning/error if needed
        if report["valid"]: # If schema somehow passed (e.g. schema changed)
             report["valid"] = False
             report["errors"].append(f"Insufficient evidence: {len(evidence)} < 3")

    # 3. Check for specific required fields if needed (schema handles this)

    return report
