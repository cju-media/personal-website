from playwright.sync_api import sync_playwright
import os
import time

def test_hover_glitch(page):
    cwd = os.getcwd()
    file_path = f"file://{cwd}/homepage/homepageFull.html"
    print(f"Loading {file_path}")

    page.goto(file_path)

    # Wait for JS to initialize (it has some timeouts/intervals)
    # The initEverything runs when elements are found or after 5s fallback.
    # It also has a checkLoad interval.
    # We should wait until the text overlays are processed into spans.

    page.wait_for_selector(".hp-mid-wrapper .text-overlay .glitch-char", timeout=10000)

    # 1. Verify Top Text (always animating)
    # This is handled by init1 and uses .text-block1 .span-class
    # Just checking it exists is probably enough, checking animation is hard without waiting
    top_spans = page.locator(".text-block1 .span-class")
    print(f"Top spans count: {top_spans.count()}")
    if top_spans.count() == 0:
        print("FAIL: Top text spans not found.")
        exit(1)

    # 2. Verify Middle Text (initially static)
    # Select a char from one of the overlays
    # e.g. AUDIO/VIDEO ENGINEER -> .text-overlay1 inside first container
    mid_char = page.locator(".hp-mid-wrapper .text-overlay1 .glitch-char").first

    # Check if it has any font class initially (it shouldn't if not hovering)
    # The code removes font classes if !active.
    # Wait a bit to ensure no animation loop started
    time.sleep(2)

    class_attr = mid_char.get_attribute("class")
    print(f"Initial class: {class_attr}")

    # It should be just 'glitch-char'
    if "font" in class_attr:
        print("FAIL: Font class found on middle text before hover.")
        exit(1)

    # 3. Hover and Verify Animation
    # Find the container
    container = page.locator(".hp-mid-wrapper .image-container").first
    print("Hovering over container...")
    container.hover()

    # Wait for animation to pick up (intervals are 300-700ms)
    time.sleep(2)

    class_attr_hover = mid_char.get_attribute("class")
    print(f"Hover class: {class_attr_hover}")

    # It SHOULD have a font class now
    if "font" not in class_attr_hover:
        print("FAIL: No font class found on middle text AFTER hover.")
        exit(1)

    # 4. Stop Hover and Verify Stop
    # Hover somewhere else (e.g. body)
    print("Moving mouse away...")
    page.mouse.move(0, 0)

    # Wait for loop to catch the flag change
    time.sleep(2)

    class_attr_end = mid_char.get_attribute("class")
    print(f"End class: {class_attr_end}")

    if "font" in class_attr_end:
        print("FAIL: Font class still present after mouse leave.")
        exit(1)

    print("PASS: Hover glitch effect verified.")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            test_hover_glitch(page)
        finally:
            browser.close()
