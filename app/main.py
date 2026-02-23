from fastapi import FastAPI
from app.llm_client import call_llm
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