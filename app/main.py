from fastapi import FastAPI

app = FastAPI(title="Automated Bug Reproduction")

@app.get("/")
def root():
    return {"status": "ok"}