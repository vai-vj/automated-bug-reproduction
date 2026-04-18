from pydantic import BaseModel
from typing import List

# Ensures jira_key is provided in request body and is valid
class JiraKeyRequest(BaseModel):
    jira_key: str

#
class BugReportOutput(BaseModel):
    reproduction_steps: List[str]
    preconditions: List[str]
    expected_behavior: str
    actual_behavior: str
    test_steps: List[str] = []

#Structured report on LLM confidence in generated test steps, including missing info and risk level
class ConfidenceReport(BaseModel):
    confidence: float #0.0-1.0
    missing_information: list[str]
    reasoning: str
    risk_level: str #low, medium, high