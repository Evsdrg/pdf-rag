"""file 过滤:LIKE 字面量化与分隔符归一(下推与 Python 兜底两侧行为必须一致)。"""
import unittest
from unittest import mock

from backend import retrieval
from tests.support import override_config


class LikeLiteralTest(unittest.TestCase):
    def test_underscore_escaped(self):
        self.assertEqual(retrieval._like_literal("a_b"), "a\\_b")

    def test_percent_escaped(self):
        self.assertEqual(retrieval._like_literal("a%b"), "a\\%b")

    def test_backslash_normalized_to_slash(self):
        self.assertEqual(retrieval._like_literal("01_x\\y.PDF"), "01\\_x/y.PDF")


class ApplyFilterTest(unittest.TestCase):
    def _cond(self, file):
        q = mock.MagicMock()
        out = retrieval._apply_filter(q, None, file)
        self.assertIsNot(out, q)          # 有 file 条件时必须经过 .where() 下推
        return q.where.call_args[0][0]    # 下推的 SQL 条件串

    def test_contains_escaped_pattern(self):
        cond = self._cond("BH1750FVI_TR")
        self.assertIn("BH1750FVI\\_TR", cond)
        self.assertIn("LIKE", cond)

    def test_normal_path_keeps_slash(self):
        cond = self._cond("01_传感器/BH1750")
        self.assertIn("01\\_传感器/BH1750", cond)

    def test_single_quote_escaped(self):
        cond = self._cond("it's")
        self.assertIn("it''s", cond)


class AcceptsTest(unittest.TestCase):
    ROW = {"file": "01_传感器/BH1750FVI-TR.PDF", "category": "01_传感器"}

    def test_substring_match(self):
        self.assertTrue(retrieval._accepts(self.ROW, None, "BH1750"))

    def test_backslash_input_normalized(self):
        self.assertTrue(retrieval._accepts(self.ROW, None, "01_传感器\\BH1750"))

    def test_literal_underscore_does_not_wildcard(self):
        # 与 SQL 下推的字面语义一致:_ 不当单字符通配符
        self.assertFalse(retrieval._accepts(self.ROW, None, "BH1750FVI_TR"))

    def test_category_mismatch(self):
        self.assertFalse(retrieval._accepts(self.ROW, "02_存储", None))


if __name__ == "__main__":
    unittest.main()
