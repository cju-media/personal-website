import urllib.request
import urllib.error
import json
import os
import sys
import shutil

# Add new iCloud shared album tokens here.
# The key should match the object array in assets/media.json
ALBUMS = {
    "headshots": "B2N5yeZFhGgD1sx",
    "avPics": "B2N5ON9t3GFCbtv"
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CONTENT_DIR = os.path.join(ASSETS_DIR, "content")
MEDIA_JSON_PATH = os.path.join(ASSETS_DIR, "media.json")

GITHUB_RAW_PREFIX = "https://raw.githubusercontent.com/cju-media/personal-website/main/assets/content"

def get_stream_data(token):
    base_url_template = "https://{}-sharedstreams.icloud.com/{}/sharedstreams/webstream"
    partition = "p01"
    headers = {
        "Origin": "https://www.icloud.com",
        "Content-Type": "text/plain",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    data = json.dumps({"streamCtag": None}).encode('utf-8')
    while True:
        url = base_url_template.format(partition, token)
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    return json.loads(response.read().decode('utf-8')), partition
        except urllib.error.HTTPError as e:
            if e.code == 330:
                new_host = e.headers.get("X-Apple-MMe-Host")
                if new_host:
                    partition = new_host.split("-")[0]
                    continue
            print(f"Error fetching stream: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

def get_asset_urls(base_url, photo_guids):
    url = f"{base_url}/webasseturls"
    headers = {
        "Origin": "https://www.icloud.com",
        "Content-Type": "text/plain",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    data = json.dumps({"photoGuids": photo_guids}).encode('utf-8')
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching asset URLs: {e}")
        sys.exit(1)

def main():
    if not os.path.exists(CONTENT_DIR):
        os.makedirs(CONTENT_DIR, exist_ok=True)

    with open(MEDIA_JSON_PATH, "r") as f:
        media_data = json.load(f)

    for album_name, token in ALBUMS.items():
        print(f"Processing album: {album_name}")
        album_dir = os.path.join(CONTENT_DIR, album_name)
        os.makedirs(album_dir, exist_ok=True)

        stream_data, partition = get_stream_data(token)
        photos = stream_data.get("photos", [])

        if not photos:
            print(f"No photos found for {album_name}.")

        base_url = f"https://{partition}-sharedstreams.icloud.com/{token}/sharedstreams"
        photo_guids = [p["photoGuid"] for p in photos]

        items = {}
        locations = {}
        if photos:
            asset_data = get_asset_urls(base_url, photo_guids)
            items = asset_data.get("items", {})
            locations = asset_data.get("locations", {})

        current_files = set()
        new_links = []

        for photo in photos:
            photo_guid = photo["photoGuid"]
            derivatives = photo.get("derivatives", {})

            # Find the best file.
            # iCloud uses string keys representing integer sizes, or specific labels like "VideoPoster" / strings for videos maybe?
            # actually if it's a video, the original video is usually in one of the keys, sometimes "Media" or it's just the largest size.
            # We sort all numeric keys by size to get the largest.
            best_image_checksum = None

            # To properly handle videos, iCloud derivatives often include the original video,
            # Let's inspect the file extensions in `items` for the checksums related to this photo.

            # gather all checksums for this photo
            photo_checksums = [d["checksum"] for d in derivatives.values() if "checksum" in d]

            # Find if any of these checksums points to a video in `items`
            video_checksum = None
            largest_image_checksum = None
            largest_size = -1

            for chk in photo_checksums:
                if chk in items:
                    path = items[chk].get("url_path", "").lower()
                    if ".mp4" in path or ".mov" in path:
                        video_checksum = chk
                        break # Found the video!

            if not video_checksum:
                # Find the largest image
                for key, deriv in derivatives.items():
                    if "checksum" in deriv and "fileSize" in deriv:
                        try:
                            size = int(deriv["fileSize"])
                            if size > largest_size:
                                largest_size = size
                                largest_image_checksum = deriv["checksum"]
                        except ValueError:
                            pass

                # If no size info but we have 2048 or something
                if not largest_image_checksum:
                    sorted_keys = sorted([k for k in derivatives.keys() if k.isdigit()], key=lambda x: int(x), reverse=True)
                    if sorted_keys:
                        largest_image_checksum = derivatives[sorted_keys[0]]["checksum"]

            best_checksum = video_checksum if video_checksum else largest_image_checksum

            if not best_checksum:
                continue

            def get_download_url(checksum):
                if not checksum or checksum not in items: return None
                item = items[checksum]
                loc = item.get("url_location")
                path = item.get("url_path")
                if loc and path and loc in locations:
                    scheme = locations[loc].get("scheme", "https")
                    host = locations[loc].get("hosts")[0]
                    return f"{scheme}://{host}{path}"
                return None

            main_url = get_download_url(best_checksum)
            if not main_url:
                continue

            ext = "jpg"
            main_url_lower = main_url.lower()
            if ".mp4" in main_url_lower:
                ext = "mp4"
            elif ".mov" in main_url_lower:
                ext = "mov"
            elif ".png" in main_url_lower:
                ext = "png"

            filename = f"{photo_guid}.{ext}"
            filepath = os.path.join(album_dir, filename)
            current_files.add(filename)

            if not os.path.exists(filepath):
                print(f"Downloading {filename}...")
                try:
                    with urllib.request.urlopen(main_url) as response, open(filepath, 'wb') as out_file:
                        out_file.write(response.read())
                except Exception as e:
                    print(f"Error downloading: {e}")

            link = f"{GITHUB_RAW_PREFIX}/{album_name}/{filename}"
            new_links.append(link)

        # Cleanup removed files in the repo
        for filename in os.listdir(album_dir):
            if filename not in current_files:
                print(f"Removing deleted file: {filename}")
                os.remove(os.path.join(album_dir, filename))

        # Update media.json for this album
        if album_name not in media_data:
            media_data[album_name] = []

        existing_links = media_data[album_name]

        # Keep manual links: ones that do NOT start with GITHUB_RAW_PREFIX + "/" + album_name
        album_prefix = f"{GITHUB_RAW_PREFIX}/{album_name}"
        manual_links = [link for link in existing_links if not link.startswith(album_prefix)]

        # New array is manual links + new links
        final_links = manual_links + new_links
        media_data[album_name] = final_links

    # Write updated media.json
    with open(MEDIA_JSON_PATH, "w") as f:
        json.dump(media_data, f, indent=2)
        f.write("\n")

if __name__ == "__main__":
    main()
