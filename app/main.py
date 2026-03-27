import os
import json

from fastapi import FastAPI, Query
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

from app.llm_client import call_llm
from app.models import BugReportOutput
from app.utils import extract_plain_text, clean_json, save_output


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
@app.get("/process-file")
def process_file(filepath: str):
    #read sample bug report from file
    with open(filepath, "r") as f:
        report_text = f.read()
        
    #call LLM and store raw output 
    llm_raw_response = call_llm(report_text)

    #validate and parse LLM output using Pydantic model
    try:
        data = json.loads(clean_json(llm_raw_response))
        bug_output = BugReportOutput(**data)
    except Exception as e:
        return {"error": str(e), "raw response": llm_raw_response}
    
    #save output to file
    filepath = save_output(bug_output.dict(), prefix="file")

    return{
        "structured_output": bug_output.dict(),
        "location_saved": filepath
        }


#---------------------------------------------------------------------------------------------
#Ensures jira_key is provided in request body and is valid
class JiraKeyRequest(BaseModel):
    jira_key: str

#Fetches Jira issue, extracts description, calls LLM, validates output, saves to file, returns structured data and file location
@app.post("/process-jira-bug")
def process_jira_bug(jira_request: JiraKeyRequest):
    #Extract jira key from request body
    jira_key = jira_request.jira_key

    #Load credentials
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")
    domain = os.getenv("JIRA_DOMAIN")

    #Call Jira API & fetch Jira issue
    url = f"{domain}/rest/api/3/issue/{jira_key}"
    response = requests.get(
        url,
        auth=HTTPBasicAuth(email, api_token),
        headers={"Accept": "application/json"}
    )

    #Error if Jira request fails
    if response.status_code != 200:
        return {"error": f"Jira returned {response.status_code}"}

    issue = response.json()

    #Extract ADF formatted description from Jira issue
    description_adf = issue["fields"]["description"]
    if not description_adf:
        return {"error": f"Issue {jira_key} has no description"}

    #Convert ADF to plain text and send to LLM for processing
    description_text = extract_plain_text(description_adf)
    llm_response = call_llm(description_text)

    #validate and parse LLM output using Pydantic model
    try:
        data = json.loads(clean_json(llm_response))
        bug_output = BugReportOutput(**data)
    except Exception as e:
        return {"error": str(e), "raw_response": llm_response}
    
    #save output to file
    filepath = save_output(bug_output.dict(), prefix=jira_key)

    return {
        "jira_key": jira_key,
        "structured_output": bug_output.dict(),
        "location_saved": filepath
    }


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
            return {"error": "jira_key is required for jira input type"}
        return process_jira_bug(JiraKeyRequest(jira_key=jira_key))
    
    #If input type is file, ensure filepath is provided and valid, then process file
    elif input_type.lower() == "file" or input_type.lower() == "filepath":
        if not filepath:
            return {"error": "filepath is required for file input type"}
        return process_file(filepath)
    else:
        return {"error": "Invalid input type. Enter 'jira' or 'file'."}



#validate JSON using Pydantic model
# @app.get("/test-json")
# def test_json():
#     #read sample bug report from file
#     with open("data/sample_bug.txt", "r") as f:
#         report_text = f.read()
        
#     llm_raw_response = call_llm(report_text)

#     try:
#         data = json.loads(clean_json(llm_raw_response))
#         bug_output = BugReportOutput(**data)
#     except Exception as e:
#         return {"error": str(e), "raw response": llm_raw_response}
    
#     return{"structured_output": bug_output.dict()}



