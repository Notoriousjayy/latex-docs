#!/usr/bin/env bash
set -euo pipefail
PKG="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$PKG/../../.." && pwd)"
if [[ ! -f "$REPO/tooling/latex/style.sty" ]]; then
  echo 'Place package inside latex-docs before building with canonical semantic styles.' >&2
  exit 2
fi
OUTPUT="${ANIMATION_PDF_OUT:-/tmp/animation-timing-pdfs}"
mkdir -p "$OUTPUT"
export TEXINPUTS="$REPO/tooling/latex//:$REPO/tooling/styles/latex//:${TEXINPUTS:-}"
pass=0;fail=0
while IFS= read -r -d '' tex; do
  rel="${tex#"$PKG"/}"
  out="$OUTPUT/$(dirname "$rel")"
  mkdir -p "$out"
  if (cd "$(dirname "$tex")" && latexmk -pdf -shell-escape \
     -interaction=nonstopmode -halt-on-error -file-line-error \
     -outdir="$out" "$(basename "$tex")" >/dev/null 2>&1); then
    ((pass+=1))
  else
    echo "FAIL: $rel (inspect $out)" >&2
    ((fail+=1))
  fi
done < <(find "$PKG" -name '*.tex' -print0 | sort -z)
echo "Compiled: $pass; failed: $fail; output: $OUTPUT"
[[ "$fail" -eq 0 ]]
