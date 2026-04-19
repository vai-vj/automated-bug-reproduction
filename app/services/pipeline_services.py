import json
import os
from fastapi import HTTPException

from app.services.llm_client import call_llm
from app.services.llm_prompts import build_bug_repro_prompt
from app.services.llm_services import generate_confidence_report
from app.schemas.models import BugReportOutput
from app.utils.utils import save_json, create_save_folder
from app.services.playwright_services import generate_playwright_test, save_playwright_file, run_playwright_test


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
    #Create output folder for this execution
    output_folder = create_save_folder(prefix)

    #Save bug reproduction steps output
    bug_filepath = os.path.join(output_folder, "bug_report.json")
    save_json(bug_output.model_dump(), bug_filepath)

    #Generate Playwright test
    test_code = generate_playwright_test(bug_output.test_steps)
    test_filepath = save_playwright_file(test_code, output_folder)

    execution_result = run_playwright_test(test_filepath)

    #Generate confidence report
    confidence_report = generate_confidence_report(
        original_text,
        bug_output.test_steps
    )

    confidence_filepath = os.path.join(output_folder, "confidence_report.json")
    save_json(confidence_report.model_dump(), confidence_filepath)

    #Return response
    return {
        "structured_output": bug_output.model_dump(),
        "confidence_report": confidence_report.model_dump(),
        "output_folder": output_folder,
        "test_file": test_filepath,
        "execution_result": execution_result
    }