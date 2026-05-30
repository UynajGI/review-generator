<p align="center">
  <strong>全自动文献综述生成器 / Automated Literature Review Generator</strong><br/>
  Claude Code 学术 PDF 处理技能集合 · A collection of Claude Code skills for academic PDF processing
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

从 N 篇 PDF 到完整中文文献综述的全自动 pipeline。全 subagent 并行驱动，含多轮审核深化。

- 论文自动重命名与排序
- PDF → Markdown 批量提取
- 并行精读生成结构化笔记
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
