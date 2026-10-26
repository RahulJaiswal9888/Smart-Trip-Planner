"""Run: python check_images.py  - shows which attractions found a photo."""
from destination_data import DESTINATION_DATA
from image_service import resolve

missing = 0
for dest, d in DESTINATION_DATA.items():
    print(f"\n{dest}")
    items = [("(hero)", d["hero_wiki"], d.get("hero_image", ""))]
    items += [(a["name"], a["wiki"], a.get("image", "")) for a in d["attractions"]]
    for name, titles, override in items:
        url = resolve(titles, override)
        if url:
            print(f"  OK       {name}")
        else:
            missing += 1
            print(f"  MISSING  {name}  -> add a direct URL in destination_data.py ('image')")
print(f"\nDone. Missing photos: {missing}")