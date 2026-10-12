import json, os, re
from html import escape

SCRATCH = "/private/tmp/claude-501/-Users-admin-Desktop-Claude-rutman-gallery/00b58d26-3cf4-403a-aa52-82ccb1057652/scratchpad"
SITE = "/Users/admin/Desktop/Claude/rutman.gallery"

data = json.load(open(f"{SCRATCH}/master_final.json"))
order = data["order"]
artists = data["artists"]

# Inject the Louvre fact into Autumn de Forest's bio
adf = artists["Autumn de Forest"]
adf["bio_blocks"].insert(1, {
    "type": "callout",
    "text": "Autumn de Forest has been cited as the only living artist with work in the Louvre, and delivered a piece she painted live at age 9 that helped launch her national recognition."
})

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="{css}">
</head>
<body>
"""
FOOT = """
<footer class="site-footer">
  <p>&copy; The Rutman Gallery. Art and artists we love.</p>
</footer>
</body>
</html>
"""

def header(prefix):
    return f"""<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="{prefix}index.html">
      <img src="{prefix}images/TheRutmanGallery.png" alt="" class="brand-logo">
      <span>The Rutman Gallery</span>
    </a>
    <nav class="header-nav"><a href="{prefix}index.html">All Artists</a></nav>
  </div>
</header>
"""

def render_blocks(blocks):
    out = []
    for b in blocks:
        if b["type"] == "artist_line":
            out.append(f'<p class="artist-line">{escape(b["text"])}</p>')
        elif b["type"] == "callout":
            out.append(f'<p class="artist-line">{escape(b["text"])}</p>')
        elif b["type"] == "heading":
            out.append(f'<h3>{escape(b["text"])}</h3>')
        elif b["type"] == "p":
            out.append(f'<p>{escape(b["text"])}</p>')
        elif b["type"] == "list":
            items = "".join(f"<li>{escape(i)}</li>" for i in b["items"])
            out.append(f"<ul>{items}</ul>")
    return "\n".join(out)

def brightcove_embed(bc):
    if not bc: return ""
    return f"""<div class="video-wrap">
  <video-js data-video-id="{bc['video_id']}" data-account="{bc['account']}" data-player="{bc['player']}" data-embed="default" data-application-id="" class="vjs-fluid" controls></video-js>
  <script src="https://players.brightcove.net/{bc['account']}/{bc['player']}_default/index.min.js"></script>
</div>"""

# ---------------- Homepage ----------------
def is_promo_only(canon):
    pieces = artists[canon]["pieces"]
    return bool(pieces) and all(p.get("promo") for p in pieces)

def artist_card(canon):
    m = artists[canon]
    img = m.get("homepage_site_image") or ""
    count = len(m["pieces"])
    count_label = "coming soon" if count == 0 else f"{count} work{'s' if count != 1 else ''}"
    return f"""<a class="artist-card" href="{m['slug']}/index.html">
  <div class="thumb"><img src="{img}" alt="{escape(m['name'])}" loading="lazy"></div>
  <div class="name">{escape(m['name'])}</div>
  <div class="count">{count_label}</div>
</a>"""

# Main section order was hand-curated by the user (2026-09-06) into a fixed 3-across
# layout -- not sorted by piece count. Any main-collection artist not in this list
# (e.g. a brand-new one added later) falls back to being appended, sorted by count,
# so the build never silently drops someone.
FEATURED_ORDER = [
    "Jay Jbon Bonadio", "Autumn de Forest", "Salvador Dali",
    "Michael Cheval", "Michael Godard", "Kre8",
    "Romero Britto", "Tim Yanke", "Duaiv",
    "Anatole Krasnyansky", "Alfred Gockel", "Rodel Gonzalez",
    "David Najar", "Animation Art",
]
promo_canons = [c for c in order if is_promo_only(c)]
main_canons = [c for c in order if not is_promo_only(c)]
by_count = lambda c: (-len(artists[c]["pieces"]), artists[c]["name"])
leftover = sorted([c for c in main_canons if c not in FEATURED_ORDER], key=by_count)
main_order = [c for c in FEATURED_ORDER if c in main_canons] + leftover
main_cards = [artist_card(c) for c in main_order]
# Promo section is arranged alphabetically in the same fixed 3-across grid as the
# main section (2026-09-08), not sorted by piece count.
promo_cards = [artist_card(c) for c in sorted(promo_canons, key=lambda c: artists[c]["name"])]

promo_section = ""
if promo_cards:
    promo_section = f"""<section class="promo-section">
    <h2 class="section-title">Promotional Pieces</h2>
    <p class="section-subtitle">Posters and gifts that came bundled with auction purchases, kept separate from the collection above.</p>
    <div class="artist-grid">
      {''.join(promo_cards)}
    </div>
  </section>"""

home_html = HEAD.format(
    title="The Rutman Gallery",
    desc="Discover the art and artists we love. Browse the collection by artist.",
    css="styles.css",
) + header("") + f"""
<main>
  <section class="intro">
    <span class="eyebrow">A Private Collection</span>
    <h1>Discover the Art and Artists We Love</h1>
    <p>Browse the artists below. Each page includes the story behind their work, and a look at every piece in the collection.</p>
  </section>
  <section class="artist-grid artist-grid--featured">
    {''.join(main_cards)}
  </section>
  {promo_section}
</main>
""" + FOOT

with open(os.path.join(SITE, "index.html"), "w") as f:
    f.write(home_html)

# ---------------- Artist + artwork pages ----------------
for canon in order:
    m = artists[canon]
    slug = m["slug"]
    artist_dir = os.path.join(SITE, slug)
    os.makedirs(artist_dir, exist_ok=True)

    # artwork cards
    aw_cards = []
    for p in m["pieces"]:
        p_slug = p["title"].lower()
        import unicodedata as _uni
        p_slug = _uni.normalize("NFKD", p_slug).encode("ascii", "ignore").decode()
        p_slug = re.sub(r"[^a-z0-9]+", "-", p_slug).strip("-")
        p["_slug"] = p_slug
        dims_line = f'<div class="dims">{escape(p["dimensions"])}</div>' if p.get("dimensions") else ""
        img = p.get("site_image") or ""  # already "images/xxx.jpg", relative to site root
        aw_cards.append(f"""<a class="artwork-card" href="{p_slug}/index.html">
  <div class="thumb"><img src="../{img}" alt="{escape(p['title'])}" loading="lazy"></div>
  <h4>{escape(p['title'])}</h4>
  {dims_line}
</a>""")

    social = m.get("social") or {}
    social_links = []
    if social.get("facebook"): social_links.append(f'<li><a href="{social["facebook"]}">Facebook</a></li>')
    if social.get("instagram"): social_links.append(f'<li><a href="{social["instagram"]}">Instagram</a></li>')
    if social.get("parkwest"): social_links.append(f'<li><a href="{social["parkwest"]}">Park West Gallery</a></li>')
    official = ""
    if social.get("official_site"):
        official = f'<p class="official-site"><a href="{social["official_site"]}">Visit {escape(m["name"])}\'s official site &rarr;</a></p>'
    social_section = ""
    if social_links or official:
        social_section = f"""<section class="social">
    <h3>Follow {escape(m['name'])}</h3>
    <ul class="social-links">{''.join(social_links)}</ul>
    {official}
  </section>"""

    n_pieces = len(m["pieces"])
    count_label = "Collection pieces coming soon" if n_pieces == 0 else f"{n_pieces} work{'s' if n_pieces != 1 else ''} in the collection"
    headshot_img = m.get("headshot_site_image")
    if headshot_img:
        hero = f"""<div class="artist-hero">
    <img class="headshot" src="../{headshot_img}" alt="{escape(m['name'])}">
    <div>
      <h1>{escape(m['name'])}</h1>
      <div class="piece-count">{count_label}</div>
    </div>
  </div>"""
    else:
        hero = f"""<div class="artist-hero no-headshot">
    <h1>{escape(m['name'])}</h1>
    <div class="piece-count">{count_label}</div>
  </div>"""

    if m.get("bio_blocks"):
        bio_html = render_blocks(m["bio_blocks"])
    else:
        bio_html = f'<p>{escape(m.get("bio_text", ""))}</p>'

    page = HEAD.format(
        title=f'{escape(m["name"])} - The Rutman Gallery',
        desc=f'Artwork by {escape(m["name"])} in the Rutman Gallery collection.',
        css="../styles.css",
    ) + header("../") + f"""
<main class="artist-page">
  {hero}
  {brightcove_embed(m.get("brightcove"))}
  <section class="bio">
    {bio_html}
  </section>
  {'<h2 class="section-title">The Collection</h2><div class="artwork-grid">' + ''.join(aw_cards) + '</div>' if aw_cards else ''}
  {social_section}
  <p class="back-link"><a href="../index.html">&larr; Back to all artists</a></p>
</main>
""" + FOOT

    with open(os.path.join(artist_dir, "index.html"), "w") as f:
        f.write(page)

    # artwork detail pages
    for p in m["pieces"]:
        p_slug = p["_slug"]
        aw_dir = os.path.join(artist_dir, p_slug)
        os.makedirs(aw_dir, exist_ok=True)

        if p.get("blocks"):
            # drop the redundant "Title: ... Artist: ..." first line and the trailing hashtag line if present
            blocks = [b for b in p["blocks"] if not (b["type"] == "p" and b["text"].startswith("Title:"))]
            blocks = [b for b in blocks if not (b["type"] == "p" and b["text"].startswith("#"))]
            # dimensions/medium bullets get shown once, authoritatively, in the spec table below --
            # strip them here to avoid contradicting figures from two different sources
            cleaned = []
            for b in blocks:
                if b["type"] == "list":
                    items = [i for i in b["items"] if not re.match(r"^(Art )?Dimensions\s*:", i, re.I)
                              and not (p.get("medium") and i.lower().startswith("medium"))]
                    if items:
                        cleaned.append({"type": "list", "items": items})
                else:
                    cleaned.append(b)
            body_html = render_blocks(cleaned)
        elif p.get("medium"):
            body_html = f'<p>{escape(p["medium"])}</p>'
        else:
            body_html = ""

        specs = []
        if p.get("medium") and not p.get("blocks"):
            pass  # already shown above
        if p.get("year"): specs.append(("Year", p["year"]))
        if p.get("dimensions"): specs.append(("Dimensions", p["dimensions"]))
        if p.get("medium") and p.get("blocks"): specs.append(("Medium", p["medium"]))
        if p.get("reg_ser"): specs.append(("Reg. / Lot No.", p["reg_ser"]))
        spec_dl = "".join(f'<dt>{escape(k)}</dt><dd>{escape(v)}</dd>' for k, v in specs)

        img = p.get("site_image") or ""

        aw_page = HEAD.format(
            title=f'{escape(p["title"])} - The Rutman Gallery',
            desc=f'{escape(p["title"])} by {escape(m["name"])} — in the Rutman Gallery collection.',
            css="../../styles.css",
        ) + header("../../") + f"""
<main class="artwork-page">
  <h1>{escape(p["title"])}</h1>
  <p class="by-line">by <a href="../index.html">{escape(m["name"])}</a></p>
  <div class="artwork-detail">
    <div class="frame"><img src="../../{img}" alt="{escape(p['title'])}"></div>
    <div class="artwork-text">
      {body_html}
      <div class="spec-table">
        <dl>{spec_dl}</dl>
      </div>
    </div>
  </div>
  <p class="back-link"><a href="../index.html">&larr; Back to {escape(m["name"])}'s collection</a></p>
</main>
""" + FOOT

        with open(os.path.join(aw_dir, "index.html"), "w") as f:
            f.write(aw_page)

print("Site v2 generated.")
