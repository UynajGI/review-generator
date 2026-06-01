#!/bin/bash
# Detect which stage the review-generator project is at.
# Usage: bash scripts/status.sh [project_dir]
# Output: stage number (0-8) and human-readable status

DIR="${1:-.}"

echo "=== review-generator status ==="
echo "Directory: $(realpath "$DIR")"
echo ""

# Read recorded stage for cross-session continuity
recorded_stage=""
if [ -f "$DIR/.review-generator-stage" ]; then
  recorded_stage=$(head -n1 "$DIR/.review-generator-stage" | tr -d '[:space:]')
  echo "Recorded stage:      $recorded_stage (from .review-generator-stage)"
else
  echo "Recorded stage:      — (no .review-generator-stage yet)"
fi
echo ""

# Stage 0: no refs/ at all
if [ ! -d "$DIR/refs" ]; then
  echo "Stage: -1 — no refs/ directory yet (need to bootstrap)"
  echo "Next: create refs/ and sections/, then collect PDFs"
  exit 0
fi

# Count PDFs
pdf_count=$(find "$DIR/refs" -maxdepth 1 -name "*.pdf" 2>/dev/null | wc -l)

# Count MDs
md_count=$(find "$DIR/refs" -maxdepth 1 -name "*.md" -not -name "not_found*" 2>/dev/null | wc -l)

# Count sections
sec_count=$(find "$DIR/sections" -maxdepth 1 -name "sec_*.tex" 2>/dev/null | wc -l)

# Count images referenced in sections
img_count=0
if [ -d "$DIR/sections" ]; then
  img_count=$(grep -rh '\\includegraphics' "$DIR/sections/" 2>/dev/null | wc -l)
fi

# Has bib?
has_bib="no"
[ -f "$DIR/refs/refs.bib" ] && has_bib="yes"

# Has main.tex?
has_main="no"
[ -f "$DIR/main.tex" ] && has_main="yes"

# Print findings
echo "PDFs in refs/:      $pdf_count"
echo "MD files in refs/:   $md_count"
echo "Section .tex files:  $sec_count"
echo "Images in sections:  $img_count"
echo "refs.bib:            $has_bib"
echo "main.tex:            $has_main"
echo ""

# Count properly renamed PDFs (NN_Author_YYYY_Keyword.pdf or NN_Author_YYYY_Keyword__DOI.pdf)
renamed_count=0
doi_count=0
unnamed_samples=()
if [ "$pdf_count" -gt 0 ]; then
  for f in "$DIR/refs"/*.pdf; do
    base=$(basename "$f")
    if [[ "$base" =~ ^[0-9]{2}_[A-Za-z\ -]+_[0-9]{4}_.*\.pdf$ ]]; then
      ((renamed_count++))
      # Check if DOI/arXiv ID is appended (NN_Author_YYYY_Keyword__IDENTIFIER.pdf)
      if [[ "$base" =~ ^[0-9]{2}_[A-Za-z\ -]+_[0-9]{4}_.*__.*\.pdf$ ]]; then
        ((doi_count++))
      fi
    else
      unnamed_samples+=("$base")
    fi
  done
  # Truncate sample list to 5
  if [ ${#unnamed_samples[@]} -gt 5 ]; then
    unnamed_samples=("${unnamed_samples[@]:0:5}")
  fi
fi

# Check pdf2doi availability
pdf2doi_ok="no"
if command -v pdf2doi &>/dev/null; then
  pdf2doi_ok="yes"
fi

echo "Properly renamed:    $renamed_count/$pdf_count"
echo "With DOI/arXiv ID:   $doi_count/$pdf_count"
echo "pdf2doi available:   $pdf2doi_ok"
if [ "$renamed_count" -lt "$pdf_count" ] && [ "$pdf_count" -gt 0 ]; then
  echo "Unnamed examples:    ${unnamed_samples[*]}"
fi
echo ""

# Determine stage
if [ "$renamed_count" -lt "$pdf_count" ] && [ "$pdf_count" -gt 0 ]; then
  echo "Stage: 1 — PDF 未规范命名"
  if [ "$pdf2doi_ok" = "no" ]; then
    echo "Next: pipx install pdf2doi → pdf2doi refs/ 提取 DOI → Crossref 查元数据 → 重命名为 NN_Author_YYYY_Keyword__IDENTIFIER.pdf"
  else
    echo "Next: pdf2doi refs/ 提取 DOI → Crossref 查元数据 → 重命名为 NN_Author_YYYY_Keyword__IDENTIFIER.pdf"
  fi
elif [ "$doi_count" -lt "$pdf_count" ] && [ "$pdf_count" -gt 0 ]; then
  echo "Stage: 1 — PDF 已重命名但缺少 DOI/arXiv ID"
  echo "Next: pdf2doi refs/ 提取 DOI → 用 DOI 元数据修正 author/year → 重新编号 → 追加 DOI 到文件名"
elif [ "$pdf_count" -gt 0 ] && [ "$md_count" -eq 0 ]; then
  echo "Stage: 2 — ready for MinerU extraction"
  echo "Prerequisite: load mineru-document-extractor skill and verify availability before proceeding"
elif [ "$md_count" -gt 0 ] && [ "$sec_count" -eq 0 ]; then
  echo "Stage: 3 — ready for parallel deep-reading"
elif [ "$sec_count" -gt 0 ] && [ "$img_count" -eq 0 ]; then
  echo "Stage: 4 — ready for image insertion"
elif [ "$sec_count" -gt 0 ] && [ "$img_count" -gt 0 ] && [ "$has_bib" = "no" ]; then
  echo "Stage: 5 — ready for bibliography"
elif [ "$has_main" = "yes" ] && [ "$has_bib" = "yes" ]; then
  echo "Stage: 6/7 — compile + review"
else
  echo "Stage: 4-5 — in progress (has sections=$sec_count, images=$img_count, bib=$has_bib)"
fi

# Cross-session hint
if [ -n "$recorded_stage" ]; then
  echo ""
  echo "Note: .review-generator-stage records Stage $recorded_stage as last completed."
  echo "If filesystem state suggests an earlier stage, some steps may need to be redone."
fi
