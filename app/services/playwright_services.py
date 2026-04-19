import os
import subprocess
import sys

def generate_playwright_test(test_steps, test_name="generated_test"):
    steps_code = []
    url = None

    #STEP 1: Extract URL
    for step in test_steps:
        step_lower = step.lower()
        if ("go to" in step_lower or "navigate" in step_lower) and not url:
            url = step.split("to")[-1].strip()

    if not url:
        url = "https://example.com"

    steps_code.append(f'        page.goto("{url}")')
    steps_code.append('        page.wait_for_timeout(1000)')

    #STEP 2: Detect login flow
    is_login_flow = any(
        "login" in step.lower() or "username" in step.lower() or "password" in step.lower()
        for step in test_steps
    )

    #STEP 3: SAFE DEMO (login handling)
    if "the-internet.herokuapp.com/login" in url or is_login_flow:
        steps_code.extend([
            '        # Fill username field',
            '        page.fill("#username", "demo_user")',
            '        page.wait_for_timeout(1000)',

            '        # Fill password field',
            '        page.fill("#password", "demo_pass")',
            '        page.wait_for_timeout(1000)',

            '        # Click login button',
            '        page.click("button[type=submit]")',
            '        page.wait_for_timeout(3000)',
        ])

    else:
        #GENERIC FALLBACK
        for step in test_steps:
            step_lower = step.lower()

            if "go to" in step_lower or "navigate" in step_lower:
                continue

            elif "click" in step_lower:
                target = step.split("click")[-1].strip()
                steps_code.append(f'        page.click("text={target}")')

            elif "enter" in step_lower or "type" in step_lower:
                steps_code.append('        page.fill("input", "sample_text")')

            elif "submit" in step_lower:
                steps_code.append('        page.click("button[type=submit]")')

            else:
                steps_code.append(f'        # TODO: {step}')

            steps_code.append('        page.wait_for_timeout(1000)')

    #FINAL CODE
    code = f"""
from playwright.sync_api import sync_playwright

def test_{test_name}():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

{chr(10).join(steps_code)}

        page.wait_for_timeout(3000)
        browser.close()

if __name__ == "__main__":
    test_{test_name}()
"""

    return code



def save_playwright_file(code, folder_path, filename="playwright_text.py"):
    filepath = os.path.join(folder_path, filename)

    with open(filepath, "w") as f:
        f.write(code)

    return filepath



def run_playwright_test(filepath):

    #Executes the generated Playwright test file
    try:
        result = subprocess.run(
            [sys.executable, filepath],
            capture_output=True,
            text=True,
            timeout=60
        )

        return {
            "status": "passed" if result.returncode == 0 else "failed",
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "stdout": "",
            "stderr": "Test execution timed out"
        }