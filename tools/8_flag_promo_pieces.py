import json

SCRATCH = "/private/tmp/claude-501/-Users-admin-Desktop-Claude-rutman-gallery/00b58d26-3cf4-403a-aa52-82ccb1057652/scratchpad"
p = f"{SCRATCH}/master_final.json"
d = json.load(open(p))
artists = d["artists"]

# Pieces Clarity's order history explicitly tags "(Promo)" or "Free Gift -" --
# bundled bonus items from an auction purchase, not a deliberately collected piece.
PROMO_PIECES = [
    ("Jim Warren", "Love is in the Air"),
    ("Michael Godard", "Dali's Muse"),
    ("Kre8", "Colorful Notes"),
    ("Daniel Wall", "Splendid Life"),
    ("Matt Beyrer", "On the Water"),
    ("Itzchak Tarkay", "Daloris #3"),
    ("Ashton Howard", "Upon a Night's Dream"),
    ("Alfred Gockel", "Atlantis"),          # "Free Gift - Atlantis"
    ("Csaba Markus", "Triumph of Venus"),   # "Free Gift - Triumph of Venus"
]
for canon, title in PROMO_PIECES:
    for piece in artists[canon]["pieces"]:
        if piece["title"] == title:
            piece["promo"] = True

# Requested by the user directly (2026-08-28) -- not Clarity-tagged "(Promo)", but
# moved into the same homepage section by request. Each is that artist's only piece,
# so this moves the whole artist.
USER_REQUESTED_MOVE = [
    "Slava Ilyayev", "Victor Spahn", "Zamy Steynovitz", "Slava Brodinsky", "Linda Le Kinff",
]
for canon in USER_REQUESTED_MOVE:
    for piece in artists[canon]["pieces"]:
        piece["promo"] = True

json.dump(d, open(p, "w"), indent=2)

# An artist goes into the homepage's "Promotional Pieces" section (see
# 6_build_site.py's is_promo_only()) only when EVERY piece they have is
# flagged promo -- an artist with a mix of real + promo pieces stays in the
# main collection.
for canon in d["order"]:
    pieces = artists[canon]["pieces"]
    if pieces and all(pc.get("promo") for pc in pieces):
        print("promo-only artist:", canon)
