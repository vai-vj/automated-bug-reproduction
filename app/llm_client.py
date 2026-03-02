from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



def call_llm(incident_text: str) -> str:
    prompt = f"""
You are a software QA assistant.

Return JSON with EXACT keys:
reproduction_steps: list of strings
preconditions: list of strings
expected_behavior: string
actual_behavior: string

Incident report:
{incident_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    return response.choices[0].message.content





# def call_llm(incident_text: str) -> str:
#     prompt = f"""
# You are a software QA assistant.

# Given the following incident report, return a valid JSON with the exact keys:
# 1. reproduction_steps: list of strings
# 2. preconditions: list of strings
# 3. expected_behavior: string
# 4. actual_behavior: string

# Do not include any explanations, numbers, or extra text. Only return the JSON object.

# Incident report:
# {incident_text}
# """

#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         response_format={"type": "json_object"},
#         # message=[
#         #     {"role": "user", "content": prompt}
#         # ]
#     )

#     return response.choices[0].message.content.strip() #strip to remove any leading/trailing whitespace
