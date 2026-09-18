# AV Events

This directory contains the code for the "AV Events" page — a running log of
events with a description and photos for each, uploadable from a phone.

The public gallery is at **`/av-engineering/events/`**, built from
`src/pages/av-engineering/events.njk`. `/av-events` and `/audiovideo-events`
301 to it for old links.

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

3. **Publishing:**
   - `src/pages/av-engineering/events.njk` is the live page — scoped styles, a
     glitch title matching the rest of the site, and JS that fetches
     `events.json` and renders each event as a card with its description and a
     photo grid (click to open a lightbox).
   - It fetches `events.json` over raw.githack at page load rather than baking
     it in at build time, so **new events appear without rebuilding the site**.
     The pipeline's commit is enough; no deploy is needed.
   - `av-events.html` is the pre-rebuild fragment this was ported from, kept
     for reference.

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
events.njk fetches events.json  →  /av-engineering/events/
```

## Files

- `dashboard/index.html` — phone upload form (GitHub Pages).
- `process_events_queue.py` — drains the queue into `images/` + `events.json`.
- `events.json` — the published manifest (generated).
- `images/` — the published photos, one subfolder per event (generated).
- `uploads_queue/` — in-flight submissions (generated/consumed; normally empty).
- `av-events.html` — the pre-rebuild fragment (superseded by
  `src/pages/av-engineering/events.njk`).

## One-time setup

1. **Enable GitHub Pages** for this repo: Settings → Pages → Source:
   "GitHub Actions". After the next push to `main`, the dashboard is live at
   `https://cju-media.github.io/personal-website/av-events/dashboard/`.
2. **Create a Personal Access Token** (Settings → Developer settings →
   Personal access tokens → Fine-grained tokens): scope it to only the
   `personal-website` repository, with **Contents: Read and write**
   permission and nothing else. Open the dashboard, tap the ⚙ icon, and
   paste it in — it's saved on that device only.
3. **Nothing else** — the gallery page is already built and deployed with the
   rest of the site.

## Manual re-run

If a submission got stuck (e.g. `_failed/`), fix the issue in
`uploads_queue/` directly (or just delete it) and re-run the workflow from
the Actions tab ("Process AV Events Queue" → "Run workflow"), or push any
change under `av-events/uploads_queue/`.
