# Personal Photos

This directory contains the code for the "Photos" page on the personal website.

## Updating Photos

The photos are fetched from an iCloud Shared Album. Due to CORS restrictions and expiring URLs, the photos must be downloaded and committed to the repository.

To update the gallery with new photos from the album:

1.  Ensure you have Python 3 installed.
2.  Run the fetch script:
    ```bash
    python3 fetch_icloud_photos.py
    ```
    This will:
    - Check for new photos in the shared album.
    - Download new photos (large and thumbnail) to the `images/` directory.
    - Update `photos.json` with the new list.

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
