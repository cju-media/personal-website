# Build Guidelines

This repository is an [Eleventy](https://11ty.dev) static site. `src/pages/`
is the sitemap — a page's path there becomes its URL — and the build output
in `_site/` is served by a Cloudflare Worker (see `wrangler.jsonc`).

Pages under `src/pages/` were ported from a previous hosted site, so many of
them still carry that origin's conventions: a single wrapper element per page
with all styling scoped to it. Those conventions are worth keeping, because
every page shares one stylesheet and one layout.

## 1. Page structure
* Pages are `.njk` templates with front matter (`layout: base.njk`, `title`).
* `base.njk` supplies `<html>`, `<head>`, and `<body>` — a page template must
  never include them itself.
* Shared markup belongs in `src/_includes/partials/`; shared data in
  `src/_data/`.

## 2. Scoped CSS
* **Strict Scoping:** styles for a ported page must stay scoped to that page's
  unique container ID (e.g. `#arrangements-page-wrapper`).
* **No Global Styles:** never write bare `body {}`, `h1 {}`, or similar in a
  page template — they leak into every other page through the shared layout.
  Prefix them (e.g. `#arrangements-page-wrapper h1 {}`).
* Site-wide styling lives in `src/css/site.css`, not in page templates.

## 3. Robust JavaScript Initialization
* **Encapsulation:** wrap page scripts in an IIFE to avoid polluting the
  global namespace.
* **Initialization Check:** check `document.readyState` rather than assuming
  a script runs before or after parsing, and guard against double
  initialization.
  ```javascript
  (function() {
      function init() {
          if (window.myComponentInitialized) return;
          window.myComponentInitialized = true;
          // ... logic ...
      }

      if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', init);
      } else {
          init();
      }
  })();
  ```
* Prefer `DOMContentLoaded` over window `load` for anything that only touches
  layout. Waiting on `load` also waits on every image and autoplay video on
  the page, which visibly delays hero animations.

## 4. Responsive Layout Patterns
* For sections combining descriptive text and interactive elements (like
  buttons), prefer a **2-column responsive layout**:
  * **Desktop:** Flex row (Text Left | Content Right)
  * **Mobile (<768px):** Flex column (Text Top | Content Bottom)
* Use a wrapper class (e.g., `.content-wrapper`) to manage this layout switch
  via media queries.

## 5. File Restrictions
* **Never edit files containing the title "export.json".**

## 6. Deploys
* Pushing to `main` builds and deploys the live site via
  `.github/workflows/cloudflare_deploy.yml`. A manual deploy is
  `npm run deploy`, which cleans `_site` first — Eleventy does not remove
  stale output on its own.
* `.nvmrc` must stay at Node 22 or higher; wrangler refuses to run below it.
