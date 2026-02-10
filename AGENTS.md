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
