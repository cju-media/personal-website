// Floating nav dropdowns: on hover-capable desktops the CSS :hover already
// reveals them (they're position:absolute overlays — never affect layout).
// On touch, there's no hover, so wire up tap-to-open / tap-again-to-follow,
// plus tap-outside and Escape to close.
(function () {
  const hasHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  if (hasHover) return;

  document.querySelectorAll('.nav-item').forEach((item) => {
    const link = item.querySelector(':scope > a');
    const folder = item.querySelector('.nav-folder');
    if (!link || !folder) return;
    link.addEventListener('click', (e) => {
      if (!item.classList.contains('open')) {
        e.preventDefault();
        document.querySelectorAll('.nav-item.open').forEach((o) => {
          if (o !== item) o.classList.remove('open');
        });
        item.classList.add('open');
      }
      // already open: let this tap follow the link normally
    });
  });

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.nav-item')) {
      document.querySelectorAll('.nav-item.open').forEach((o) => o.classList.remove('open'));
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.nav-item.open').forEach((o) => o.classList.remove('open'));
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
