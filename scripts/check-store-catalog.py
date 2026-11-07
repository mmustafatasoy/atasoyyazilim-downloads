#!/usr/bin/env python3
"""Validate ATASOY STORE catalog structure without exposing private sources."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
catalog = json.loads((ROOT / "store/catalog.json").read_text(encoding="utf-8"))
assert catalog.get("schemaVersion") == 1, "Unsupported catalog schema"
apps = catalog.get("applications")
assert isinstance(apps, list) and 0 < len(apps) <= 80, "Invalid app catalog size"
ids = set()
packages = set()
trusted = {"atasoyyazilim-downloads", "EymenTv", "Gelirgider"}
configured = 0
for a in apps:
    app_id = a.get("id")
    assert isinstance(app_id, str) and re.fullmatch(r"[a-z0-9-]{2,48}", app_id), "Invalid ID"
    assert app_id not in ids, "Duplicate app ID: " + app_id
    ids.add(app_id)
    pkg = a.get("packageName")
    if pkg:
        assert re.fullmatch(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*){1,8}", pkg), "Invalid package"
        assert pkg not in packages, "Duplicate package: " + pkg
        packages.add(pkg)
    assert isinstance(a.get("name"), str) and a["name"].strip(), "Missing name"
    assert isinstance(a.get("description"), str) and a["description"].strip(), "Missing description"
    assert a.get("status") in {"published", "test", "in-progress"}, "Unknown status"
    repo = a.get("releaseRepo")
    if repo:
        assert repo in trusted, "Unapproved or private APK release repository"
        assert re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", a.get("tagPrefix", "")), "Invalid release tagPrefix"
        assert a.get("assetName") or a.get("assetPrefix"), "Release APK selector missing"
        configured += 1
    else:
        assert not a.get("downloadUrl"), "No release source must mean no download"
    if a.get("iconUrl"):
        assert a["iconUrl"].startswith("https://"), "Unsafe icon URL"
media = json.loads((ROOT / "store/media-index.json").read_text(encoding="utf-8"))
assert media.get("schemaVersion") == 1 and isinstance(media.get("applications"), dict)
assert set(media["applications"]).issubset(ids), "Orphan media index entries"
print(f"Catalog OK: {len(apps)} apps, {configured} published release selectors, "
      f"{len(apps)-configured} awaiting public APKs; {len(media['applications'])} media folders.")
