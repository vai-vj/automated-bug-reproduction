from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm(incident_text: str) -> str:
    prompt = f"""
You are a software QA assistant.

Given the following incident report, describe:
1. Possible reproduction steps
2. Preconditions
3. Expected vs actual behavior

Incident report:
{incident_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


# from openai import OpenAI
# import os
# from dotenv import load_dotenv


# load_dotenv()

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# def call_llm(report_text: str) -> str:
#     prompt = f"""
#     You are a software QA assistant.

#     Given the following bug report, describe:
#     1. Possible reproduction steps
#     2. Preconditions
#     3. Expected vs. actual behavior

#     Bug Report:
#     {report_text}
#     """

#     response = client.chat_completions.create(
#         messages=[ {"role": "user", "content": prompt} ],
#         max_tokens=400,
#         temperature=0.3
#     )
#     return response.choices[0].message.content











# # from huggingface_hub import InferenceClient
# # import os
# # from dotenv import load_dotenv

# # load_dotenv()

# # client = InferenceClient(
# #     model="mistralai/Mistral-7B-Instruct-v0.2",
# #     token="REMOVEDqfYDHTGbUAPiQMDuQyELSAjGNKATfhBggc"
# # )

# # def call_llm(report_text: str) -> str:
# #     prompt = f"""
# # You are a software QA assistant.

# # Given the following bug report, describe:
# # 1. Possible reproduction steps
# # 2. Preconditions
# # 3. Expected vs. actual behavior

# # Bug Report:
# # {report_text}
# # """

# #     response = client.text_generation(
# #         prompt,
# #         max_new_tokens=400,
# #         temperature=0.3
# #     )

# #     return response
