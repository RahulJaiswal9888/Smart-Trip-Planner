"""Run once with internet: python download_images.py
Saves photos into the 'images' folder. Existing files are skipped."""
import json
import re
import ssl
import urllib.parse
import urllib.request
from pathlib import Path

from destination_data import DESTINATION_DATA
from image_service import IMAGE_DIR, find_file, slug

API = "https://en.wikipedia.org/api/rest_v1/page/summary/"
HEADERS = {"User-Agent": "WanderlyStudentProject/1.0 (educational project)"}

try:
    import certifi
    CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    CTX = ssl.create_default_context()


def page_image_url(title):
    url = API + urllib.parse.quote(title, safe="")
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15, context=CTX) as r:
        data = json.load(r)
    original = data.get("originalimage") or {}
    thumb = data.get("thumbnail") or {}
    if thumb.get("source") and original.get("width", 0) >= 1000:
        return re.sub(r"/\d+px-", "/1000px-", thumb["source"], count=1)
    return original.get("source") or thumb.get("source")


def download(url, target_base):
    ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".jpg"
    target = target_base.with_suffix(ext)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
        target.write_bytes(r.read())
    return target


def fetch(destination, name, wiki_titles, override):
    if find_file(destination, name):
        print(f"  skip     {name} (already saved)")
        return True
    folder = IMAGE_DIR / slug(destination)
    folder.mkdir(parents=True, exist_ok=True)
    base = folder / slug(name)

    candidates = [override] if override else []
    errors = []
    for title in wiki_titles:
        try:
            u = page_image_url(title)
            if u:
                candidates.append(u)
                break
        except Exception as exc:
            errors.append(f"{title}: {type(exc).__name__}: {exc}")
    for url in candidates:
        try:
            saved = download(url, base)
            print(f"  OK       {name} -> {saved.relative_to(IMAGE_DIR.parent)}")
            return True
        except Exception as exc:
            errors.append(f"download: {type(exc).__name__}: {exc}")

    print(f"  MISSING  {name}")
    for e in errors:
        print(f"           {e}")
    print(f"           -> save your own photo as: images/{slug(destination)}/{slug(name)}.jpg")
    return False


missing = 0
for dest, d in DESTINATION_DATA.items():
    print(f"\n{dest}")
    if not fetch(dest, "hero", d["hero_wiki"], d.get("hero_image", "")):
        missing += 1
    for a in d["attractions"]:
        if not fetch(dest, a["name"], a["wiki"], a.get("image", "")):
            missing += 1
print(f"\nDone. Missing photos: {missing}")