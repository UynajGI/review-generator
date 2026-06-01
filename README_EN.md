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

## Skills

### review-generator

Turn your PDF collection into a well-structured literature review. **Humans collect the papers** (AI can't find them all), AI does the deep reading, chronological ordering, and per-paper detail preservation. Output language is determined by the user.

Core ideas:
- **You find papers, AI writes the review**: just drop PDFs into `refs/` — no manual renaming needed
- **One subagent per paper, no content skipped**: sequential reading makes AI lazy and skip details; parallel subagents ensure every paper gets full deep reading — formulas, data, and physical interpretations preserved
- **Chronological narrative**: papers are auto-sorted by year and author, building a timeline from foundational work to latest advances

- Automatic DOI extraction, paper renaming and chronological ordering
- PDF → Markdown batch extraction (MinerU OCR)
- Parallel subagent deep reading, one structured section per paper
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
    │   │   ├── status.sh          # Project stage detection (cross-session continuity)
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
