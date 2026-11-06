#!/usr/bin/env python3
"""Build the public ATASOY STORE image/video index from files on GitHub."""
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "store" / "media"
CATALOG = ROOT / "store" / "catalog.json"
DEST = ROOT / "store" / "media-index.json"
IMAGE = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".avif"}
VIDEO = {".mp4", ".webm", ".m4v"}
BASE = "https://raw.githubusercontent.com/mmustafatasoy/atasoyyazilim-downloads/main/"

def build_index():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    ids = {
        item["id"] for item in catalog.get("applications", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    apps = {}
    for app_id in sorted(ids):
        folder = MEDIA / app_id
        if not folder.is_dir():
            continue
        entries = []
        # Numeric filenames can control gallery ordering (01, 02, 03...).
        for file in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
            if not file.is_file() or file.is_symlink():
                continue
            suffix = file.suffix.lower()
            if suffix not in IMAGE | VIDEO or file.stat().st_size > 80_000_000:
                continue
            relative = file.relative_to(ROOT).as_posix()
            entries.append({
                "url": BASE + quote(relative, safe="/"),
                "type": "video" if suffix in VIDEO else "image",
            })
            if len(entries) == 30:
                break
        if entries:
            apps[app_id] = entries
    DEST.write_text(
        json.dumps({"schemaVersion": 1, "applications": apps},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("Indexed " + str(sum(len(v) for v in apps.values())) + " media files.")

if __name__ == "__main__":
    build_index()
