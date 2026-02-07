# Personal Photos

This directory contains the code for the "Photos" page on the personal website.

## Architecture: Automated Backend Scraping

Due to security restrictions (CORS) that prevent reliable browser-based access to iCloud, this gallery uses a **GitHub Actions** workflow to automate the process.

1.  **Backend (GitHub Actions):**
    -   A workflow (`.github/workflows/update-photos.yml`) runs every hour.
    -   It executes a Python script (`fetch_icloud_photos.py`) that:
        -   Connects to the iCloud Shared Album.
        -   Downloads new photos to the `images/` directory in this repository.
        -   Updates `photos.json` with the new file list.
    -   It commits and pushes these changes back to the repository.

2.  **Frontend (Client-Side):**
    -   `photos.html` is a static HTML fragment injected into the website (e.g., Squarespace).
    -   It fetches `photos.json` from the raw GitHub content (via `raw.githack.com` or similar CDN).
    -   It displays the images directly from the repository.

## Advantages

-   **Reliability:** No dependence on flaky public CORS proxies.
-   **Performance:** Images are served via GitHub/CDN, not proxied.
-   **Automation:** New photos appear automatically within ~1 hour.

## Files

-   `photos.html`: The gallery interface.
-   `fetch_icloud_photos.py`: The Python scraper.
-   `photosBlock.html`: Loader for Squarespace.
-   `photos.json`: The manifest of photos (generated).
-   `images/`: The downloaded photos (generated).

## Manual Update

To force an update immediately without waiting for the schedule:

1.  Go to the "Actions" tab in your GitHub repository.
2.  Select "Update iCloud Photos".
3.  Click "Run workflow".
