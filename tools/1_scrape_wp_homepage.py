import json, re, sys, time
import urllib.request
from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")

def get_main(html):
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    return main, soup

def clean_text(el):
    return el.get_text("\n", strip=True) if el else ""

results = {}

# ---- Homepage ----
html = fetch("https://rutman.gallery/")
main, soup = get_main(html)
h3s = main.find_all("h3")
imgs = [img for img in main.find_all("img") if "/wp-content/uploads/" in (img.get("src") or "")]
home_intro = main.find("p")
artists = []
for h3, img in zip(h3s, imgs):
    m = re.match(r"^(.*?)\s*\((\d+)\)\s*$", h3.get_text(strip=True))
    name, count = (m.group(1), m.group(2)) if m else (h3.get_text(strip=True), "")
    link = None
    img_a = img.find_parent("a", href=True)
    if img_a:
        link = img_a["href"].replace("http://", "https://")
    else:
        h3_a = h3.find("a", href=True)
        if h3_a:
            link = h3_a["href"].replace("http://", "https://")
    artists.append({"name": name, "count": count, "img": img.get("src"), "link": link})

results["homepage"] = {
    "intro_paragraphs": [p.get_text(" ", strip=True) for p in main.find_all("p")[:2]],
    "artists": artists,
}

with open("home_data.json", "w") as f:
    json.dump(results, f, indent=2)
print(json.dumps(results, indent=2))
