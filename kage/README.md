# Kage landing page

`<KageLandingPage />` from ThreeUI (`kage-landing-page`, source revision SHA-256 `c8e06b90397a`), mounted with the configured usage in `src/Scene.tsx`.

```sh
npm install
npm run dev      # http://localhost:5173
npm run verify   # checks every registered file against threeui-manifest.json
npm run build
```

## Layout

- `public/landing-pages/kage.html` – the canonical Kage document, loaded in an iframe at `/landing-pages/kage.html`.
- `public/landing-pages/secret-pathways-assets/` – its fonts, Three.js runtime and image assets.
- `src/shaders/` – the registered ThreeUI sources (`LandingPageFrame.tsx`, `pageTypography.ts`, `pageRecipes.ts`, `threeui.css`).
- `src/threeui.ts` – what `@designcodeio/threeui` resolves to (see the alias in `vite.config.ts`).

All 22 registered files are byte-identical to `@designcodeio/threeui@1.2.0` and match their SHA-256 hashes. The one exception to "imported as-is" is `LandingPages.tsx`: it also imports the sources of every other ThreeUI page, which are not part of the Kage bundle. It is kept byte-exact for reference but excluded from compilation, and `KageLandingPage.tsx` holds its `KageLandingPage` function verbatim.
