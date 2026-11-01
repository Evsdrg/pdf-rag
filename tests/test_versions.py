"""版本解析与同文档合并:多版本去重的核心,历史上出过 296 对误合并。"""
import unittest

from backend import doc_utils, ingest, retrieval


class VersionKeyTest(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(doc_utils.version_key(""), (0,))

    def test_numeric_versions_compare_numerically(self):
        # 字符串比较会把 V9 排在 V10 后面;必须按数字比较
        self.assertGreater(doc_utils.version_key("1.10"), doc_utils.version_key("1.9"))
        self.assertGreater(doc_utils.version_key("9"), doc_utils.version_key("1.2.3"))

    def test_letter_revision(self):
        self.assertGreater(doc_utils.version_key("RevD"), doc_utils.version_key(""))
        self.assertEqual(doc_utils.version_key("B")[0], 2)


class ParseVersionTest(unittest.TestCase):
    def test_v_forms(self):
        self.assertEqual(ingest.parse_version("W25Q32_V1.9_手册"), "1.9")
        self.assertEqual(ingest.parse_version("manual_V1.2.0"), "1.2.0")

    def test_rev_form(self):
        self.assertEqual(ingest.parse_version("规格书_RevD"), "D")
        self.assertEqual(ingest.parse_version("规格书 Rev. C"), "C")

    def test_missing(self):
        self.assertEqual(ingest.parse_version("无版本号手册"), "")


def row(file="a.pdf", md5="", model_no="", title="", text="x", version="", page=0):
    return {"file": file, "md5": md5, "model_no": model_no, "title": title,
            "text": text, "version": version, "page": page}


class SameDocumentTest(unittest.TestCase):
    def test_same_md5_same_document_even_if_model_differs(self):
        # 一份手册覆盖整个料号族:md5 相同必须合并,否则结果全是同一份手册
        self.assertTrue(retrieval._same_document([row(md5="m1")], [row(md5="m1", model_no="X")]))

    def test_different_model_never_merges(self):
        # 仅凭标题指纹会把不同型号并成一组(实测三份手册标题同为"主要特点")
        self.assertFalse(retrieval._same_document(
            [row(model_no="A", title="主要特点")],
            [row(model_no="B", title="主要特点")]))

    def test_same_model_title_or_text_does_not_prove_same_source(self):
        self.assertFalse(retrieval._same_document(
            [row(md5="supplier-a", model_no="A", title="手册 V1.0", text="same text")],
            [row(md5="supplier-b", model_no="A", title="手册 V2.0", text="same text")]))

    def test_no_model_no_merge(self):
        self.assertFalse(retrieval._same_document([row(title="x")], [row(title="x")]))


class PickLatestTest(unittest.TestCase):
    def test_distinct_bytes_keep_both_versions_and_sources(self):
        cands = [(("a.pdf", 0), 0.05), (("a_v2.pdf", 0), 0.04), (("b.pdf", 0), 0.03)]
        rows_by_key = {
            ("a.pdf", 0): row("a.pdf", md5="first", model_no="M", title="手册", text="t", version="1.0"),
            ("a_v2.pdf", 0): row("a_v2.pdf", md5="second", model_no="M", title="手册", text="t", version="2.0"),
            ("b.pdf", 0): row("b.pdf", model_no="N", title="其它", text="t"),
        }
        kept = retrieval._pick_latest(cands, rows_by_key, dict(cands))
        self.assertEqual(kept, cands)

    def test_same_bytes_dedup_is_page_local_and_prefers_requested_identity(self):
        cands = [(("family.pdf", 0), 0.05), (("part.pdf", 0), 0.01), (("family.pdf", 1), 0.02)]
        rows = {key: row(key[0], md5="same", model_no="MX25R3235FM2IH0" if key[0] == "part.pdf" else "MX25R3235F",
                         page=key[1]) for key, _ in cands}
        aliases = {}
        kept = retrieval._pick_latest(cands, rows, dict(cands), "MX25R3235FM2IH0", aliases)
        self.assertEqual([key for key, _ in kept], [("part.pdf", 0), ("family.pdf", 1)])
        self.assertEqual(aliases[("part.pdf", 0)]["items"][0]["file"], "family.pdf")
        self.assertEqual(aliases[("part.pdf", 0)]["items"][0]["scope"], "same_bytes")

    def test_source_aliases_are_bounded(self):
        cands = [((f"{i}.pdf", 0), 1 / (i + 1)) for i in range(8)]
        rows = {key: row(key[0], md5="same") for key, _ in cands}
        aliases = {}
        kept = retrieval._pick_latest(cands, rows, dict(cands), aliases=aliases)
        self.assertEqual(len(kept), 1)
        self.assertEqual(len(aliases[kept[0][0]]["items"]), 4)
        self.assertEqual(aliases[kept[0][0]]["omitted"], 3)


if __name__ == "__main__":
    unittest.main()
