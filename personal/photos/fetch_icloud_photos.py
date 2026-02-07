import urllib.request
import urllib.error
import json
import os
import sys

# Configuration
TOKEN = "B2N5n8hH4Gdkz1m"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
JSON_PATH = os.path.join(BASE_DIR, "photos.json")

# Ensure images directory exists
os.makedirs(IMAGES_DIR, exist_ok=True)

def get_stream_data(token):
    """
    Fetches the webstream data, handling 330 Redirects.
    """
    base_url_template = "https://{}-sharedstreams.icloud.com/{}/sharedstreams/webstream"
    partition = "p01" # Start with p01

    headers = {
        "Origin": "https://www.icloud.com",
        "Content-Type": "text/plain",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    data = json.dumps({"streamCtag": None}).encode('utf-8')

    while True:
        url = base_url_template.format(partition, token)
        print(f"Fetching stream metadata from {url}...")
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    return json.loads(response.read().decode('utf-8')), partition
        except urllib.error.HTTPError as e:
            if e.code == 330:
                new_host = e.headers.get("X-Apple-MMe-Host")
                if new_host:
                    print(f"Redirected to {new_host}")
                    partition = new_host.split("-")[0]
                    continue
            print(f"Error fetching stream: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

def get_asset_urls(base_url, photo_guids):
    """
    Fetches the asset URLs for the given photo GUIDs.
    """
    url = f"{base_url}/webasseturls"
    headers = {
        "Origin": "https://www.icloud.com",
        "Content-Type": "text/plain",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    # iCloud API expects photoGuids as a list of strings
    data = json.dumps({"photoGuids": photo_guids}).encode('utf-8')

    print(f"Fetching asset URLs from {url}...")
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching asset URLs: {e}")
        sys.exit(1)

def download_file(url, filepath):
    """
    Downloads a file from a URL to the specified path.
    """
    if os.path.exists(filepath):
        # Optional: check size or force update?
        # For now, skip if exists to save bandwidth.
        # print(f"Skipping {filepath} (already exists)")
        return

    print(f"Downloading to {filepath}...")
    try:
        with urllib.request.urlopen(url) as response, open(filepath, 'wb') as out_file:
            out_file.write(response.read())
    except Exception as e:
        print(f"Error downloading {url}: {e}")

def main():
    print("Starting iCloud Photo Downloader...")

    # 1. Get Stream Data
    stream_data, partition = get_stream_data(TOKEN)
    photos = stream_data.get("photos", [])
    print(f"Found {len(photos)} items in stream.")

    if not photos:
        print("No photos found.")
        # Create empty JSON so frontend doesn't break
        with open(JSON_PATH, "w") as f:
            json.dump([], f)
        return

    # 2. Get Asset URLs
    # Construct base URL with correct partition
    base_url = f"https://{partition}-sharedstreams.icloud.com/{TOKEN}/sharedstreams"
    photo_guids = [p["photoGuid"] for p in photos]

    asset_data = get_asset_urls(base_url, photo_guids)
    items = asset_data.get("items", {})
    locations = asset_data.get("locations", {})

    output_photos = []

    for photo in photos:
        photo_guid = photo["photoGuid"]
        derivatives = photo.get("derivatives", {})

        # Determine best quality image and thumbnail
        # We try to find specific derivative IDs (integers as strings)
        # 2048: Large image
        # 342: Thumbnail

        best_image_checksum = None
        thumb_checksum = None

        # Helper to get checksum safely
        def get_chk(key):
            return derivatives[key]["checksum"] if key in derivatives else None

        # Try to find best image (2048 or similar large one)
        # We sort keys numerically to find largest if '2048' isn't exact
        sorted_keys = sorted([k for k in derivatives.keys() if k.isdigit()], key=lambda x: int(x), reverse=True)

        # Priority: 2048, then largest
        if "2048" in derivatives:
            best_image_checksum = derivatives["2048"]["checksum"]
        elif sorted_keys:
            best_image_checksum = derivatives[sorted_keys[0]]["checksum"]

        # Helper to construct URL
        def get_download_url(checksum):
            if not checksum or checksum not in items:
                return None
            item = items[checksum]
            loc = item.get("url_location")
            path = item.get("url_path")
            if loc and path and loc in locations:
                scheme = locations[loc].get("scheme", "https")
                host = locations[loc].get("hosts")[0]
                return f"{scheme}://{host}{path}"
            return None

        main_url = get_download_url(best_image_checksum)

        if not main_url:
            print(f"Skipping {photo_guid}: No URL found for checksum {best_image_checksum}")
            continue

        # Check file extension
        is_video = False
        ext = "jpg"
        if ".mp4" in main_url.lower():
            is_video = True
            ext = "mp4"
        elif ".png" in main_url.lower():
            ext = "png"

        filename = f"{photo_guid}.{ext}"
        filepath = os.path.join(IMAGES_DIR, filename)

        download_file(main_url, filepath)

        # Use main image as thumbnail for higher quality
        thumb_filename = filename

        # Caption Logic
        # iCloud Shared Albums store captions as the first comment by the owner, usually.
        # The 'caption' field in the photo object is often empty.
        # We check if there's a 'caption' (explicit) or 'comments' (array).
        caption = photo.get("caption", "")
        if not caption:
            # Check comments
            comments = photo.get("comments", [])
            if comments:
                # Use the first comment as the caption? Or the most recent?
                # Usually the owner's comment describing the photo is what we want.
                # Let's take the text of the first comment.
                # comments is a list of objects like { "commentContent": "...", "isBatchComment": "...", ... }
                first_comment = comments[0]
                caption = first_comment.get("commentContent", "")

        output_photos.append({
            "id": photo_guid,
            "type": "video" if is_video else "image",
            "src": f"images/{filename}",
            "thumb": f"images/{thumb_filename}" if thumb_filename else None,
            "caption": caption,
            "date": photo.get("dateCreated")
        })

    # Write JSON
    with open(JSON_PATH, "w") as f:
        json.dump(output_photos, f, indent=2)
    print(f"Successfully generated {JSON_PATH} with {len(output_photos)} items.")

if __name__ == "__main__":
    main()
