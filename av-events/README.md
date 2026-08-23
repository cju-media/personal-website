# AV Events

This directory contains the code for the "AV Events" page (`/av-events` on the
Squarespace site) — a running log of events with a description and photos for
each, uploadable from a phone.

## Architecture

1. **Upload (phone, anywhere):**
   - `dashboard/index.html` is a small form (title, date, location, description,
     photos) hosted on GitHub Pages, so it works from a phone browser with no
     app or server of your own.
   - It authenticates straight to the GitHub REST API with a Personal Access
     Token you generate once and save in the page (stored only in that
     browser's `localStorage` — never sent anywhere but `api.github.com`).
   - Submitting the form pushes each photo, then a `meta.json` last, into
     `uploads_queue/<timestamp>/` as individual commits via the Contents API.
     `meta.json` arriving last is the signal a submission is complete.

2. **Processing (GitHub Actions):**
   - `.github/workflows/process_av_events.yml` runs on every push to
     `av-events/uploads_queue/**` (and can be run manually).
   - It runs `process_events_queue.py`, which drains any complete submission
     (folders with a `meta.json`) into `images/<event-slug>/` and appends/merges
     the event into `events.json`, then deletes the queue folder.
   - A submission that fails to parse (bad JSON, missing fields, no usable
     photos) is moved to `uploads_queue/_failed/` instead of being retried
     forever.
   - The workflow commits and pushes the result back to `main`.

3. **Publishing (Squarespace):**
   - `av-events.html` is the static HTML fragment — scoped styles, a glitch
     title matching the rest of the site, and JS that fetches `events.json`
     and renders each event as a card with its description and a photo grid
     (click to open a lightbox).
   - `av-eventsBlock.html` is the loader: paste its contents into a Squarespace
     Code Block on the `/av-events` page. It fetches `av-events.html` from
     GitHub (via raw.githack) at page-load time and injects it, so the page
     always shows the latest published content without touching Squarespace
     again.

```
Phone (dashboard/index.html)
   │  GitHub Contents API (PAT)
   ▼
uploads_queue/<timestamp>/{meta.json, photos/*}
   │  push triggers workflow
   ▼
process_events_queue.py  →  images/<slug>/*, events.json
   │  git commit + push
   ▼
av-events.html fetches events.json  ←  av-eventsBlock.html (Squarespace Code Block)
```

## Files

- `dashboard/index.html` — phone upload form (GitHub Pages).
- `process_events_queue.py` — drains the queue into `images/` + `events.json`.
- `events.json` — the published manifest (generated).
- `images/` — the published photos, one subfolder per event (generated).
- `uploads_queue/` — in-flight submissions (generated/consumed; normally empty).
- `av-events.html` — the gallery fragment injected on Squarespace.
- `av-eventsBlock.html` — the Squarespace Code Block loader.

## One-time setup

1. **Enable GitHub Pages** for this repo: Settings → Pages → Source:
   "GitHub Actions". After the next push to `main`, the dashboard is live at
   `https://cju-media.github.io/personal-website/av-events/dashboard/`.
2. **Create a Personal Access Token** (Settings → Developer settings →
   Personal access tokens → Fine-grained tokens): scope it to only the
   `personal-website` repository, with **Contents: Read and write**
   permission and nothing else. Open the dashboard, tap the ⚙ icon, and
   paste it in — it's saved on that device only.
3. **Add the Squarespace page:** create a page at `/av-events`, add a Code
   Block, and paste in the contents of `av-eventsBlock.html`.

## Manual re-run

If a submission got stuck (e.g. `_failed/`), fix the issue in
`uploads_queue/` directly (or just delete it) and re-run the workflow from
the Actions tab ("Process AV Events Queue" → "Run workflow"), or push any
change under `av-events/uploads_queue/`.
