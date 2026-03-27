import os
import json
from datetime import datetime

#Clean JSON from LLM (remove extra whitespace and backticks)
def clean_json(text):
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]  # Get content between triple backticks
        return text.strip()


#extract plain text from ADF (Atlassian Document Format = JSON with nodes of par/lists)
def extract_plain_text(adf_content):
    text_parts = []

    def traverse(nodes):
        for node in nodes:
            #extract text from paragraphs and add newline after each
            if node['type'] == 'paragraph':
                for c in node.get('content', []):
                    if c['type'] == 'text':
                        text_parts.append(c['text'])
                text_parts.append('\n') 
            #read order of list, extract text, prepend with numeric order, add newline after each
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


#save structured JSON output to file with timestamped filename & jira_key / file prefix
def save_output(data, prefix=""):
    timestamp = datetime.now().strftime("%m%d%Y_%H%M%S")
    filename = f"{prefix}_{timestamp}.json"
    filepath = os.path.join("output", filename)

    #store output in output folder
    with open(filepath, "w") as f:
        #Write JSON to file with indentation
        json.dump(data, f, indent=2)

    return filepath