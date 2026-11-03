#!/usr/bin/env python3
"""Copy verified, released public EYMEN OS APKs to this repo's GitHub Releases.

Only whitelisted public source URLs from manifest.json; verify byte count and
SHA-256 before publishing. Never alter prior assets without review.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import urllib.request

HERE = Path(__file__).resolve().parent
manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
source = "https://github.com/mmaapps/eymenostv/releases/download/"
destination = os.environ["DEST_REPOSITORY"]
assert destination == "mmustafatasoy/atasoyyazilim-downloads"
assert manifest["source_repository"] == "mmaapps/eymenostv"
versions = manifest["archived_versions"]
assert len(versions) == 7 and sum(len(x["assets"]) for x in versions) == 14


def gh(*args, check=True):
    return subprocess.run(["gh", *args], text=True, capture_output=True, check=check)


for row in versions:
    version = row["version"]
    tag = f"eymen-os-v{version}"
    assert row["source_tag"] == f"v{version}"
    print(f"\n::group::EYMEN OS TV {version}", flush=True)
    # Check existing assets; never silently replace an existing public binary.
    found = gh("api", f"repos/{destination}/releases/tags/{tag}", check=False)
    if found.returncode == 0:
        old = json.loads(found.stdout)
        existing = {item["name"]: item for item in old.get("assets", [])}
        if all(asset["name"] in existing
               and existing[asset["name"]]["size"] == asset["bytes"]
               and existing[asset["name"]].get("digest") == "sha256:" + asset["sha256"]
               for asset in row["assets"]):
            print(f"Already mirrored: {tag}", flush=True)
            print("::endgroup::", flush=True)
            continue
        raise SystemExit(f"Existing destination release differs: {tag}; refusing overwrite")
    with tempfile.TemporaryDirectory(prefix=f"eymen-{version}-") as tmp:
        download_paths = []
        for asset in row["assets"]:
            name = asset["name"]
            assert name in ("EYMEN-OS-TV.apk", "EYMEN-Kurulum.apk")
            assert asset["source_url"] == f"{source}v{version}/{name}"
            path = Path(tmp) / name
            req = urllib.request.Request(asset["source_url"], headers={"User-Agent": "Atasoy-Yazilim-Release-Mirror/1.0"})
            hasher = hashlib.sha256()
            size = 0
            with urllib.request.urlopen(req, timeout=120) as response, path.open("wb") as out:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    size += len(chunk)
                    out.write(chunk)
                    hasher.update(chunk)
            assert size == asset["bytes"], f"Unexpected byte count in {tag}/{name}"
            assert hasher.hexdigest() == asset["sha256"], f"SHA-256 mismatch in {tag}/{name}"
            print(f"Verified {tag}/{name}: {size} bytes, SHA-256 {hasher.hexdigest()}", flush=True)
            download_paths.append(str(path))
        notes = (
            f"# EYMEN OS TV {version}\n\n"
            f"**Orijinal yayın tarihi:** {row['source_published_at'][:10]}  \n"
            "Android 11 / Vestel 17MB170 hedef cihaz. "
            "Telefon ve televizyon APK dosyaları ayrı sunulur.\n\n"
            "## Orijinal sürüm açıklaması\n\n" + row["notes"] + "\n\n"
            "## Dosya doğrulama (SHA-256)\n\n"
            + "\n".join(f"- \`{a['name']}\`: \`{a['sha256']}\`" for a in row["assets"])
            + "\n\n**Kaynak:** Orijinal herkese açık EYMEN OS TV GitHub Releases APK dosyalarıdır. "
              "Bu arşiv kaynak kod içermez. Kurulum için TV modelinin uyumluluğunu kontrol edin.\n"
        )
        notes_file = Path(tmp) / "RELEASE_NOTES.md"
        notes_file.write_text(notes, encoding="utf-8")
        cmd = [
            "release", "create", tag, *download_paths,
            "--repo", destination, "--target", "main",
            "--title", f"EYMEN OS TV v{version} | TV + Telefon APK",
            "--notes-file", str(notes_file), "--latest=false",
        ]
        gh(*cmd)
        published = json.loads(gh("api", f"repos/{destination}/releases/tags/{tag}").stdout)
        published_assets = {a["name"]: a for a in published["assets"]}
        for asset in row["assets"]:
            remote = published_assets.get(asset["name"])
            assert remote and remote["size"] == asset["bytes"], f"Upload missing: {tag}/{asset['name']}"
            if remote.get("digest"):
                assert remote["digest"] == "sha256:" + asset["sha256"], f"Remote digest differs: {tag}"
        print(f"Published verified archive release: {tag}", flush=True)
    print("::endgroup::", flush=True)
print("\nAll seven EYMEN OS versions are published and verified.", flush=True)
