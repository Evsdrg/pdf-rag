"""关系检索评测器的关键行为测试。

只测**评测器自身的判定逻辑**(指标口径、身份约束、条件错配、坏标注拒绝),
不依赖真实索引内容,也不用网络。真实数据面的结论由
`python tools/eval_relations.py --validate-only` 与实际跑分给出。
"""
import json
import unittest
from pathlib import Path

from tools import eval_relations as er

ROOT = Path(__file__).resolve().parent.parent


def make_dataset(questions):
    return {"version": 1, "questions": questions}


def q(qid, category, targets, **kw):
    d = {"id": qid, "category": category, "query": qid + " query", "targets": targets}
    d.update(kw)
    return d


def t(file, page, literals, **kw):
    d = {"file": file, "page": page, "literals": literals}
    d.update(kw)
    return d


class FakeTable:
    """最小表替身:只提供 eval_relations 用到的搜索接口。"""

    def __init__(self, pages, models=None):
        # pages: {file: {page: text}};models: {file: model_no}
        self.pages = pages
        self.models = models or {}

    def count_rows(self):
        return sum(len(v) for v in self.pages.values())

    def _rows(self, file=None):
        out = []
        for fname, pmap in self.pages.items():
            if file is not None and fname != file:
                continue
            for page, text in pmap.items():
                out.append({"file": fname, "page": page - 1, "text": text,
                            "model_no": self.models.get(fname)})
        return out

    def search(self, *args, **kwargs):
        table = self

        class Result:
            def __init__(self, rows):
                self._rows = rows

            def where(self, clause):
                file = clause.split("file = '", 1)[1].split("'", 1)[0]
                return Result(table._rows(file))

            def select(self, cols):
                return self

            def limit(self, n):
                return self

            def to_list(self):
                return self._rows

        return Result(table._rows())


class NormTest(unittest.TestCase):
    def test_separator_tolerant_literal_matching(self):
        self.assertTrue(er.has_all("500 Ω and VDD APC", ["500Ω"]))
        self.assertTrue(er.has_all("500Ω and VDD APC", ["500 Ω"]))
        self.assertTrue(er.has_all("VDD APC", ["VDD_APC"]))
        self.assertFalse(er.has_all("500 mA", ["500Ω"]))
        self.assertFalse(er.has_all("500Ω", ["500Ω", "250Ω"]))


class SummaryTest(unittest.TestCase):
    def test_metrics_use_documented_denominators(self):
        # 2 题:第一题两个 target 全覆盖;第二题一个覆盖一个没覆盖。
        records = [
            {"id": "Q1", "category": "condition", "query": "q",
             "targets": [], "all_targets_page_covered": True, "all_targets_snippet_covered": False,
             "target_recall": 1.0, "snippet_coverage": 0.5,
             "condition_misassociation": 1, "wrong_variant_hit": 0, "wrong_variant_hits": 0,
             "additional_page_reads": 2, "candidates": 10, "degraded": [], "hits": []},
            {"id": "Q2", "category": "variant", "query": "q",
             "targets": [], "all_targets_page_covered": False, "all_targets_snippet_covered": False,
             "target_recall": 0.5, "snippet_coverage": 0.0,
             "condition_misassociation": 0, "wrong_variant_hit": 1, "wrong_variant_hits": 1,
             "additional_page_reads": 0, "candidates": 30, "degraded": [], "hits": []},
        ]
        s = er.summarize(records, [10, 30])["summary"]
        self.assertEqual(s["questions"], 2)
        self.assertEqual(s["all_target_evidence_coverage"], 50.0)   # 1/2
        self.assertEqual(s["mean_target_recall"], 75.0)            # (100 + 50)/2
        self.assertEqual(s["identity_constrained_snippet_coverage"], 25.0)  # (50 + 0)/2
        self.assertEqual(s["condition_misassociation_events"], 1)
        self.assertEqual(s["wrong_variant_hit_rate"], 50.0)        # 1 hit / 2 questions
        self.assertEqual(s["additional_page_reads"], 2)
        self.assertEqual(s["candidates_p50"], 20)
        self.assertEqual(s["candidates_p95"], 30)

    def test_by_category_breakdown_sums_to_whole(self):
        records = [
            {"id": "Q1", "category": "condition", "query": "q", "targets": [],
             "all_targets_page_covered": True, "all_targets_snippet_covered": True,
             "target_recall": 1.0, "snippet_coverage": 1.0,
             "condition_misassociation": 2, "wrong_variant_hit": 0, "wrong_variant_hits": 0,
             "additional_page_reads": 1, "candidates": 5, "degraded": [], "hits": []},
            {"id": "Q2", "category": "variant", "query": "q", "targets": [],
             "all_targets_page_covered": False, "all_targets_snippet_covered": False,
             "target_recall": 0.0, "snippet_coverage": 0.0,
             "condition_misassociation": 0, "wrong_variant_hit": 1, "wrong_variant_hits": 3,
             "additional_page_reads": 0, "candidates": 9, "degraded": [], "hits": []},
        ]
        s = er.summarize(records, [5, 9])["summary"]
        self.assertEqual(s["by_category"]["condition"]["questions"], 1)
        self.assertEqual(s["by_category"]["variant"]["wrong_variant_hits"], 3)
        self.assertEqual(
            sum(v["questions"] for v in s["by_category"].values()), s["questions"])


class ValidateTest(unittest.TestCase):
    """坏标注必须被拒绝,不能静默计为成功。"""

    def build(self):
        pages = {
            "cat/A.pdf": {1: "Max Output Current 500 mA and 1117-3.3 row 13.2 mV under IO=10mA"},
            "cat/B.pdf": {2: "RDS(ON) 9.5 mΩ VGS=-10V"},
        }
        table = FakeTable(pages, {"cat/A.pdf": "AAA", "cat/B.pdf": "BBB"})
        ds = make_dataset([
            q("OK1", "multi_model_compare", [
                t("cat/A.pdf", 1, ["500", "mA"], model_no="AAA"),
                t("cat/B.pdf", 2, ["9.5"], model_no="BBB"),
            ]),
        ])
        return ds, table

    def test_good_annotation_passes(self):
        ds, table = self.build()
        self.assertEqual(er.validate(ds, table), [])

    def test_missing_literal_is_rejected(self):
        ds, table = self.build()
        ds["questions"][0]["targets"][0]["literals"] = ["500", "999"]
        errs = er.validate(ds, table)
        self.assertTrue(errs)
        self.assertIn("999", errs[0][0])

    def test_wrong_page_is_rejected(self):
        ds, table = self.build()
        ds["questions"][0]["targets"][0]["page"] = 99
        errs = er.validate(ds, table)
        self.assertTrue(errs)
        self.assertIn("物理页", errs[0][0])

    def test_ambiguous_file_fragment_is_rejected(self):
        ds, table = self.build()
        ds["questions"][0]["targets"][0]["file"] = "cat/"
        errs = er.validate(ds, table)
        self.assertTrue(errs)
        self.assertIn("匹配 2 个索引文件", errs[0][0])

    def test_model_no_mismatch_is_rejected(self):
        ds, table = self.build()
        ds["questions"][0]["targets"][0]["model_no"] = "WRONG"
        errs = er.validate(ds, table)
        self.assertTrue(errs)
        self.assertIn("model_no", errs[0][0])

    def test_multi_model_requires_distinct_models(self):
        # 两个 target 指向不同文件但同一型号:multi_model 类别下必须判为坏标注。
        pages = {"cat/A.pdf": {1: "500 mA"}, "cat/B.pdf": {2: "9.5 mΩ"}}
        table = FakeTable(pages, {"cat/A.pdf": "AAA", "cat/B.pdf": "AAA"})
        ds = make_dataset([
            q("OK1", "multi_model_compare", [
                t("cat/A.pdf", 1, ["500"], model_no="AAA"),
                t("cat/B.pdf", 2, ["9.5"], model_no="AAA"),
            ]),
        ])
        errs = er.validate(ds, table)
        self.assertTrue(errs)
        self.assertIn("型号必须互不相同", errs[0][0])

    def test_cond_not_on_page_is_rejected(self):
        ds, table = self.build()
        ds["questions"][0]["targets"][0]["cond"] = ["IO=1A"]
        errs = er.validate(ds, table)
        self.assertTrue(errs)
        self.assertIn("条件词", errs[0][0])

    def test_wrong_value_must_exist_on_page(self):
        ds, table = self.build()
        ds["questions"][0]["targets"][0]["wrong"] = ["250mA"]
        errs = er.validate(ds, table)
        self.assertTrue(errs)
        self.assertIn("错值标注", errs[0][0])

    def test_forbidden_variant_must_resolve_and_contain_literals(self):
        pages = {"cat/A.pdf": {1: "500 mA"}, "cat/B.pdf": {2: "9.5 mΩ"},
                 "cat/C.pdf": {3: "42 mΩ"}}
        table = FakeTable(pages, {"cat/A.pdf": "AAA", "cat/B.pdf": "BBB"})
        ds = make_dataset([
            q("OK1", "multi_model_compare", [
                t("cat/A.pdf", 1, ["500"], model_no="AAA"),
                t("cat/B.pdf", 2, ["9.5"], model_no="BBB"),
            ], forbidden_variants=[{"file": "cat/C.pdf", "page": 3, "literals": ["42"]}]),
        ])
        self.assertEqual(er.validate(ds, table), [])
        ds["questions"][0]["forbidden_variants"][0]["literals"] = ["7mΩ"]
        errs = er.validate(ds, table)
        self.assertTrue(errs)
        self.assertIn("缺字面值", errs[0][0])

    def test_forbidden_variant_must_not_be_a_target_file(self):
        ds, table = self.build()
        ds["questions"][0]["forbidden_variants"] = [
            {"file": "cat/A.pdf", "page": 1, "literals": ["500"]},
        ]
        errs = er.validate(ds, table)
        self.assertTrue(errs)
        self.assertIn("同一文件", errs[0][0])

    def test_target_count_outside_two_to_three_is_rejected(self):
        ds, table = self.build()
        ds["questions"][0]["targets"] = ds["questions"][0]["targets"][:1]
        errs = er.validate(ds, table)
        self.assertTrue(errs)
        self.assertIn("2-3", errs[0][0])

    def test_duplicate_question_id_is_rejected(self):
        ds, table = self.build()
        ds["questions"].append(ds["questions"][0])
        errs = er.validate(ds, table)
        self.assertTrue(any("重复" in m for m, _ in errs))


class DatasetShapeTest(unittest.TestCase):
    """真实标注文件的结构性约束(内容真实性由 --validate-only 负责)。"""

    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "eval_relations.json").read_text(encoding="utf-8"))

    def test_thirty_two_questions_in_four_equal_categories(self):
        qs = self.data["questions"]
        self.assertEqual(len(qs), 32)
        counts = {}
        for item in qs:
            counts[item["category"]] = counts.get(item["category"], 0) + 1
        self.assertEqual(set(counts), set(er.CATEGORIES))
        self.assertEqual(sorted(counts.values()), [8, 8, 8, 8])

    def test_each_question_has_two_or_three_targets(self):
        for item in self.data["questions"]:
            self.assertTrue(2 <= len(item["targets"]) <= 3, item["id"])

    def test_targets_carry_file_page_literals_and_model(self):
        for item in self.data["questions"]:
            for target in item["targets"]:
                self.assertTrue(target["file"])
                self.assertIsInstance(target["page"], int)
                self.assertTrue(target["literals"])
                self.assertTrue(target["model_no"])

    def test_multi_model_targets_use_distinct_models(self):
        for item in self.data["questions"]:
            if item["category"] != "multi_model_compare":
                continue
            models = [x["model_no"] for x in item["targets"]]
            self.assertEqual(len(set(models)), len(models), item["id"])

    def test_variant_questions_declare_forbidden_variants(self):
        for item in self.data["questions"]:
            if item["category"] != "variant":
                continue
            self.assertTrue(item.get("forbidden_variants"), item["id"])

    def test_condition_questions_declare_wrong_values(self):
        for item in self.data["questions"]:
            if item["category"] != "condition":
                continue
            self.assertTrue(any(x.get("wrong") for x in item["targets"]), item["id"])


class NetworkGuardTest(unittest.TestCase):
    def test_block_network_raises_on_connect(self):
        import socket
        from unittest.mock import patch
        with patch.object(socket.socket, "connect"), patch.object(socket.socket, "connect_ex"), \
             patch.object(socket, "create_connection"), patch.object(socket, "create_server"):
            er.block_network()
            sock = socket.socket()
            try:
                with self.assertRaises(er.NetworkBlocked):
                    sock.connect(("127.0.0.1", 80))
            finally:
                sock.close()


class EvaluateLogicTest(unittest.TestCase):
    """评测判定逻辑:身份约束、条件错配、额外读页代理。"""

    def setUp(self):
        self.pages = {
            # 正确文件:第 1 页含 13.2 mV 与错误档位 7.2 mV
            "cat/right.pdf": {1: "Load Regulation 1117-3.3 13.2 mV 1117-1.8 7.2 mV IO=10mA"},
            # 错误文件:字面值完全相同,但不是目标身份
            "cat/wrong.pdf": {1: "Load Regulation 1117-3.3 13.2 mV 1117-1.8 7.2 mV IO=10mA"},
            # 兄弟变体手册
            "cat/sibling.pdf": {1: "Load Regulation 1117-3.3 13.2 mV"},
        }
        self.table = FakeTable(self.pages, {"cat/right.pdf": "AAA", "cat/wrong.pdf": "BBB",
                                            "cat/sibling.pdf": "AAA"})
        self.ds = make_dataset([
            q("Q1", "condition", [
                t("cat/right.pdf", 1, ["1117-3.3", "13.2"], model_no="AAA",
                  cond=["IO=10mA"], wrong=["7.2"]),
            ], forbidden_variants=[{"file": "cat/sibling.pdf", "page": 1, "literals": ["13.2"]}]),
        ])

    def _run(self, hits):
        original = er.search
        er.search = lambda *a, **k: hits
        try:
            return er.evaluate(self.ds, self.table, mode="fts", no_rerank=True, k=5)
        finally:
            er.search = original

    def test_same_literal_in_wrong_file_does_not_count_as_hit(self):
        hits = [{"file": "cat/wrong.pdf", "page": 1, "snippet": "1117-3.3 13.2 mV 7.2 mV"}]
        rec = self._run(hits)["records"][0]
        self.assertFalse(rec["all_targets_page_covered"])
        self.assertEqual(rec["target_recall"], 0.0)
        self.assertEqual(rec["snippet_coverage"], 0.0)

    def test_correct_file_hit_covers_target(self):
        hits = [{"file": "cat/right.pdf", "page": 1, "snippet": "1117-3.3 13.2 mV IO=10mA"}]
        rec = self._run(hits)["records"][0]
        self.assertTrue(rec["all_targets_page_covered"])
        self.assertTrue(rec["all_targets_snippet_covered"])
        self.assertEqual(rec["target_recall"], 1.0)

    def test_same_value_on_wrong_page_is_not_target_coverage(self):
        hits = [{"file": "cat/right.pdf", "page": 2, "snippet": "1117-3.3 13.2 mV IO=10mA"}]
        rec = self._run(hits)["records"][0]
        self.assertFalse(rec["all_targets_snippet_covered"])
        self.assertFalse(rec["all_targets_page_covered"])

    def test_missing_condition_does_not_count_as_complete_snippet(self):
        hits = [{"file": "cat/right.pdf", "page": 1, "snippet": "1117-3.3 13.2 mV"}]
        rec = self._run(hits)["records"][0]
        self.assertFalse(rec["all_targets_snippet_covered"])
        self.assertEqual(rec["additional_page_reads"], 1)

    def test_page_covered_but_snippet_missing_counts_as_additional_page_read(self):
        # 命中正确文件与正确页,但片段里没有 13.2 —— 整页有,需要再读这一页。
        hits = [{"file": "cat/right.pdf", "page": 1, "snippet": "unrelated filler text"}]
        rec = self._run(hits)["records"][0]
        self.assertTrue(rec["all_targets_page_covered"])
        self.assertFalse(rec["all_targets_snippet_covered"])
        self.assertEqual(rec["additional_page_reads"], 1)

    def test_condition_misassociation_needs_wrong_value_and_missing_cond(self):
        # 片段含正确值 + 错值,但缺条件词 -> 记一次字面共现错配
        hits = [{"file": "cat/right.pdf", "page": 1, "snippet": "1117-3.3 13.2 mV 1117-1.8 7.2 mV"}]
        rec = self._run(hits)["records"][0]
        self.assertEqual(rec["condition_misassociation"], 1)

    def test_no_misassociation_when_condition_word_present(self):
        hits = [{"file": "cat/right.pdf", "page": 1,
                 "snippet": "1117-3.3 13.2 mV 1117-1.8 7.2 mV IO=10mA"}]
        rec = self._run(hits)["records"][0]
        self.assertEqual(rec["condition_misassociation"], 0)

    def test_wrong_variant_hit_counted(self):
        hits = [{"file": "cat/sibling.pdf", "page": 1, "snippet": "1117-3.3 13.2 mV"},
                {"file": "cat/right.pdf", "page": 1, "snippet": "1117-3.3 13.2 mV"}]
        rec = self._run(hits)["records"][0]
        self.assertEqual(rec["wrong_variant_hit"], 1)


if __name__ == "__main__":
    unittest.main()
