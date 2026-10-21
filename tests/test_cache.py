"""缓存失效:配置改动后旧结果必须不可复用(实测出过的回归)。"""
import unittest
from unittest import mock

from backend import config, retrieval
from tests.support import override_config


class FakeResponse:
    def __init__(self, dim):
        self._dim = dim

    def json(self):
        return {"data": [{"embedding": [0.5] * self._dim, "index": 0}]}


class ParamsFingerprintTest(unittest.TestCase):
    def test_fingerprint_changes_with_retrieval_params(self):
        k1 = retrieval._params_fingerprint()
        with override_config(snippet_width=300):
            k2 = retrieval._params_fingerprint()
        with override_config(rrf_k=1):
            k3 = retrieval._params_fingerprint()
        self.assertNotEqual(k1, k2)
        self.assertNotEqual(k2, k3)

    def test_fingerprint_restores(self):
        k1 = retrieval._params_fingerprint()
        with override_config(num_unit_bonus=9.9):
            retrieval._params_fingerprint()
        self.assertEqual(k1, retrieval._params_fingerprint())

    def test_cache_key_includes_fingerprint_and_version(self):
        class T:
            version = 7
        base = dict(query="q", category=None, top_k=5, mode="mixed",
                    rerank=True, file=None, max_per_doc=0)
        k1 = retrieval._cache_key(T, **base)
        with override_config(snippet_width=300):
            k2 = retrieval._cache_key(T, **base)
        self.assertNotEqual(k1, k2)
        T.version = 8
        self.assertNotEqual(k1, retrieval._cache_key(T, **base))


class EmbedQueryCacheTest(unittest.TestCase):
    def setUp(self):
        retrieval.reset_cache()

    def tearDown(self):
        retrieval.reset_cache()

    def _fake_post(self, calls, dim=768):
        def fake(url, payload):
            calls.append((payload.get("dimensions"), payload["input"][0],
                          payload.get("model")))
            return FakeResponse(payload.get("dimensions") or dim)
        return fake

    def test_same_text_hits_cache_once(self):
        calls = []
        with override_config(embed_cache_size=8):
            with mock.patch.object(retrieval, "_post_retry", side_effect=self._fake_post(calls)):
                retrieval.embed_query("A")
                retrieval.embed_query("A")
                retrieval.embed_query("B")
        self.assertEqual(len(calls), 2)

    def test_cache_key_includes_model_and_dim(self):
        calls = []
        with override_config(embed_cache_size=8):
            with mock.patch.object(retrieval, "_post_retry", side_effect=self._fake_post(calls)):
                retrieval.embed_query("A")
                with override_config(embed_dimensions=1024):
                    retrieval.embed_query("A")
                with override_config(embed_model="other"):
                    retrieval.embed_query("A")
        self.assertEqual(len(calls), 3)

    def test_disabled_cache_always_calls(self):
        calls = []
        with override_config(embed_cache_size=0):
            with mock.patch.object(retrieval, "_post_retry", side_effect=self._fake_post(calls)):
                retrieval.embed_query("Z")
                retrieval.embed_query("Z")
        self.assertEqual(len(calls), 2)

    def test_request_carries_dimensions(self):
        calls = []
        with override_config(embed_cache_size=8):
            with mock.patch.object(retrieval, "_post_retry", side_effect=self._fake_post(calls)):
                retrieval.embed_query("A")
        self.assertEqual(calls[0][0], config.get("embed_dimensions"))

    def test_reset_cache_clears_both(self):
        retrieval._EMBED_CACHE["x"] = [0.0]
        retrieval._RESULT_CACHE[("y",)] = (0.0, [], {})
        retrieval.reset_cache()
        self.assertEqual(len(retrieval._EMBED_CACHE), 0)
        self.assertEqual(len(retrieval._RESULT_CACHE), 0)


class EmbedQueryModelOverrideTest(unittest.TestCase):
    """查询向量必须按**分区的** model/dim/input_type 生成。

    最危险的组合是两个模型维度相同(都截断到 768):此时维度检查通不出任何异常,
    拿 A 模型的查询向量去搜 B 模型建的向量不会报错,只会静默给出无意义的相似度。
    """

    def setUp(self):
        retrieval.reset_cache()
        self.calls = []

    def tearDown(self):
        retrieval.reset_cache()

    def _run(self, **kwargs):
        def fake(url, payload):
            self.calls.append(payload)
            return FakeResponse(payload.get("dimensions") or 768)
        with mock.patch.object(retrieval, "_post_retry", side_effect=fake):
            return retrieval.embed_query("查询", **kwargs)

    def test_model_override_used_in_request(self):
        self._run(model_override="nemotron-3-embed-1b", dim_override=2048,
                  input_type_override="search_query")
        self.assertEqual(self.calls[0]["model"], "nemotron-3-embed-1b")
        self.assertEqual(self.calls[0]["dimensions"], 2048)
        self.assertEqual(self.calls[0]["input_type"], "search_query")

    def test_override_beats_global_config(self):
        with override_config(embed_model="global-model"):
            self._run(model_override="partition-model")
        self.assertEqual(self.calls[0]["model"], "partition-model")

    def test_no_override_uses_global_config(self):
        with override_config(embed_model="global-model"):
            self._run()
        self.assertEqual(self.calls[0]["model"], "global-model")

    def test_cache_separates_same_dim_different_model(self):
        # 同一维度、不同模型:必须各发一次请求,不能复用同一缓存条目
        self._run(model_override="model-a", dim_override=768)
        self._run(model_override="model-b", dim_override=768)
        self.assertEqual(len(self.calls), 2)
        self.assertEqual({c["model"] for c in self.calls}, {"model-a", "model-b"})


if __name__ == "__main__":
    unittest.main()
