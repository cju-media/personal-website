from playwright.sync_api import sync_playwright
import time
import os

def test_bio_section(page):
    # Get absolute path to the file
    cwd = os.getcwd()
    file_path = f"file://{cwd}/homepage/homepageFull.html"
    print(f"Loading {file_path}")

    page.goto(file_path)

    # Scroll to bottom to trigger intersection observer
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # Wait for the bio text to be visible or have the 'show' class
    # The container has class 'container hidden' initially.
    # When intersecting, it gets 'show'.

    # Note: there might be multiple elements with class 'hidden' if I didn't scope correctly,
    # but the bio container is the one I am interested in.
    # It contains text "Cameron Johnston-Ushijima"

    bio_text = page.get_by_text("Cameron Johnston-Ushijima is a composer")

    # Scroll into view explicitly
    bio_text.scroll_into_view_if_needed()

    # Wait for the parent to have class 'show' (or just wait for visibility if transition finishes)
    # Since opacity starts at 0, we should wait for it to become visible.
    # However, playright 'visible' check might pass even if opacity is changing.

    # Let's wait a bit for transition
    time.sleep(2)

    # Take screenshot of the bottom area
    page.screenshot(path="verification/verification.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        try:
            test_bio_section(page)
        finally:
            browser.close()
