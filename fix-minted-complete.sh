#!/bin/bash
# fix-remove-all-cache-options.sh
# 
# ROOT CAUSE: We replaced "frozencache" with "cache=false", but "cache=false" was
# added to places that don't understand it (listings fallback, stub commands, etc.)
#
# SOLUTION: Remove ALL caching options entirely. When minted runs with shell-escape,
# it will generate syntax highlighting on-the-fly (no caching needed).

set -euo pipefail

TARGET_DIR="${1:-src}"

echo "=============================================="
echo "COMPREHENSIVE MINTED CACHE FIX"
echo "=============================================="
echo "Target: $TARGET_DIR"
echo ""

echo "=== PHASE 1: Remove ALL cache-related options ==="
echo ""

# 1a. Remove cache=false from \usepackage options
echo "Step 1a: Cleaning \\usepackage[...]{minted} options..."
# [newfloat,cache=false] -> [newfloat]
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/\\usepackage\[newfloat,cache=false\]{minted}/\\usepackage[newfloat]{minted}/g' {} \;
# [cache=false,newfloat] -> [newfloat]
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/\\usepackage\[cache=false,newfloat\]{minted}/\\usepackage[newfloat]{minted}/g' {} \;
# [cache=false] -> (no options)
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/\\usepackage\[cache=false\]{minted}/\\usepackage{minted}/g' {} \;
# Handle other combinations with commas
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/,cache=false,/,/g' {} \;
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/,cache=false\]/]/g' {} \;
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/\[cache=false,/[/g' {} \;
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/,cache=false}/}/g' {} \;
echo "  ✓ Done"

# 1b. Remove frozencache from \usepackage options (in case any remain)
echo "Step 1b: Removing any remaining frozencache..."
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/\\usepackage\[frozencache\]{minted}/\\usepackage{minted}/g' {} \;
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/,frozencache,/,/g' {} \;
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/,frozencache\]/]/g' {} \;
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/\[frozencache,/[/g' {} \;
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/,frozencache}/}/g' {} \;
echo "  ✓ Done"

# 1c. Remove cache options from \setminted commands
echo "Step 1c: Cleaning \\setminted commands..."
# \setminted{cache=false,...} -> \setminted{...}
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/\\setminted{cache=false,/\\setminted{/g' {} \;
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/\\setminted{cache=false}/\\setminted{}/g' {} \;
# \setminted{...,cache=false} -> \setminted{...}
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/,cache=false}/}/g' {} \;
# \setminted{frozencache,...} -> \setminted{...}
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/\\setminted{frozencache,/\\setminted{/g' {} \;
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/\\setminted{frozencache}/\\setminted{}/g' {} \;
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/,frozencache}/}/g' {} \;
# Clean up empty \setminted{}
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/\\setminted{}//g' {} \;
echo "  ✓ Done"

# 1d. Remove cache options from \begin{minted}[...] environments
echo "Step 1d: Cleaning minted environment options..."
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/\\begin{minted}\[cache=false,/\\begin{minted}[/g' {} \;
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/\\begin{minted}\[cache=false\]/\\begin{minted}/g' {} \;
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/\\begin{minted}\[frozencache,/\\begin{minted}[/g' {} \;
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/\\begin{minted}\[frozencache\]/\\begin{minted}/g' {} \;
echo "  ✓ Done"

# 1e. Clean up empty option brackets
echo "Step 1e: Cleaning up empty option brackets..."
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/\\begin{minted}\[\]/\\begin{minted}/g' {} \;
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's/\\usepackage\[\]{minted}/\\usepackage{minted}/g' {} \;
echo "  ✓ Done"

echo ""
echo "=== PHASE 2: Remove cache directories and files ==="
echo ""

echo "Step 2a: Removing _minted-* cache directories..."
find "$TARGET_DIR" -type d -name '_minted-*' -exec rm -rf {} + 2>/dev/null || true
echo "  ✓ Done"

echo "Step 2b: Removing stale .pyg/.pygtex/.pygstyle files..."
find "$TARGET_DIR" -type f \( -name "*.pyg" -o -name "*.pygtex" -o -name "*.pygstyle" \) -delete 2>/dev/null || true
echo "  ✓ Done"

echo ""
echo "=== PHASE 3: Verification ==="
echo ""

echo "Checking for remaining problematic patterns:"
echo ""

echo "1. Files with 'cache=false' (should be 0):"
count=$(grep -rln 'cache=false' "$TARGET_DIR" --include="*.tex" 2>/dev/null | wc -l || echo "0")
echo "   Count: $count"
if [ "$count" -gt 0 ]; then
    echo "   Files:"
    grep -rln 'cache=false' "$TARGET_DIR" --include="*.tex" 2>/dev/null | head -10
fi

echo ""
echo "2. Files with 'frozencache' (should be 0):"
count=$(grep -rln 'frozencache' "$TARGET_DIR" --include="*.tex" 2>/dev/null | wc -l || echo "0")
echo "   Count: $count"
if [ "$count" -gt 0 ]; then
    echo "   Files:"
    grep -rln 'frozencache' "$TARGET_DIR" --include="*.tex" 2>/dev/null | head -10
fi

echo ""
echo "3. Sample of minted configurations:"
grep -rn 'usepackage.*{minted}' "$TARGET_DIR" --include="*.tex" 2>/dev/null | head -10

echo ""
echo "=============================================="
echo "FIX COMPLETE"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. git add -A"
echo "2. git commit -m 'fix: remove all minted cache options for CI compatibility'"
echo "3. git push"