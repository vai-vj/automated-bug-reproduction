import os

from fastapi import FastAPI, Query, HTTPException
from dotenv import load_dotenv

from app.schemas.models import JiraKeyRequest
from app.services.pipeline_services import run_pipeline
from app.services.jira_service import fetch_jira_description


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

#----------------------------------------------------------------------------------------------

#Process bug report from file
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
        
    return run_pipeline(report_text, prefix="file")


#---------------------------------------------------------------------------------------------

#Process bug report from Jira key
@app.post("/process-jira-bug", include_in_schema=False)
def process_jira_bug(jira_request: JiraKeyRequest):

    #Extract jira key from request body
    jira_key = jira_request.jira_key

    #Fetch Jira description as plain text 
    report_text = fetch_jira_description(jira_key)
    
    #Run pipeline
    response = run_pipeline(report_text, prefix=jira_key)
    
    #Add jira_key to response
    response["jira_key"] = jira_key

    return response


#---------------------------------------------------------------------------------------------
#Unified endpoint to process either Jira key or file input
@app.post("/analyze", 
          summary="Analayze a bug report from Jira or a file", 
          description="Provide either a Jira key or a file path to analyze a bug report. The response will contain structured information extracted from the report.")
def analyze_bug(
    input_type: str = Query(..., description="Type: 'jira' or 'file'"), 
    jira_key: str = None, 
    filepath: str = None
    ):

    #If Jira, ensure jira_key is provided and valid before processing
    if input_type.lower() == "jira" or input_type.lower() == "jira_key":
        if not jira_key:
            raise HTTPException(
                status_code=400, 
                detail="jira_key is required for Jira input type"
            )
        return process_jira_bug(JiraKeyRequest(jira_key=jira_key))
    
    #If file, ensure filepath is provided and valid before processing
    elif input_type.lower() == "file" or input_type.lower() == "filepath":
        if not filepath:
            raise HTTPException(
                status_code=400,
                detail="filepath is required for file input type"
            )
        return process_file(filepath)
    
    #Invalid input type
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid input_type. Must be 'jira' or 'file'"
        )
