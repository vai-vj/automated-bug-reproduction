import json
from fastapi import HTTPException

from app.services.llm_client import call_llm
from app.services.llm_prompts import build_bug_repro_prompt, build_confidence_prompt
from app.utils import utils
from app.schemas.models import BugReportOutput, ConfidenceReport


def extract_bug_structure(incident_text: str) -> BugReportOutput:
    prompt = build_bug_repro_prompt(incident_text)
    raw = call_llm(prompt)
    data = json.loads(utils.clean_json(raw))
    
    return BugReportOutput(**data)


def generate_confidence_report(report_text: str, test_steps: list[str]) -> ConfidenceReport:
    prompt = build_confidence_prompt(report_text, test_steps)
    raw = call_llm(prompt)

    try:
        content = json.loads(utils.clean_json(raw))
        return ConfidenceReport(**content)
    
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate confidence report"
        )