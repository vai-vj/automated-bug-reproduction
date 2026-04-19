def build_bug_repro_prompt(incident_text: str) -> str:
    return f"""
You are a QA automation assistant.

Return ONLY a valid JSON object. The response MUST be in JSON format

Required EXACT JSON keys:
reproduction_steps: list of strings
preconditions: list of strings
expected_behavior: string
actual_behavior: string
test_steps: list of strings

CRITICAL RULES:
- test_steps MUST NOT be empty
- test_steps MUST contain at least 3 steps
- Each step MUST start with an action verb
- Each step MUST be executable UI action

VALID EXAMPLES:
- go to https://example.com/login
- enter "user" into username field
- click login button

INVALID EXAMPLES:
- try logging in
- check the page
- attempt to submit

If unsure, make reasonable assumptions.

Incident report:
{incident_text}
"""


 
def build_confidence_prompt(report_text: str, test_steps: list[str]) -> str:
    return f"""
You are a QA automation expert.
Given a bug report and generated reproductions steps, evaluate the quality of the reproduction steps in the exact format specified below without explaining.   

BUG REPORT:
{report_text}
GENERATED STEPS:
{test_steps}

Analyze:
1. How confident are you that these steps will reproduce the bug? (return a value between 0.0-1.0 with 1 decimal place where 1.0 is very confident)
2. Identify any critical information missing from the steps that could prevent successful reproduction.
3. Provide a brief resoning for your confidence rating based on the completeness and clarity of the steps.
4. Assess the risk level of relying on these steps for reproduction (low, medium, high). Do not explain this. 

Return ONLY a valid JSON object. The response MUST be in JSON format.

Required JSON structure:
{{
    "confidence": float,
    "missing_information": list of strings,
    "reasoning": string,
    "risk_level": string
}}
    """