#!/usr/bin/env python3
"""
Drains av-events/uploads_queue/ into av-events/images/ + av-events/events.json.

Run by .github/workflows/process_av_events.yml whenever something is pushed
into the queue (see av-events/dashboard/index.html, which is what pushes to
it). Each submission is a folder named after a millisecond timestamp:

    uploads_queue/<timestamp>/meta.json          {title, date, location, description}
    uploads_queue/<timestamp>/photos/photo-01.jpg
    uploads_queue/<timestamp>/photos/photo-02.jpg
    ...

meta.json is uploaded *last* by the dashboard, so its presence is the signal
that a submission finished uploading and is ready to publish. A folder with
only photos (no meta.json yet) is left alone -- it'll be picked up on a
later run once the upload finishes.

A submission that can't be processed (bad/missing JSON, no usable photos)
is moved to uploads_queue/_failed/ instead of being retried forever.
"""

import json
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUEUE_DIR = os.path.join(BASE_DIR, "uploads_queue")
FAILED_DIR = os.path.join(QUEUE_DIR, "_failed")
IMAGES_DIR = os.path.join(BASE_DIR, "images")
JSON_PATH = os.path.join(BASE_DIR, "events.json")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic", ".heif"}


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "event"


def quarantine(submission_dir, submission_name, reason):
    print(f"Quarantining '{submission_name}': {reason}")
    os.makedirs(FAILED_DIR, exist_ok=True)
    dest = os.path.join(FAILED_DIR, submission_name)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.move(submission_dir, dest)


def load_events():
    if not os.path.exists(JSON_PATH):
        return []
    try:
        with open(JSON_PATH, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError) as e:
        print(f"Warning: could not read existing events.json ({e}); starting fresh.")
        return []


def unique_slug(base_slug, existing_ids):
    if base_slug not in existing_ids:
        return base_slug
    n = 2
    while f"{base_slug}-{n}" in existing_ids:
        n += 1
    return f"{base_slug}-{n}"


def process_submission(submission_dir, submission_name, events, existing_ids):
    meta_path = os.path.join(submission_dir, "meta.json")
    if not os.path.isfile(meta_path):
        # Still uploading (photos may have arrived, meta.json hasn't yet).
        return False

    try:
        with open(meta_path, "r") as f:
            meta = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        quarantine(submission_dir, submission_name, f"invalid meta.json ({e})")
        return True

    title = (meta.get("title") or "").strip()
    description = (meta.get("description") or "").strip()
    date = (meta.get("date") or "").strip()
    location = (meta.get("location") or "").strip()

    if not title or not description or not date:
        quarantine(submission_dir, submission_name, "missing title, date, or description")
        return True

    photos_dir = os.path.join(submission_dir, "photos")
    photo_files = []
    if os.path.isdir(photos_dir):
        photo_files = sorted(
            f for f in os.listdir(photos_dir)
            if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
        )

    if not photo_files:
        quarantine(submission_dir, submission_name, "no usable photos")
        return True

    base_slug = slugify(f"{date}-{title}")

    # If this event already exists (e.g. a second batch of photos for the
    # same date+title), append to it instead of creating a duplicate card.
    existing_event = next(
        (e for e in events if e.get("id") == base_slug and e.get("title") == title and e.get("date") == date),
        None,
    )

    if existing_event is not None:
        slug = base_slug
    else:
        slug = unique_slug(base_slug, existing_ids)

    dest_dir = os.path.join(IMAGES_DIR, slug)
    os.makedirs(dest_dir, exist_ok=True)

    existing_filenames = set(os.listdir(dest_dir)) if existing_event is not None else set()
    new_photo_entries = []
    next_index = len(existing_filenames) + 1

    for fname in photo_files:
        src_path = os.path.join(photos_dir, fname)
        ext = os.path.splitext(fname)[1].lower()
        dest_fname = f"photo-{next_index:02d}{ext}"
        while dest_fname in existing_filenames:
            next_index += 1
            dest_fname = f"photo-{next_index:02d}{ext}"
        shutil.copyfile(src_path, os.path.join(dest_dir, dest_fname))
        existing_filenames.add(dest_fname)
        next_index += 1
        new_photo_entries.append({"src": f"images/{slug}/{dest_fname}", "caption": ""})

    if existing_event is not None:
        existing_event.setdefault("photos", []).extend(new_photo_entries)
    else:
        event = {
            "id": slug,
            "title": title,
            "date": date,
            "description": description,
            "photos": new_photo_entries,
        }
        if location:
            event["location"] = location
        events.append(event)
        existing_ids.add(slug)

    shutil.rmtree(submission_dir)
    print(f"Processed '{submission_name}' -> event '{slug}' ({len(new_photo_entries)} photo(s)).")
    return True


def main():
    os.makedirs(QUEUE_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)

    events = load_events()
    existing_ids = {e.get("id") for e in events if e.get("id")}

    processed = 0
    for name in sorted(os.listdir(QUEUE_DIR)):
        if name.startswith("_") or name.startswith("."):
            continue
        submission_dir = os.path.join(QUEUE_DIR, name)
        if not os.path.isdir(submission_dir):
            continue
        if process_submission(submission_dir, name, events, existing_ids):
            processed += 1

    events.sort(key=lambda e: e.get("date", ""), reverse=True)

    with open(JSON_PATH, "w") as f:
        json.dump(events, f, indent=2)
        f.write("\n")

    print(f"Done. {processed} submission(s) touched. {len(events)} total event(s) in events.json.")


if __name__ == "__main__":
    main()
