<p align="center">
  <strong>从文献库到结构化综述 / From PDF Collection to Structured Review</strong><br/>
  把收集好的论文变成逐篇精读、按时序编排的文献综述 · Turn your PDF collection into a chronologically-organized literature review with per-paper deep reading
</p>

<p align="center">
  <a href="README.md">中文</a> · <a href="README_EN.md">English</a>
</p>

<p align="center">
  <a href="https://github.com/UynajGI/review-generator/blob/main/LICENSE"><img alt="license" src="https://img.shields.io/github/license/UynajGI/review-generator?style=flat-square&color=2f855a" /></a>
  <img alt="platform" src="https://img.shields.io/badge/platform-Claude%20Code-blue?style=flat-square" />
  <img alt="Stars" src="https://img.shields.io/github/stars/UynajGI/review-generator?style=flat-square&color=805ad5" />
</p>

---

## 技能列表

### review-generator

把收集好的论文 PDF 变成一篇结构完整的文献综述。**论文由人收集**（AI 找不全文献），AI 负责逐篇精读、按时序编排、保留每篇细节不偷懒。输出语言由使用者决定。

核心理念：
- **人找论文，AI 写综述**：你只管把 PDF 丢进 `refs/`，不用手动命名，剩下的全交给 AI
- **每篇独立 subagent，不偷懒**：串行读 16 篇 AI 会跳读漏内容，并行 subagent 每篇都被完整深读，不会丢公式、丢数据、丢物理诠释
- **按时间脉络编排**：自动提取年份和作者，从最早的奠基工作到最新进展，按时间线层层展开

- 论文自动重命名与按时序排序
- PDF → Markdown 批量提取（MinerU OCR）
- 并行 subagent 逐篇精读，每篇生成独立结构化笔记
- 图片插入与 DPI 自适应
- 参考文献自动获取（Crossref API）
- 主文档编译（ElegantNote + XeLaTeX）
- 三轮审核深化循环

### elegantnote-assistant

ElegantNote LaTeX 中文笔记模板助手。提供文档类选项配置、DPI 自适应插图、定理环境、编译排错等完整支持。

- 多设备选项（A4/平板/Kindle/投影）
- 颜色主题与背景模式
- DPI 自动检测与图片尺寸修正
- 中文 LaTeX 编译链（XeLaTeX + BibTeX）

### mineru-document-extractor

MinerU 文档提取 CLI 技能封装。支持 PDF、图片和网页到 Markdown / HTML / LaTeX / DOCX 的转换。

- Token 模式：表格与公式识别、批量处理、多格式输出
- Flash 模式：无需注册，快速提取（有限制）
- 网页抓取转 Markdown

## 安装

```bash
npx skills add https://github.com/UynajGI/review-generator/tree/main/skills
```

在 Claude Code 中，技能会自动被发现和加载。

### mineru-document-extractor 额外依赖

```bash
npm install -g mineru-open-api
```

## 目录结构

```
.
└── skills/
    ├── review-generator/
    │   ├── SKILL.md
    │   ├── scripts/
    │   │   ├── status.sh          # 项目阶段检测
    │   │   └── fetch_bib.py       # Crossref 参考文献获取
    │   ├── references/
    │   │   └── workflow.md
    │   └── evals/
    ├── elegantnote-assistant/
    │   ├── SKILL.md
    │   ├── assets/
    │   │   ├── elegantnote.cls
    │   │   ├── elegantnote-cn.tex
    │   │   ├── elegantnote-en.tex
    │   │   └── logo-blue.png
    │   ├── scripts/
    │   │   └── dpi_check.py       # DPI 检测与图片尺寸修正
    │   └── evals/
    └── mineru-document-extractor/
        ├── SKILL.md
        ├── CONTRIBUTING.md
        └── _meta.json
```

## 鸣谢

本项目基于以下开源项目：

- [ElegantNote](https://github.com/ElegantLaTeX/ElegantNote) — 优雅的 LaTeX 中文笔记模板
- [MinerU](https://github.com/opendatalab/MinerU) — 高精度 PDF 文档解析与 OCR 引擎
- [MinerU-Ecosystem](https://github.com/opendatalab/MinerU-Ecosystem) — MinerU 工具链生态（含 CLI 封装）

## 许可证

MIT License - 详见 [LICENSE](./LICENSE)
