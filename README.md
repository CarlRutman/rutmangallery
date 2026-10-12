# The Rutman Gallery

A static-HTML recreation of [rutman.gallery](https://rutman.gallery) — a private art collection
site, rebuilt with a light, gallery-white design. Plain HTML/CSS, no build step, no framework,
same approach as the [Sharon Cub Scouts](https://github.com/CarlRutman/cubpack95sharon) site.

## Structure

- `index.html` — homepage grid of all 21 artists in the collection.
- `<artist-slug>/index.html` — one page per artist: bio, embedded Brightcove video where
  available, and a grid of every piece by that artist.
- `<artist-slug>/<piece-slug>/index.html` — one page per artwork, with description, medium,
  dimensions, year, price, and Park West registration/lot number where known.
- `images/` — every artwork photo, headshot, and the site logo.
- `styles.css` — shared stylesheet for every page.

## Sources

Content was merged from two places:

1. **The live WordPress site** (rutman.gallery, snapshotted 2026-01-23) — full artist
   biographies and artwork descriptions for the 4 artists that had real pages there (Jay Jbon
   Bonadio, Michael Cheval, Autumn de Forest, Kre8).
2. **Park West Gallery purchase records** from Apple Notes — authoritative titles, dimensions,
   medium, edition info, price, and registration/lot numbers for ~40 individual pieces, covering
   every artist in the collection. This is what let the other 17 artists (previously "coming
   soon" placeholders) get real pages.

Where no sourced biography existed, short factual artist intro paragraphs were written from
general public knowledge; artists with no such record are honestly labeled rather than given a
fabricated backstory (see `tools/3_authored_bios.py`).

## Rebuilding

The `tools/` scripts document how this was built (they use absolute paths from the original
session, so treat them as reference rather than a one-command pipeline):

1. `1_scrape_wp_homepage.py` / `2_scrape_wp_artists.py` — scrape the live WordPress site.
2. `3_authored_bios.py` — hand-written bios for artists without a sourced one.
3. `4_merge_data.py` — merges WordPress + Park West purchase-record data into `master.json`.
4. `5_consolidate_images.py` — copies/renames every artwork image into `images/`.
5. `6_build_site.py` — generates every HTML page from the merged data.

Park West source exports (Apple Notes markdown + attachment photos) aren't checked into this
repo — see `tools/source_notes/` locally if you need to re-run the merge.

## Previewing locally

```bash
python3 -m http.server 8899
```

Then open http://localhost:8899.
