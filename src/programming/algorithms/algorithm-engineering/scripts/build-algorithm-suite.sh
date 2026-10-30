#!/usr/bin/env bash
set -euo pipefail
PACKAGE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_ROOT="${ALGO_SUITE_SOURCE_ROOT:-${PACKAGE_ROOT}}"
OUTPUT_ROOT="${ALGO_SUITE_OUTPUT_ROOT:-${PACKAGE_ROOT}/build/pdf}"
mkdir -p "$OUTPUT_ROOT"
if ! command -v pdflatex >/dev/null; then
  echo 'pdflatex is required' >&2
  exit 2
fi
success=0
failures=0
while IFS= read -r -d '' file; do
  folder="$(dirname "$file")"
  name="$(basename "${file%.tex}")"
  target="$OUTPUT_ROOT/$(basename "$folder")"
  mkdir -p "$target"
  if [[ "${ALGO_SUITE_SKIP_EXISTING:-0}" == "1" ]] && [[ -s "$target/$name.pdf" ]] && pdfinfo "$target/$name.pdf" >/dev/null 2>&1; then
    echo "[skip] $(basename "$folder")/$name"
    success=$((success+1))
    continue
  fi
  echo "[latex] $(basename "$folder")/$name"
  if (cd "$folder" && pdflatex -interaction=nonstopmode -halt-on-error -file-line-error \
       -output-directory="$target" "$name.tex" > "$target/$name-pass1.txt" 2>&1 && \
       pdflatex -interaction=nonstopmode -halt-on-error -file-line-error \
       -output-directory="$target" "$name.tex" > "$target/$name-pass2.txt" 2>&1); then
    success=$((success+1))
  else
    echo "FAILED: $file (see $target/$name-pass*.txt)" >&2
    failures=$((failures+1))
  fi
done < <(find "$SOURCE_ROOT" -name '*.tex' ! -path '*/shared/*' -print0 | sort -z)
echo "Compiled $success LaTeX documents; failed $failures."
if ((failures)); then exit 1; fi
