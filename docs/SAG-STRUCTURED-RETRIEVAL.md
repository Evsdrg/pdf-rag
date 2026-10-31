# SAG-inspired 结构化检索实验

## 1. 定位与边界

本项目没有引入 SAG 应用或 `zleap-sag` 依赖。本实验借鉴“实体连接、查询时局部扩展、
原始 chunk 作为证据”，而不是复刻 SAG 的 LLM event 抽取或完整动态超图引擎。

实现位于 `backend/entity.py`，通过 `backend/retrieval.py` 的可选召回通道使用。
它不修改主表、uid、`model_no`、向量分区、OCR 或数据包格式，不要求重新索引。
实体桥本身不请求任何模型；完整搜索仍按 `mode/rerank` 选择是否调用原有嵌入和重排服务。

**默认关闭，只在请求显式传 `structured=true` 时运行。** 它是候选扩展实验，
不是结构化参数数据库，不能据此完成精确数值筛选、Min/Typ/Max 推断或兼容料号判定。

## 2. 调用与诊断

```text
GET /api/v2/search?query=QMC6309%20VDD&structured=true
```

MCP `pdf_rag_search`、Web「检索测试」的「结构化扩展（实验）」和 pi 工具支持同名参数。
工具总数仍为 10，`schema_version=2` 不变。省略参数或设为 false 时默认三路检索不变。
不需要在配置中心保存开关，也不会修改 `data/settings.json`。

搜索响应的 `structured` 是诊断对象。以下仅为字段示例，不是实测指标：

```json
{
  "enabled": true,
  "status": "used",
  "query_entities": 2,
  "direct_candidates": 4,
  "expanded_candidates": 2,
  "added_pages": 6,
  "index_rows": 100,
  "index_entities": 60,
  "index_build_ms": 25.0,
  "index_cached": true
}
```

- `disabled`：请求未启用；不会构建或访问实体索引。
- `skipped`：没有可连接的查询实体，或只有数值而没有型号/参数等信号；不构建索引。
- `empty`：已检查实体索引，但没有匹配候选。
- `used`：产生了直接或扩展候选；不保证这些候选进入最终 top-k。
- `failed`：构建、预算或回表失败；`degraded` 包含 `structured`，继续使用其他检索通道。

`direct_candidates/expanded_candidates` 是有限候选页数，`added_pages` 是成功回表并通过过滤后
参与融合的页数，并非相对于其他通道的“新增页数”。`index_build_ms` 是当前内存索引最初的
构建耗时，不是每次查询耗时；`index_cached` 表示本次是否复用了实体索引。整个搜索响应
命中结果缓存时，这些字段是被缓存的原查询诊断，应结合顶层 `cached` 判断。

这些字段不是实体事实、正确率或条件满足证明。证据继续使用 `results[].snippet`、
`snippet_ref`、`file/page`，必要时读页、grep 或查看页图。

命中可带有界的 `retrieval_trace`，区分 `entity_direct` 与 `entity_expansion`；扩展包含
种子块、文件、物理页和最多四个共享实体，`scope=retrieval_only`。种子和目标均回主表核对，
找不到种子时不返回该条扩展。轨迹解释候选来源，不证明实体关系是事实；参与桥接的块与
同页最终展示的片段块可能不同，后者以 `snippet_ref` 为准。

## 3. 确定性实体规则

| 类型 | 来源与约束 |
|---|---|
| `model` | 文档仅使用既有 `model_no`，查询识别字母数字料号；保留 `-C/-TR/#PBF` 等后缀 |
| `interface` | I²C、SPI、QSPI、UART、USART、USB、GPIO、CAN、SDIO、I²S、PWM 白名单 |
| `symbol` | VDD、VIN、VOUT、VDD_APC、SDA、SCL 等有限符号；下划线/横向空白安全归一 |
| `parameter` | 供电电压、电流、频率、地址、封装、引脚、温度、功耗等有限中英文别名 |
| `value` | 原文中的数字+单位字符串，只作为辅助排序信号，不形成条件事实 |

具体约束：

- 不从文件名或正文猜测缺失的 `model_no`，不回写主表身份字段。
- 精确料号存在时不扩成其他前缀变体。精确身份不存在且查询型号至少五字符时，可做
  单向字面前缀候选匹配；这是模糊召回，不是型号等同，仍须核对返回的文件身份。
- 连字符连接的多完整料号（如 `MSM8216-MSM8616-MSM8916`）可分别建索引；普通后缀不拆。
- 显式型号无法解析时实体桥返回空候选，不放宽到其他型号；原有三路检索不受影响。
- `mA` 与 `MA`、`mΩ` 与 `MΩ` 保持不同；只归一空白、微符号和摄氏度符号。
  不换算 `3300 mV = 3.3 V`，不猜测 `mhz/UF` 等非规范写法。
- 大写 `CAN` 才按总线抽取，避免英语助动词 `can`。大小写不明确可能漏召回，交给其他通道。
- 不提取工作条件、Min/Typ/Max 关系、封装尺寸事实、兼容或替代关系。

## 4. 查询流程、预算与缓存

```text
已有 chunks 主表（只读、分批投影）
          │
          ▼
进程内 uid ↔ typed entity 反向索引
          │
查询实体 ─直接命中─> 有限候选页
          │               │
          └─共享实体─> 有限邻居页
                          │
                          ▼
主表按 uid 回表 → 页级 RRF → 去重 → 原有重排 → 原文 snippet/引用
```

查询先按型号、category 和 file 字面条件过滤，再按查询信号的文档稀有度选择每条 posting。
种子来自原有 FTS/子串/向量召回中的高相关页，不再直接把实体直召页当作检索管线种子。
最多八个种子页做一跳扩展；只有页眉型号而无当前查询参数/符号/接口的页不扩展。
显式型号限制邻居仍在解析出的型号范围内；无型号时只沿查询中的非通用符号/接口连接，
并要求至少两个共同实体。每个型号有独立队列轮转选种子、直召和扩展候选，候选池截断和
最终结果也保留型号配额；组内保持原有相关性顺序，不修改 reranker 原始分数。

诊断增加 `seeds/pruned_neighbors/by_model`，分别表示种子页数、剪枝次数和每型号候选页数。
`pruned_neighbors` 按检查路径计数，同页经不同边被拒可能多次计数，不是全库不相关页总数。

实体通道每页最多贡献一个块，RRF 名次从原有通道候选上限之后开始，不把实体分数混入
reranker 分数。这仍会影响 opt-in 查询的页排序；不是“只补候选且排序绝不变化”的保证。

结构化模式还用 `backend/evidence.py` 对同页全部命中块选最多两个不同证据窗口，
共享原有 `snippet_width` 正文预算，附 `evidence_refs[]` 的块与组合片段偏移。
启用窗口重排时，这份证据包同时构造重排正文与最终 snippet；不增加模型请求，
不改变默认模式的窗口算法，也不把召回分混入重排分。`snippet_ref` 只是第一窗引用，
多个窗口需逐项使用 `evidence_refs` 核对。

预算是保守实现常量，不是额外配置中心参数：

- 每块最多 48 个实体，查询最多 16 个；每块最多保留前 16 个数值实体。
- 直接候选最多 `min(64, limit/2)` 页，扩展候选最多 `min(32, limit/4)` 页；
  每条直接 posting 最多 256 个合格块，每条扩展边最多检查 64 个合格块。
- 内存实体索引最多 50000 块、累计 128000000 字节主表投影和 1000000 条实体连接。
  按 512 行一批读取，超限拒绝构建，不发布部分索引。这是输入规模预算，不是 Python RSS 上限。

进程内只保留一份实体索引，按表句柄身份和 `table.version` 失效。并发首查串行共享一次冷建，
因此同批结构化查询会等待首次构建完成；默认关闭的查询不进入该锁。预算超限按表版本缓存
失败，避免每次重扫；主表变化或 `retrieval.reset_cache()` 后可重试。临时读取异常不缓存失败。
数据包替换仍按既有流程成对清理表句柄和检索缓存。

空召回不是降级。构建/回表失败显式返回告警，不缓存该次搜索结果。孤儿 uid 丢弃，
category/file 回表后再校验，原有片段偏移和证据链保持不变。

## 5. 验证方式

下列质量对照不调用模型，不运行 ingest，不改持久配置或索引：

```bash
uv run --frozen python eval_retrieval.py --mode fts --no-rerank --json /tmp/baseline.json
uv run --frozen python eval_retrieval.py --mode fts --no-rerank --structured --json /tmp/structured.json
uv run --frozen python tools/bench_logic.py --structured-only --json /tmp/bench-structured.json
```

`eval_retrieval.py` 保留历史 `snippet@k` 字面值指标，另报：

- `grounded_snippet_at_1/at_k`：正确文件身份且片段含全部答案字面值。
- `grounded_page_at_k`：正确文件身份且命中整页的索引文本含全部答案字面值。

“grounded”仍不证明数值列、单位、条件和版本正确，只排除来自错误文件的数值碰巧命中。
纯逻辑基准把模型替换为确定性本地替身，只测计算成本，不测模型排序质量。
两轮最终对照和性能数据见 [BENCHMARKS.md](BENCHMARKS.md) §4.7。

## 6. 当前结论与后续边界

本地旧查询集显示正确文件的 top-5 片段和整页覆盖有所改善，但 top-1 未改善；尚未运行真实
mixed+rerank 质量对照，也没有独立的多跳/条件筛选标注集或全库错误连接率。因此保留为
默认关闭的实验能力，不宣称 SAG 完整集成或生产准确率提升。

只有补充真实关系问题标注、错误连接审查和获授权的端到端对照后，才应重新评审默认开启。
任何索引期 LLM event 抽取、条件事实数据库或生产部署均不在本实验内。

## 7. 参考

- [SAG 官方仓库](https://github.com/Zleap-AI/SAG)
- [SAG 论文](https://arxiv.org/abs/2606.15971)

官方英文多跳问答指标不能直接外推到元器件手册；本文件只定义本仓库的借鉴实现和边界。
