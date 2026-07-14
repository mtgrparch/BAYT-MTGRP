# BEIT — بيت

Pre-approved, fixed-price productized houses for Lebanon. A product line by
[MTGRP / Metagroupe](https://mtgrp.xyz):
one team, one contract, one USD price; houses engineered once as products
(SAHEL · JABAL · WADI) and built with a network of Lebanese workshops.

## Stack

Plain static site, no build step — same as mtgrp.xyz:

- `index.html` — all content
- `style.css` — Karla 800 / EB Garamond italic / Amiri (Arabic), white–black
  with terracotta accent, `mix-blend-mode: difference` fixed chrome
- `script.js` — GSAP ScrollTrigger (CDN): pinned pillar swaps, scrubbed hero,
  timeline bars, horizontal house gallery, counters. Degrades to a fully
  readable static page with JS off or `prefers-reduced-motion`.

## Preview locally

```
python -m http.server
```

## Deploy

Push to GitHub, enable Pages. Add a `CNAME` file when the domain is decided
(e.g. `bayt.mtgrp.xyz` — then add a DNS CNAME record pointing to
`<user>.github.io`).

## Placeholders to replace before launch

- Prices, areas and durations on the house cards (marked "indicative")
- Partner marquee entries (currently region/craft placeholders)
- House SVG line drawings → real axonometrics/photos when available
- Product name **BEIT** itself, if a different name is chosen
