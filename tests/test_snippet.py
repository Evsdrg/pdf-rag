"""片段窗口:当前准确率瓶颈(snippet@1)所在的定位逻辑。"""
import unittest

from backend import retrieval
from tests.support import override_config

# 页眉 + 查询词在前 + 答案值在 1300 字符处的典型表格块
LONG_TEXT = "W25Q32JW 手册\n" + "目录与概述内容。\n" * 100 + "供电电压范围 2.7V 至 3.6V\n" + "尾部说明。\n" * 20


class MakeSnippetTest(unittest.TestCase):
    def test_short_text_returned_whole(self):
        self.assertEqual(retrieval.make_snippet("短文本", "查询", width=600), "短文本")

    def test_window_positions_on_query_terms_not_block_head(self):
        with override_config(snippet_width=600, window_stride_div=4, num_unit_bonus=1.5):
            sn = retrieval.make_snippet(LONG_TEXT, "供电电压 范围", width=600)
        self.assertIn("供电电压", sn)
        self.assertIn("3.6", sn)

    def test_no_hit_falls_back_to_head(self):
        with override_config(snippet_width=150, window_stride_div=4, num_unit_bonus=1.5):
            sn = retrieval.make_snippet("A" * 500 + "\n" + "B" * 100, "毫不相关的词", width=150)
        self.assertTrue(sn.startswith("A"))


class ModelTokensTest(unittest.TestCase):
    def test_extracts_mixed_alnum_tokens(self):
        self.assertIn("w25q32jw", [t.lower() for t in retrieval._model_tokens("W25Q32JW 供电电压")])

    def test_min_length(self):
        # 太短的 token 不算型号
        self.assertEqual(retrieval._model_tokens("ab 12 供电"), [])

    def test_requires_digit_and_letter(self):
        # 纯字母或纯数字不算型号
        self.assertEqual(retrieval._model_tokens("abcdef 123456 供电"), [])


class ScoreWindowTest(unittest.TestCase):
    def test_number_unit_bonus_applies(self):
        with override_config(num_unit_bonus=1.5):
            with_unit = retrieval._score_window("输出 3.6V", ["输出"], set())
            without = retrieval._score_window("输出", ["输出"], set())
        self.assertGreater(with_unit, without)

    def test_model_tokens_excluded_from_window_scoring(self):
        # 型号 token 每页页眉都有,参与定位会让页眉窗口压过答案窗口(实测回归)
        with override_config(num_unit_bonus=0.0):
            sc = retrieval._score_window("W25Q32JW W25Q32JW W25Q32JW", ["w25q32jw"], {"w25q32jw"})
        self.assertEqual(sc, 0.0)


if __name__ == "__main__":
    unittest.main()
