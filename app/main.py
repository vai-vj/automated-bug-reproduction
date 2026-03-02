from fastapi import FastAPI
from app.llm_client import call_llm
from app.models import BugReportOutput
from dotenv import load_dotenv
import json

load_dotenv()
import os

print("OPENAI_API KEY exists:", bool(os.getenv("OPENAI_API_KEY"))) #debugging

app = FastAPI(title="Automated Bug Reproduction")

@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/debug-llm")
def debug_llm():
    with open("data/sample_bug.txt", "r") as f:
        report_text = f.read()

    llm_output = call_llm(report_text)
    print("LLM Output:", repr(llm_output))  #debug print

    # llm_json = json.loads(llm_output)    # Convert to a Python dict

    return {
        "report": report_text,
        "llm_output": llm_output
    }

@app.get("/test-json")
def test_json():
    report = "Submit button crashes the app when clicked without filling the form."
    response_text = call_llm(report)

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