#!/usr/bin/env python3
"""EYMEN Store katalog tarayıcısı: Releases içindeki APK'ları okur, catalog.json üretir."""
import glob, hashlib, json, os, pathlib, re, subprocess, tempfile, time, urllib.request, zipfile
from PIL import Image

ROOT = pathlib.Path(__file__).parent
BASE = "https://raw.githubusercontent.com/mmustafatasoy/atasoyyazilim-downloads/store-feed/store/"
SDK = os.environ.get("ANDROID_HOME", "/usr/local/lib/android/sdk")
AAPT = sorted(glob.glob(f"{SDK}/build-tools/*/aapt2"))[-1]
SIGNER = sorted(glob.glob(f"{SDK}/build-tools/*/apksigner"))[-1]
TOKEN = os.environ.get("GH_TOKEN", "")

def api(path):
    req = urllib.request.Request("https://api.github.com/" + path, headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {TOKEN}"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)

def releases(repo, cache={}):
    if repo not in cache:
        rows = api(f"repos/{repo}/releases?per_page=50")
        cache[repo] = sorted([r for r in rows if not r["draft"]], key=lambda r: r["published_at"], reverse=True)
    return cache[repo]

def inspect(asset):
    with tempfile.TemporaryDirectory() as d:
        apk = pathlib.Path(d) / "a.apk"
        urllib.request.urlretrieve(asset["browser_download_url"], apk)
        out = subprocess.run([AAPT, "dump", "badging", str(apk)], capture_output=True, text=True, check=True).stdout
        pkg = re.search(r"package: name='([^']+)' versionCode='(\d+)' versionName='([^']*)'", out)
        sdk = re.search(r"(?:minSdkVersion|sdkVersion):'(\d+)'", out)
        label = re.search(r"application-label:'([^']*)'", out)
        signer = subprocess.run([SIGNER, "verify", "--print-certs", str(apk)], capture_output=True, text=True).stdout
        tv_only = "leanback-launchable-activity" in out and "launchable-activity:" not in out.replace("leanback-launchable-activity", "")
        icons = re.findall(r"application-icon-(\d+):'([^']+)'", out)
        icon_bytes = None
        for _, path in sorted(icons, key=lambda x: int(x[0]), reverse=True):
            if path.endswith((".png", ".webp")):
                icon_bytes = zipfile.ZipFile(apk).read(path)
                break
        return {
            "packageName": pkg[1], "versionCode": int(pkg[2]), "versionName": pkg[3], "minSdk": int(sdk[1]) if sdk else 26,
            "label": label[1] if label else "", "tvOnly": tv_only, "sha256": hashlib.sha256(apk.read_bytes()).hexdigest(),
            "debugSigned": "CN=Android Debug" in signer, "iconBytes": icon_bytes,
        }

def clean_notes(body):
    notes = []
    for line in (body or "").splitlines():
        if not re.match(r"^\s*(?:[-*•]|\d+[.)])\s+", line):
            continue
        line = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s+|[*`_]+", "", line).strip()
        if 4 <= len(line) and not re.search(r"https?:|sha-?256|kaynak:", line, re.I):
            notes.append(line[:90])
        if len(notes) == 4:
            break
    return notes

def visuals(entry, src):
    key = src.get("iconFrom", src["id"])
    if (ROOT / "icons" / f"{key}.png").exists():
        entry["icon"] = f"{BASE}icons/{key}.png"
    key = src.get("shotsFrom", src["id"])
    shots = []
    for f in sorted((ROOT / "shots" / key).glob("*.webp")):
        w, h = Image.open(f).size
        shots.append({"url": f"{BASE}shots/{key}/{f.name}", "w": w, "h": h})
    entry["shots"] = shots

def from_release(src, prev):
    pattern = re.compile(src["tag"])
    asset_re = re.compile(src.get("asset", r"\.apk$"), re.I)
    rows = [r for r in releases(src["repo"]) if pattern.search(r["tag_name"]) and (src.get("prerelease") or not r["prerelease"])]
    rows.sort(key=lambda r: ([int(n) for n in re.findall(r"\d+", r["tag_name"])], r["published_at"]), reverse=True)
    for rel in rows:
        asset = next((a for a in rel["assets"] if asset_re.search(a["name"]) and a["state"] == "uploaded"), None)
        if asset is None:
            continue
        total = sum(a["download_count"] for r in rows for a in r["assets"] if a["name"] == asset["name"])
        if prev and prev.get("assetId") == asset["id"]:
            info = {k: prev[k] for k in ("packageName", "versionCode", "versionName", "minSdk", "sha256", "debugSigned", "tvOnly", "label") if k in prev}
        else:
            info = inspect(asset)
            icon = info.pop("iconBytes", None)
            if icon and not (ROOT / "icons" / f"{src['id']}.png").exists():
                (ROOT / "icons" / f"{src['id']}.png").write_bytes(icon)
        info.update(assetId=asset["id"], sizeBytes=asset["size"], apkUrl=asset["browser_download_url"], updatedAt=rel["published_at"], downloads=total,
                    notes=clean_notes(rel.get("body")), status="test" if rel["prerelease"] or info.get("debugSigned") else "ready")
        return info
    return None

def build():
    conf = json.loads((ROOT / "apps.json").read_text(encoding="utf8"))
    path = ROOT / "catalog.json"
    old = json.loads(path.read_text(encoding="utf8")) if path.exists() else {"apps": []}
    prev = {a["id"]: a for a in old["apps"]}
    sources = list(conf["apps"])
    known = [(s.get("repo"), re.compile(s["tag"])) for s in sources if "tag" in s]
    disc = conf.get("discover") or {}
    seen = set()
    for rel in releases(disc["repo"]) if disc else []:
        tag = rel["tag_name"]
        key = re.sub(r"-v\d.*$", "", tag)
        if key in disc.get("exclude", []) or key in seen or any(repo == disc["repo"] and rx.search(tag) for repo, rx in known):
            continue
        seen.add(key)
        for a in [x for x in rel["assets"] if x["name"].lower().endswith(".apk")]:
            sources.append({"id": key, "name": "", "tagline": "Yeni uygulama", "platform": "phone", "category": "Yeni", "tone": "#17224A", "repo": disc["repo"],
                            "tag": "^" + re.escape(key) + r"-v\d", "asset": "^" + re.escape(a["name"]) + "$", "prerelease": True, "auto": True})
            break
    apps = []
    for src in sources:
        entry = {k: src.get(k) for k in ("id", "name", "tagline", "platform", "category", "tone")}
        entry.update(page=src.get("page", ""), highlights=src.get("highlights", []), featured=bool(src.get("featured")), hidden=bool(src.get("hidden")))
        try:
            if src.get("soon"):
                entry.update(status="soon", packageName="", versionCode=0, versionName="", minSdk=26, sizeBytes=0, sha256="", apkUrl="", updatedAt="", downloads=0, notes=[])
            else:
                info = from_release(src, prev.get(src["id"]))
                if info is None:
                    print(f"ATLANDI  {src['id']}: uygun sürüm yok")
                    continue
                entry.update(info)
                if src.get("auto"):
                    entry["name"] = info.get("label") or src["id"]
                    if info.get("tvOnly"):
                        entry["platform"] = "tv"
                entry.pop("tvOnly", None)
            visuals(entry, src)
            apps.append(entry)
            print(f"TAMAM    {src['id']}: {entry.get('packageName')} {entry.get('versionName')} ({entry.get('versionCode')}) {entry.get('status')}")
        except Exception as e:
            print(f"HATA     {src['id']}: {e}")
            if src["id"] in prev:
                apps.append(prev[src["id"]])
    apps.sort(key=lambda a: a.get("updatedAt") or "", reverse=True)
    body = {"schema": conf["schema"], "minStoreVersionCode": conf["minStoreVersionCode"], "requireAccount": conf["requireAccount"], "apps": apps}
    if {k: v for k, v in old.items() if k != "generatedAt"} != body:
        body = {"generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **body}
        path.write_text(json.dumps(body, ensure_ascii=False, indent=1) + "\n", encoding="utf8")
        print("catalog.json güncellendi")
    else:
        print("değişiklik yok")

if __name__ == "__main__":
    build()
