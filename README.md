# cju.media — static rebuild

An [Eleventy](https://11ty.dev) scaffold that rebuilds the Squarespace site as a
plain static site, organized to mirror the site's nav/sitemap, with the
header/nav and footer defined **once** and shared across every page at build
time.

## Run it

```bash
npm install
npm start        # dev server with live reload, http://localhost:8080
npm run build     # writes static HTML to _site/
```

## Site structure

The repo layout **is** the sitemap. Every routable page lives under
`src/pages/`, laid out exactly like the nav — Eleventy turns a page's path
here directly into its URL, so there's no separate routing config to keep in
sync:

```
src/
├── pages/                     ← every routable page lives here; the URL is the path
│   ├── index.njk               /
│   ├── contact.njk             /contact/       ← non-nav page: loose file at
│   ├── subscribe.njk           /subscribe/       the top level, not in a nav folder
│   ├── about/                  /about/, /about/bio/, /about/resume/, ...
│   ├── music/                  /music/, /music/arrangements/, ...
│   ├── video-art/              /video-art/, /video-art/highlights/
│   ├── conductor/              /conductor/, /conductor/laptop-ensemble/, ...
│   ├── max-programming/        /max-programming/, /max-programming/max/, ...
│   ├── av-engineering/         /av-engineering/, /av-engineering/production/, ...
│   ├── affects/                /affects/, /affects/list/, /affects/photos/, /affects/way/
│   └── tools/                  /tools/, /tools/scales/, ...
├── _includes/                 ← shared layout/partials — not a page, not a route
├── _data/                     ← nav.json, footerLinks.json, media.json — not a page
├── css/                       ← shared stylesheet — not a page
└── assets/                    ← images/audio/JSON assets — not a page
```

The rule for a new page: if it's reachable from the nav dropdown, it goes in
that section's folder (`pages/<section>/`). If it isn't (contact, subscribe,
a future 404/thank-you page), it goes as a loose file directly under
`pages/` — never nested inside a nav-section folder, so a glance at a
folder's contents tells you whether everything in it is really in the nav.

`_includes`, `_data`, `css`, and `assets` sit as siblings to `pages/`
(configured via `dir.includes`/`dir.data` in `eleventy.config.js`, resolved
as `../` relative to the `pages/` input root) — they're build machinery and
shared resources, not routes, so they deliberately don't live inside the
folder that mirrors the sitemap.

URLs are cleaner than the live Squarespace site's (e.g. `/music/arrangements/`
instead of `/arrangements` with a top-level `/music-2` folder link) — a
deliberate improvement made during the reorg, not a constraint carried over.

## How the "edit once, appears everywhere" part works

See the original explanation below — unchanged from the first prototype:

- `src/_data/nav.json` / `footerLinks.json` — nav + footer, edited once.
- `src/_includes/base.njk` — shared shell (fonts, header, `<main>`, footer, nav.js).
- `src/_includes/partials/section-index.njk` — the template every section's
  `index.njk` (About, Music, AV Engineering, etc.) uses to render its own
  "overview" landing page, listing that section's children from `nav.json`.
- `src/css/site.css` — shared chrome styling, plus a new `.content-page`
  component (see below) for pages authored directly for this site.

## Migration status — what moved where

**Ported from this repo's existing Squarespace-block files** (content
unchanged, just re-homed and given front matter):

| New page | Ported from |
|---|---|
| `/music/arrangements/` | `Scores/Arrangements/arrangements.html` |
| `/music/originals/` | `Scores/Originals/originals.html` |
| `/music/media-scores/` | `Scores/media-scores/mediaScores.html` |
| `/affects/way/` | `Scores/way/way.html` |
| `/about/resume/` | `resume/resume.html` |
| `/max-programming/max/` | `max/max.html` |
| `/max-programming/programming/` | `programming/programming.html` |
| `/max-programming/vst/` | `programming/vst.html` |
| `/max-programming/webdev/` | `programming/webdev.html` |
| `/tools/stream-setup/` | `stream-setup/streamSetup.html` |
| `/affects/list/` | `personal/list/theList.html` |
| `/affects/photos/` | `personal/photos/photos.html` |
| `/av-engineering/production/` | `avengineering/avEngineering.html` |
| `/video-art/highlights/` | `videoArt/videoArt.html` |
| `/tools/scales/` | `scales/scales.html` |
| `/tools/harvard-sentences/` | `harvard-sentences/harvard.html` |
| `/music/sound-artist/` | `sound-artist/soundArtist.html` |
| `/tools/hald-clut/` | `hald-clut/hald-clut.html` |

The last two weren't in the live site's header dropdown at all (reachable only
by direct URL) but are real, working pages, so they were added to `nav.json`
during this pass — Sound Artist under Music, Hald CLUT under Tools.

**New — didn't exist in this repo at all, only as live pages inside the
Squarespace page builder.** These were scraped from the live site's text and
rebuilt as plain content pages (`.content-page` styling in `site.css`), since
there was no source to port from:

`/about/bio/`, `/about/education/`, `/about/ensembles/`, `/about/press/`,
`/about/awards/`, `/conductor/new-music-ensemble/`,
`/conductor/laptop-ensemble/`, `/conductor/pile-of-wires/`,
`/max-programming/externals/` (empty on the live site too),
`/av-engineering/highlights/`, `/av-engineering/podcasts/`,
`/av-engineering/video-editing/`, `/av-engineering/gear/`.

A few of these have a `stub-note` line marking content the scrape pass
couldn't capture — mainly embedded video/audio players and a handful of
outbound press links. Worth a manual pass against the live site before this
replaces it.

**New — section landing pages**, one per nav item (`/about/`, `/music/`,
`/video-art/`, `/conductor/`, `/max-programming/`, `/av-engineering/`,
`/affects/`, `/tools/`). On the live site these top-level folder links mostly
just duplicate their first child page; here each is a real (short) landing
page listing that section's children instead, via `section-index.njk`.

## No runtime fetches for this repo's own content

The old Squarespace Code Block pattern loaded a page's own HTML from GitHub
at runtime (fetch → inject into DOM). Every page here already avoids that —
content is compiled in at build time, one file per page.

A few pages went further and fetched *their own repo's assets* over the
network too (leftover from the Squarespace-era code, where that was the only
way to keep a Code Block under Squarespace's size limits). Those are now
committed directly alongside the page instead:

| Page | Used to fetch | Now |
|---|---|---|
| Homepage | `assets/media.json` from GitHub raw | `src/_data/media.json`, inlined into the page at build time |
| `/tools/hald-clut/` | sample photo from `raw.githack.com` | `src/assets/hald-clut-sample-photo.jpg` |
| `/music/sound-artist/` | RNBO patch + audio samples from GitHub raw | `src/assets/sound-artist/` |

**What's intentionally still a live fetch:** Arrangements, Originals, Media
Scores, The Way, and The List pull their listings from the separate
`cju-media/Scores` / `cju-media/The-List` repos; the Max/Programming pages
pull from the GitHub API directly. That's by design — new content there
shouldn't require a commit to this repo. (Currently client-side fetches at
page load; could move to Eleventy build-time data fetches later for speed/
resilience, with a rebuild trigger on those repos changing — not done yet.)

## What's still open

- **The legacy top-level folders in the repo root** (`Scores/`, `avengineering/`,
  `programming/`, `max/`, `stream-setup/`, `scales/`, `harvard-sentences/`,
  `videoArt/`, `personal/`, `resume/`) are **untouched** — they're still what
  the *live* Squarespace site fetches via its Code Blocks. Don't delete or
  move them until Squarespace is actually decommissioned; at that point they're
  fully superseded by `src/` (this build) and can be retired.
- **Media**: still pointing at Squarespace-hosted images/video and at
  `cameronjohnston.xyz/s/...` (also Squarespace). Needs downloading and
  rehosting before Squarespace can actually be canceled.
- **Fonts**: free Google Font substitutes (`Cormorant SC`, `Barlow Condensed`)
  stand in for the real site's paid Adobe fonts, served through Squarespace's
  own Typekit account.
- **Forms**: the "Contact" / "Subscribe" footer links are placeholders —
  need a real form backend (e.g. Formspree) once off Squarespace.
- **Content gaps** noted with `stub-note` above.
- **`Utilities/`** is dev scaffolding (a Block-loader template, a glitch-text
  design reference), never a live page — intentionally left out of the new
  sitemap.
- **`av-events/`** is its own app (phone upload form → GitHub Actions
  pipeline → `events.json` → gallery), not a content page — intentionally
  left out of the new sitemap. The AV Engineering page keeps linking to it
  by URL, same as the live site does today.
