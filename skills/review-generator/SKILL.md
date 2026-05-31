---
name: review-generator
description: 全自动文献综述生成器。从 N 篇 PDF 到完整中文综述（每篇详解 + 图片 + 引用），全 subagent 并行驱动，含多轮审核深化。当用户提到"写综述"、"文献综述"、"整理文献"、"批量读论文"、"论文笔记"、"literature review"、或需要把一堆 PDF 整理成带图片和引用的结构化笔记时使用。即使用户没有明确说"综述"，只要涉及多篇论文的批量阅读和整理，也优先使用此技能。
---

# 文献综述全自动生成器

你是编排者，不是执行者。你的工作是在每个阶段告诉用户"现在该做什么"，然后 spawn 并行 subagent 完成实际工作。

## 入口：自动检测 + 确认

首先跑 `bash scripts/status.sh [project_dir]` 自动判断当前阶段。脚本输出 PDF 数、MD 数、section 数、图片数、bib 有無、main.tex 有無，以及建议的下一阶段。

然后问用户确认：是否从这个阶段继续？如果用户说"前面已经做过了"，根据 status.sh 输出跳到对应阶段。如果用户说"从头来"，回到阶段 0。

**🔴 CHECKPOINT**：`status.sh` 输出结果后，必须停下来让用户确认阶段，不要自动跳转。

**如果 `status.sh` 输出 Stage -1（连 refs/ 都没有）**：
→ 问用户想在哪里创建项目。目录不存在就 `mkdir -p` 创建，然后建 `refs/`（放 PDF）、`sections/`（输出 .tex）。

**关键**：不主动检查文件是否存在。万一文件有问题，subagent 会报错，那时再处理。

## 长任务管理：Goal + Loop

这是一个跨越多轮对话的长任务。利用 Claude Code 的 harness 机制保持连续性：

**Goal**：每个大阶段（3/4/7）开始时，用 `/goal` 设定当前阶段目标。例如阶段 3 启动时：
```
/goal 完成 N 篇论文的并行精读，写出 sections/sec_NN.tex
```
Goal 会在 session 结束时提醒用户未完成，下次打开时自动续接。

**Loop**：阶段 7（审核循环）可用 `/loop` 自动轮询。例如：
```
/loop 30m 检查 sections/ 是否有新的修改需要重新编译审核
```
这样在用户手动修改 section 后，编译-审核-深化循环可以自动推进。

**状态文件**：每次阶段结束后，在项目根目录写一个 `.lit-review-stage` 文件记录当前阶段号，下次 `status.sh` 会读取。跨 session 无需重新判断。

## 核心工作方式

你通过 spawn subagent 完成所有重活。每篇论文 = 一个 subagent，3 篇以上全并行启动。原因很简单：串行读 16 篇论文要 6 小时，并行只要 10 分钟。

每一轮 spawn agent 时，Agent prompt 里必须嵌入：
- 前文概念清单（阶段 3/4/7）：前 K-1 篇的核心概念，确保不丢失不重复
- 关键约束（所有阶段）：`\SI{}{}` 是文本命令不能包 `$`、图片 DPI 用 `pixel/6.3/scale≥120` 校验、Crossref 只用精确 DOI 不用标题搜索、编译链用 `;` 不用 `&&`（xelatex 的 warning 也会导致非零退出码阻断 `&&` 链）

## 八个阶段

每个阶段结束后：向用户汇报结果，把当前阶段号写入项目根目录的 `.lit-review-stage` 文件（`echo "N" > .lit-review-stage`），然后确认是否继续。

### 阶段 0：确认目标

**🔴 CHECKPOINT**：处理任何 PDF 之前，必须先和用户敲定三件事：综述主题、预期论文数量、输出格式偏好（A4=打印用 `normal`、平板用 `pad`、投影用 `screen`）。格式决定后续 ElegantNote 设备选项和 DPI 计算基准。三件事未确认前不进入阶段 1。

### 阶段 1：论文收集 + 自动重命名

用户只需把 PDF 丢进 `refs/`，不用手动命名。接下来的流程：

**1a. 提取元数据**：对每个 PDF spawn 一个 subagent，读取 PDF 首页（或通过 MinerU 快速提取标题/摘要），返回：
- 第一作者姓氏
- 发表年份
- 1-2 个关键词（从标题取）
- 格式：`{year}|{first_author}|{keyword}`

**1b. 排序重命名**：收集所有 agent 返回的元数据，按年份升序排列。同年论文按作者字母序。然后依次编号：
```
refs/
├── 01_White_1992_DMRG.pdf
├── 02_Olivares-Amaya_2015_Ab-Initio_DMRG.pdf
├── 03_LeCun_2015_Deep_Learning.pdf
└── ...
```

编号即脉络——`01` 是最早的奠基工作，后续论文依次建立在前面基础上。如果有论文无法确定年份（arXiv 预印本），用 arXiv 提交日期。

非 arXiv 论文记录 DOI 到 `refs/not_found.txt`，之后通过期刊官网获取。

### 阶段 2：PDF → Markdown

调用 `Skill("mineru-document-extractor")` 批量提取。该技能会自动处理 token 配置（学术论文推荐 token 模式，支持表格和公式识别）。输出 Markdown 到 `refs/`，图片到 `refs/images/`。

### 阶段 3：并行精读

全并行 spawn N 个 subagent，每个读一篇 MD 写出 `sections/sec_NN.tex`。Agent prompt 要求：
- 仅写 section body（无 preamble）
- 覆盖背景、方法、公式、结果、意义
- 用 `\subsection{}` 组织，`\cite{key}` 引用
- 对前文已介绍的概念简要回顾，新概念充分展开
- 告诉用户 agent 数量，完成后自动进入下一阶段

### 阶段 4：图片 + DPI

全并行 spawn N 个 subagent。每个读取 MD + 当前 TEX，取 3-5 张关键图插入。图片必须带扩展名（MinerU 出的都是 `.jpg`），用 `identify` 获取像素宽度计算 DPI。全部完成后跑 `Skill("elegantnote-assistant")` 的 `scripts/dpi_check.py` 统一修正——低 DPI 图缩小，高 DPI 图放大，缺失扩展名自动补全。

### 阶段 5：参考文献

扫描所有 sections 的 `\cite{...}` 去重。对每个引用键确定 DOI 或 arXiv ID，然后跑：

```bash
python scripts/fetch_bib.py --file dois.txt -o refs/refs.bib
```

脚本通过 Crossref API 精确 DOI 查询获取正式 BibTeX（不依赖标题搜索），arXiv ID 自动生成 `@misc` 条目。重复条目自动跳过。生成 `refs/refs.bib`。

注意：`apsrev4-2` 要求 `@article` 必须有 `journal` 字段，arXiv 论文用 `@misc` 规避。脚本自动处理这个分类。

### 阶段 6：主文档与编译

调用 `Skill("elegantnote-assistant")` 创建 `main.tex`，选设备选项（默认 A4 `normal`）。`\input` 所有 sections，加引言（预告脉络）和总结（收束未竟之业）。

编译链：`xelatex main; bibtex main; xelatex main; xelatex main`。用 `;` 不用 `&&`——xelatex 的 warning 也导致 exit≠0，会阻断后续步骤。三步检查：`! ` 计 0、`Citation.*undefined` 计 0、`nqs.blg` 中 `Warning` 计 0。

### 阶段 7：审核 + 深化

三轮并行审核：
1. **内容审核**：每 4 篇一个 agent，查 LaTeX 语法、内容完整性、图片质量、交叉引用
2. **图注核对**：每张图 hash 在 MD 上下文 vs TEX 图注，逐张比对数值
3. **内容深化**：每篇一个 agent，对比 MD 补充遗漏的公式、数据、物理诠释

每轮修完后重新编译。循环直到用户说"可以了"。

**🛑 STOP**：审核循环的退出条件是用户明确说"可以了"，不要自作主张判定"质量够了"而提前结束。

### 阶段 8：交付

**🔴 CHECKPOINT**：交付前最后确认——展示编译结果，让用户检查 PDF 输出。用户确认无误后再 `git add -A && git commit && git status` 确认 clean。

## 遇到问题时

编译阶段的常见坑（也是你 spawn agent 时必须塞进 prompt 的）：
- `\SI{}{}` 余 `$` → 删掉。`\SI` 是文本命令，不能在 `$...$` 内
- 图片找不到 → 扩展名丢了，跑 `dpi_check.py` 自动补
- 引用全 `[?]` → bibtex 没跑或被 `&&` 跳过了
- 中文乱码 → 没用 XeLaTeX
- `\mathbb{1}` 未定义 → 缺 `\usepackage{bbm}`

详细 workflow 在 `references/workflow.md`，当需要完整 agent prompt 模板、DPI 公式推导、或 BibTeX 样式选择细节时查阅。
