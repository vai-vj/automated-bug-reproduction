import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv
load_dotenv()

email = os.getenv("JIRA_EMAIL")
api_token = os.getenv("JIRA_API_TOKEN")
domain = os.getenv("JIRA_DOMAIN")


# New JQL search endpoint
url = f"{domain}/rest/api/3/search/jql"

params = {
    "jql": "project = AIBUG",
    "maxResults": 5,
    "fields": ["summary", "description"]
}

response = requests.get(
    url,
    auth=HTTPBasicAuth(email, api_token),
    headers={"Accept": "application/json"},
    params=params
)

data = response.json()

print(data["issues"][0])
print(data["issues"][1])

'''debugging to check if issues are being fetched correctly and to understand the structure of the response'''
# if "issues" in data:
#     for issue in data["issues"]:
#         issue_key = issue.get("key", "NoKey")
#         summary = issue.get("fields", {}).get("summary", "No summary")
#         description = issue.get("fields", {}).get("description", "No description")
#         print(issue_key, ":", summary)
#         print("Description:", description)
#         print("---")
# else:
#     print("No issues found.")


#extract plain text from ADF (Atlassian Document Format) content
def extract_text(adf_content):
    text_parts = []

    def traverse(nodes):
        for node in nodes:
            if node['type'] == 'paragraph':
                for c in node.get('content', []):
                    if c['type'] == 'text':
                        text_parts.append(c['text'])
                text_parts.append('\n')  # new line after paragraph
            elif node['type'] == 'orderedList':
                order = node.get('attrs', {}).get('order', 1)
                for i, item in enumerate(node.get('content', []), start=order):
                    for c in item.get('content', []):
                        for t in c.get('content', []):
                            if t['type'] == 'text':
                                text_parts.append(f"{i}. {t['text']}")
                    text_parts.append('\n')

    traverse(adf_content.get('content', []))
    return ''.join(text_parts)


for issue in data["issues"]:
    key = issue["key"]
    summary = issue["fields"]["summary"]
    description_adf = issue["fields"]["description"]
    description_text = extract_text(description_adf)

    print(key, ":", summary)
    print(description_text)
    print("---")



#######################################################################

# # Jira search endpoint
# url = f"{domain}/rest/api/3/search/jql"

# # JQL to get all bugs in the project
# params = {
#     "jql": "project = AIBUG",
#     "maxResults": 5  # fetch first 5 tickets
# }

# response = requests.get(
#     url,
#     auth=HTTPBasicAuth(email, api_token),
#     headers={"Accept": "application/json"},
#     params=params
# )

# data = response.json()

# print(data.keys())

# for issue in data["issues"]:
#     print(issue["key"], ":", issue["fields"]["summary"])

############################################################################

# issue_key = "AIBUG-1"

# url = f"{domain}/rest/api/3/issue/{issue_key}"

# response = requests.get(
#     url,
#     auth=HTTPBasicAuth(email, api_token),
#     headers={"Accept": "application/json"}
# )

# print(response.status_code)
# print(response.text)