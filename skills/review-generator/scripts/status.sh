#!/bin/bash
# Detect which stage the lit-review project is at.
# Usage: bash scripts/status.sh [project_dir]
# Output: stage number (0-8) and human-readable status

DIR="${1:-.}"

echo "=== lit-review status ==="
echo "Directory: $(realpath "$DIR")"
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

# Determine stage
if [ "$pdf_count" -eq 0 ] && [ "$md_count" -eq 0 ]; then
  echo "Stage: 1 — PDFs collected, rename them"
elif [ "$pdf_count" -gt 0 ] && [ "$md_count" -eq 0 ]; then
  echo "Stage: 2 — ready for MinerU extraction"
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
