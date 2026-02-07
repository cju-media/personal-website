# Personal Photos

This directory contains the code for the "Photos" page on the personal website.

## How It Works

The gallery displays photos from an iCloud Shared Album. Because iCloud's API is private and restricts direct browser access (CORS), we use a two-step process:

1.  A Python script (`fetch_icloud_photos.py`) runs periodically to scrape the album, download new images, and update a manifest (`photos.json`).
2.  The frontend (`photos.html`) simply loads this `photos.json` and the local images.

## Automation

A GitHub Action (`.github/workflows/update-photos.yml`) is configured to run this update process automatically every 6 hours.

-   **When new photos are added to the album:** They will appear on the site within ~6 hours (or after the next scheduled run).
-   **Manual Update:** You can manually trigger the workflow from the "Actions" tab in your GitHub repository if you want to see changes immediately.

## Updating Manually (Local)

If you prefer to run the update locally:

1.  Ensure you have Python 3 installed.
2.  Run the fetch script:
    ```bash
    python3 fetch_icloud_photos.py
    ```
3.  Commit and push the changes:
    ```bash
    git add images/ photos.json
    git commit -m "Update photos from iCloud"
    git push
    ```

## Files

-   `photos.html`: The HTML fragment that displays the gallery. It fetches `photos.json` from the main branch.
-   `photosBlock.html`: A loader file to inject `photos.html` into a Squarespace page.
-   `fetch_icloud_photos.py`: The Python script to download photos.
-   `photos.json`: The data file used by the frontend.
-   `images/`: The directory containing the downloaded images.

## Configuration

The iCloud Shared Album token is hardcoded in `fetch_icloud_photos.py`. If you change albums, update the `TOKEN` variable.
