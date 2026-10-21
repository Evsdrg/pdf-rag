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


class SettingsRestoreOrderTest(unittest.TestCase):
    """包内 settings 恢复后,后续配置写入必须以它为基础,不能覆盖回旧值。

    历史 bug:import_bundle 先 copy settings、后调 _apply_partition_priority,
    后者 set_many() 落盘的是**内存里的旧 _overrides** —— 刚导入的配置被整个覆盖,
    界面却提示"已恢复配置覆盖值"。
    """

    def setUp(self):
        import json
        import pathlib
        import shutil
        import tempfile
        self._json = json
        self._shutil = shutil
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.before = config.SETTINGS_FILE
        config.SETTINGS_FILE = self.tmp / "settings.json"
        config.reload()

    def tearDown(self):
        config.SETTINGS_FILE = self.before
        config.reload()
        self._shutil.rmtree(self.tmp, ignore_errors=True)

    def _write_bundle_settings(self, values):
        p = self.tmp / "incoming.json"
        p.write_text(self._json.dumps(values), encoding="utf-8")
        self._shutil.copy2(p, config.SETTINGS_FILE)
        config.reload()

    def test_reload_picks_up_file_changes(self):
        config.set_many({"rrf_k": 60})
        self._write_bundle_settings({"rrf_k": 42})
        self.assertEqual(config.get("rrf_k"), 42)

    def test_priority_write_keeps_restored_values(self):
        self._write_bundle_settings({"rrf_k": 42, "snippet_width": 1200})
        m = mk_manifest([{"slug": "a", "model": str(config.get("embed_model")), "dim": 768}])
        bundle._apply_partition_priority(m)
        disk = self._json.loads(config.SETTINGS_FILE.read_text(encoding="utf-8"))
        self.assertEqual(disk["rrf_k"], 42)
        self.assertEqual(disk["snippet_width"], 1200)
        self.assertEqual(disk["vector_models_priority"], "a")
