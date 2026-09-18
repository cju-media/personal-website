# Hald CLUT Previewer

A small tool page: drop in a [Hald CLUT](https://www.quelsolaar.com/technology/clut.html)
image (the square identity-grid PNG a color LUT ships as) and see exactly what
it does, applied live in the browser — no upload, no server round-trip.

## How it works

- `hald-clut.html` is the static HTML fragment — scoped styles, a glitch
  title matching the rest of the site, and a self-contained Hald CLUT engine.
  This fragment is superseded: the live page is `src/pages/tools/hald-clut.njk`,
  built and deployed with the rest of the site. This copy is kept as the
  pre-rebuild reference.
- `sample-photo.jpg` is the bundled default test photo (1200px, ~130KB).
  The live page no longer fetches it over the network — it serves its own
  copy from `src/assets/hald-clut-sample-photo.jpg`.
  It's a real, previously-published photo of Cameron already used elsewhere
  on the site, chosen for its mixed colored stage lighting and skin tones —
  good for judging what a LUT does to both.

## The algorithm

A Hald CLUT of level `n` is a square image of width `n^3` encoding a 3D color
cube of `n^2` steps per channel (e.g. level 8 → 512×512, level 12 → 1728×1728,
both common exports from RawTherapee/GIMP/DaVinci-style LUT packs). For a
source pixel `(r, g, b)`:

1. Quantize each channel to the cube's step count: `ri = round(r/255 * (cube-1))`.
2. Compute the linear cube index: `index = ri + gi*cube + bi*cube^2`.
3. Look that index up as `(index % W, floor(index / W))` in the Hald image —
   that pixel is the transformed color.

This is done with nearest-neighbor lookup (no trilinear interpolation),
which is standard for Hald CLUT previews and fast enough to run per-pixel
on a downscaled canvas in plain JS.

## Using it

- Drop a Hald CLUT PNG on the left. The bundled sample photo loads
  automatically in the background, so a preview renders as soon as the CLUT
  is dropped — no photo upload required.
- Switch the default source with the "Sample Photo" / "Test Chart" pills
  (the chart is a synthetic hue sweep, grayscale ramp, and primary/skin-tone
  swatch grid — useful for judging a LUT's effect precisely rather than on a
  specific photo). If the sample photo fails to load (e.g. offline), it
  falls back to the chart automatically.
- Optionally drop your own photo on the right to preview the LUT on it
  instead (large photos are downscaled to a max 1400px edge for speed).
- Either dropzone also takes a pasted image link instead of a file, so you
  don't need to first download an image (a CLUT from a LUT-pack site, a
  photo from elsewhere) just to drag it back in. This fetches the URL
  client-side, so it only works when the host allows cross-origin reads
  (most raw file hosts and CDNs do; some sites block it, in which case the
  page says so and you can fall back to saving + dropping the file).
- Drag the divider (or click the toggle buttons) to compare before/after.
  "Open Result Link" opens the processed image in a new tab to view, copy,
  or share, with no file save required; "Download Result" still saves a PNG
  if you want the file itself.
