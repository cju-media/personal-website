from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch()
    # Set viewport to mobile size
    context = browser.new_context(viewport={'width': 400, 'height': 800})
    page = context.new_page()
    page.goto('file://' + __import__('os').path.abspath('homepage/homepageFull.html'))

    # Check if the bio-container has flex-direction column-reverse
    flex_direction = page.evaluate('window.getComputedStyle(document.querySelector(".bio-container")).flexDirection')
    print(f'flex-direction: {flex_direction}')

    # Get bounding boxes to verify image is below text
    img_box = page.locator('.bio-container img').bounding_box()
    text_box = page.locator('.text-block').bounding_box()

    print(f'img_box: {img_box}')
    print(f'text_box: {text_box}')

    if img_box and text_box:
        if img_box['y'] > text_box['y']:
            print("SUCCESS: Image is below text.")
        else:
            print("FAILURE: Image is not below text.")
    else:
         print("FAILURE: Could not get bounding boxes.")

    # check widths
    img_width = page.evaluate('window.getComputedStyle(document.querySelector(".image-left")).width')
    text_width = page.evaluate('window.getComputedStyle(document.querySelector(".text-block")).width')
    print(f'img_width: {img_width}')
    print(f'text_width: {text_width}')

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
