#!/usr/bin/env python3
"""Register or update a verified public ATASOY STORE release in the catalog.

Only tags store-<app-id>-v<version> from THIS public repository are accepted.
The APK must be signed and its package/version extracted with Android aapt.
Optional release assets: icon.png, 01.png, 02.webp, 03.mp4 (up to 30).
Optional editorial metadata: store/submissions/<app-id>.json.
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

TAG = re.compile(r"^store-(?P<id>[a-z0-9-]{2,48})-v(?P<version>[0-9]+(?:\.[0-9]+){0,2}(?:[-+][A-Za-z0-9.-]+)?)$")
PKG = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*){1,8}$")
HASH = re.compile(r"^[a-f0-9]{64}$")
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif", ".svg"}
VIDEO_EXT = {".mp4", ".webm", ".m4v"}
ASSET_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,110}$")
OWNER_REPO = "mmustafatasoy/atasoyyazilim-downloads"
BASE = "https://github.com/" + OWNER_REPO + "/releases/download/"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def asset_url(release, asset):
    name = asset.get("name", "")
    require(bool(ASSET_NAME.fullmatch(name)), "Unsafe asset filename")
    url = asset.get("browser_download_url", "")
    expected = BASE + release["tag_name"] + "/" + name
    require(url == expected and asset.get("state") == "uploaded",
            "Release asset does not belong to the verified public repository")
    require(isinstance(asset.get("size"), int) and asset["size"] > 0,
            "Empty release asset")
    return url


def read_badging(text):
    first = next((line for line in text.splitlines() if line.startswith("package: ")), "")
    fields = dict(re.findall(r"([A-Za-z][A-Za-z0-9_]*)='([^']*)'", first))
    package = fields.get("name", "")
    version = fields.get("versionName", "")
    code = fields.get("versionCode", "")
    require(bool(PKG.fullmatch(package)), "APK package name is invalid")
    require(code.isdigit() and int(code) > 0, "APK versionCode is invalid")
    require(bool(version), "APK versionName is absent")
    label_match = re.search(r"^application-label:'([^']*)'", text, re.MULTILINE)
    label = (label_match.group(1) if label_match else "").strip()
    return package, version, int(code), label


def release_text(value):
    lines = []
    for line in str(value or "").splitlines():
        line = re.sub(r"^[#>\s*-]+", "", line).strip()
        if line:
            lines.append(line)
    return re.sub(r"\s+", " ", " ".join(lines)).strip()[:220]


def clean_meta(data):
    require(isinstance(data, dict), "Submission must be a JSON object")
    fields = ("name", "description", "category", "platform", "icon", "accent",
              "pageUrl", "featured")
    require(set(data).issubset(set(fields)), "Unknown submission field")
    clean = {}
    for key in fields:
        if key not in data:
            continue
        value = data[key]
        if key == "featured":
            require(isinstance(value, bool), "featured must be true/false")
        else:
            require(isinstance(value, str), key + " must be text")
            value = value.strip()
            require(len(value) <= (220 if key == "description" else 75),
                    key + " is too long")
        clean[key] = value
    if "accent" in clean:
        require(re.fullmatch(r"#[0-9a-fA-F]{6}", clean["accent"]) is not None,
                "accent must be #RRGGBB")
    if "pageUrl" in clean:
        parsed = urlsplit(clean["pageUrl"])
        require(parsed.scheme == "https" and parsed.hostname in
                {"atasoyyazilim.com", "www.atasoyyazilim.com"} and
                parsed.username is None and parsed.password is None,
                "pageUrl must be the official website")
    return clean


def register(root, tag, release, badging, apk, signer):
    match = TAG.fullmatch(tag)
    require(match is not None, "Only store-<app-id>-v<version> release tags are accepted")
    app_id, version = match.group("id"), match.group("version")
    require(release.get("tag_name") == tag and release.get("draft") is False,
            "Release tag/draft mismatch")
    assets = release.get("assets")
    require(isinstance(assets, list), "Missing GitHub release assets")
    apks = [a for a in assets if str(a.get("name", "")).lower().endswith(".apk")]
    require(len(apks) == 1 and apks[0]["name"] == "app-release.apk",
            "Exactly one signed APK named app-release.apk is required")
    apk_asset = apks[0]
    asset_url(release, apk_asset)
    file_sha = hashlib.sha256(apk.read_bytes()).hexdigest()
    declared = apk_asset.get("digest") or ""
    if declared:
        require(declared.lower() == "sha256:" + file_sha, "APK SHA-256 does not match GitHub")
    require(apk_asset["size"] == apk.stat().st_size, "APK file size mismatch")
    signer = signer.strip().lower().replace(":", "")
    require(bool(HASH.fullmatch(signer)), "APK signing certificate SHA-256 missing")
    package, apk_version, version_code, label = read_badging(badging)
    require(apk_version == version, "Release tag version must match APK versionName")

    catalog_file = root / "store" / "catalog.json"
    catalog = json.loads(catalog_file.read_text(encoding="utf-8"))
    require(catalog.get("schemaVersion") == 1, "Unsupported catalog schema")
    apps = catalog.get("applications")
    require(isinstance(apps, list), "Invalid applications list")
    existing = next((x for x in apps if x.get("id") == app_id), None)
    require(existing is not None or len(apps) < 80, "Store catalog limit reached")
    if existing is not None:
        require(existing.get("releaseRepo") == "atasoyyazilim-downloads"
                and existing.get("tagPrefix") == "store-" + app_id + "-v"
                and existing.get("assetName") == "app-release.apk",
                "Existing manually managed app ID cannot be taken over")
        require(existing.get("packageName") == package,
                "APK package identity changed; refusing automatic update")
        prior = existing.get("signerSha256")
        require(not prior or prior == signer,
                "APK signing certificate changed; refusing automatic update")
        prior_code = existing.get("androidVersionCode")
        require(not isinstance(prior_code, int) or version_code >= prior_code,
                "Android versionCode must not decrease")

    submission_file = root / "store" / "submissions" / (app_id + ".json")
    meta = clean_meta(json.loads(submission_file.read_text(encoding="utf-8"))) \
        if submission_file.is_file() else {}
    raw_name = release.get("name", "").strip()
    name = meta.get("name") or (raw_name if raw_name != tag else "") or label or app_id
    desc = meta.get("description") or release_text(release.get("body")) \
        or "Atasoy Yazılım Android uygulaması"
    name = name[:75]
    derived_icon = "".join(w[0].upper() for w in name.split() if w)[:3] or "A"

    entry = dict(existing) if existing is not None else {
        "id": app_id,
        "name": name,
        "description": desc,
        "category": "Uygulama",
        "platform": "Android Telefon",
        "status": "published",
        "icon": derived_icon,
        "accent": "#2F5BFF",
        "pageUrl": "https://atasoyyazilim.com",
        "featured": False
    }
    if existing is None:
        entry["name"], entry["description"] = name, desc
    entry.update(meta)
    entry["releaseRepo"] = "atasoyyazilim-downloads"
    entry["tagPrefix"] = "store-" + app_id + "-v"
    entry["assetName"] = "app-release.apk"
    entry["packageName"] = package
    entry["signerSha256"] = signer
    entry["androidVersionCode"] = version_code
    entry["status"] = "test" if release.get("prerelease") else "published"

    media = []
    icon_url = None
    for asset in sorted(assets, key=lambda a: a.get("name", "").lower()):
        filename = asset.get("name", "")
        if filename == "app-release.apk":
            continue
        suffix = Path(filename).suffix.lower()
        if suffix not in IMAGE_EXT | VIDEO_EXT:
            continue
        if asset.get("size", 0) > 80_000_000:
            continue
        url = asset_url(release, asset)
        if filename.lower() in {"icon.png", "icon.jpg", "icon.jpeg", "icon.webp"}:
            require(asset["size"] <= 5_000_000, "App logo exceeds 5 MB")
            icon_url = url
            continue
        media.append({"url": url, "type": "video" if suffix in VIDEO_EXT else "image"})
        if len(media) == 30:
            break
    if media:
        entry["media"] = media
    if icon_url:
        entry["iconUrl"] = icon_url
    else:
        # A manually uploaded icon can be used without changing Android app code.
        for ext in (".png", ".webp", ".jpg", ".jpeg"):
            if (root / "store" / "icons" / (app_id + ext)).is_file():
                entry["iconUrl"] = (
                    "https://raw.githubusercontent.com/" + OWNER_REPO +
                    "/main/store/icons/" + app_id + ext
                )
                break

    if existing is None:
        apps.append(entry)
    else:
        existing.clear()
        existing.update(entry)
    catalog["updatedAt"] = date.today().isoformat()
    catalog_file.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
    print("Registered %s: %s %s (%s), versionCode=%d, %d media"
          % (app_id, name, version, package, version_code, len(media)))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--release-json", type=Path, required=True)
    parser.add_argument("--badging", type=Path, required=True)
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--signer-sha256", required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        register(args.root, args.tag,
                 json.loads(args.release_json.read_text(encoding="utf-8")),
                 args.badging.read_text(encoding="utf-8"), args.apk,
                 args.signer_sha256)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        sys.exit("Registration blocked: " + str(exc))


if __name__ == "__main__":
    main()
