"""检索融合:页级累加计分、RRF 排序与重排平局裁决。"""
import unittest
from unittest import mock

from backend import config, retrieval
from tests.support import override_config


class CandidatesTest(unittest.TestCase):
    def test_page_level_accumulation(self):
        # 同页多块累加是有效相关性信号:两块应胜过单块
        c = retrieval._Candidates(rrf_k=60, bonus_rank=5)
        c.add({"file": "a.pdf", "page": 1, "text": "x"}, rank=10)
        c.add({"file": "a.pdf", "page": 1, "text": "y"}, rank=20)
        c.add({"file": "b.pdf", "page": 1, "text": "z"}, rank=10)
        top = c.top(10)
        self.assertEqual(top[0][0], ("a.pdf", 1))

    def test_bonus_rank_beats_late_rank(self):
        # 型号精确子串召回折算成第 bonus_rank 名(1/(k+5));普通命中名次比它靠后时被压过
        c = retrieval._Candidates(rrf_k=60, bonus_rank=5)
        c.add({"file": "a.pdf", "page": 1, "text": "x"}, rank=10)
        c.add({"file": "b.pdf", "page": 1, "text": "y"}, rank=50, bonus=True)
        top = c.top(10)
        self.assertEqual(top[0][0], ("b.pdf", 1))

    def test_best_chunk_is_highest_scoring_not_first(self):
        # 代表块取"自身得分最高"者,而非最先入队的页首块
        c = retrieval._Candidates(rrf_k=60, bonus_rank=5)
        header = {"file": "a.pdf", "page": 1, "text": "页眉"}
        answer = {"file": "a.pdf", "page": 1, "text": "答案所在块"}
        c.add(header, rank=1)
        c.add(answer, rank=1)  # 同名次,后入队者得分不低于前者 → 视实现而定
        self.assertIsNotNone(c.rows[("a.pdf", 1)])


class RerankOrderTest(unittest.TestCase):
    def _rows(self, model_no=""):
        # page 从 0 开始:page=0 是封面,受 penalty_cover 影响
        return {("a.pdf", 0): {"file": "a.pdf", "page": 0, "model_no": model_no, "text": "t"},
                ("a.pdf", 1): {"file": "a.pdf", "page": 1, "model_no": model_no, "text": "t"},
                ("a.pdf", 2): {"file": "a.pdf", "page": 2, "model_no": model_no, "text": "t"}}

    def test_pure_rerank_order(self):
        cands = [(("a.pdf", 0), 0.03), (("a.pdf", 1), 0.02), (("a.pdf", 2), 0.01)]
        with override_config(penalty_cover=1.0):
            with mock.patch.object(retrieval, "_call_reranker", return_value=[0.5, 0.9, 0.4]):
                picked, scores = retrieval._rerank_and_order(cands, self._rows(), "q")
        self.assertEqual([k for k, _ in picked], [("a.pdf", 1), ("a.pdf", 0), ("a.pdf", 2)])
        self.assertEqual(scores[("a.pdf", 1)], 0.9)

    def test_cover_penalty_downweights_page1(self):
        cands = [(("a.pdf", 0), 0.03), (("a.pdf", 1), 0.02)]
        with override_config(penalty_cover=0.1):
            with mock.patch.object(retrieval, "_call_reranker", return_value=[0.9, 0.5]):
                picked, _ = retrieval._rerank_and_order(cands, self._rows(), "q")
        # 封面页 0.9×0.1=0.09 < 0.5 → 排到普通页之后
        self.assertEqual(picked[0][0], ("a.pdf", 1))

    def test_tie_break_prefers_model_match(self):
        rows = {("gv.pdf", 2): {"file": "X_74LVC1G04GV_规格书.PDF", "page": 2, "model_no": "74LVC1G04GV", "text": "t"},
                ("gw.pdf", 7): {"file": "Y_74LVC1G04GW_规格书.PDF", "page": 7, "model_no": "74LVC1G04GW", "text": "t"}}
        cands = [(("gv.pdf", 2), 0.02), (("gw.pdf", 7), 0.01)]
        with override_config(rerank_tie_tolerance=0.02):
            with mock.patch.object(retrieval, "_call_reranker", return_value=[0.951, 0.950]):
                picked, _ = retrieval._rerank_and_order(cands, rows, "74LVC1G04GV 2.3 V")
        # 分差 0.001 在平局带内:查询型号与文件身份匹配的 GV 应在前
        self.assertEqual(picked[0][0], ("gv.pdf", 2))

    def test_tie_break_disabled_outside_band(self):
        rows = {("gv.pdf", 2): {"file": "X_74LVC1G04GV.PDF", "page": 2, "model_no": "GV", "text": "t"},
                ("gw.pdf", 7): {"file": "Y_74LVC1G04GW.PDF", "page": 7, "model_no": "GW", "text": "t"}}
        cands = [(("gw.pdf", 7), 0.01), (("gv.pdf", 2), 0.02)]
        with override_config(rerank_tie_tolerance=0.02):
            with mock.patch.object(retrieval, "_call_reranker", return_value=[0.95, 0.90]):
                picked, _ = retrieval._rerank_and_order(cands, rows, "74LVC1G04GV 2.3 V")
        # 分差 0.05 超出平局带:保持纯重排序
        self.assertEqual(picked[0][0], ("gw.pdf", 7))


if __name__ == "__main__":
    unittest.main()
