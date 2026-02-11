# Squarespace Deployment Guidelines

This repository contains HTML fragments and scripts intended to be injected into Squarespace sites via Code Blocks. To ensure compatibility and prevent side effects, all future builds must adhere to the following guidelines.

## 1. HTML Fragments vs. Full Documents
* **Do NOT** use `<html>`, `<head>`, or `<body>` tags in the main content file (e.g., `arrangements.html`, `scales.html`).
* The file should be a standalone HTML fragment.
* **Loader Pattern:** Create a separate "Block" file (e.g., `arrangementsBlock.html`) that acts as a loader. This file should contain a script to fetch the raw content of the fragment from the GitHub repository (usually the `main` branch) and inject it into the DOM.

## 2. Scoped CSS
* **Strict Scoping:** All CSS styles must be scoped to a unique container ID specific to that page component (e.g., `#arrangements-page-wrapper`).
* **No Global Styles:** Never write `body {}`, `h1 {}`, or other global selectors. Always prefix them (e.g., `#arrangements-page-wrapper h1 {}`).
* This prevents your styles from bleeding into and breaking the parent Squarespace site's theme.

## 3. Robust JavaScript Initialization
* **Encapsulation:** Wrap all scripts in an Immediately Invoked Function Expression (IIFE) to avoid polluting the global namespace.
* **Initialization Check:** Scripts injected via AJAX (common in Squarespace) might run at unpredictable times. Always check `document.readyState` or use a guard clause to prevent double initialization.
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

## 4. Responsive Layout Patterns
* For sections combining descriptive text and interactive elements (like buttons), prefer a **2-column responsive layout**:
  * **Desktop:** Flex row (Text Left | Content Right)
  * **Mobile (<768px):** Flex column (Text Top | Content Bottom)
* Use a wrapper class (e.g., `.content-wrapper`) to manage this layout switch via media queries.

## 5. File Restrictions
* **Never edit files containing the title "export.json".**

## 6. RNBO Integration Guidelines
When integrating Cycling '74 RNBO (Web Audio) patches into this repository, strictly adhere to the following patterns to ensure reliability on Squarespace and other hosting environments:

### A. Library Loading
* **Explicit Import:** Do not assume the parent environment has loaded the RNBO library. Always include the script tag explicitly within your fragment.
  ```html
  <script type="text/javascript" src="https://cdn.cycling74.com/rnbo/1.4.2/rnbo.min.js"></script>
  ```
* **Initialization Loop:** Even with the tag present, use `setInterval` to wait for `RNBO` to be defined in the global scope before running setup logic.

### B. AudioContext Management (Crucial for Reliability)
* **Singleton Pattern:** Browsers enforce a strict limit on the number of hardware AudioContexts (often ~6). Repeated page navigations or block re-injections can quickly exhaust this limit if new contexts are created blindly.
* **Shared Window Property:** Store the context in a unique window property (e.g., `window.RNBO_AudioContext`) and reuse it if it exists.
  ```javascript
  const WAContext = window.AudioContext || window.webkitAudioContext;
  if (!window.RNBO_AudioContext) {
      window.RNBO_AudioContext = new WAContext();
  }
  const context = window.RNBO_AudioContext;
  ```
* **User Interaction Resume:** Always call `context.resume()` inside a user interaction handler (e.g., `mousedown`, `touchstart`) to comply with browser autoplay policies.

### C. Asset Fetching
* **No GitHub API Calls:** Do not use `api.github.com` to list assets dynamically. The unauthenticated rate limit (60 requests/hour) is easily exceeded by public traffic, causing the entire audio experience to fail silently.
* **Raw URLs:** Use hardcoded lists of known assets and fetch them directly from `raw.githubusercontent.com`.
  ```javascript
  const ASSETS = ["sound1.aiff", "sound2.aiff"]; // Static list
  const url = `https://raw.githubusercontent.com/user/repo/main/path/${ASSETS[0]}`;
  ```

### D. Error Handling & Diagnostics
* **Granular Errors:** Distinguish between network errors (e.g., 404 Fetch) and codec errors (e.g., `EncodingError`). This aids debugging across different environments (e.g., testing environments without certain codecs).
* **Verbose Logging:** Log every step of the initialization sequence (Library Load -> Context Creation -> Fetch -> Decode -> Device Creation) to the console.

### E. Interaction Logic
* **Ghost Events:** On touch devices, a `touchstart` is often followed by a `mousemove`. Implement logic to ignore mouse events immediately following touch events (e.g., within 1000ms) to prevent double-triggering or jittery interaction.
