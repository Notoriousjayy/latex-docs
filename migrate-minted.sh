#!/bin/bash
# migrate-minted.sh
# Updates existing .tex files to use CI-safe minted configuration
#
# Usage: ./migrate-minted.sh [--dry-run] [directory]

set -euo pipefail

DRY_RUN=false
TARGET_DIR="${2:-src}"

if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    TARGET_DIR="${2:-src}"
    echo "=== DRY RUN MODE ==="
fi

echo "Scanning $TARGET_DIR for minted usage..."

# Find all .tex files using minted
FILES_WITH_MINTED=$(grep -rl '\\usepackage.*{minted}' "$TARGET_DIR" --include="*.tex" 2>/dev/null || true)
FILES_WITH_FROZENCACHE=$(grep -rl 'frozencache' "$TARGET_DIR" --include="*.tex" 2>/dev/null || true)

echo ""
echo "Files with \\usepackage{minted}: $(echo "$FILES_WITH_MINTED" | grep -c . || echo 0)"
echo "Files with frozencache option:   $(echo "$FILES_WITH_FROZENCACHE" | grep -c . || echo 0)"

if [[ -z "$FILES_WITH_MINTED" ]]; then
    echo "No files to update."
    exit 0
fi

echo ""
echo "=== Migration Options ==="
echo ""
echo "Option 1: Replace minted with minted-config (recommended)"
echo "  Changes: \\usepackage{minted} -> \\usepackage{minted-config}"
echo "  Requires: shared/minted-config.sty in TEXINPUTS"
echo ""
echo "Option 2: Add cache=false to existing minted packages"
echo "  Changes: \\usepackage{minted} -> \\usepackage[cache=false]{minted}"
echo "  Changes: \\usepackage[frozencache]{minted} -> \\usepackage[cache=false]{minted}"
echo ""

read -p "Choose option (1/2) or 'q' to quit: " CHOICE

case "$CHOICE" in
    1)
        echo ""
        echo "Applying Option 1: Replace with minted-config..."
        
        for file in $FILES_WITH_MINTED; do
            echo "  Processing: $file"
            
            if $DRY_RUN; then
                echo "    Would replace minted package declarations"
            else
                # Handle various minted package patterns
                sed -i.bak \
                    -e 's/\\usepackage\[frozencache\]{minted}/\\usepackage{minted-config}/g' \
                    -e 's/\\usepackage\[cache=false\]{minted}/\\usepackage{minted-config}/g' \
                    -e 's/\\usepackage\[cache=true[^]]*\]{minted}/\\usepackage{minted-config}/g' \
                    -e 's/\\usepackage{minted}/\\usepackage{minted-config}/g' \
                    "$file"
                
                # Remove backup if no changes
                if diff -q "$file" "${file}.bak" > /dev/null 2>&1; then
                    rm "${file}.bak"
                else
                    echo "    ✓ Updated"
                    rm "${file}.bak"
                fi
            fi
        done
        ;;
        
    2)
        echo ""
        echo "Applying Option 2: Add cache=false..."
        
        for file in $FILES_WITH_MINTED; do
            echo "  Processing: $file"
            
            if $DRY_RUN; then
                echo "    Would add cache=false option"
            else
                sed -i.bak \
                    -e 's/\\usepackage\[frozencache\]{minted}/\\usepackage[cache=false]{minted}/g' \
                    -e 's/\\usepackage{minted}/\\usepackage[cache=false]{minted}/g' \
                    "$file"
                
                if diff -q "$file" "${file}.bak" > /dev/null 2>&1; then
                    rm "${file}.bak"
                else
                    echo "    ✓ Updated"
                    rm "${file}.bak"
                fi
            fi
        done
        ;;
        
    q|Q)
        echo "Aborted."
        exit 0
        ;;
        
    *)
        echo "Invalid choice."
        exit 1
        ;;
esac

echo ""
echo "=== Migration Complete ==="
echo ""
echo "Next steps:"
echo "1. Add shared/minted-config.sty to your repo (if using Option 1)"
echo "2. Add .latexmkrc to your repo root"
echo "3. Update .github/workflows/ with the new build workflow"
echo "4. Run a test build locally:"
echo "   TEXINPUTS=./shared//: latexmk -pdflatex -shell-escape your-doc.tex"
echo ""
