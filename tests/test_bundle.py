"""数据包:多分区清单与导入兼容判断（v2 语义）。"""
import unittest

from backend import bundle, config, vecstore


def mk_manifest(parts, version=None, embedding=None):
    m = {"format": bundle.BUNDLE_FORMAT,
         "version": version if version is not None else bundle.BUNDLE_VERSION}
    if parts is not None:
        m["vector_partitions"] = parts
    if embedding is not None:
        m["embedding"] = embedding
    return m


class LocalUsablePartitionsTest(unittest.TestCase):
    def setUp(self):
        self.cur = str(config.get("embed_model"))

    def test_partition_with_local_model(self):
        m = mk_manifest([{"slug": "a", "model": self.cur, "dim": 768}])
        self.assertEqual(bundle._local_usable_partitions(m), ["a"])

    def test_other_model_not_usable(self):
        m = mk_manifest([{"slug": "b", "model": "someone-else", "dim": 1024}])
        self.assertEqual(bundle._local_usable_partitions(m), [])

    def test_mixed_returns_only_local(self):
        m = mk_manifest([{"slug": "b", "model": "x", "dim": 1024},
                         {"slug": "a", "model": self.cur, "dim": 768}])
        self.assertEqual(bundle._local_usable_partitions(m), ["a"])

    def test_v1_bundle_falls_back_to_embedding(self):
        # 老包没有 vector_partitions，只能看 embedding 块
        m = mk_manifest(None, embedding={"model": self.cur, "dim": 768})
        self.assertEqual(bundle._local_usable_partitions(m),
                         [vecstore.model_slug(self.cur, 768)])

    def test_v1_bundle_other_model(self):
        m = mk_manifest(None, embedding={"model": "nope", "dim": 768})
        self.assertEqual(bundle._local_usable_partitions(m), [])


class CheckCompatibleTest(unittest.TestCase):
    def setUp(self):
        self.cur = str(config.get("embed_model"))

    def test_apply_provider_always_ok(self):
        m = mk_manifest([{"slug": "b", "model": "other", "dim": 1024}])
        self.assertEqual(bundle._check_compatible(m, apply_provider=True), "")

    def test_keep_local_with_matching_partition_ok(self):
        m = mk_manifest([{"slug": "a", "model": self.cur, "dim": 768}])
        self.assertEqual(bundle._check_compatible(m, apply_provider=False), "")

    def test_keep_local_without_matching_partition_rejected(self):
        m = mk_manifest([{"slug": "b", "model": "other", "dim": 1024}])
        msg = bundle._check_compatible(m, apply_provider=False)
        self.assertIn("可用的向量分区", msg)
        self.assertIn(str(self.cur), msg)       # 提示里应说明本地模型名
        self.assertIn("other", msg)             # 以及包内实际有什么

    def test_v1_bundle_same_model_still_ok(self):
        m = mk_manifest(None, embedding={"model": self.cur, "dim": 768})
        self.assertEqual(bundle._check_compatible(m, apply_provider=False), "")

    def test_v1_bundle_other_model_rejected(self):
        m = mk_manifest(None, embedding={"model": "nope", "dim": 768})
        self.assertNotEqual(bundle._check_compatible(m, apply_provider=False), "")

    def test_wrong_format_rejected(self):
        m = {"format": "something-else", "version": 1}
        self.assertNotEqual(bundle._check_compatible(m), "")

    def test_future_version_rejected(self):
        m = mk_manifest([], version=bundle.BUNDLE_VERSION + 1)
        self.assertIn("高于当前支持", bundle._check_compatible(m))


if __name__ == "__main__":
    unittest.main()


class ApplyPartitionPriorityTest(unittest.TestCase):
    def setUp(self):
        self.cur = str(config.get("embed_model"))

    def tearDown(self):
        config.override_local({"vector_models_priority": ""})

    def test_writes_usable_partitions_when_priority_empty(self):
        m = mk_manifest([{"slug": "a", "model": self.cur, "dim": 768},
                         {"slug": "b", "model": "other", "dim": 1024}])
        config.override_local({"vector_models_priority": ""})
        picked = bundle._apply_partition_priority(m)
        self.assertEqual(picked, ["a"])
        self.assertEqual(config.get("vector_models_priority"), "a")

    def test_respects_existing_priority(self):
        m = mk_manifest([{"slug": "a", "model": self.cur, "dim": 768}])
        config.override_local({"vector_models_priority": "manual-choice"})
        self.assertEqual(bundle._apply_partition_priority(m), [])
        self.assertEqual(config.get("vector_models_priority"), "manual-choice")

    def test_nothing_usable_does_nothing(self):
        m = mk_manifest([{"slug": "b", "model": "other", "dim": 1024}])
        config.override_local({"vector_models_priority": ""})
        self.assertEqual(bundle._apply_partition_priority(m), [])
        self.assertEqual(config.get("vector_models_priority"), "")
