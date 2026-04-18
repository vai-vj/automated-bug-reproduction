from pydantic import BaseModel
from typing import List

class BugReportOutput(BaseModel):
    reproduction_steps: List[str]
    preconditions: List[str]
    expected_behavior: str
    actual_behavior: str
    test_steps: List[str] = []


class ConfidenceReport(BaseModel):
    confidence: float #0.0-1.0
    missing_information: list[str]
    reasoning: str
    risk_level: str #low, medium, high