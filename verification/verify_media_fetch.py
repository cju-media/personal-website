from playwright.sync_api import sync_playwright
import os
import json
import time

def test_media_fetch(page):
    cwd = os.getcwd()
    file_path = f"file://{cwd}/homepage/homepageFull.html"
    media_path = f"{cwd}/media.json"

    # Read local media.json content
    with open(media_path, 'r') as f:
        media_data = json.load(f)

    # Intercept network requests to media.json and serve local file
    def handle_route(route):
        print(f"Intercepted request: {route.request.url}")
        if "media.json" in route.request.url:
            route.fulfill(status=200, body=json.dumps(media_data), content_type="application/json")
        else:
            route.continue_()

    page.route("**/*", handle_route)

    print(f"Loading {file_path}")
    page.goto(file_path)

    # Wait for the page to process data (fetch is async)
    time.sleep(3)

    # Verify that images are loaded
    # Check #mid-av, #mid-composer, etc.
    # Note: initEverything logic sets src randomly from the array.
    # If fetch failed, src would be empty or unchanged (or code would crash).

    # mid-av is one of the images set in IIFE
    mid_av = page.locator("#mid-av")
    src = mid_av.get_attribute("src")
    print(f"mid-av src: {src}")

    if not src or "squarespace-cdn" not in src:
        # Check if it matches any of the expected URLs from media.json
        # media.json avPics has squarespace urls
        print("FAIL: mid-av src not set correctly.")
        exit(1)

    # Check bio headshot (initBio)
    bio_headshot = page.locator("#myHeadshot")
    bio_src = bio_headshot.get_attribute("src")
    print(f"bio headshot src: {bio_src}")

    if not bio_src or "squarespace.com" not in bio_src:
        print("FAIL: Bio headshot src not set correctly.")
        exit(1)

    print("PASS: Media loaded via fetch and applied.")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            test_media_fetch(page)
        finally:
            browser.close()
