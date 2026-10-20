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
            calls.append((payload.get("dimensions"), payload["input"][0]))
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


if __name__ == "__main__":
    unittest.main()
