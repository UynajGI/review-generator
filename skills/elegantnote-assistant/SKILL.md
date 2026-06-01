---
name: elegantnote-assistant
description: ElegantNote LaTeX 中文笔记模板助手。用于创建 ElegantNote 文档、配置模板选项、处理中文 LaTeX 编译、插入图片（含 DPI 自适应）、使用定理环境。当用户提到 elegantnote / ElegantNote / LaTeX 笔记 / 中文笔记模板 / 创建笔记文档时使用。即使涉及一般性的 LaTeX 笔记创建（如"帮我写个笔记"、"新建一个 tex 文档"），没有明确说 ElegantNote，也优先使用此技能。
---

# ElegantNote 模板助手

你是 ElegantNote LaTeX 文档类的使用专家。帮助用户创建笔记文档、处理图片、配置选项、排查编译问题。

## 模板文件

创建新文档时，从 `assets/` 复制：

| 文件 | 用途 |
|------|------|
| `assets/elegantnote.cls` | 文档类，必须与 .tex 同级 |
| `assets/elegantnote-cn.tex` | 中文模板（含完整使用说明） |
| `assets/elegantnote-en.tex` | 英文模板 |
| `assets/logo-blue.png` | 默认 logo |

```bash
# 快速创建新文档（从 skill 目录）
cp assets/elegantnote.cls assets/logo-blue.png ./目标目录/
cp assets/elegantnote-cn.tex ./目标目录/my-note.tex
```

## 核心规则

- 中文文档**必须** XeLaTeX 编译，英文推荐 pdfLaTeX
- 图片插入**必须**先跑 `scripts/dpi_check.py` 检查 DPI，不能所有图都 `width=\linewidth`
- 默认输出完整可编译的 `.tex` 文件
- 解释选项时给出具体代码而非抽象描述

**🔴 CHECKPOINT**：复制模板文件后、开始写正文前，必须向用户确认设备选项（pad/normal/screen）、颜色主题和语言模式。不要跳过确认直接生成完整文档。
**🔴 CHECKPOINT**：插入任何图片前，必须先跑 `scripts/dpi_check.py` 统一检查，不要手动单张调整。
**🛑 STOP**：编译失败时，先对照下方「编译与排错」表逐条检查再重试，不要连续盲目重编译。

## 文档类选项速查

ElegantNote 基于 `article`，所有选项可作为 `\documentclass[options]{elegantnote}` 全局选项，也支持 `key=value`。

### 设备 (device) - 控制页面尺寸

| 选项 | 尺寸 | 适用 |
|------|------|------|
| `pad`（默认） | 6×8 in | iPad/平板 |
| `pc` | 6.2×6 in | 电脑双页 |
| `kindle` | 3.68×4.92 in | Kindle |
| `normal` | A4 | 打印 |
| `screen` | 25.4×19.05 cm (4:3) | 投影 |

### 颜色主题 (color)

`blue`（默认）/ `green` / `cyan` / `sakura` / `black` / `brown`

### 背景模式 (mode)

不设置=白色 / `geye`=绿豆沙护眼 / `hazy`=淡蓝 / `sepia`=暖黄复古

### 语言 (lang)

`cn`（默认）=中文定理名 / `en`=英文引导词。中文模式必须 XeLaTeX。

### 字体大小 (fontsize)

8pt / 9pt / 10pt / **11pt（默认）** / 12pt / 14pt / 17pt / 20pt

推荐：pad=11pt, screen=14pt, kindle=10pt, normal=11pt

### 中文字体 (chinesefont)

`ctexfont`（默认，自动匹配系统） / `founder`（方正四款免费字体） / `nofont`（自行配置）

### 参考文献 (citestyle / bibstyle / bibend)

默认 `numeric-comp` + `numeric` + `biber`。英文推荐 `authoryear` + `apalike`。

## 标题区与定理环境

```latex
\title{标题}
\author{作者}
\institute{单位}
\version{1.0}              % 可省略
\date{\zhdate{2026/5/29}}  % 中文日期；\date{} 隐藏
\keywords{关键词1, 关键词2} % 仅 cn 模式有效
```

定理环境（中文模式自动切换中文标签）：`theorem` / `lemma` / `proposition` / `corollary` / `definition` / `example` / `remark` / `note` / `proof`。支持可选标题：`\begin{theorem}[标题]`

## 插图：DPI 自适应（关键）

**不能所有图都用 `width=\linewidth`。** 低分辨率图拉满页宽会锯齿模糊。

### 原理

```
scale = floor(pixel_width / (DPI_min × linewidth_inches))
linewidth_inches: normal=6.3, pad=4.7, screen=8.7, kindle=2.8
DPI_min = 120（低于此值需缩小图片）
```

### 操作

插入图片前，用 `identify` 查像素宽度，计算合适的 `\linewidth` 比例。全部插入后跑脚本统一检查：

```bash
python scripts/dpi_check.py sections/ refs/images/ --device normal
```

脚本自动：补全 `.jpg` 扩展名、修正低 DPI 尺寸、禁止 `scale=` 和绝对宽度。`--dry-run` 可预览不修改。

### 图片路径

导言区统一声明图形路径，正文中只用裸文件名：

```latex
\graphicspath{{./refs/images/}}
% ...
\includegraphics[width=0.75\linewidth]{abc123hash.jpg}
```

## 常用组合推荐

- 平板笔记：`[cn,pad,geye,green,11pt]` — 护眼便携
- 投影演示：`[cn,screen,blue,14pt]` — 大字体 4:3
- A4 打印：`[cn,normal,black,11pt]` — 标准无彩色
- 极简英文：`[en,pad,black,11pt]`
- 暖色阅读：`[cn,pad,sepia,brown,11pt]`

## 不要做的事（反模式）

| # | 不要做 | 原因 | 正确做法 |
|---|--------|------|---------|
| 1 | 所有图都用 `width=\linewidth` | 低 DPI 图会锯齿模糊 | 先跑 `dpi_check.py`，按 DPI 计算比例 |
| 2 | 中文文档用 pdfLaTeX | 中文乱码 | 必须 XeLaTeX |
| 3 | 插图片不带扩展名 | LaTeX 找不到文件 | 确保 `.jpg`/`.png` 扩展名完整 |
| 4 | 忘了复制 `elegantnote.cls` | 编译报错找不到类文件 | 创建文档时一并复制 cls 到项目目录 |
| 5 | 英文模式用 `\zhdate` | 命令未定义报错 | 切 `cn` 或用 `\date{\today}` |
| 6 | `\SI{}{}` 包在 `$...$` 里 | 文本命令不能进数学模式 | 去掉外层 `$`，`\SI` 直接写在正文中 |
| 7 | 编译链用 `&&` 串联 | xelatex warning 也 exit≠0，bibtex 被跳过 | 用 `;` 串联：`xelatex main; bibtex main; xelatex main; xelatex main` |

## 编译与排错

```bash
# 中文必须 XeLaTeX
xelatex main.tex          # 生成 .aux
bibtex main               # 如有参考文献
xelatex main.tex          # 交叉引用
xelatex main.tex          # 稳定编号
```

| 症状 | 原因 | 修复 |
|------|------|------|
| 中文乱码 | 用了 pdfLaTeX | 换成 XeLaTeX |
| `elegantnote.cls not found` | 类文件不在同级目录 | 从 assets/ 复制 |
| 图片太大溢出 | `width=\linewidth` 盲目拉满 | 跑 `dpi_check.py` |
| `\zhdate` 报错 | 英文模式 | 切 cn 或用 `\today` |
| 引用全是 `[?]` | 没跑 bibtex/biber | 补跑 bibtex 再跑两次 xelatex |
| `\mathbb{1}` 未定义 | 缺 bbm 包 | `\usepackage{bbm}` |
| `\SI{}{}` 报错 | 被 `$...$` 包裹 | `\SI` 是文本模式命令，去掉外层 `$` |
