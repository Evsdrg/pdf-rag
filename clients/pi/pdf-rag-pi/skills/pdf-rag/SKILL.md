---
name: pdf-rag
description: 检索本地元器件手册库(已索引的 PDF/Markdown 数据手册)以回答引脚、电气参数、寄存器、封装、订购型号等问题。当需要查阅芯片/模组/器件手册,或用户提到某个元件型号并想知道其规格时使用。
---

# 元器件手册库检索

`pdf_rag_*` 工具检索的是一份**已索引的 PDF/Markdown 手册语料库**，**不是工作区文件系统**。查工作区里的代码/文档用内置 `grep`/`read`;
查元器件手册用这里的工具。两者搜的是完全不同的东西,不要混用。

## 先判断用哪条路

库里有三条互补的检索路径,选错会白跑:

| 工具 | 走什么 | 什么时候用 |
|---|---|---|
| `pdf_rag_search` | BM25 + 型号子串 + 向量,RRF 融合 + 重排 | **默认首选**。问"某个参数是多少""这个型号支持什么" |
| `pdf_rag_grep` | 纯正则/字面,不走向量 | 已知**精确符号**:`VDD_APC`、`IddHP`、寄存器位名、引脚名。也用于 `search` 结果不理想时兜底 |
| `pdf_rag_read_page` / `pdf_rag_read_pages` | 直接读页 | 已从 `search`/`grep` 拿到 file+page,要读完整上下文 |

**关键区分**:`search` 是语义检索(适合自然语言问题),`grep` 是字面匹配(适合确切
符号)。查"W25Q32 的供电电压范围"用 `search`;查"VDD_APC 出现在哪一页"用 `grep`。

## 推荐工作流

1. **定位**:`pdf_rag_search("W25Q32 供电电压")` → 拿到 `file` + `page` + `snippet`。
   `snippet` 已经是"含答案的窗口",很多时候直接就能回答,不必读整页。
2. **导航**(大手册):`pdf_rag_get_outline(file)` 看书签目录,找到目标章节页码。
3. **读全**:`pdf_rag_read_page(file, page)`,或跨页规格表用
   `pdf_rag_read_pages(file, "58-60")`。Markdown 长章优先用目录返回的 `section_id`
   调用 `pdf_rag_read_section`，不凭标题文字猜标识。
4. **续读**：文本返回是 `schema_version=2` JSON。`truncated=true` 时保持参数不变，
   传入 `next_cursor`，直到返回完整；不要把首批当全文。游标失效需从首批重新读取。
5. **看图**：曲线、封装尺寸、原理图用 `pdf_rag_render_page`，可传归一化裁剪坐标。
   此工具只本地渲染，不调用 OCR；图片消费取决于客户端/模型能力。

`search` 返回的 `file` 字段是**库内相对路径**(如 `02_存储/C2456252_...PDF`),
直接原样传给读页工具即可,不要拼接、不要加前缀。

## 容易踩的点

- **`grep` 的 `flex_separator` 默认开**:PDF 提取常丢失下标,同一符号在库里有
  `VDD_APC` 和 `VDD APC` 两种形态(空格形态实测占 71%)。默认把下划线/空白视为
  等价,别为了"精确"关掉它,否则会漏掉一大半实例。
- **`grep` 的 `pattern` 是正则**:查 `2.4MHz` 要写成 `2\.4MHz`;纯字面串直接写即可。
- **同族手册正文高度相似**:EC800M 与 ML307R 这类同族型号,正文几乎一样。命中结果
  里的 `model_no` / `product` 是区分依据,回答时要说清是哪份手册的哪个型号,不要
  张冠李戴。
- **`degraded` 字段**：表示某个检索通道发生降级，具体原因看 `notice/warnings`；
  不一定是上游限流，也可能是本地分区或配置问题。结果可能不完整，必要时用不依赖向量的
  `pdf_rag_grep` 交叉核对。
- **别猜型号**：`identity=unconfirmed` 只表示返回文档未确认型号，不代表全库不存在。
  重排分不是正确率概率。可用 `pdf_rag_list_files(model_no=...)` 筛选确认并按游标翻页。
- **计数与页号**：grep 的 `indexed_matches` 包含索引重复，不是印刷页次数；PDF `page`
  是物理页，Markdown 是一级标题伪页；文件列表的 `pages` 是索引最大页号。
- **提取告警**：检查 `warnings`，OCR 失败保留原生文本；乱码单位、公式和曲线不能靠猜测修复。

## 类别与文件范围

用 `pdf_rag_list_categories` 取实时类别，用 `pdf_rag_list_files` 按类别、文件或型号筛选并
按游标翻页。文件列表只包含**已索引**文件；源目录存在但未索引的文件需要另行核对 `status`
中的 `source_files/unindexed_files`，不要假设它一定能被搜索命中。

已知类别时给 `search`/`grep` 传 `category` 能显著缩小范围。

## 引用规范

回答时给出**具体出处**:`文件路径` + 页码。例:"W25Q32JW 工作电压 1.7–1.95V
(`02_存储/C2456252_NOR+FLASH_W25Q32JWSSIQ+TR_规格书_WJ210118.PDF` 第 5 页)"。
手册数据可能有版本差异,给出处便于用户复核。
