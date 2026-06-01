# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Claude Code skills repository containing three skills that together form a pipeline: PDF papers → structured LaTeX literature review. Skills are installed via `npx skills add https://github.com/UynajGI/review-generator/tree/main/skills`.

## Skill dependency chain

```
mineru-document-extractor  (Stage 2: PDF → Markdown)
         ↓
review-generator           (Orchestrator: all 8 stages)
         ↓
elegantnote-assistant      (Stage 4/6: DPI check + main.tex creation + compilation)
```

`review-generator` invokes the other two via `Skill("mineru-document-extractor")` and `Skill("elegantnote-assistant")`. Do not reimplement what those skills already provide — DPI checking, template creation, and compilation troubleshooting live in their respective skills.

## Key constraints (must embed in every subagent prompt)

- `\SI{}{}` is a text-mode command — never wrap it in `$...$` or append `$`
- Compilation chain uses `;` not `&&` — xelatex warnings produce nonzero exit codes that block `&&`
- Crossref queries use exact DOI only — title search has ~90% ambiguity, never use it
- Image DPI formula: `scale = floor(pixel_width / (DPI_target × linewidth_inches))`, DPI_min = 120
- MinerU extraction: always `auth --verify` before `extract`; never assume token is valid

## review-generator scripts

- `skills/review-generator/scripts/status.sh [project_dir]` — Detect which stage a project is at by counting PDFs, MDs, sections, images, bib, and main.tex. Also validates the `NN_Author_YYYY_Keyword.pdf` naming gate.
- `skills/review-generator/scripts/fetch_bib.py` — Fetch BibTeX from Crossref by DOI or arXiv ID. Handles `--doi`, `--arxiv`, `--file` inputs. arXiv entries use `@misc` (not `@article`) because `apsrev4-2` requires `journal` for `@article`. `--output` appends and skips existing keys.

## elegantnote-assistant scripts

- `skills/elegantnote-assistant/scripts/dpi_check.py <tex_dir> <image_dir> [--device normal|pad|screen|kindle]` — Scans `\includegraphics` in .tex files, reads pixel dimensions via `identify`, calculates optimal `\linewidth` scale, fixes missing extensions (appends `.jpg`), and reports DPI violations. `--dry-run` previews without modifying.

## The 8-stage pipeline (review-generator)

Each stage writes `echo "N" > .review-generator-stage` on completion. `status.sh` reads this file for cross-session continuity.

0. Confirm topic, paper count, output format (normal/pad/screen — determines DPI baseline)
1. `pdf2doi` for DOI/arXiv ID → Crossref/arXiv API for formal metadata → rename to `NN_Author_YYYY_Keyword__DOI.pdf`
2. MinerU batch extraction: PDF → Markdown (checkpoint: verify auth/token/mode before running)
3. Parallel subagent deep reading: one agent per paper → `sections/sec_NN.tex`
4. Image insertion + DPI adaptation: `dpi_check.py` run at end of stage
5. Bibliography: scan `\cite{}` keys → `fetch_bib.py` → `refs/refs.bib`
6. Intro + conclusion subagents (parallel), main.tex construction, compilation (4-pass xelatex chain)
7. Three-round review loop: content audit, caption verification, content deepening — exit only on user confirmation
8. Delivery: verify compilation, git commit

Hard gates that block progression: Stage 0 three-item confirmation, Stage 1 naming convention, Stage 2 MinerU availability check.
