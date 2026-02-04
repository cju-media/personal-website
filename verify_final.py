from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:8000/test_videoArt.html")

        # Verify styles
        overflow1 = page.eval_on_selector('.image-container1', 'el => window.getComputedStyle(el).overflow')
        overflow2 = page.eval_on_selector('.image-container2', 'el => window.getComputedStyle(el).overflow')

        print(f"Container 1 Overflow: {overflow1}")
        print(f"Container 2 Overflow: {overflow2}")

        if overflow1 != 'visible' or overflow2 != 'visible':
            print("ERROR: Overflow should be visible")

        # Verify border radius on video
        br1 = page.eval_on_selector('#myVideo', 'el => window.getComputedStyle(el).borderTopLeftRadius')
        print(f"Video 1 Top-Left Radius: {br1}")

        # Screenshot
        time.sleep(0.5)
        page.screenshot(path="final_flight.png")

        time.sleep(5)
        page.screenshot(path="final_landed.png")

        browser.close()

if __name__ == "__main__":
    run()
