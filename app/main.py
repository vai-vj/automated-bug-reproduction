from fastapi import FastAPI
from app.llm_client import call_llm
from app.models import BugReportOutput
from app.jira_test import extract_plain_text
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth
import json
import os

#get OPENAI_API_KEY from .env file
load_dotenv()
print("OPENAI_API KEY exists:", bool(os.getenv("OPENAI_API_KEY"))) #debugging print

app = FastAPI(title="Automated Bug Reproduction")

#confirm server is running at root directory
@app.get("/")
def root():
    return {"status": "ok"}

#Clean JSON from LLM
def clean_json(text):
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]  # Get content between triple backticks
        return text.strip()

#call LLM on sample bug report and return result
@app.get("/debug-llm")
def debug_llm():
    #read sample bug report from file
    with open("data/sample_bug.txt", "r") as f:
        report_text = f.read()

    #call LLM function and store raw AI output
    llm_output = call_llm(report_text)
    print("LLM Output:", repr(llm_output))  #debugging print

    #return original report and structured LLM output as JSON
    return {
        "report": report_text,
        "llm_output": llm_output
    }

#validate JSON using Pydantic model
@app.get("/test-json")
def test_json():
    #read sample bug report from file
    with open("data/sample_bug.txt", "r") as f:
        report_text = f.read()
        
    response_text = call_llm(report_text)

    try:
        data = json.loads(clean_json(response_text))
        bug_output = BugReportOutput(**data)
    except Exception as e:
        return {"error": str(e), "raw response": response_text}
    
    return{"structured_output": bug_output.dict()}
    
#---------------------------------------------------------------------------------------------
class JiraKeyRequest(BaseModel):
    jira_key: str

#Fetch Jira issue & send to LLM
@app.post("/process-jira-bug")
def process_jira_bug(jira_request: JiraKeyRequest):
    jira_key = jira_request.jira_key

    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")
    domain = os.getenv("JIRA_DOMAIN")

    # Fetch single Jira issue
    url = f"{domain}/rest/api/3/issue/{jira_key}"
    response = requests.get(
        url,
        auth=HTTPBasicAuth(email, api_token),
        headers={"Accept": "application/json"}
    )
    if response.status_code != 200:
        return {"error": f"Jira returned {response.status_code}"}

    issue = response.json()
    description_adf = issue["fields"]["description"]
    if not description_adf:
        return {"error": f"Issue {jira_key} has no description"}

    description_text = extract_plain_text(description_adf)
    llm_response = call_llm(description_text)

    try:
        data = json.loads(clean_json(llm_response))
        bug_output = BugReportOutput(**data)
    except Exception as e:
        return {"error": str(e), "raw_response": llm_response}

    return {
        "jira_key": jira_key,
        "structured_output": bug_output.dict()
    }



# @app.post("/process-jira-bug")
# def process_jira_bug(jira_request: JiraKeyRequest):
#     jira_key = jira_request.jira_key

#     email = os.getenv("JIRA_EMAIL")
#     api_token = os.getenv("JIRA_API_TOKEN")
#     domain = os.getenv("JIRA_DOMAIN")


#     # New JQL search endpoint
#     url = f"{domain}/rest/api/3/search/jql"

#     response = requests.get(
#         url,
#         auth=HTTPBasicAuth(email, api_token),
#         headers={"Accept": "application/json"},
#     )

#     issue = response.json()

#     description_adf = issue["fields"]["description"]
#     description_text = extract_plain_text(description_adf)
#     llm_response = call_llm(description_text)

#     try:
#         data = json.loads(clean_json(llm_response))
#         bug_output = BugReportOutput(**data)

#     except Exception as e:
#         return {"error": str(e), "raw response": llm_response}

#     return {
#         "jira_key": jira_key,
#         "structured_output": bug_output.dict()
#         }


