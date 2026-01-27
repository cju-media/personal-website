from playwright.sync_api import sync_playwright
import os
import time

def test_bio_responsive(page):
    cwd = os.getcwd()
    file_path = f"file://{cwd}/homepage/homepageFull.html"
    print(f"Loading {file_path}")

    page.goto(file_path)

    # Scroll to bottom
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # Wait for content to appear (opacity transition)
    # The observer adds .bio-show class
    page.wait_for_selector(".bio-container.bio-show")

    # Give it a moment for layout to settle and transitions to end
    time.sleep(2)

    image = page.locator("#myHeadshot")
    text_block = page.locator(".text-block")

    image_box = image.bounding_box()
    text_box = text_block.bounding_box()

    print(f"Image box: {image_box}")
    print(f"Text box: {text_box}")

    # Verify image is below text
    # text top should be < image top
    if image_box['y'] > text_box['y']:
        print("PASS: Image is below text.")
    else:
        print("FAIL: Image is NOT below text.")
        exit(1)

    page.screenshot(path="verification/verification_mobile.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        # Use a mobile viewport
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 400, "height": 800})
        try:
            test_bio_responsive(page)
        finally:
            browser.close()
