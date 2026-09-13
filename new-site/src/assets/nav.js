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
