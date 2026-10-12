import json, re

SCRATCH = "/private/tmp/claude-501/-Users-admin-Desktop-Claude-rutman-gallery/00b58d26-3cf4-403a-aa52-82ccb1057652/scratchpad"
data = json.load(open(f"{SCRATCH}/master_final.json"))
order = data["order"]
artists = data["artists"]

def blank_piece(title, dims=None, reg=None, price=None, medium=None, year=None, image=None):
    return {
        "title": title, "full_title": title, "image": None, "blocks": None,
        "dimensions": dims, "price": price, "reg_ser": reg, "medium": medium, "year": year,
        "site_image": image,
    }

def new_artist(name, slug, bio, homepage_image):
    return {
        "name": name, "slug": slug, "homepage_img": None, "homepage_count": "0",
        "bio_blocks": None, "headshot": None, "brightcove": None, "social": {},
        "pieces": [], "bio_text": bio, "homepage_site_image": homepage_image,
    }

# ---------------- 1. Corrections to existing pieces (Clarity is authoritative) ----------------
def find_piece(artist_canon, title_substr):
    for p in artists[artist_canon]["pieces"]:
        if title_substr.lower() in p["title"].lower():
            return p
    return None

corrections = [
    ("Michael Cheval", "Winds of Fortune", {"dimensions": "17 in x 26 ½ in", "reg_ser": "754151.0065"}),
    ("Michael Cheval", "Nothing but a Pack of Cards", {"reg_ser": "812794.0047"}),
    ("Autumn de Forest", "Maslow", {"dimensions": "26 ¾ in x 20 ¼ in", "reg_ser": "889101.0048"}),
    ("Autumn de Forest", "Power of She", {"dimensions": "10 in x 23 in", "reg_ser": "889131.0029"}),
    ("Matt Beyrer", "On the Water", {"dimensions": "23 ½ in x 33 ¾ in", "reg_ser": "719562.CXMQ"}),
    ("Daniel Wall", "Splendid Life", {"dimensions": "26 in x 31 ¾ in", "reg_ser": "719069.CBQZ"}),
    ("Jim Warren", "Love is in the Air", {"dimensions": "32 ½ in x 25 ¼ in", "reg_ser": "719067.FFBT"}),
    ("Linda Le Kinff", "Le Tapis de Simire III", {"dimensions": "12 ¾ in x 10 ⅞ in", "reg_ser": "265821.0008"}),
]
for canon, title_substr, fields in corrections:
    p = find_piece(canon, title_substr)
    if p:
        p.update(fields)
        print(f"corrected: {canon} / {p['title']}")
    else:
        print(f"NOT FOUND: {canon} / {title_substr}")

# ---------------- 2. New pieces for existing artists ----------------
artists["Michael Cheval"]["pieces"].append(
    blank_piece("Alter Ego Convention", "25 in x 15 in", "894902.0184",
                image="images/michael-cheval--alter-ego-convention.jpg"))
artists["Kre8"]["pieces"].append(
    blank_piece("Visions of a Dreamer", "20 in x 12 in", "764458.0167",
                image="images/kre8--visions-of-a-dreamer.jpg"))
artists["Animation Art"]["pieces"].append(
    blank_piece("Scooby-Doo Haunted House", "22 ¾ in x 29 ½ in", "R04606.3438",
                image="images/animation-art--scooby-doo-haunted-house.jpg"))
artists["Tim Yanke"]["pieces"].append(
    blank_piece("Heart Gallery", "24 in x 24 in", "974070.0049",
                image="images/tim-yanke--heart-gallery.jpg"))
artists["Michael Godard"]["pieces"].append(
    blank_piece("Love in the Air", "24 in x 16 in", "764770.0150",
                image="images/michael-godard--love-in-the-air.jpg"))
artists["Michael Godard"]["pieces"].append(
    blank_piece("The G.O.A.T.", "24 in x 16 in", "758354.0154",
                image="images/michael-godard--the-goat.jpg"))
artists["Michael Godard"]["pieces"].append(
    blank_piece("Snow Dance", "18 in x 18 in", "756430.0144",
                image="images/michael-godard--snow-dance.jpg"))

# Slava Ilyayev finally gets a real piece
artists["Slava Ilyayev"]["pieces"].append(
    blank_piece("Walking in the Rain Ver. XLVII", "27 in x 27 in", "721867.BQDM",
                image="images/slava-ilyayev--walking-in-the-rain.jpg"))
artists["Slava Ilyayev"]["homepage_site_image"] = "images/slava-ilyayev--walking-in-the-rain.jpg"

# ---------------- 3. Brand-new artists ----------------
NEW_ARTISTS = [
    ("Rodel Gonzalez", "rodel-gonzalez",
     "Rodel Gonzalez is a Filipino-American fine artist and an official Disney Fine Art "
     "licensed artist, known for nostalgic, illustrative paintings that blend Americana "
     "imagery with a warm, storybook sensibility.",
     [blank_piece("Midnight Cowboy", "12 in x 15 in", "752110.0159",
                   image="images/rodel-gonzalez--midnight-cowboy.jpg")]),
    ("Alfred Gockel", "alfred-gockel",
     "Alfred Gockel is a German-American contemporary artist known for bold, gestural "
     "abstract paintings built from sweeping calligraphic brushwork over vivid fields "
     "of color.",
     [blank_piece("Orange Lust", "9 ¾ in x 9 ¾ in", "258483.1358",
                   image="images/alfred-gockel--orange-lust.jpg"),
      blank_piece("Atlantis", "39 ¼ in x 27 ½ in", "410634.0445",
                   image="images/alfred-gockel--atlantis.jpg")]),
    ("Anatole Krasnyansky", "anatole-krasnyansky",
     "Anatole Krasnyansky is a Ukrainian-American artist known for vividly colored, "
     "cubist-influenced depictions of musicians and harlequin figures, rendered in "
     "watercolor and fine-art serigraph editions.",
     [blank_piece("Violinist II", "22 in x 14 ⅝ in", "816581.0086",
                   image="images/anatole-krasnyansky--violinist-ii.jpg")]),
    ("Csaba Markus", "csaba-markus",
     "Csaba Markus is a Hungarian-American artist known for glamorous, Art Deco-inspired "
     "figurative paintings, often finished with gold leaf and a romantic, old-Hollywood "
     "sensibility.",
     [blank_piece("Triumph of Venus", "14 ⅛ in x 22 ⅜ in", "409189.0226",
                   image="images/csaba-markus--triumph-of-venus.jpg")]),
    # Note: Jeffrey C Wright's "The Book of Albert" was deliberately excluded -- it's a
    # signed reference book, not a piece of art, and doesn't belong in the collection.
]
for name, slug, bio, pieces in NEW_ARTISTS:
    a = new_artist(name, slug, bio, pieces[0]["site_image"])
    a["pieces"] = pieces
    artists[name] = a
    order.append(name)

json.dump(data, open(f"{SCRATCH}/master_final.json", "w"), indent=2)
print("done. new artist count:", len(order))
