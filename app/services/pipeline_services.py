import json
from fastapi import HTTPException

from app.services.llm_client import call_llm
from app.services.llm_prompts import build_bug_repro_prompt
from app.services.llm_services import generate_confidence_report
from app.schemas.models import BugReportOutput
from app.utils.utils import save_output, extract_plain_text
from app.services.playwright_services import generate_playwright_test, save_test_file, run_playwright_test


def run_pipeline(report_text: str, prefix: str):
    #Extract structured bug info using LLM
    bug_output = process_bug_text(report_text)

    #Build final response (Playwright, confidence report, save output)
    return build_response(
        bug_output, 
        prefix = prefix, 
        original_text = report_text
    )


def process_bug_text(report_text: str):

    prompt = build_bug_repro_prompt(report_text)
    data = call_llm(prompt)

    #validate and parse LLM output using Pydantic model
    try:
        return BugReportOutput(**data)
    
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse LLM output: {str(e)} | DATA: {data}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse LLM output: {str(e)}"
        )


def build_response(bug_output, prefix, original_text):
    test_filepath, execution_result = run_playwright_pipeline(bug_output.test_steps, prefix)

    output_path = save_output(bug_output.model_dump(), prefix=prefix)

    confidence_report = generate_confidence_report(
        original_text,
        bug_output.test_steps
    )   

    return {
        "structured_output": bug_output.model_dump(),
        "confidence_report": confidence_report.model_dump(),
        "location_saved": output_path,
        "test_file": test_filepath,
        "execution_result": execution_result
    }


def run_playwright_pipeline(test_steps, prefix="playwright"):
    # Generate Playwright test
    test_code = generate_playwright_test(test_steps)
    # Save test file
    test_filepath = save_test_file(test_code, prefix=prefix)
    # Run test
    execution_result = run_playwright_test(test_filepath)
    return test_filepath, execution_result


