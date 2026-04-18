
from playwright.sync_api import sync_playwright

def test_generated_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()



        browser.close()
