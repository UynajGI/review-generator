# 文献综述全自动生成工作流

> 从 N 篇 PDF 论文到完整综述（每篇详解 + 图片 + 引用），全 agent 驱动，零手动排版。输出语言由使用者决定。
> 将 `N` 替换为你的论文数量，其余参数自动适配。
>
> **依赖技能**：`Skill("elegantnote-assistant")` — 处理文档创建、图片 DPI 适配和编译排错。`Skill("mineru-document-extractor")` — 处理 PDF 提取。

## 前置条件

- `Skill("mineru-document-extractor")`：按技能文档安装 `mineru-open-api` CLI 并配置 token
- `Skill("elegantnote-assistant")`：无需额外安装，模板和脚本已在技能内
- ImageMagick：`identify --version`（DPI 检查依赖）

## 项目结构

```
project/
├── main.tex               # 主文档（ElegantNote 类）
├── refs/                   # 论文原料
│   ├── images/             # MinerU 提取的图片（hash 命名）
│   ├── 01_Author_Year.md   # MinerU 提取的 Markdown
│   ├── 01_Author_Year.pdf  # 原始 PDF
│   ├── ...
│   └── refs.bib            # 参考文献
├── sections/               # Subagent 输出的 LaTeX 章节
│   ├── sec_01.tex
│   └── ...
└── workflow-lit-review.md  # 本文档
```

---

## 核心原则：按时间与演化顺序组织

文献综述的灵魂是**逻辑脉络**，而非简单罗列。论文必须按**时间线和概念演化顺序**排列：

1. **先排基础方法**（如 DMRG、深度学习基础），再排**在此基础上的创新**（如 NQS、Transformer-NNQS）
2. 编号本身承载演进关系：`sec_K` 必须建立在 `sec_{1..K-1}` 的概念之上
3. 每次 spawn agent 时，给它一份**前文概念清单**，确保它理解前面已经建立了什么基础，不会丢失也不重复
4. 最终文档的 `\section{引言}` 和 `\section{总结}` 分别作为"预告片"和"收束线"，把 N 篇离散章节编织成连贯故事

**反例**：如果按作者字母序或下载顺序排列，读者会看到 DMRG → 深度学习 → NQS → BERT → FermiNet → Transformer，逻辑完全断裂。

---

## 阶段 1：论文收集

确定 N 篇论文后，按**时间顺序**分配编号（`01` = 最早，`NN` = 最新）。命名建议：`NN_FirstAuthor_Year_Keyword.pdf`。

没有 arXiv 版本的论文记录 DOI 到 `refs/not_found.txt`，之后通过期刊官网获取。

---

## 阶段 2：PDF → Markdown 提取

调用 `Skill("mineru-document-extractor")` 批量提取 `refs/` 下所有 PDF。

该技能会自动处理 token 配置（学术论文推荐使用 token 模式以获得表格和公式识别），输出 Markdown 到同目录，图片提取到 `refs/images/`（SHA256 hash 命名）。

---

## 阶段 3：并行精读 → LaTeX Section

**核心模式**：每篇论文一个 subagent，全并行启动。

**Agent prompt 模板**：

```
你是第 K 篇论文的精读 agent。阅读 /path/to/refs/paper_K.md，
写出完整的 LaTeX section（语言由使用者决定）。保存到 /path/to/sections/sec_K.tex。

要求：
1. 仅写 section body（无 \documentclass、无 \begin{document}）
2. 覆盖全部：背景、方法、关键公式、核心结果、意义
3. 至少 X 单词/汉字（按论文篇幅调整，综述类 5000+，方法类 3000+）
4. 使用 \subsection{} 组织，用 \textbf{} 标关键词
5. 用 \cite{key} 引用文献

上下文：这篇论文前面已介绍的概念有：
[列出前 K-1 篇论文的核心概念清单]

撰写时：对前面已介绍的概念，简要回顾而非重新定义；
对自己引入的新概念，充分展开。
```

**关键设计**：
- 给每个 agent 提供**前文概念清单**，确保逻辑连贯不丢失
- `\cite{key}` 的 key 与 `.bib` 文件一致
- 主文档用 `\input{sections/sec_K}` 依次组装

---

## 阶段 4：图片插入 + DPI 自适应

### 原则

**不能所有图都用 `width=\linewidth`。** 图片物理尺寸必须匹配其像素分辨率。

```
DPI_min = 120（底线），DPI_target = 150
scale = floor(pixel_width / (DPI_target × linewidth_inches))
linewidth: normal(A4)=6.3″, pad=4.7″, screen=8.7″
```

### Agent prompt 模板

```
阅读 /path/to/refs/paper_K.md 和 /path/to/sections/sec_K.tex。
从 MD 中选取 3-5 张关键图，插入到 TEX 对应位置。

图片规则：
- \begin{figure}[htbp] \centering ... \end{figure}
- \includegraphics[width=X\linewidth]{hash.jpg}
- X 由 DPI 公式计算（先用 identify 获取像素宽度）
- \caption{}，必要时加 \label{fig:xxx}（语言由使用者决定）
- 深化内容：MD 中有但 TEX 中遗漏的细节

所有图片必须带 .jpg/.png/.pdf 扩展名。
图形路径已在主文档中设为 \graphicspath{{./refs/images/}}。
```

### 批量 DPI 检查

所有 agent 完成后，调用 `Skill("elegantnote-assistant")` 中的 `scripts/dpi_check.py` 统一跑：

```bash
python scripts/dpi_check.py sections/ refs/images/ --device normal
```

脚本自动：补全缺失的扩展名、修正低 DPI 尺寸、禁止 `scale=` 和绝对宽度。加 `--dry-run` 可预览不修改。

---

## 阶段 5：参考文献

1. 扫描所有 `sections/sec_*.tex` 中的 `\cite{...}`，去重得到引用键列表
2. 对于核心论文：从 MD 原文或已确认的 DOI 构造条目
3. 对于 arXiv 论文：`doi = {10.48550/arXiv.XXXX}`
4. 对于有正式 DOI 的论文：用 Crossref API **精确 DOI 查询**

```bash
# 精确 DOI 查询（标题搜索歧义率约 90%，不可用）
curl -H "Accept: application/x-bibtex" \
  "https://api.crossref.org/works/DOI_HERE/transform/application/x-bibtex"
```

**BibTeX 样式选择**（ElegantNote 默认 `biber` + `numeric`）：

| 场景 | 样式 | 引用格式 |
|------|------|----------|
| 物理/化学 | `apsrev4-2` + `natbib[numbers]` | `[1]` |
| 计算机 | `unsrt` | `[1]` |
| 数学 | `plain` | `[1]` |

APS 样式对 `@article` 要求 `journal` 字段；arXiv 论文和技术报告用 `@misc` 类型规避。

---

## 阶段 6：主文档与编译

### 创建主文档

调用 `Skill("elegantnote-assistant")` 创建 `main.tex`。该技能会自动从 `assets/` 复制模板文件，根据项目需求选择设备选项。

**主文档模板**（A4 打印）：

```latex
\documentclass[cn,normal,blue,11pt]{elegantnote}
\usepackage{amsmath,amssymb}
\usepackage{siunitx}
\usepackage{bbm}
\usepackage{graphicx}
\usepackage[numbers,sort&compress]{natbib}
\usepackage{hyperref}
\graphicspath{{./refs/images/}}
\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=blue}

\title{标题}
\author{作者}
\date{\today}

\begin{document}
\maketitle
\tableofcontents
\clearpage

\section{引言}
% 写清楚 N 篇论文的逻辑脉络

\input{sections/sec_01}
\clearpage
\input{sections/sec_02}
\clearpage
% ... 按时间顺序 \input 所有 section

\section{总结与展望}
% 收束脉络，指出未竟之业

\bibliographystyle{apsrev4-2}
\bibliography{refs/refs}
\end{document}
```

设备选项速查（详见 `Skill("elegantnote-assistant")`）：`normal`=A4/打印，`pad`=平板，`screen`=投影，`kindle`=电子书。

### 编译链

**注意用 `;` 而非 `&&`**，因为 xelatex 的 Warning 也会导致非零退出码，阻断 `&&` 链：

```bash
xelatex -interaction=nonstopmode main.tex
bibtex main
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```

### 零错误检查

```bash
grep -c '! ' main.log              # 期望: 0
grep -c 'Citation.*undefined' main.log  # 期望: 0
grep -c 'Warning' main.blg          # 期望: 0
```

### 常见错误速查

以下整理自 `Skill("elegantnote-assistant")` 排错表 + 本工作流实战经验：

| 错误 | 原因 | 修复 |
|------|------|------|
| `Missing $ inserted` | `\SI{...}{unit}$` 多余 `$` | 删掉末尾 `$`（`\SI` 是文本命令） |
| `Missing $ inserted` | `\SI{...}{unit}` 被 `$...$` 包裹 | 去掉外层 `$` |
| `Missing $ inserted` | 文本模式出现 `_` | 改成 `\_` 或进数学模式 |
| `Missing $ inserted` | `\includegraphics` 路径有 `_` | 改文件名或加 `\_` |
| 非英文文档乱码/不显示 | 用了 pdfLaTeX | 换成 XeLaTeX |
| `elegantnote.cls not found` | 类文件不在同级 | `Skill("elegantnote-assistant")` 自动处理 |
| Citation undefined | bibtex 被 `&&` 链跳过 | 用 `;` 替代 `&&` |
| `\mathbb{1}` 未定义 | 缺 `bbm` 宏包 | `\usepackage{bbm}` |
| 图片 file not found | 漏写扩展名 | 跑 `dpi_check.py`（自动补 `.jpg`） |
| 引用全是 `[?]` | 没跑 bibtex | 补跑 bibtex + 两次 xelatex |

---

## 阶段 7：Subagent 审核 + 深化

### 内容审核

每 4 个 section 派一个 agent，检查四类问题：

| 维度 | 检查项 |
|------|--------|
| LaTeX 语法 | `$` 配对、花括号、`\SI` 用法、`_` 逃逸、`\cite` 格式 |
| 内容质量 | 缺失公式、逻辑断裂、数据矛盾、描述不准确 |
| 图片 | 路径是否正确、DPI ≥ 120、有无 `\caption`/`\label` |
| 交叉引用 | `\ref` 是否指向存在的 `\label`、有无硬编码编号 |

### 图注核对

单独一轮：每个图片 hash 在 MD 原文中的上下文 vs TEX 图注内容，逐张比对（数值、方法名、系统规格）。

### 内容深化

审核后，对比 MD 原文补充遗漏内容：

```
阅读 /path/to/refs/paper_K.md 和 /path/to/sections/sec_K.tex。
找出 MD 中有但 TEX 中缺失的内容（公式、数据、算法步骤、物理诠释），
添加这些内容到 TEX 文件中。不删除任何已有内容。
```

---

## 阶段 8：交付

```bash
git add -A
git commit -m "Complete literature review: N papers, zero errors"
git status  # 期望: clean
```

---

## 关键经验

1. **并行度最大化**：阶段 3/4/7 中所有 subagent 完全独立 → 全并行。N 篇论文的精读 + 插图 ≈ 2N 个 agent，总耗时约 N×30秒 ÷ 并行度，而非串行的 N×30分。

2. **DPI 是图片质量的唯一客观指标**：无法看图时，`pixel_width / (linewidth_inches × scale)` 是唯一可靠的质量度量。低于 120 DPI 必须缩小，高于 300 可放大。用 `dpi_check.py` 自动化。

3. **Crossref 标题搜索不可用**：歧义率约 90%。只做精确 DOI 查询。arXiv 论文用 `10.48550/arXiv.XXXX` 作为 DOI。

4. **xelatex 非零退出码阻断 `&&`**：用 `;` 逐条执行编译链。

5. **`\SI{}{}` 是文本模式命令**：不能嵌套在 `$...$` 中，末尾也不要有 `$`。

6. **`.bib` 条目类型要匹配**：`apsrev4-2` 要求 `@article` 必须有 `journal`。arXiv 论文用 `@misc`。

7. **扩展名必须有**：MinerU 提取的图片都是 `.jpg`，agent 写 `\includegraphics` 时常漏掉。`dpi_check.py` 自动补全。

8. **技能复用**：文档创建、DPI 检查、编译排错全部通过 `Skill("elegantnote-assistant")` 完成。该技能自包含模板文件和脚本，无需每个项目重复造轮子。

---

## 与新项目的对接

1. 安装 `Skill("elegantnote-assistant")` 和 `Skill("mineru-document-extractor")`
2. 替换阶段 1 的论文列表
3. 按本文档各阶段模板 spawn agent
4. 主文档创建和图片 DPI 检查均通过对应 Skill 调用完成
