# Personal Photos

This directory contains the code for the "Photos" page on the personal website.

## How It Works

The gallery displays photos dynamically from an iCloud Shared Album.

Because iCloud does not allow direct browser access (CORS), the frontend uses a public CORS proxy (`https://corsproxy.io/`) to fetch the album metadata and asset URLs.

1.  **Loader:** `photosBlock.html` injects `photos.html`.
2.  **Logic:** `photos.html` contains JavaScript that:
    -   Connects to iCloud's `webstream` API via the proxy.
    -   Handles partition redirects (trying `p01` then failing over to `p147` if needed).
    -   Fetches image URLs using `webasseturls`.
    -   Renders the images directly from iCloud's CDNs (which generally allow hotlinking for `<img>` tags).

## Limitations

-   **Proxy Dependency:** The site relies on `corsproxy.io` being up and running. If the proxy goes down or blocks the traffic, the gallery will fail to load.
-   **Rate Limiting:** Excessive traffic might trigger rate limits on the proxy or iCloud side.
-   **Partitioning:** iCloud Shared Albums are sharded across different partitions (e.g., `p147`). The script attempts to guess or hardcode a fallback, but if iCloud changes partitioning logic significantly, it might break.

## Files

-   `photos.html`: The main gallery component with all logic.
-   `photosBlock.html`: Loader for Squarespace injection.
-   `README.md`: This file.

## Configuration

The `ALBUM_TOKEN` is hardcoded in the `photos.html` script. Update this if you switch albums.
