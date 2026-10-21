"""测试包:把配置持久化文件重定向到临时目录。

**必须在任何 test 模块导入 config 之前生效**,所以放在包初始化里而不是 support.py
——后者只有部分测试模块导入,漏掉的那些仍会写到线上配置。

背景:`config.set_many()` 会落盘到 `config.SETTINGS_FILE`(即仓库的
`data/settings.json`)。而 compose.yaml 把 `./data` bind mount 进生产容器,
这个文件就是**线上生效的配置**。历史上跑一次单测就把
`vector_models_priority` 写成了测试值,该值匹配不到任何分区,导致生产检索的
向量通道整体降级 —— 测试污染了服务,而且没有任何提示。

重定向后,测试里任何 set_many / reset 都只写临时文件,进程退出即丢。
"""
import atexit
import shutil
import tempfile
from pathlib import Path

from backend import config

_TEST_DATA_DIR = Path(tempfile.mkdtemp(prefix="pdfrag_test_data_"))
config.SETTINGS_FILE = _TEST_DATA_DIR / "settings.json"
atexit.register(shutil.rmtree, _TEST_DATA_DIR, True)
