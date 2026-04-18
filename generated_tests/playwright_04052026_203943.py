
from playwright.sync_api import sync_playwright

def test_generated_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://example.com")
        page.goto("https://the-internet.herokuapp.com/login")
        page.fill("input", "test_input")
        page.fill("input", "test_input")
        page.click("text=Click login button")

        browser.close()
if __name__ == "__main__":
    test_generated_test()
