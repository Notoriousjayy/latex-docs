#!/bin/bash
# fix-minted-complete.sh - Find and fix ALL minted caching issues
# This script addresses frozencache in ALL locations, not just \usepackage

set -euo pipefail

TARGET_DIR="${1:-src}"

echo "=== Complete Minted Cache Fix Script ==="
echo "Target: $TARGET_DIR"
echo ""

# List of known failing files (from CI output)
FAILING_FILES=(
    # DevOps
    "devops/foundations/sdlc/explore-github.tex"
    "devops/github-actions/ci-cd-starter-github-actions-ghcr.tex"
    "devops/github-actions/github-actions-for-wasm-cpp-game.tex"
    "devops/github-actions/github-actions-workflows.tex"
    "devops/github-actions/minimal-github-actions-for-wasm-c-game.tex"
    "devops/github-actions/workflows-in-github-actions.tex"
    "devops/platform/github/github-profile.tex"
    "devops/platform/github/releases-quick-reference.tex"
    "devops/secrets-management/hashicorp-vault/vault-dev-server.tex"
    "devops/secrets-management/hashicorp-vault/vault-http-api-with-postman.tex"
    "devops/secrets-management/hashicorp-vault/vault-production-style.tex"
    "devops/secrets-management/hashicorp-vault/vault-secrets-access-primer.tex"
    # Security
    "security/application-security/processes/appsec-cicd-pipeline-mapping.tex"
    "security/github-advanced-security/administration/ghas-best-practices.tex"
    "security/github-advanced-security/administration/practical-overview-ghas.tex"
    "security/github-advanced-security/code-scanning/applying-codeql-scanning.tex"
    "security/github-advanced-security/code-scanning/codeql-triage-sop.tex"
    "security/github-advanced-security/dependabot/dependabot-alerts.tex"
    "security/github-advanced-security/references/code-scanning-cheatsheet.tex"
    "security/github-advanced-security/references/codeql-cheatsheet.tex"
    "security/github-advanced-security/references/dependabot-cheatsheet.tex"
    "security/github-advanced-security/references/ghas-cheatsheet.tex"
    "security/github-advanced-security/references/ghas-dependabot-cheatsheet-detailed.tex"
    "security/github-advanced-security/references/secret-scanning-cheatsheet.tex"
    "security/github-advanced-security/secret-scanning/ghas-secret-scanning-sop.tex"
    "security/github-advanced-security/secret-scanning/secret-scanning-triage-sop.tex"
    # Game Development
    "game-development/physics-engines/physics-engine-gap-analysis.tex"
)

echo "=== Step 1: Diagnose - Check what's in failing files ==="
echo ""

for relpath in "${FAILING_FILES[@]}"; do
    filepath="$TARGET_DIR/$relpath"
    if [[ -f "$filepath" ]]; then
        echo "--- $relpath ---"
        
        # Check for frozencache anywhere
        frozen=$(grep -n 'frozencache' "$filepath" 2>/dev/null || true)
        if [[ -n "$frozen" ]]; then
            echo "  FOUND frozencache:"
            echo "$frozen" | sed 's/^/    /'
        fi
        
        # Check for \setminted
        setminted=$(grep -n '\\setminted' "$filepath" 2>/dev/null || true)
        if [[ -n "$setminted" ]]; then
            echo "  FOUND \\setminted:"
            echo "$setminted" | sed 's/^/    /'
        fi
        
        # Check for cache= options
        cache=$(grep -n 'cache=' "$filepath" 2>/dev/null || true)
        if [[ -n "$cache" ]]; then
            echo "  FOUND cache= options:"
            echo "$cache" | sed 's/^/    /'
        fi
        
        # Check for .pyg references
        pyg=$(grep -n '\.pyg' "$filepath" 2>/dev/null || true)
        if [[ -n "$pyg" ]]; then
            echo "  FOUND .pyg references:"
            echo "$pyg" | sed 's/^/    /'
        fi
        
        # Check minted usepackage line
        usepackage=$(grep -n 'usepackage.*minted' "$filepath" 2>/dev/null || true)
        if [[ -n "$usepackage" ]]; then
            echo "  minted usepackage:"
            echo "$usepackage" | sed 's/^/    /'
        fi
        
        echo ""
    fi
done

echo "=== Step 2: Apply Fixes ==="
echo ""

# Fix 1: Replace ALL occurrences of frozencache with cache=false
echo "Fix 1: Replacing frozencache -> cache=false globally..."
find "$TARGET_DIR" -name "*.tex" -type f -exec grep -l 'frozencache' {} \; 2>/dev/null | while read -r file; do
    sed -i 's/frozencache/cache=false/g' "$file"
    echo "  ✓ Fixed frozencache in: $file"
done

# Fix 2: Ensure \setminted has cache=false
echo ""
echo "Fix 2: Checking \\setminted commands..."
find "$TARGET_DIR" -name "*.tex" -type f -exec grep -l '\\setminted' {} \; 2>/dev/null | while read -r file; do
    # If \setminted exists but doesn't have cache=false, we need to add it
    if grep -q '\\setminted{' "$file" && ! grep '\\setminted{' "$file" | grep -q 'cache=false'; then
        # Add cache=false to \setminted{...}
        sed -i 's/\\setminted{/\\setminted{cache=false,/g' "$file"
        echo "  ✓ Added cache=false to \\setminted in: $file"
    fi
done

# Fix 3: Handle minted environments with options
echo ""
echo "Fix 3: Checking minted environments with frozencache..."
find "$TARGET_DIR" -name "*.tex" -type f -print0 2>/dev/null | while IFS= read -r -d '' file; do
    # Check for \begin{minted}[...frozencache...] patterns
    if grep -q 'begin{minted}\[.*frozencache' "$file" 2>/dev/null; then
        sed -i 's/\(begin{minted}\[.*\)frozencache/\1cache=false/g' "$file"
        echo "  ✓ Fixed minted environment in: $file"
    fi
done

# Fix 4: Remove any .pyg file references (these are for frozencache mode)
echo ""
echo "Fix 4: Checking for hardcoded .pyg references..."
find "$TARGET_DIR" -name "*.tex" -type f -exec grep -l '\.pyg' {} \; 2>/dev/null | while read -r file; do
    echo "  ⚠ WARNING: $file contains .pyg references - may need manual review"
done

# Fix 5: Clean up cache directories
echo ""
echo "Fix 5: Removing _minted-* cache directories..."
find "$TARGET_DIR" -type d -name '_minted-*' -exec rm -rf {} + 2>/dev/null || true
echo "  ✓ Cache directories removed"

# Fix 6: Remove stale .pyg, .pygtex, .pygstyle files
echo ""
echo "Fix 6: Removing stale pygments files..."
find "$TARGET_DIR" -type f \( -name "*.pyg" -o -name "*.pygtex" -o -name "*.pygstyle" \) -delete 2>/dev/null || true
echo "  ✓ Stale pygments files removed"

echo ""
echo "=== Step 3: Verification ==="
echo ""

# Check for remaining issues
remaining_frozen=$(grep -rln 'frozencache' "$TARGET_DIR" --include="*.tex" 2>/dev/null | wc -l || echo 0)
echo "Remaining frozencache references: $remaining_frozen"

remaining_pyg=$(find "$TARGET_DIR" -name "*.pyg" -type f 2>/dev/null | wc -l || echo 0)
echo "Remaining .pyg files: $remaining_pyg"

echo ""
echo "=== Summary of minted configurations in failing files ==="
echo ""
for relpath in "${FAILING_FILES[@]}"; do
    filepath="$TARGET_DIR/$relpath"
    if [[ -f "$filepath" ]]; then
        minted_line=$(grep 'usepackage.*minted' "$filepath" 2>/dev/null | head -1 || echo "NOT FOUND")
        setminted_line=$(grep '\\setminted' "$filepath" 2>/dev/null | head -1 || echo "")
        echo "$relpath:"
        echo "  usepackage: $minted_line"
        [[ -n "$setminted_line" ]] && echo "  setminted: $setminted_line"
    fi
done

echo ""
echo "=== Done ==="
echo ""
echo "If files still fail, check for:"
echo "1. \\setminted commands that override cache settings"
echo "2. Individual minted environment options: \\begin{minted}[cache=true]{...}"
echo "3. \\inputminted commands with cache options"
echo "4. Custom minted wrapper commands"
