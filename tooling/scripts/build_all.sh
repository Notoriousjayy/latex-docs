#!/usr/bin/env bash
#
# Build all LaTeX documents under src/ into build/
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SRC_DIR="$REPO_ROOT/src"
BUILD_DIR="$REPO_ROOT/build"

echo "Building LaTeX documents..."
echo "Source: $SRC_DIR"
echo "Output: $BUILD_DIR"

mkdir -p "$BUILD_DIR"

find "$SRC_DIR" -name "*.tex" -type f | while read -r tex_file; do
  relative_path="${tex_file#$SRC_DIR/}"
  output_dir="$BUILD_DIR/$(dirname "$relative_path")"
  mkdir -p "$output_dir"

  echo "Building: $relative_path"

  (
    cd "$(dirname "$tex_file")"
    pdflatex -interaction=nonstopmode -halt-on-error       -output-directory="$output_dir"       "$(basename "$tex_file")" > /dev/null 2>&1 || true

    pdflatex -interaction=nonstopmode -halt-on-error       -output-directory="$output_dir"       "$(basename "$tex_file")" > /dev/null 2>&1 || echo "  Warning: Build may have issues"
  )
done

echo "Build complete!"
echo "PDFs are in: $BUILD_DIR"
