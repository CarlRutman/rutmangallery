import re, json, os, unicodedata, shutil

SCRATCH = "/private/tmp/claude-501/-Users-admin-Desktop-Claude-rutman-gallery/00b58d26-3cf4-403a-aa52-82ccb1057652/scratchpad"
NOTES_BASE = "/Users/admin/Desktop/Claude/rutman.gallery/tools/source_notes"
SITE = "/Users/admin/Desktop/Claude/rutman.gallery"

home = json.load(open(f"{SCRATCH}/home_data.json"))
artists_full = json.load(open(f"{SCRATCH}/artists_full.json"))

# ---------- Parse Park West style-A records ----------
FILES_A = [
    "Park West 1st Purchase (24)/Park West 1st Purchase (24).md",
    "Park West 2nd Purchase (9)/Park West 2nd Purchase (9).md",
]
pw_records = []

def parse_style_A(text, folder):
    blocks = re.split(r'(?=!\[)', text)
    for b in blocks:
        img_m = re.search(r'!\[([^\]]+)\]\(Attachments/([^)]+)\)', b)
        if not img_m:
            continue
        img_file = img_m.group(2)
        title_m = re.search(r'Title\s*:\s*(.+)', b)
        artist_m = re.search(r'Artist\s*:\s*(.+)', b)
        dim_m = re.search(r'(?:Dimensions|Art Dimensions)\s*:\s*(.+)', b)
        regser_m = re.search(r'Reg\.?Ser\s*:\s*(\S+)', b)
        price_m = re.search(r'\$([0-9,]+(?:\.\d{2})?)', b)
        if title_m and artist_m:
            pw_records.append({
                "title": title_m.group(1).strip(),
                "artist": artist_m.group(1).strip(),
                "dimensions": dim_m.group(1).strip() if dim_m else None,
                "reg_ser": regser_m.group(1).strip() if regser_m else None,
                "price": re.sub(r"\.00$", "", price_m.group(1).strip()) if price_m else None,
                "image": os.path.join(NOTES_BASE, folder, "Attachments", img_file),
                "medium": None,
                "year": None,
            })

for rel in FILES_A:
    folder = rel.split("/")[0]
    text = open(os.path.join(NOTES_BASE, rel), encoding="utf-8").read()
    parse_style_A(text, folder)

# ---------- Manually-curated style-B records (long-form catalog entries) ----------
pw_records += [
    {
        "title": "Discord of Analogy II",
        "artist": "Michael Cheval",
        "dimensions": "26 in x 32 ½ in",
        "reg_ser": "CP1868 / 349314",
        "price": None,
        "image": os.path.join(NOTES_BASE, "Park West 5th Purchase (3)/Attachments/AB979F5A-DE50-4B24-840B-E853B3292D2A.jpg"),
        "medium": "Dye sublimation on aluminum. Hand-signed in ink center right by the artist.",
        "year": "2015",
    },
    {
        "title": "Coffee Lovers",
        "artist": "Michael Godard",
        "dimensions": "5 ⅝ in x 9 ⅜ in",
        "reg_ser": "CP0734 / 948361",
        "price": None,
        "image": os.path.join(NOTES_BASE, "Park West 5th Purchase (3)/Attachments/97B8D63E-26B1-4776-9FC7-53697968B48E.jpg"),
        "medium": "Hand-painted sculpture in resin. Hand-signed in pigment by the artist.",
        "year": "2022",
    },
    {
        "title": "Don Quichotte (Don Quixote) - Horse",
        "artist": "Salvador Dali",
        "dimensions": "22 in x 14 ⅜ in",
        "reg_ser": "714635",
        "price": None,
        "image": os.path.join(NOTES_BASE, "Park West 5th Purchase (3)/Attachments/13EC262C-3AC1-4990-898C-B54BC811A9CD.jpg"),
        "medium": "Lithograph in color on Arches paper, from the 18-piece suite “Les Chevaux de Dali” (Dali's Horses). With the artist's authorized facsimile signature.",
        "year": "1983",
    },
    {
        "title": "Nothing but a Pack of Cards",
        "artist": "Michael Cheval",
        "dimensions": "25 in x 20 in",
        "reg_ser": "812799",
        "price": None,
        "image": os.path.join(NOTES_BASE, "Park West Telecast 21214/Attachments/DF943B98-0C7A-4E8D-BACF-446A613F5745.jpg"),
        "medium": "Dye sublimation on aluminum. Hand-signed in pigment lower right by the artist.",
        "year": "2017",
    },
    {
        "title": "Beautiful Struggle - Silver Face",
        "artist": "Jay Bonadio",
        "dimensions": "24 in x 16 in",
        "reg_ser": "763780",
        "price": None,
        "image": None,  # will reuse WP image
        "medium": None,
        "year": None,
    },
]

print(f"Total Park West records: {len(pw_records)}")

# ---------- Normalize artist names ----------
def norm(s):
    s = unicodedata.normalize("NFKD", s)
    return re.sub(r"[^a-z0-9]", "", s.lower())

def norm_title(s):
    s = unicodedata.normalize("NFKD", s)
    s = re.sub(r"[’']", "", s)
    return re.sub(r"[^a-z0-9]", "", s.lower())

# canonical artist name -> display name (prefer WP naming where available)
CANON = {
    "jayjbonbonadio": "Jay Jbon Bonadio", "jaybonadio": "Jay Jbon Bonadio",
    "michelcheval": "Michael Cheval", "michaelcheval": "Michael Cheval",
    "autumndeforest": "Autumn de Forest",
    "kre8": "Kre8",
    "michaelgodard": "Michael Godard",
    "animationart": "Animation Art",
    "salvadordali": "Salvador Dali",
    "davidnajar": "David Najar",
    "timyanke": "Tim Yanke",
    "romerobritto": "Romero Britto",
    "duaiv": "Duaiv",
    "ashtonhoward": "Ashton Howard",
    "lindalekinff": "Linda Le Kinff",
    "mattbeyrer": "Matt Beyrer",
    "zamysteynovitz": "Zamy Steynovitz",
    "itzchaktarkay": "Itzchak Tarkay",
    "jimwaren": "Jim Warren", "jimwarren": "Jim Warren",
    "danielwall": "Daniel Wall",
    "slavabrodinsky": "Slava Brodinsky",
    "slavailyayev": "Slava Ilyayev",
    "victorspahn": "Victor Spahn",
}

def canon_artist(name):
    n = norm(name)
    return CANON.get(n, name.strip())

for r in pw_records:
    r["artist_canon"] = canon_artist(r["artist"])

# ---------- Build master artist dict from homepage (21 artists, ordered) ----------
master = {}
order = []
for a in home["homepage"]["artists"]:
    disp = a["name"]
    canon = canon_artist(disp)
    slug = re.sub(r"[^a-z0-9]+", "-", canon.lower()).strip("-")
    order.append(canon)
    master[canon] = {
        "name": canon,
        "slug": slug,
        "homepage_img": a["img"],
        "homepage_count": a["count"],
        "bio_blocks": None,
        "headshot": None,
        "brightcove": None,
        "social": {},
        "pieces": {},  # keyed by norm_title
    }

# ---------- Merge in WP artists_full (rich bios + described artworks) ----------
WP_SLUG_TO_CANON = {
    "jay-jbon-bonadio": "Jay Jbon Bonadio",
    "michael-cheval": "Michael Cheval",
    "autumn-de-forest": "Autumn de Forest",
    "kre8": "Kre8",
}
for wp_slug, a in artists_full.items():
    canon = WP_SLUG_TO_CANON[wp_slug]
    m = master[canon]
    m["bio_blocks"] = a["bio_blocks"]
    m["headshot"] = a["headshot"]
    m["brightcove"] = a["brightcove"]
    m["social"] = a["social"]
    m["wp_url"] = a["url"]
    for aw in a["artworks"]:
        key = norm_title(aw.get("short_title") or aw["title"])
        m["pieces"][key] = {
            "title": aw.get("short_title") or aw["title"],
            "full_title": aw["title"],
            "image": aw["img"],  # remote URL, downloaded already to images/
            "blocks": aw["blocks"],
            "dimensions": None, "price": None, "reg_ser": None, "medium": None, "year": None,
        }

# ---------- Merge in Park West records ----------
unmatched = []
for r in pw_records:
    canon = r["artist_canon"]
    if canon not in master:
        # New artist not on homepage (shouldn't happen given our 21, but just in case)
        continue
    m = master[canon]
    key = norm_title(r["title"])
    # try exact match, then substring match against existing pieces
    match_key = None
    if key in m["pieces"]:
        match_key = key
    else:
        for pk in m["pieces"]:
            if key in pk or pk in key:
                match_key = pk
                break
    if match_key:
        p = m["pieces"][match_key]
        p["dimensions"] = r["dimensions"]
        p["price"] = r["price"]
        p["reg_ser"] = r["reg_ser"]
        p["medium"] = r["medium"]
        p["year"] = r["year"]
        if r["image"] and not p.get("local_source_image"):
            p["local_source_image"] = r["image"]
    else:
        m["pieces"][key] = {
            "title": r["title"],
            "full_title": f'{r["title"]} by {canon}',
            "image": None,
            "local_source_image": r["image"],
            "blocks": None,
            "dimensions": r["dimensions"], "price": r["price"],
            "reg_ser": r["reg_ser"], "medium": r["medium"], "year": r["year"],
        }

# ---------- Fallback pieces for artists with only a homepage thumbnail ----------
FALLBACK_TITLES = {
    "Matt Beyrer": "On the Water",
    "Jim Warren": "Love is in the Air",
    "Daniel Wall": "Splendid Life",
}
for canon, title in FALLBACK_TITLES.items():
    m = master[canon]
    if not m["pieces"]:
        m["pieces"][norm_title(title)] = {
            "title": title,
            "full_title": f"{title} by {canon}",
            "image": m["homepage_img"],
            "blocks": None,
            "dimensions": None, "price": None, "reg_ser": None, "medium": None, "year": None,
        }

# Slava Ilyayev shares a homepage thumbnail with Slava Brodinsky (data gap on the
# source site) -- no distinct piece to show yet, leave pieces empty intentionally.

import sys
sys.path.insert(0, SCRATCH)
from bios import BIOS
for canon, bio_text in BIOS.items():
    m = master.get(canon)
    if m and not m["bio_blocks"]:
        m["bio_text"] = bio_text

for canon in order:
    m = master[canon]
    m["pieces"] = list(m["pieces"].values())

json.dump({"order": order, "artists": master}, open(f"{SCRATCH}/master.json", "w"), indent=2)
print("Wrote master.json")
for canon in order:
    m = master[canon]
    print(f"{canon}: {len(m['pieces'])} pieces, bio={'yes' if m['bio_blocks'] else 'no'}")
