import os
import json

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

from app.services.llm_client import call_llm, generate_confidence_report
from app.schemas.models import BugReportOutput, JiraKeyRequest
from app.utils import utils
from app.services.playwright_services import generate_playwright_test, save_test_file, run_playwright_test


#get environment variables from .env file
load_dotenv()

#Create API app (Swagger UI)
app = FastAPI(title="Automated Bug Reproduction")

#confirm server is running at root directory
@app.get("/")
def root():
    return {
        "status": "ok",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "jira_configured": all([
           os.getenv("JIRA_EMAIL"),
           os.getenv("JIRA_API_TOKEN"),
           os.getenv("JIRA_DOMAIN") 
        ])
        }



#fetches file from filepath, extracts description, calls LLM, validates output, saves to file, returns structured data and file location
@app.get("/process-file", include_in_schema=False)
def process_file(filepath: str):

    #Check if filepath exists/ valid
    if not filepath.endswith(".txt"):
        raise HTTPException(
            status_code=400, 
            detail="Only .txt files are supported"
        )
    elif not os.path.exists(filepath):
        raise HTTPException(
            status_code=404, 
            detail="File not found"
        )

    #read bug report from file
    with open(filepath, "r") as f:
        report_text = f.read()
        
    bug_output = process_bug_text(report_text)
    
    return build_response(bug_output, prefix="file", original_text=report_text)


#---------------------------------------------------------------------------------------------

#Fetches Jira issue, extracts description, calls LLM, validates output, saves to file, returns structured data and file location
@app.post("/process-jira-bug", include_in_schema=False)
def process_jira_bug(jira_request: JiraKeyRequest):
    #Extract jira key from request body
    jira_key = jira_request.jira_key

    report_text = fetch_jira_description(jira_key)
    bug_output = process_bug_text(report_text)
    
    response = build_response(bug_output, prefix=jira_key, original_text=report_text)
    response["jira_key"] = jira_key

    return response


#---------------------------------------------------------------------------------------------
@app.post("/analyze", 
          summary="Analayze a bug report from Jira or a file", 
          description="Provide either a Jira key or a file path to analyze a bug report. The response will contain structured information extracted from the report.")
def analyze_bug(
    input_type: str = Query(..., description="Type: 'jira' or 'file'"), 
    jira_key: str = None, 
    filepath: str = None
    ):

    #If input type is Jira, ensure jira_key is provided and valid, then process Jira bug
    if input_type.lower() == "jira" or input_type.lower() == "jira_key":
        if not jira_key:
            raise HTTPException(
                status_code=400, 
                detail="jira_key is required for Jira input type"
            )
        return process_jira_bug(JiraKeyRequest(jira_key=jira_key))
    
    #If input type is file, ensure filepath is provided and valid, then process file
    elif input_type.lower() == "file" or input_type.lower() == "filepath":
        if not filepath:
            raise HTTPException(
                status_code=400,
                detail="filepath is required for file input type"
            )
        return process_file(filepath)
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid input_type. Must be 'jira' or 'file'"
        )


def process_bug_text(report_text: str):
    #call LLM and store raw output 
    llm_raw_response = call_llm(report_text)

    #validate and parse LLM output using Pydantic model
    try:
        data = json.loads(utils.clean_json(llm_raw_response))
        return BugReportOutput(**data)
    
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail=f"LLM returned invalid JSON format"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse LLM output: {str(e)}"
        )


def run_playwright_pipeline(test_steps, prefix="playwright"):
    # Generate Playwright test
    test_code = generate_playwright_test(test_steps)
    # Save test file
    test_filepath = save_test_file(test_code, prefix=prefix)
    # Run test
    execution_result = run_playwright_test(test_filepath)
    return test_filepath, execution_result

def build_response(bug_output, prefix, original_text):
    test_filepath, execution_result = run_playwright_pipeline(
        bug_output.test_steps, prefix
    )

    output_path = utils.save_output(bug_output.dict(), prefix=prefix)

    confidence_report = generate_confidence_report(
        original_text,
        bug_output.test_steps
    )   

    return {
        "structured_output": bug_output.dict(),
        "confidence_report": confidence_report.dict(),
        "location_saved": output_path,
        "test_file": test_filepath,
        "execution_result": execution_result
    }

def fetch_jira_description(jira_key: str):
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")
    domain = os.getenv("JIRA_DOMAIN")

    url = f"{domain}/rest/api/3/issue/{jira_key}"
    response = requests.get(
        url,
        auth=HTTPBasicAuth(email, api_token),
        headers={"Accept": "application/json"}
    )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404, 
            detail=f"Issue {jira_key} not found in Jira"
        )
    
    if response.status_code != 200:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch issue {jira_key} from Jira: {response.text}"
        )

    issue = response.json()
    description_adf = issue["fields"]["description"]

    if not description_adf:
        raise HTTPException(
            status_code=400, 
            detail=f"Issue {jira_key} does not have a description"
        )

    return utils.extract_plain_text(description_adf)