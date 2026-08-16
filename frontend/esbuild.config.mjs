import { build } from "esbuild";

// outdir + splitting, not a single outfile (Phase 11) -- house-view.ts is
// dynamically import()-ed from chromacal-panel.ts only when House View is
// actually opened, so its Three.js weight doesn't ship to every dashboard
// page loaded dashboard-wide via add_extra_js_url. Verified empirically
// (a throwaway build) that a single entry point still lands at
// panel_dist/chromacal-panel.js unchanged -- frontend.py's module_url
// doesn't need to change. The dynamic chunk gets its own content-hashed
// filename (e.g. house-view-XXXXXXXX.js) automatically, which is real
// cache-busting on its own -- no ?v= trick needed for it, unlike the
// entry file.
await build({
  entryPoints: ["src/chromacal-panel.ts"],
  bundle: true,
  format: "esm",
  target: "es2021",
  splitting: true,
  outdir: "../custom_components/chromacal/panel_dist",
  minify: true,
  sourcemap: false,
  tsconfig: "tsconfig.json",
  legalComments: "none",
});

console.log("Built ../custom_components/chromacal/panel_dist/");
