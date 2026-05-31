---
name: mineru-document-extractor
description: MinerU document extraction CLI that converts PDFs, images, and web pages into Markdown, HTML, LaTeX, or DOCX via the MinerU API. Supports token-free flash extraction for quick start, precision extraction with table/formula recognition, web crawling, batch processing, and piped workflows.
read_when:
  - Extracting text from PDF documents
  - Converting documents to Markdown
  - Crawling web pages to Markdown
  - Batch document processing
  - OCR on scanned documents
  - Converting PDF to HTML, LaTeX, or DOCX
  - Parsing document content
  - Reading PDF files
  - Extracting tables from documents
  - Converting Word documents
  - Quick document parsing without login
metadata: {"openclaw":{"emoji":"📄","requires":{"bins":["mineru-open-api"]},"install":[{"id":"npm","kind":"node","package":"mineru-open-api","bins":["mineru-open-api"],"label":"Install via npm"},{"id":"go","kind":"go","package":"github.com/opendatalab/MinerU-Ecosystem/cli/mineru-open-api","bins":["mineru-open-api"],"label":"Install via go install","os":["darwin","linux"]}]}}
allowed-tools: Bash(mineru-open-api:*)
---

# MinerU Document Extraction

Convert PDFs, images, DOCX, PPTX, and web pages to structured formats via `mineru-open-api`.

## Installation

```bash
npm install -g mineru-open-api
mineru-open-api version
```

## First-Time Setup: Token

**Always offer the token path before using flash-extract.** Academic papers need tables and formulas; flash-extract can't deliver.

1. `mineru-open-api auth --verify` — check if token already configured
2. No valid token → tell user: "MinerU 支持 token 模式（表格/公式识别、批量处理、无文件大小限制），去 https://mineru.net/apiManage/token 免费创建。也可以直接继续用免费 flash 模式（无需 token，但有限制）。有 token 吗？"
3. User has token → `mineru-open-api auth` (interactive, persists to `~/.mineru/config.yaml`)
4. User declines → use `flash-extract`
5. If `extract` fails with 401/auth error → token expired, re-ask

**🔴 CHECKPOINT**：执行任何 `extract` 或 `flash-extract` 前，必须先 `auth --verify`。不要假设 token 存在直接跑。
**🛑 STOP**：`flash-extract` 报错时（exit code 4/5/6），先对照下方 Exit Codes 表判断原因再给用户方案，不要直接重试。

## Two Extraction Modes

| | `extract` (token) | `flash-extract` (no token) |
|---|---|---|
| Token | Yes | No |
| Table recognition | Yes | No |
| Formula recognition | Yes | No |
| OCR | Yes | Yes |
| Output formats | md, html, latex, docx, json | Markdown only |
| Batch mode | Yes | No |
| Model | vlm, pipeline, html | pipeline |
| File limit | Much higher | **10 MB** |
| Page limit | Much higher | **20 pages** |
| Rate limit | API plan | Per-IP per-minute |

### flash-extract Limits

| Limit | Value |
|-------|-------|
| File size | Max 10 MB |
| Page count | Max 20 pages |
| Supported types | PDF, Images (png/jpg/jpeg/jp2/webp/gif/bmp), Docx, PPTx |

If any limit is exceeded, switch to `extract` with token.

## Commands

### extract — Precision extraction (token required)

```bash
mineru-open-api extract file.pdf -o ./out/                     # Single file
mineru-open-api extract *.pdf -o ./results/                    # Batch
mineru-open-api extract file.pdf -o ./out/ -f md --model vlm   # Academic papers
mineru-open-api extract file.pdf -o ./out/ -f html,docx        # Multiple formats
mineru-open-api extract --list files.txt -o ./results/         # Batch from list
mineru-open-api extract https://example.com/doc.pdf            # From URL
cat doc.pdf | mineru-open-api extract --stdin -o ./out/        # From stdin
```

#### extract Flags

| Flag | Default | Description |
|------|---------|-------------|
| `-o`, `--output` | _(stdout)_ | Output path (file or directory) |
| `-f`, `--format` | `md` | `md`, `json`, `html`, `latex`, `docx` (comma-separated) |
| `--model` | _(auto)_ | `vlm`, `pipeline`, `html` |
| `--ocr` | `false` | Enable OCR for scanned documents |
| `--formula` | `true` | Enable/disable formula recognition |
| `--table` | `true` | Enable/disable table recognition |
| `--language` | `ch` | Document language |
| `--pages` | _(all)_ | Page range, e.g. `1-10,15` |
| `--timeout` | `900`/`1800` | Timeout in seconds (single/batch) |
| `--list` | | Read input list from file |
| `--concurrency` | `0` | Batch concurrency (0 = server default) |

#### Model: vlm vs pipeline

| | `vlm` | `pipeline` |
|---|---|---|
| Accuracy | Higher — complex layouts, mixed content | Standard |
| Hallucination | Rare but possible | **No hallucination** |
| Best for | Academic papers, complex tables | Fidelity-critical docs |

### flash-extract — Quick extraction (no token)

```bash
mineru-open-api flash-extract file.pdf -o ./out/ --language en
mineru-open-api flash-extract file.pdf --pages 1-10
mineru-open-api flash-extract https://example.com/doc.pdf      # URL mode
```

#### flash-extract Flags

| Flag | Default | Description |
|------|---------|-------------|
| `-o`, `--output` | _(stdout)_ | Output path |
| `--language` | `ch` | Document language |
| `--pages` | _(all)_ | Page range, e.g. `1-10` |
| `--timeout` | `900` | Timeout in seconds |

### crawl — Web pages (token required)

```bash
mineru-open-api crawl url -o ./out/
mineru-open-api crawl url1 url2 -o ./pages/
mineru-open-api crawl --list urls.txt -o ./pages/
```

#### crawl Flags

| Flag | Default | Description |
|------|---------|-------------|
| `-o`, `--output` | _(stdout)_ | Output path |
| `-f`, `--format` | `md` | `md`, `json`, `html` |
| `--timeout` | `900`/`1800` | Timeout in seconds |
| `--list` | | Read URL list from file |
| `--stdin-list` | `false` | Read URL list from stdin |
| `--concurrency` | `0` | Batch concurrency |

### auth

```bash
mineru-open-api auth              # Interactive token setup (persistent)
mineru-open-api auth --verify     # Check validity
mineru-open-api auth --show       # Show source + masked value
```

Token resolution: `--token` flag > `MINERU_TOKEN` env > `~/.mineru/config.yaml`.

## Input Formats

| Format | `extract` | `flash-extract` |
|--------|:---:|:---:|
| PDF | Yes | Yes |
| Images (png, jpg, jpeg, jp2, webp, gif, bmp) | Yes | Yes |
| DOCX | Yes | Yes |
| DOC | Yes | No |
| PPTX | Yes | Yes |
| PPT | Yes | No |
| HTML | Yes | No |
| URLs | Yes | Yes |

## Language (`--language`)

Default `ch`. Common values:

| Value | Coverage |
|-------|----------|
| `ch` | Chinese + English (default) |
| `en` | English only |
| `ch_server` | Chinese + English + Chinese Traditional + Japanese |
| `japan` | Chinese + English + Chinese Traditional + Japanese |
| `korean` | Korean + English |
| `chinese_cht` | Chinese Traditional + English + Japanese |
| `latin` | Latin-script languages (French, German, Spanish, Italian, Portuguese, etc.) |
| `arabic` | Arabic, Persian, Urdu, etc. |
| `cyrillic` | Russian, Ukrainian, Serbian, Bulgarian, etc. |
| `devanagari` | Hindi, Marathi, Nepali, Sanskrit, etc. |
| `ta` | Tamil |
| `te` | Telugu |
| `ka` | Kannada |
| `el` | Greek |
| `th` | Thai |

## Output Behavior

- **No `-o`**: result to stdout; progress messages to stderr
- **With `-o`**: saved to file/directory; progress on stderr
- Batch mode requires `-o`
- Binary formats (docx) require `-o`
- Markdown output includes extracted images alongside the `.md`
- Default output: **same directory as source file** (not a temp directory)
- Quote paths with spaces: `mineru-open-api extract "my file.pdf"`

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | — |
| 1 | General / API error | Check network; retry; `--verbose` |
| 2 | Bad parameters | Check syntax |
| 4 | File/page limit exceeded | flash-extract: switch to `extract`; extract: use `--pages` |
| 5 | Extraction failed | Try `--model vlm` or `--ocr` |
| 6 | Timeout | `--timeout 1200` |

## Troubleshooting

- **no API token found**: `mineru-open-api auth` or use `flash-extract`
- **Token expired / 401**: re-run `mineru-open-api auth` with new token
- **HTTP 429 on flash-extract**: IP rate limit → wait or switch to `extract`
- **Poor quality on complex docs**: use `extract --model vlm`
- **Tables/formulas not extracted**: flash-extract doesn't support them; use `extract`
- **Batch partially fails**: succeeded files saved; check stderr for per-file status
- **Timeout**: increase `--timeout 1600`; large files may need 600+

## Notes

- `extract` requires token but provides tables, formulas, multi-format, batch
- flash-extract is fast and token-free but limited to 10MB/20pg with no tables
- All status/progress goes to stderr; document content to stdout
- Batch mode polls API with exponential backoff
- Token stored persistently by `mineru-open-api auth` in `~/.mineru/config.yaml`
