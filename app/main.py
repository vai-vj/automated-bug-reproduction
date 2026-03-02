from fastapi import FastAPI
from app.llm_client import call_llm
from app.models import BugReportOutput
from dotenv import load_dotenv
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
    ####report = "Submit button crashes the app when clicked without filling the form."
    #read sample bug report from file
    with open("data/sample_bug.txt", "r") as f:
        report_text = f.read()
        
    response_text = call_llm(report_text)

    def clean_json(text):
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]  # Get content between triple backticks
        return text.strip()

    try:
        data = json.loads(clean_json(response_text))
        bug_output = BugReportOutput(**data)
    except Exception as e:
        return {"error": str(e), "raw response": response_text}
    
    return{"structured_output": bug_output.dict()}