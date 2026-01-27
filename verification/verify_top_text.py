from playwright.sync_api import sync_playwright
import os
import json
import time

def test_top_text(page):
    cwd = os.getcwd()
    file_path = f"file://{cwd}/homepage/homepageFull.html"

    # Mock media.json
    media_data = {"headshots": [], "perfVids": [], "artVids": [], "avPics": [], "compPics": [], "prodPics": [], "progPics": [], "soundPics": [], "condPics": []}
    def handle_route(route):
        if "media.json" in route.request.url:
            route.fulfill(status=200, body=json.dumps(media_data), content_type="application/json")
        else:
            route.continue_()
    page.route("**/*", handle_route)

    print(f"Loading {file_path}")
    page.goto(file_path)

    # Wait for JS to load media and init
    time.sleep(2)

    # Scroll to ensure intersection observer triggers
    page.evaluate("window.scrollTo(0, 0)") # Top text is at top

    # Wait a bit for observer
    time.sleep(1)

    # Select all spans
    spans = page.locator(".text-block1 .span-class")
    count = spans.count()
    print(f"Total spans found: {count}")

    if count != 23:
        print(f"FAIL: Expected 23 spans, found {count}")

    # Check delays
    print("Checking transition delays:")
    for i in range(count):
        span = spans.nth(i)
        delay = span.evaluate("el => el.style.transitionDelay")
        txt = span.inner_text()
        classes = span.get_attribute("class")
        print(f"Span {i} ({txt}): delay={delay}, classes={classes}")

        if "landed" not in classes:
            print(f"FAIL: Span {i} does not have 'landed' class!")

    print("Verification done.")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            test_top_text(page)
        finally:
            browser.close()
