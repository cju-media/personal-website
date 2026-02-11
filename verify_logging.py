from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        console_logs = []
        page.on("console", lambda msg: console_logs.append(msg.text))

        # Monitor network requests to ensure we are NOT hitting api.github.com
        def handle_request(request):
            if "api.github.com" in request.url:
                print(f"FAILURE: Request to GitHub API detected: {request.url}")

        page.on("request", handle_request)

        print("Navigating to reliability test page...")
        page.goto("http://localhost:8000/test_logging.html")

        # Wait for initialization
        try:
            # We expect AUDIO DECODE ERROR because of EncodingError
            page.wait_for_selector("text=AUDIO DECODE ERROR", timeout=20000)
            print("Saw AUDIO DECODE ERROR (expected due to codec).")

            # Print captured logs
            print("\nCaptured Console Logs:")
            for log in console_logs:
                print(f"  {log}")

            # Verify Dev Button Visibility
            print("\nChecking Dev Button Visibility (Before Click)...")
            dev_btn = page.query_selector("#dev-bypass")
            if dev_btn and dev_btn.is_visible():
                print("SUCCESS: Dev Button is visible initially.")
            else:
                print("FAILURE: Dev Button is NOT visible initially.")

            # Perform Interaction (Click Overlay)
            print("Clicking Overlay (TAP TO FOCUS)...")
            overlay = page.query_selector("#focus-overlay")
            overlay.click()

            # Verify Dev Button Hidden
            print("Checking Dev Button Visibility (After Click)...")
            # Wait a tiny bit for the style change to propagate if needed (though it's sync)
            page.wait_for_timeout(100)

            # In Playwright, is_visible() checks style/opacity/size.
            # We set display: none, so it should return False.
            if not dev_btn.is_visible():
                 print("SUCCESS: Dev Button is hidden after interaction.")
            else:
                 print("FAILURE: Dev Button is STILL visible after interaction.")

        except Exception as e:
            print(f"Timed out or error: {e}")

        finally:
            page.screenshot(path="verification_logging.png")
            print("Screenshot saved to verification_logging.png")

        browser.close()

if __name__ == "__main__":
    run()
