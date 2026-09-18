// Floating nav dropdowns: on hover-capable desktops the CSS :hover already
// reveals them (they're position:absolute overlays — never affect layout).
// On touch, there's no hover, so wire up tap-to-open / tap-again-to-follow,
// plus tap-outside and Escape to close.
(function () {
  const hasHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  if (hasHover) return;

  function closeItem(item) {
    item.classList.remove('open');
    if (item._closeGlitch) item._closeGlitch();
  }

  document.querySelectorAll('.nav-item').forEach((item) => {
    const link = item.querySelector(':scope > a');
    const folder = item.querySelector('.nav-folder');
    if (!link || !folder) return;
    link.addEventListener('click', (e) => {
      if (!item.classList.contains('open')) {
        e.preventDefault();
        document.querySelectorAll('.nav-item.open').forEach((o) => {
          if (o !== item) closeItem(o);
        });
        item.classList.add('open');
        if (item._openGlitch) item._openGlitch();
      }
      // already open: let this tap follow the link normally
    });
  });

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.nav-item')) {
      document.querySelectorAll('.nav-item.open').forEach(closeItem);
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.nav-item.open').forEach(closeItem);
    }
  });
})();

// Keep dropdown panels inside the viewport.
//
// CSS anchors panels to one edge of their nav item — the right edge on
// desktop, the left edge below 980px where the nav switches to flex-start.
// Either way a single fixed anchor can still overhang when an item sits near
// the opposite edge of a wrapped row, and because panels are hidden with
// opacity rather than display:none an overhang widens the document and the
// whole page scrolls sideways at rest. CSS cannot express "only shift the
// ones that would overflow", so nudge those with a margin after layout.
//
// This runs on every device, unlike the tap handling above: the overflow is
// a layout problem, not an input one.
(function () {
  const GUTTER = 8;
  const panels = document.querySelectorAll('.nav-folder');
  if (!panels.length) return;

  function clamp() {
    const vw = document.documentElement.clientWidth;
    panels.forEach((panel) => {
      panel.style.marginLeft = '';
      const rect = panel.getBoundingClientRect();
      let shift = 0;
      if (rect.right > vw - GUTTER) shift = vw - GUTTER - rect.right;
      else if (rect.left < GUTTER) shift = GUTTER - rect.left;
      // Never push a panel off the far side to rescue the near side.
      if (shift && rect.width <= vw - GUTTER * 2) panel.style.marginLeft = Math.round(shift) + 'px';
    });
  }

  // Debounced with a timer rather than requestAnimationFrame: rAF is paused
  // while the tab is hidden, so a resize in a background tab would leave the
  // panels unclamped until it was next looked at.
  let pending;
  function scheduleClamp() {
    clearTimeout(pending);
    pending = setTimeout(clamp, 60);
  }

  clamp();
  window.addEventListener('resize', scheduleClamp);
  // Nav item widths shift once the webfonts swap in, moving the panels with
  // them, so measure again after that settles.
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(clamp);
  window.addEventListener('load', scheduleClamp);
})();

// Letter glitch: the same random-font/random-color flicker as the hero name
// on the homepage (see homepage-content.njk), reimplemented small so it can
// run site-wide in the header — once on the "cju.media" logo, and once per
// nav item's label, active only while that item's dropdown is open.
(function () {
  const fontClasses = ['logo-glitch-font1', 'logo-glitch-font2', 'logo-glitch-font3', 'logo-glitch-font4', 'logo-glitch-font5', 'logo-glitch-font6'];
  // Warm/cool tones tuned for the dark header bar, in place of the hero's
  // jewel tones (those were picked for the light homepage background and
  // would be nearly invisible here).
  const colors = ['#b98a5a', '#d9a869', '#e0b980', '#c2c9cc', '#8fa3a8', '#c97b4a'];
  const katakanaMap = {
    'A': 'ア', 'B': 'ブ', 'C': 'ク', 'D': 'デ', 'E': 'エ',
    'F': 'フ', 'G': 'グ', 'H': 'ハ', 'I': 'イ', 'J': 'ジ',
    'K': 'ケ', 'L': 'ル', 'M': 'ム', 'N': 'ン', 'O': 'オ',
    'P': 'プ', 'Q': 'キュ', 'R': 'ラ', 'S': 'ス', 'T': 'ト',
    'U': '牛', 'V': 'ヴ', 'W': 'ワ', 'X': 'クス', 'Y': 'ヤ', 'Z': 'ズ'
  };
  // Builds up over rampDuration ms after the trigger starts, rather than
  // jumping straight to full glitch — the same slow-build trick the
  // hover-triggered tile glitch uses further down in homepage-content.njk.
  const rampDuration = 600;

  // Wraps `el`'s text into per-character spans and returns start()/stop()
  // to drive the glitch loop — start() (re)begins the ramp-up, stop() lets
  // each character finish its current step and settle back to plain text.
  function createLetterGlitch(el) {
    const text = el.textContent;
    el.textContent = '';
    el.setAttribute('aria-label', text);
    const chars = [];
    for (const ch of text) {
      const span = document.createElement('span');
      span.className = 'logo-char';
      span.textContent = ch;
      // Without this, a lone space between words (e.g. "AV ENGINEERING")
      // collapses to nothing once it's the sole content of an inline-block.
      if (ch === ' ') span.style.whiteSpace = 'pre';
      span.setAttribute('aria-hidden', 'true');
      el.appendChild(span);
      chars.push(span);
    }

    // Different glitch fonts render the same text at different widths
    // (and font6 bumps font-size too), so left unchecked, glitching one
    // nav item resizes its box and reflows/rewraps every item after it.
    // Pin `el` to its own resting size and clip overflow instead — a
    // wide font variant gets clipped inside its own box rather than
    // pushing neighbors around.
    //
    // The lock is applied lazily, on the first start() rather than right
    // here at setup: at setup time (page load) the webfonts (Cormorant SC /
    // Barlow Condensed) can still be loading, and measuring against their
    // fallback would freeze in a too-narrow box that clips the real text
    // even at rest, forever. By the time a person actually hovers, the
    // fonts have long since settled.
    let sizeLocked = false;
    function lockSize() {
      el.style.display = 'inline-block';
      el.style.verticalAlign = 'top';
      el.style.width = '';
      el.style.height = '';
      const rect = el.getBoundingClientRect();
      el.style.width = Math.ceil(rect.width) + 'px';
      el.style.height = Math.ceil(rect.height) + 'px';
      el.style.overflow = 'hidden';
      sizeLocked = true;
    }

    let active = false;

    function rampFactor(span) {
      const start = parseInt(span.dataset.hoverStart || 0);
      return Math.min((Date.now() - start) / rampDuration, 1);
    }

    function changeFontRandomly(span) {
      if (!active) {
        span.dataset.looping = 'false';
        fontClasses.forEach((fontClass) => span.classList.remove(fontClass));
        span.textContent = span.dataset.original;
        return;
      }
      span.dataset.looping = 'true';

      if (!span.dataset.original) span.dataset.original = span.textContent;

      if (Math.random() > rampFactor(span)) {
        fontClasses.forEach((fontClass) => span.classList.remove(fontClass));
        span.textContent = span.dataset.original;
        setTimeout(() => changeFontRandomly(span), 50);
        return;
      }

      fontClasses.forEach((fontClass) => span.classList.remove(fontClass));
      span.classList.add(fontClasses[Math.floor(Math.random() * fontClasses.length)]);

      if (Math.random() < 0.05) {
        const originalChar = span.dataset.original.toUpperCase();
        span.textContent = katakanaMap[originalChar] || span.dataset.original;
      } else {
        span.textContent = span.dataset.original;
      }

      const interval = Math.floor(Math.random() * (700 - 300 + 1)) + 300;
      setTimeout(() => changeFontRandomly(span), interval);
    }

    function changeColorRandomly(span) {
      if (!active) {
        span.dataset.coloring = 'false';
        span.style.color = '';
        return;
      }
      span.dataset.coloring = 'true';

      if (Math.random() > rampFactor(span)) {
        span.style.color = '';
        setTimeout(() => changeColorRandomly(span), 50);
        return;
      }

      span.style.color = colors[Math.floor(Math.random() * colors.length)];
      const interval = Math.floor(Math.random() * (1500 - 800 + 1)) + 800;
      setTimeout(() => changeColorRandomly(span), interval);
    }

    return {
      start() {
        if (!sizeLocked) lockSize();
        active = true;
        const now = Date.now();
        chars.forEach((span) => {
          span.dataset.hoverStart = now;
          if (span.dataset.looping !== 'true') changeFontRandomly(span);
          if (span.dataset.coloring !== 'true') changeColorRandomly(span);
        });
      },
      stop() {
        active = false;
      }
    };
  }

  const logo = document.querySelector('.logo');
  if (logo) {
    const logoGlitch = createLetterGlitch(logo);
    logo.addEventListener('mouseenter', logoGlitch.start);
    logo.addEventListener('mouseleave', logoGlitch.stop);
  }

  document.querySelectorAll('.nav-item').forEach((item) => {
    const label = item.querySelector(':scope > a > .nav-label');
    if (!label) return;
    const labelGlitch = createLetterGlitch(label);
    // Desktop: the dropdown opens on CSS :hover/:focus-within of the item
    // itself, so tying start/stop to the item's own mouseenter/mouseleave
    // matches exactly when the menu is showing.
    item.addEventListener('mouseenter', labelGlitch.start);
    item.addEventListener('mouseleave', labelGlitch.stop);
    // Touch: the tap-to-open handling above toggles .open and calls these
    // directly, since there's no hover to key off of.
    item._openGlitch = labelGlitch.start;
    item._closeGlitch = labelGlitch.stop;
  });
})();
