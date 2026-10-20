"""路径边界防护:resolve_under 是所有读页/原文端点的安全闸门。"""
import os
import tempfile
import unittest

from backend import doc_utils


class ResolveUnderTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.root, "01_x"))
        with open(os.path.join(self.root, "01_x", "a.pdf"), "w") as f:
            f.write("x")

    def test_normal_relative_path(self):
        full = doc_utils.resolve_under(self.root, "01_x/a.pdf")
        self.assertEqual(full, os.path.realpath(os.path.join(self.root, "01_x", "a.pdf")))

    def test_root_itself_allowed(self):
        self.assertEqual(doc_utils.resolve_under(self.root, "."), os.path.realpath(self.root))

    def test_absolute_path_rejected(self):
        # os.path.join 遇绝对路径会丢前缀,不设防等于任意文件读
        with self.assertRaises(FileNotFoundError):
            doc_utils.resolve_under(self.root, "/etc/passwd")

    def test_dotdot_traversal_rejected(self):
        with self.assertRaises(FileNotFoundError):
            doc_utils.resolve_under(self.root, "../../etc/passwd")

    def test_mixed_separator_traversal_rejected(self):
        # Linux 把 ..\..\x 当普通文件名,归一为 / 后必须按穿越拦截(fail-closed)
        with self.assertRaises(FileNotFoundError):
            doc_utils.resolve_under(self.root, "..\\..\\x")

    def test_backslash_separator_normalized(self):
        # 语料路径是正斜杠;Windows 风格输入归一后应能命中同一文件
        full = doc_utils.resolve_under(self.root, "01_x\\a.pdf")
        self.assertEqual(full, os.path.realpath(os.path.join(self.root, "01_x", "a.pdf")))

    def test_deep_inside_still_allowed(self):
        os.makedirs(os.path.join(self.root, "a", "b", "c"))
        full = doc_utils.resolve_under(self.root, "a/b/c/../..")
        self.assertTrue(full.startswith(os.path.realpath(self.root) + os.sep))


if __name__ == "__main__":
    unittest.main()
