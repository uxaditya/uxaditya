# Andamana — island tours of the Andaman Sea

A static, dependency-free tourism website: dark cinematic layout, condensed display
typography, and **scenery that the repository generates itself** rather than
hotlinking stock photography.

Open `index.html` straight off disk, or run a local server:

```bash
npm install && npm start      # http://localhost:3000
# or, with nothing installed:
python3 -m http.server 8000
```

`npm start` is a convenience only — the site itself has no build step and no
runtime dependencies. `serve.json` turns off `serve`'s clean-URL rewriting,
because that issues a 301 which **drops the query string** and would break the
`?slug=` and `?tag=` deep links.

`npm run server` and `npm run dev` are aliases of `npm start`. Other scripts:
`npm run art` regenerates the scenery, `npm run art:list` prints the scene
manifest, `npm run fonts` re-vendors the webfonts.

## Pages

| File | What it is |
| --- | --- |
| `index.html` | Home — rotating hero with an image-filled display word, featured trips, story, experience tiles, reviews, newsletter |
| `tours.html` | Full catalogue with client-side filtering, deep-linkable via `?tag=` and `?from=` |
| `tour.html` | Trip detail template, populated from `?slug=` — itinerary, inclusions, gallery lightbox, live booking total |
| `about.html` | Operator story, safety, marine park fees, season guide |

## How it is put together

```
index.html tours.html tour.html about.html   pages (plain HTML, no build step)
assets/css/style.css                         design tokens + components
assets/css/fonts.css                         @font-face for the vendored fonts
assets/js/tours.js                           the tour catalogue — single source of truth
assets/js/main.js                            all behaviour, ~700 lines, no dependencies
assets/img/*.svg                             generated scenery
assets/fonts/*.woff2                         self-hosted Anton / Barlow Condensed / Inter
tools/gen_art.py                             the scenery generator
tools/get_fonts.py                           re-vendors the webfonts
package.json serve.json                      optional local dev server
```

`assets/js/tours.js` drives every grid, the search index, the departure mega menu and
the detail page, so a price or an itinerary is only ever edited in one place.

### The artwork

`tools/gen_art.py` renders every image as a layered SVG seascape — limestone karst
towers with sunlit flanks and vegetated crowns, depth-of-field ridges veiled by
aerial haze, water carrying the towers' reflections and a specular sun path, palm
silhouettes, then a colour grade, vignette and film grain over the top.

```bash
python3 tools/gen_art.py          # write all 17 scenes to assets/img/
python3 tools/gen_art.py --list   # the manifest: name, kind, palette, seed
python3 tools/gen_art.py --only hero-krabi
```

Six palettes (`lagoon`, `ember`, `abyss`, `jade`, `dawn`, `gold`) and three framings
(`hero`, `card`, `banner`) mean no two cards in a grid look alike. Every scene is
seeded, so re-running never churns the repo.

**Swapping in real photographs:** the artwork is deliberately self-contained, but
nothing depends on it being generated. Drop your own files into `assets/img/`, point
the `img`, `gallery` and `hero` fields in `assets/js/tours.js` at them, and update the
`src` attributes in the four HTML pages. Portrait cards want roughly 3:4, heroes and
banners want something wide.

## Behaviour

Everything in `main.js` is opt-in — a module only runs when the markup it needs is on
the page, so one script serves all four pages.

- Hero rotator with Ken Burns drift; the display word's photographic fill and the
  mirrored echo below it re-point at each slide
- Departure mega menu, mobile drawer, and a full-screen search (`/` to open,
  `Esc` to close) that filters the catalogue live by text and tag
- Scroll reveals, section staggering, and parallax on the wide banners
- Client-side catalogue filtering, count-up stats, review slider, gallery lightbox
  with arrow-key navigation, live booking total

## Accessibility and performance notes

- Skip link, visible focus rings, `aria-expanded` / `aria-pressed` state on every
  toggle, labelled icon buttons, and `Esc` handling on all overlays
- `prefers-reduced-motion` disables the rotator, parallax, grain drift and marquee
- Reveal animations are scoped to `.js`, so with JavaScript off the content is simply
  visible rather than stuck at `opacity: 0`
- No third-party requests at runtime: fonts are self-hosted, there are no trackers,
  and the only images are local SVGs
- Print stylesheet strips the chrome

## Licence and content

The copy, prices, itineraries and reviews are fictional and written for this demo.
The vendored fonts are Anton, Barlow Condensed and Inter, all under the
SIL Open Font License 1.1.
