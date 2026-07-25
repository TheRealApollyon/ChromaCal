import { build } from "esbuild";

await build({
  entryPoints: ["src/chromacal-panel.ts"],
  bundle: true,
  format: "esm",
  target: "es2021",
  outfile: "../custom_components/chromacal/panel_dist/chromacal-panel.js",
  minify: true,
  sourcemap: false,
  tsconfig: "tsconfig.json",
  legalComments: "none",
});

console.log("Built ../custom_components/chromacal/panel_dist/chromacal-panel.js");
