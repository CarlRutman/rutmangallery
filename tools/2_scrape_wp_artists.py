import json, re, sys, time
import urllib.request
from bs4 import BeautifulSoup, NavigableString

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")

def get_main(url):
    html = fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    return soup.find("main"), soup

ARTIST_PAGES = {
    "jay-jbon-bonadio": "https://rutman.gallery/jay-jbon-bonadio-gallery/",
    "michael-cheval": "https://rutman.gallery/michael-cheval/",
    "autumn-de-forest": "https://rutman.gallery/autumn-de-forest/",
    "kre8": "https://rutman.gallery/kre8/",
}

def bio_blocks(main):
    """Return ordered content blocks from Artist: ... through end of Key Elements list."""
    blocks = []
    started = False
    for el in main.find_all(["h1","h2","h3","h4","p","ul","ol"], recursive=True):
        txt = el.get_text(" ", strip=True)
        if el.name == "h1" and started:
            break  # hit "Our Collection" h1
        if el.name == "p" and txt.startswith("Artist:"):
            started = True
            blocks.append({"type":"artist_line","text":txt})
            continue
        if not started:
            continue
        if el.name in ("h3","h4"):
            blocks.append({"type":"heading","text":txt})
        elif el.name == "p":
            if txt == "":
                continue
            blocks.append({"type":"p","text":txt})
        elif el.name in ("ul","ol"):
            items = [li.get_text(" ", strip=True) for li in el.find_all("li")]
            blocks.append({"type":"list","items":items})
    return blocks

def artwork_blocks(main):
    blocks = []
    for el in main.find_all(["h1","p","ul","ol"], recursive=True):
        txt = el.get_text(" ", strip=True)
        if el.name == "h1":
            continue
        if el.name == "p":
            if txt == "":
                continue
            blocks.append({"type":"p","text":txt})
        elif el.name in ("ul","ol"):
            items = [li.get_text(" ", strip=True) for li in el.find_all("li")]
            blocks.append({"type":"list","items":items})
    return blocks

def scrape_artist(slug, url):
    main, soup = get_main(url)
    title = main.find("h1")
    headshot = None
    hs = main.find("img", src=re.compile(r"headshot", re.I))
    if hs: headshot = hs.get("src")
    bc = main.find("video-js")
    brightcove = None
    if bc:
        brightcove = {"video_id": bc.get("data-video-id"), "account": bc.get("data-account"), "player": bc.get("data-player")}
    social = {}
    official_site = None
    for a in main.find_all("a", href=True):
        href = a["href"]; text = a.get_text(strip=True).lower()
        if "facebook.com" in href: social["facebook"] = href
        elif "instagram.com" in href: social["instagram"] = href
        elif "parkwestgallery.com" in href: social["parkwest"] = href
        elif href.startswith("http") and "rutman.gallery" not in href and ("official" in text or "site" in text):
            social["official_site"] = href

    artworks = []
    seen = set()
    for a in main.find_all("a", href=True):
        href = a["href"].replace("http://","https://")
        text = a.get_text(strip=True)
        if not text: continue
        if "rutman.gallery" in href and href.rstrip("/") != url.rstrip("/") and href not in seen:
            seen.add(href)
            artworks.append({"title": text, "url": href})

    artworks_full = []
    for aw in artworks:
        print(f"  scraping artwork {aw['url']}...", file=sys.stderr)
        am, _ = get_main(aw["url"])
        title_el = am.find("h1")
        img = am.find("img", src=re.compile(r"/wp-content/uploads/"))
        artworks_full.append({
            "url": aw["url"],
            "title": title_el.get_text(strip=True) if title_el else aw["title"],
            "short_title": aw["title"],
            "img": img.get("src") if img else None,
            "blocks": artwork_blocks(am),
        })
        time.sleep(0.2)

    return {
        "slug": slug,
        "url": url,
        "name": title.get_text(strip=True) if title else slug,
        "headshot": headshot,
        "brightcove": brightcove,
        "social": social,
        "bio_blocks": bio_blocks(main),
        "artworks": artworks_full,
    }

out = {}
for slug, url in ARTIST_PAGES.items():
    print(f"scraping artist {slug}...", file=sys.stderr)
    out[slug] = scrape_artist(slug, url)

with open("artists_full.json", "w") as f:
    json.dump(out, f, indent=2)
print("done", file=sys.stderr)
