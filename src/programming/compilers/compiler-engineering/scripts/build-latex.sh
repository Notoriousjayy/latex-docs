#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/build/pdf}"
mkdir -p "$OUT"
for family in technical-references study-guides curricula laboratories workbooks procedures security-assessments templates blank; do
  mkdir -p "$OUT/$family"
  for f in "$ROOT/$family"/*.tex; do
    [ -f "$f" ] || continue
    (cd "$ROOT/$family" && latexmk -pdf -quiet -interaction=nonstopmode -halt-on-error -output-directory="$OUT/$family" "$(basename "$f")")
  done
done
