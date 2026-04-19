import os
from fastapi import HTTPException
import requests
from requests.auth import HTTPBasicAuth
from app.utils.utils import extract_plain_text

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

    return extract_plain_text(description_adf)