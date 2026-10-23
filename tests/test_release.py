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


if __name__ == "__main__":
    unittest.main()
