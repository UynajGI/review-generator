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

## Skills

### review-generator

Fully automated pipeline from N PDFs to a complete Chinese literature review. Entirely driven by parallel subagents with multi-round review and refinement.

- Automatic paper renaming and chronological ordering
- PDF → Markdown batch extraction
- Parallel deep reading with structured note generation
- Image insertion with DPI-adaptive sizing
- Automatic bibliography retrieval (Crossref API)
- Main document compilation (ElegantNote + XeLaTeX)
- Three-round review and refinement cycle

### elegantnote-assistant

ElegantNote LaTeX Chinese note template assistant. Provides document class configuration, DPI-adaptive image insertion, theorem environments, and compilation troubleshooting.

- Multi-device options (A4/tablet/Kindle/projector)
- Color themes and background modes
- Automatic DPI detection and image size correction
- Chinese LaTeX compilation chain (XeLaTeX + BibTeX)

### mineru-document-extractor

MinerU document extraction CLI skill wrapper. Converts PDFs, images, and web pages to Markdown / HTML / LaTeX / DOCX.

- Token mode: table and formula recognition, batch processing, multi-format output
- Flash mode: no registration required, fast extraction (with limits)
- Web crawling to Markdown

## Installation

```bash
npx skills add https://github.com/UynajGI/review-generator/tree/main/skills
```

In Claude Code, skills are automatically discovered and loaded.

### Extra dependency for mineru-document-extractor

```bash
npm install -g mineru-open-api
```

## Directory Structure

```
.
└── skills/
    ├── review-generator/
    │   ├── SKILL.md
    │   ├── scripts/
    │   │   ├── status.sh          # Project stage detection
    │   │   └── fetch_bib.py       # Crossref bibliography fetcher
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
    │   │   └── dpi_check.py       # DPI detection and image resizing
    │   └── evals/
    └── mineru-document-extractor/
        ├── SKILL.md
        ├── CONTRIBUTING.md
        └── _meta.json
```

## Acknowledgments

This project builds on the following open-source projects:

- [ElegantNote](https://github.com/ElegantLaTeX/ElegantNote) — Elegant LaTeX note template
- [MinerU](https://github.com/opendatalab/MinerU) — High-precision PDF parsing and OCR engine
- [MinerU-Ecosystem](https://github.com/opendatalab/MinerU-Ecosystem) — MinerU ecosystem toolchain (including CLI wrapper)

## License

MIT License - see [LICENSE](./LICENSE)
