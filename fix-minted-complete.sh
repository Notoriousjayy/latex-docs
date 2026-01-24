#!/bin/bash
# fix-minted-usepackage-only.sh
#
# This script adds cache=false ONLY to \usepackage{minted} lines.
# This is safe because \usepackage{minted} only appears inside the
# shell-escape conditional block where minted is actually loaded.
#
# We do NOT modify \setminted, \providecommand, or any other commands
# that might be stub definitions in the listings fallback.

set -euo pipefail

TARGET_DIR="${1:-src}"

echo "=============================================="
echo "PRECISE MINTED FIX - usepackage only"
echo "=============================================="
echo "Target: $TARGET_DIR"
echo ""

# Use a different delimiter for sed (| instead of /) to avoid issues with special chars
# Process files one at a time to avoid issues with filenames

echo "=== Adding cache=false to \\usepackage{minted} lines ==="

# Pattern 1: \usepackage[newfloat]{minted} -> \usepackage[newfloat,cache=false]{minted}
echo "Pattern 1: [newfloat] -> [newfloat,cache=false]"
find "$TARGET_DIR" -name "*.tex" -type f -print0 | while IFS= read -r -d '' file; do
    if grep -q '\\usepackage\[newfloat\]{minted}' "$file" 2>/dev/null; then
        sed -i 's|\\usepackage\[newfloat\]{minted}|\\usepackage[newfloat,cache=false]{minted}|g' "$file"
        echo "  Fixed: $file"
    fi
done

# Pattern 2: \usepackage{minted} (no options) -> \usepackage[cache=false]{minted}
echo "Pattern 2: {minted} -> [cache=false]{minted}"
find "$TARGET_DIR" -name "*.tex" -type f -print0 | while IFS= read -r -d '' file; do
    # Only match \usepackage{minted} NOT \usepackage[...]{minted}
    if grep -qE '\\usepackage\{minted\}' "$file" 2>/dev/null; then
        # Make sure it's not already \usepackage[...]{minted}
        if ! grep -q '\\usepackage\[.*\]{minted}' "$file" 2>/dev/null; then
            sed -i 's|\\usepackage{minted}|\\usepackage[cache=false]{minted}|g' "$file"
            echo "  Fixed: $file"
        fi
    fi
done

# Pattern 3: Other option combinations - add cache=false if not present
echo "Pattern 3: Adding cache=false to other option combinations"
find "$TARGET_DIR" -name "*.tex" -type f -print0 | while IFS= read -r -d '' file; do
    # If file has \usepackage[...]{minted} but no cache=false in that line
    if grep -q '\\usepackage\[.*\]{minted}' "$file" 2>/dev/null; then
        if ! grep '\\usepackage\[.*\]{minted}' "$file" | grep -q 'cache=false'; then
            # Add cache=false after the opening bracket
            sed -i 's|\\usepackage\[\([^]]*\)\]{minted}|\\usepackage[\1,cache=false]{minted}|g' "$file"
            echo "  Fixed: $file"
        fi
    fi
done

# Clean up any double cache=false that might have been created
echo ""
echo "=== Cleaning up duplicates ==="
find "$TARGET_DIR" -name "*.tex" -type f -print0 | while IFS= read -r -d '' file; do
    if grep -q 'cache=false,cache=false' "$file" 2>/dev/null; then
        sed -i 's|cache=false,cache=false|cache=false|g' "$file"
        echo "  Cleaned: $file"
    fi
done

# Clean up ,cache=false,cache=false patterns
find "$TARGET_DIR" -name "*.tex" -type f -exec sed -i 's|,cache=false,cache=false|,cache=false|g' {} \;

echo ""
echo "=== Verification ==="
echo ""
echo "Files with \\usepackage{minted} and cache=false:"
grep -rn 'usepackage.*minted' "$TARGET_DIR" --include="*.tex" | grep -c 'cache=false' || echo "0"

echo ""
echo "Files with \\usepackage{minted} WITHOUT cache=false (should be 0):"
grep -rn 'usepackage.*{minted}' "$TARGET_DIR" --include="*.tex" | grep -v 'cache=false' | grep -v 'minted-config' | wc -l

echo ""
echo "Sample of fixed lines:"
grep -rn 'usepackage.*cache=false.*minted' "$TARGET_DIR" --include="*.tex" | head -5

echo ""
echo "=============================================="
echo "DONE"
echo "=============================================="