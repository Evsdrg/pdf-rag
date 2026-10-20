"""测试公共设施:配置覆盖的临时生效与还原。"""
import contextlib

from backend import config


@contextlib.contextmanager
def override_config(**values):
    """进程内覆盖可调参数,退出时按 snapshot 还原(不写 settings.json)。"""
    snap = config.snapshot()
    saved = {k: snap[k]["value"] for k in values if k in snap}
    config.override_local(values)
    try:
        yield
    finally:
        if saved:
            config.override_local(saved)
