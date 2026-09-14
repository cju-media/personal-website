module.exports = function (eleventyConfig) {
  // Static passthroughs — CSS and any images/media placed in src/assets ship
  // as-is. Explicit {source: target} form, because these folders sit outside
  // `dir.input` (src/pages) — with a bare path Eleventy can't strip an input
  // prefix that isn't there, and copies them to _site/src/... instead of
  // _site/... (breaking every /css/... and /assets/... reference on every
  // page). Pin the output paths directly instead of relying on that stripping.
  eleventyConfig.addPassthroughCopy({ "src/css": "css" });
  eleventyConfig.addPassthroughCopy({ "src/assets": "assets" });
  // Cloudflare Pages reads _redirects from the output root.
  eleventyConfig.addPassthroughCopy({ "src/_redirects": "_redirects" });

  return {
    dir: {
      // Routable pages live in src/pages, organized to mirror the site's
      // nav (src/pages/<nav-section>/<page>.njk) — a page's URL comes
      // straight from its path here, so the repo layout IS the sitemap.
      // Non-nav pages (contact, subscribe, ...) sit as loose files
      // directly under src/pages, not nested in a nav-section folder.
      input: "src/pages",
      // _includes and _data are shared build machinery, not routes, so
      // they stay outside src/pages — paths below are relative to `input`.
      includes: "../_includes",
      data: "../_data",
      output: "_site",
    },
  };
};
