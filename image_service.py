"""Loads photographs from the local 'images' folder. No internet needed.

Layout:
  images/<destination>/hero.jpg
  images/<destination>/<attraction>.jpg      (.jpeg, .png and .webp also work)
Names are lowercase with underscores, e.g. images/manali/hadimba_temple.jpg.
The original flat image collection is supported as well.
"""
import base64
from io import BytesIO
import re
from pathlib import Path

import streamlit as st
from PIL import Image, ImageOps

from destination_data import DESTINATION_DATA

IMAGE_DIR = Path(__file__).resolve().parent / "images"
EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
FLAT_IMAGE_FILES = {
    ("Manali", "hero"): "Manali_cover.jpg",
    ("Manali", "Hadimba Temple"): "hidimba.jpg",
    ("Manali", "Solang Valley"): "solang.jpg",
    ("Manali", "Atal Tunnel"): "atulTunnel.jpg",
    ("Manali", "Old Manali"): "oldManali.jpg",
    ("Shimla", "The Ridge"): "ridge.jpg",
    ("Shimla", "Mall Road"): "mall road.jpg",
    ("Shimla", "Jakhoo Temple"): "jakhu.jpg",
    ("Shimla", "Kufri"): "kufri.jpg",
    ("Jaipur", "Hawa Mahal"): "hawamahal.jpg",
    ("Jaipur", "Amber Fort"): "amberfort.jpg",
    ("Jaipur", "City Palace"): "citypalace.jpg",
    ("Jaipur", "Jantar Mantar"): "jantar mantar.jpg",
    ("Amritsar", "Golden Temple"): "golden temple.jpg",
    ("Amritsar", "Jallianwala Bagh"): "Jalianwala bag.jpg",
    ("Amritsar", "Wagah Border"): "wagah border.jpg",
    ("Amritsar", "Partition Museum"): "Partition Museum.jpg",
    ("Udaipur", "City Palace"): "city palace udaipur.jpg",
    ("Udaipur", "Lake Pichola"): "Pichola Lake.jpg",
    ("Udaipur", "Sajjangarh Palace"): "Sajjangarh Fort.jpg",
    ("Udaipur", "Jag Mandir"): "jag mandir.jpg",
    ("Rishikesh", "Laxman Jhula"): "laxman jhula.jpg",
    ("Rishikesh", "Ram Jhula"): "ram jhula.jpg",
    ("Rishikesh", "Triveni Ghat"): "triveni ghat.jpg",
    ("Rishikesh", "Beatles Ashram"): "Beatles Ashram.jpg",
}


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def find_file(destination, name):
    folder = IMAGE_DIR / slug(destination)
    for ext in EXTENSIONS:
        path = folder / (slug(name) + ext)
        if path.is_file():
            return path

    flat_name = FLAT_IMAGE_FILES.get((destination, name))
    if flat_name:
        path = IMAGE_DIR / flat_name
        if path.is_file():
            return path
    return None


@st.cache_data(show_spinner=False)
def _to_data_uri(path_str, modified_time):
    path = Path(path_str)
    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source)
        image.thumbnail((1600, 1200), Image.Resampling.LANCZOS)
        output = BytesIO()
        extension = path.suffix.lower()
        if extension in (".jpg", ".jpeg"):
            image.convert("RGB").save(output, format="JPEG", quality=82, optimize=True)
        elif extension == ".png":
            image.save(output, format="PNG", optimize=True)
        else:
            image.save(output, format="WEBP", quality=82, method=6)
    encoded = base64.b64encode(output.getvalue()).decode("ascii")
    return f"data:{MIME[path.suffix.lower()]};base64,{encoded}"


def _load(destination, name):
    path = find_file(destination, name)
    if not path:
        return None
    try:
        return _to_data_uri(str(path), path.stat().st_mtime)
    except Exception:
        return None


def _destination_hero(destination):
    image = _load(destination, "hero")
    if image:
        return image

    for attraction in DESTINATION_DATA[destination]["attractions"]:
        image = _load(destination, attraction["name"])
        if image:
            return image
    return None


def hero_images():
    return {name: _destination_hero(name) for name in DESTINATION_DATA}


def attraction_images(destination):
    result = {"__hero__": _destination_hero(destination)}
    for att in DESTINATION_DATA[destination]["attractions"]:
        result[att["name"]] = _load(destination, att["name"])
    return result