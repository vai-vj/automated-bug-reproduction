# 🪲 Automated Bug Reproduction System

## 📌 Overview
The Automated Bug Reproduction System converts natural language bug reports into structured, executable reproduction steps. By leveraging large language models (LLMs) and browser automation tools, the system generates and executes scripts that reproduce reported issues, reducing manual debugging effort and improving consistency in bug reporting.

---

## 🚀 Features
- Accepts bug inputs as:
  - Plain text files (`.txt`)
  - Jira bug keys (for issue retrieval and processing)
- Converts bug descriptions into structured reproduction steps  
- Generates executable automation scripts using Playwright  
- Automatically runs scripts to reproduce issues in a browser  
- Generates an ambiguity and confidence report
- Organizes outputs into uniquely labeled folders per run 

---

## 🏗️ System Architecture
The system consists of the following components:

- **Backend API (FastAPI)**  
  Handles incoming requests and orchestrates the pipeline  

- **LLM Service**  
  Generates reproduction steps, test generation, and confidence report from bug descriptions  

- **Pipeline Service**  
  Transforms LLM output into structured steps and scripts  

- **Automation Engine (Playwright)**  
  Executes generated scripts to reproduce bugs in a live browser session

---

## 🔄 Workflow
1. User provides input as a `.txt` bug description or Jira bug key  
2. The system constructs a prompt and sends it to the LLM  
3. The LLM generates structured reproduction steps  
4. Steps are converted into an executable Playwright script  
5. The script is executed to simulate the bug scenario
6. LLM generates ambiguity and confidence report 
7. Outputs are generated and stored in a labeled folder within the `output/` directory 

---

## 🛠️ Tech Stack
- **Backend:** Python, FastAPI  
- **Automation:** Playwright  
- **LLM Integration:** OpenAI API
- **Other:** JSON-based pipeline processing  

---
## ⚙️ Setup & Installation

```bash
git clone https://github.com/vai-vj/automated-bug-reproduction.git
cd automated-bug-reproduction

#Optional but recommended
python -m venv venv

venv\Scripts\activate      #Windows
#source venv/bin/activate  #Mac/ Linux

pip install -r requirements.txt

uvicorn app.main:app --reload
```

## 👤 Contributor
**Vaishnavi Vijayaraghavan**
