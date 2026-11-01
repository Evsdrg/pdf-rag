# 工具入口与执行边界

所有命令从仓库根目录执行。`tools/` 同时包含只读验证和会写索引的维护脚本，
不能因为脚本在工具目录里就批量运行。安装/启动见[部署指南](../DEPLOY.md)，
索引维护见[运维手册](../docs/OPERATIONS.md)。

## 检索与证据验证

| 入口 | 用途 | 模型/网络与写入边界 |
|---|---|---|
| `../eval_retrieval.py` | 历史55题检索对照，支持默认/结构化方案 | 默认mixed+rerank会调用模型；`--mode fts --no-rerank`不走模型。不是默认断网工具 |
| `eval_relations.py` | 关系证据集v2；支持标注校验及历史v1重放 | 内部封锁socket，只允许本地FTS/无重排；只读索引 |
| `eval_evidence_efficiency.py` | 冻结20题的来源、行绑定、补查、紧凑输出分项验证 | 内部封锁socket，只读索引；研究原型不接入生产API |
| `eval_evidence_protocol_cost.py` | 正式序列化/分页与按需详情成本情境 | 内部封锁socket；正文为索引Reader替身，不调用OCR；不是实际模型token计量 |
| `prepare_evidence_answer_trial.py` | 离线生成4题×两组回答对照输入 | 只有prepare入口，无模型发送代码；同名文件拒绝覆盖 |
| `bench_structured_latency.py` | 27关系题+旧55题的实体冷建、热态默认/结构化与可选重排替身对照 | 内部封锁socket，只读FTS；结果缓存关闭，替身分数不评价模型质量 |
| `bench_logic.py` | 逻辑性能：现有向量与确定性本地重排替身 | 不调用模型；向量检索使用现有分区，只读；需要断网保护时用独立进程额外封锁socket |
| `check_docs.py` | 跟踪Markdown相对链接与确定形态敏感信息检查 | 不访问外链，不修改文件；启发式扫描不是完备的密钥审计 |

### 安全的收尾检查

```bash
.venv/bin/python -m unittest discover -s tests
.venv/bin/python tools/check_docs.py
git diff --check
```

以上不需要运行模型实验或索引任务。测试使用临时夹具/替身并隔离运行设置；
不要为执行检查安装或升级依赖，也不要把历史测试通过状态当作当前检查结果。

### 显式选择离线实验

```bash
# 只检查标注；不执行检索或模型请求
.venv/bin/python tools/eval_relations.py --validate-only

# 输出只留本地；目录由调用者新建，不能与已有冻结实验混用
work=$(mktemp -d)
.venv/bin/python tools/eval_evidence_efficiency.py --variant compact --json "$work/metrics.json"
.venv/bin/python tools/eval_evidence_protocol_cost.py --json "$work/protocol-cost.json"
```

这些命令会读取现有本地索引并写指定结果文件，不会运行ingest。结果可能包含手册片段、
短表行或来源引用，不提交、不上传。重新跑分不应覆盖已有证据或重新生成冻结标注来追分。

## 当前研究状态

本阶段按**离线验证收尾**。真实回答模型的8次对照请求尚未执行，既有本地输入保留；
准备工具和绿色测试不能证明最终答案准确率或实际token节省。没有生产默认开启、部署或推送。

- 当前已实现的可选检索能力：[SAG结构化检索](../docs/SAG-STRUCTURED-RETRIEVAL.md)。
- 分项结果、负结果与成本：[证据效率验证](../docs/EVIDENCE-EFFICIENCY-VALIDATION.md)。
- 尚未执行的回答模型对照与判分规则：[离线冻结规范](../docs/EVIDENCE-ANSWER-TRIAL.md)。
- 历史质量/性能对照：[评测记录](../docs/BENCHMARKS.md)。

`backend/evidence_probe.py` 仅由研究工具和测试使用；它不增加MCP工具，不改变生产API/schema。
对照输入的外发、回答模型选择、真实usage测量都需要新的明确安排，不因仓库整理自动开始。

## 索引、数据包及交付维护

`reembed_index.py`、`build_vec_index.py`、`compact_index.py`、`migrate_vec_partition.py`
与增量/重建索引属于写入维护，不是测试收尾动作。数据包导入/导出和交付构建也应先查看
[运维手册](../docs/OPERATIONS.md)、[向量分区](../docs/VECTOR-PARTITION.md)及各脚本参数。
保留唯一备份、手册、运行数据和冻结实验产物，不执行通配清理。
