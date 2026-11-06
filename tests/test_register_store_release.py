"""Local smoke tests for safe automatic registration (no network needed)."""
import hashlib
import json
import runpy
import tempfile
import unittest
from pathlib import Path

SCRIPT = runpy.run_path(str(Path(__file__).resolve().parents[1] /
                            "scripts" / "register-store-release.py"))
register = SCRIPT["register"]
read_badging = SCRIPT["read_badging"]
BASE = SCRIPT["BASE"]
SIGNER = "a" * 64


class StoreRegistrationTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        (self.root / "store").mkdir()
        (self.root / "store" / "catalog.json").write_text(
            json.dumps({"schemaVersion": 1, "applications": []}), encoding="utf-8")
        self.apk = self.root / "app-release.apk"
        self.apk.write_bytes(b"signed-test-apk-fixture")
        self.tag = "store-ornek-app-v1.0.0"
        self.badging = ("package: name='com.atasoy.ornek' versionCode='10' "
                        "versionName='1.0.0'\napplication-label:'Örnek Uygulama'")
        self.release = self.make_release(self.tag)

    def make_release(self, tag):
        return {
            "tag_name": tag, "name": "Örnek Uygulama",
            "body": "Uygulama açıklaması ve özellikleri.",
            "draft": False, "prerelease": False,
            "assets": [
                {"name": "app-release.apk", "state": "uploaded",
                 "size": self.apk.stat().st_size,
                 "digest": "sha256:" + hashlib.sha256(self.apk.read_bytes()).hexdigest(),
                 "browser_download_url": BASE + tag + "/app-release.apk"},
                {"name": "icon.png", "state": "uploaded", "size": 1024,
                 "browser_download_url": BASE + tag + "/icon.png"},
                {"name": "01.png", "state": "uploaded", "size": 1024,
                 "browser_download_url": BASE + tag + "/01.png"},
                {"name": "02.mp4", "state": "uploaded", "size": 8096,
                 "browser_download_url": BASE + tag + "/02.mp4"}
            ]
        }

    def registered(self):
        return json.loads(
            (self.root / "store" / "catalog.json").read_text(encoding="utf-8")
        )["applications"][0]

    def test_apk_badging(self):
        self.assertEqual(
            read_badging(self.badging),
            ("com.atasoy.ornek", "1.0.0", 10, "Örnek Uygulama")
        )

    def test_first_release_generates_entire_record(self):
        register(self.root, self.tag, self.release, self.badging, self.apk, SIGNER)
        app = self.registered()
        self.assertEqual(app["name"], "Örnek Uygulama")
        self.assertEqual(app["description"], "Uygulama açıklaması ve özellikleri.")
        self.assertEqual(app["packageName"], "com.atasoy.ornek")
        self.assertEqual(app["tagPrefix"], "store-ornek-app-v")
        self.assertEqual(app["assetName"], "app-release.apk")
        self.assertEqual(app["androidVersionCode"], 10)
        self.assertEqual(len(app["media"]), 2)
        self.assertTrue(app["media"][1]["url"].endswith("02.mp4"))
        self.assertTrue(app["iconUrl"].endswith("icon.png"))

    def test_subsequent_version_updates_without_new_icon(self):
        register(self.root, self.tag, self.release, self.badging, self.apk, SIGNER)
        tag = "store-ornek-app-v1.0.1"
        release = self.make_release(tag)
        release["assets"] = release["assets"][:1]
        badge = self.badging.replace("versionCode='10'", "versionCode='11'") \
            .replace("versionName='1.0.0'", "versionName='1.0.1'")
        register(self.root, tag, release, badge, self.apk, SIGNER)
        app = self.registered()
        self.assertEqual(app["androidVersionCode"], 11)
        self.assertTrue(app["iconUrl"].endswith("v1.0.0/icon.png"))
        self.assertEqual(len(app["media"]), 2)

    def test_mismatched_apk_package_is_rejected(self):
        register(self.root, self.tag, self.release, self.badging, self.apk, SIGNER)
        second_tag = "store-ornek-app-v1.0.1"
        changed = self.badging.replace("com.atasoy.ornek", "com.evil.package") \
            .replace("versionName='1.0.0'", "versionName='1.0.1'") \
            .replace("versionCode='10'", "versionCode='11'")
        with self.assertRaisesRegex(ValueError, "package identity changed"):
            register(self.root, second_tag, self.make_release(second_tag),
                     changed, self.apk, SIGNER)

    def test_different_signer_is_rejected(self):
        register(self.root, self.tag, self.release, self.badging, self.apk, SIGNER)
        with self.assertRaisesRegex(ValueError, "signing certificate changed"):
            register(self.root, self.tag, self.release,
                     self.badging, self.apk, "b" * 64)

    def test_bad_digest_is_rejected(self):
        self.release["assets"][0]["digest"] = "sha256:" + ("0" * 64)
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            register(self.root, self.tag, self.release,
                     self.badging, self.apk, SIGNER)

    def test_manual_app_id_cannot_be_overwritten(self):
        original = {"id": "ornek-app", "releaseRepo": "EymenTv",
                    "packageName": "com.atasoy.ornek"}
        path = self.root / "store" / "catalog.json"
        path.write_text(json.dumps({"schemaVersion": 1,
                                    "applications": [original]}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "cannot be taken over"):
            register(self.root, self.tag, self.release,
                     self.badging, self.apk, SIGNER)

    def test_same_version_code_cannot_publish_a_new_version(self):
        register(self.root, self.tag, self.release, self.badging, self.apk, SIGNER)
        next_tag = "store-ornek-app-v1.0.1"
        badge = self.badging.replace("versionName='1.0.0'", "versionName='1.0.1'")
        with self.assertRaisesRegex(ValueError, "increase Android versionCode"):
            register(self.root, next_tag, self.make_release(next_tag), badge, self.apk, SIGNER)

    def test_duplicate_package_cannot_register_twice(self):
        path = self.root / "store" / "catalog.json"
        path.write_text(json.dumps({
            "schemaVersion": 1,
            "applications": [{
                "id": "another-app", "packageName": "com.atasoy.ornek",
                "releaseRepo": "atasoyyazilim-downloads"
            }]
        }), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "already belongs"):
            register(self.root, self.tag, self.release, self.badging, self.apk, SIGNER)

    def test_release_tag_must_match_apk(self):
        bad = self.make_release("store-ornek-app-v2.0.0")
        with self.assertRaisesRegex(ValueError, "tag version must match"):
            register(self.root, "store-ornek-app-v2.0.0", bad,
                     self.badging, self.apk, SIGNER)


if __name__ == "__main__":
    unittest.main()
