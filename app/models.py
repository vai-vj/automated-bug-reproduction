from pydantic import BaseModel
from typing import List

class BugReportOutput(BaseModel):
    reproduction_steps: List[str]
    preconditions: List[str]
    expected_behavior: str
    actual_behavior: str