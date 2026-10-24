"""交付包的前端覆盖必须兼容 dist 已随源码入库的布局。"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import build_release


class StageFrontendTest(unittest.TestCase):
    def test_overwrites_dist_already_present_from_git_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source" / "dist"
            source.mkdir(parents=True)
            (source / "index.html").write_text("current build", encoding="utf-8")
            existing = root / "stage" / "web" / "dist"
            existing.mkdir(parents=True)
            (existing / "index.html").write_text("archived build", encoding="utf-8")
            with patch.object(build_release, "FRONTEND_DIST", source):
                build_release.stage_frontend(root / "stage")
            self.assertEqual((existing / "index.html").read_text(encoding="utf-8"),
                             "current build")
class ManifestTest(unittest.TestCase):
    def test_manifest_uses_partition_migration_semantics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.lance").mkdir()
            (root / "parsed").mkdir()
            provider = {"embed_base_url": "https://example.invalid/v1",
                        "embed_model": "example-model", "reranker_model": "example-rerank"}
            with patch.object(build_release.bundle, "provider_block", return_value=provider), \
                 patch.object(build_release.bundle, "_chunk_count", return_value=1), \
                 patch.object(build_release, "_git_rev", return_value="test-commit"):
                build_release.write_manifest(root, 1)
            text = (root / "MANIFEST.txt").read_text(encoding="utf-8")
            self.assertIn("vec_meta", text)
            self.assertIn("--rebuild-vectors", text)
            self.assertNotIn("必须与上表一致", text)


if __name__ == "__main__":
    unittest.main()
