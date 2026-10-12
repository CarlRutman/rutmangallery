import json, os, re, shutil, unicodedata

SCRATCH = "/private/tmp/claude-501/-Users-admin-Desktop-Claude-rutman-gallery/00b58d26-3cf4-403a-aa52-82ccb1057652/scratchpad"
SITE = "/Users/admin/Desktop/Claude/rutman.gallery"
IMAGES = os.path.join(SITE, "images")

data = json.load(open(f"{SCRATCH}/master.json"))

def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

for canon, m in data["artists"].items():
    artist_slug = m["slug"]
    for p in m["pieces"]:
        piece_slug = slugify(p["title"])
        ext = ".jpg"
        dest_name = f"{artist_slug}--{piece_slug}{ext}"
        dest_path = os.path.join(IMAGES, dest_name)

        src = None
        if p.get("image") and p["image"].startswith("http"):
            # already-downloaded WP image; find local copy by basename
            base = p["image"].split("/")[-1]
            local = os.path.join(IMAGES, base)
            if os.path.exists(local):
                src = local
        elif p.get("image") and os.path.exists(p["image"] or ""):
            src = p["image"]
        if not src and p.get("local_source_image") and os.path.exists(p["local_source_image"]):
            src = p["local_source_image"]

        if src:
            shutil.copyfile(src, dest_path)
            p["site_image"] = f"images/{dest_name}"
        else:
            p["site_image"] = None
            print(f"MISSING IMAGE: {canon} / {p['title']}")

    # homepage thumbnail for artist card -- reuse first piece's image if possible
    if m["pieces"] and m["pieces"][0].get("site_image"):
        m["homepage_site_image"] = m["pieces"][0]["site_image"]
    else:
        # fall back to original homepage thumbnail
        base = m["homepage_img"].split("/")[-1]
        local = os.path.join(IMAGES, base)
        dest_name = f"{m['slug']}--homepage.jpg"
        dest_path = os.path.join(IMAGES, dest_name)
        if os.path.exists(local):
            shutil.copyfile(local, dest_path)
            m["homepage_site_image"] = f"images/{dest_name}"
        else:
            m["homepage_site_image"] = None
            print(f"MISSING HOMEPAGE IMAGE: {canon}")

    # headshot
    if m.get("headshot"):
        base = m["headshot"].split("/")[-1]
        local = os.path.join(IMAGES, base)
        if os.path.exists(local):
            dest_name = f"{m['slug']}--headshot{os.path.splitext(base)[1]}"
            shutil.copyfile(local, os.path.join(IMAGES, dest_name))
            m["headshot_site_image"] = f"images/{dest_name}"

json.dump(data, open(f"{SCRATCH}/master_final.json", "w"), indent=2)
print("done")
