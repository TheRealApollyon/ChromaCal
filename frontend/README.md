# ChromaCal panel frontend

Source for the sidebar panel ChromaCal's Python integration registers via
`custom_components/chromacal/frontend.py`. Built with
[Lit](https://lit.dev) + TypeScript, bundled with
[esbuild](https://esbuild.github.io/) into a single ES module.

## Why the build output is committed

A HACS install just copies `custom_components/chromacal/` onto the user's
HA host — there's no npm/Node available there, and there shouldn't need to
be. So the built bundle,
`custom_components/chromacal/panel_dist/chromacal-panel.js`, is committed
to the repo as a tracked build artifact, same as any other release asset.
**Never hand-edit that file** — it's generated. Edit `src/` and rebuild.

## Rebuilding

Requires Node.js (any recent LTS). From this directory:

```bash
npm install
npm run build
```

That regenerates `../custom_components/chromacal/panel_dist/chromacal-panel.js`.
Commit the regenerated file alongside your source changes.

If Node isn't installed locally, the same build runs fine in a throwaway
container from the repo root:

```bash
docker run --rm -v "$(pwd)/frontend:/frontend" -w /frontend node:22-slim \
  sh -c "npm install && npm run build"
```

## Type-checking (optional, not required for the build)

`esbuild` transpiles TypeScript without checking types. Run the real
compiler separately if you want that:

```bash
npm run typecheck
```
