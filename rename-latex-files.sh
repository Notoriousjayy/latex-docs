#!/usr/bin/env bash
#===============================================================================
# rename-latex-files.sh
# 
# Comprehensive renaming of LaTeX files in src/ directory to follow consistent,
# descriptive naming conventions.
#
# Issues addressed:
#   - Generic names (main.tex, user-stories.tex)
#   - Awkward concatenations (missing hyphens/spaces)
#   - Inconsistent spelling (git-hub → github, type-script → typescript)
#   - Unclear abbreviations
#   - Inconsistent suffixes (-v2 vs -2)
#
# Run from the repository root (where src/ directory exists):
#   chmod +x rename-latex-files.sh
#   ./rename-latex-files.sh [--dry-run]
#
# Options:
#   --dry-run    Show what would be renamed without making changes
#===============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

DRY_RUN=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--dry-run]"
            echo ""
            echo "Comprehensive renaming of LaTeX files to consistent, descriptive names."
            echo ""
            echo "Options:"
            echo "  --dry-run    Show what would be renamed without making changes"
            echo "  -h, --help   Show this help message"
            exit 0
            ;;
    esac
done

# Counters
RENAMED=0
SKIPPED=0
ERRORS=0

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_section() {
    echo -e "${CYAN}[SECTION]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_rename() {
    local src_base=$(basename "$1")
    local dst_base=$(basename "$2")
    echo -e "  ${GREEN}→${NC} $src_base ${GREEN}→${NC} $dst_base"
}

# Function to safely rename a file
rename_file() {
    local src="$1"
    local dst="$2"
    
    # Check if source exists
    if [[ ! -f "$src" ]]; then
        # Silently skip - file may have been renamed in earlier migration
        return 0
    fi
    
    # Check if destination already exists
    if [[ -f "$dst" ]]; then
        log_warning "Destination exists, skipping: $(basename "$dst")"
        ((SKIPPED++)) || true
        return 0
    fi
    
    # Check if source and destination are the same
    if [[ "$src" == "$dst" ]]; then
        return 0
    fi
    
    if $DRY_RUN; then
        log_rename "$src" "$dst"
        ((RENAMED++)) || true
    else
        if mv "$src" "$dst"; then
            log_rename "$src" "$dst"
            ((RENAMED++)) || true
        else
            log_error "Failed to rename: $(basename "$src")"
            ((ERRORS++)) || true
        fi
    fi
}

#===============================================================================
# MAIN SCRIPT
#===============================================================================

echo ""
echo "============================================================"
echo "  LaTeX File Renaming Script (Comprehensive)"
echo "============================================================"
echo ""

if $DRY_RUN; then
    log_warning "Running in DRY-RUN mode - no changes will be made"
    echo ""
fi

# Verify we're in the right place
if [[ ! -d "src" ]]; then
    log_error "No 'src' directory found. Run this script from the repository root."
    exit 1
fi

log_info "Starting comprehensive file renames..."
echo ""

#===============================================================================
# ARCHITECTURE
#===============================================================================
log_section "Architecture"

# Generic main.tex files
rename_file "src/architecture/systems-engineering/main.tex" \
            "src/architecture/systems-engineering/systems-engineering-software-architecture.tex"

rename_file "src/architecture/togaf/main.tex" \
            "src/architecture/togaf/togaf-overview.tex"

# Fix concatenated names
rename_file "src/architecture/togaf/togafuser-stories.tex" \
            "src/architecture/togaf/togaf-user-stories.tex"

# Generic user-stories.tex
rename_file "src/architecture/togaf/user-stories.tex" \
            "src/architecture/togaf/togaf-adm-user-stories.tex"

#===============================================================================
# DATA SYSTEMS
#===============================================================================
log_section "Data Systems"

# Generic user-stories.tex
rename_file "src/data-systems/ai-ml/llm/user-stories.tex" \
            "src/data-systems/ai-ml/llm/llm-adoption-user-stories.tex"

#===============================================================================
# DEVOPS - GitHub Actions (fix "git-hub" → "github")
#===============================================================================
log_section "DevOps - GitHub Actions"

rename_file "src/devops/github-actions/advanced-git-hub-actions.tex" \
            "src/devops/github-actions/advanced-github-actions.tex"

rename_file "src/devops/github-actions/cicdstarter.tex" \
            "src/devops/github-actions/ci-cd-starter-github-actions-ghcr.tex"

rename_file "src/devops/github-actions/controlling-job-executionin-git-hub-actions.tex" \
            "src/devops/github-actions/controlling-job-execution-in-github-actions.tex"

rename_file "src/devops/github-actions/git-hub-actions-practical-cheat-sheet.tex" \
            "src/devops/github-actions/github-actions-practical-cheatsheet.tex"

rename_file "src/devops/github-actions/git-hub-actions-quick-reference-workflow-action-attributes.tex" \
            "src/devops/github-actions/github-actions-workflow-attributes-quick-reference.tex"

rename_file "src/devops/github-actions/git-hub-actions-workflows.tex" \
            "src/devops/github-actions/github-actions-workflows.tex"

rename_file "src/devops/github-actions/git-hub-actionsfora-wasmcpp-game.tex" \
            "src/devops/github-actions/github-actions-for-wasm-cpp-game.tex"

rename_file "src/devops/github-actions/minimal-git-hub-actionsfora-wasm-c-game.tex" \
            "src/devops/github-actions/minimal-github-actions-for-wasm-c-game.tex"

rename_file "src/devops/github-actions/workflows-in-git-hub-actions.tex" \
            "src/devops/github-actions/workflows-in-github-actions.tex"

#===============================================================================
# DEVOPS - Platform
#===============================================================================
log_section "DevOps - Platform"

# Generic user-stories.tex
rename_file "src/devops/platform/nginx/user-stories.tex" \
            "src/devops/platform/nginx/nginx-fundamentals-user-stories.tex"

# Kubernetes abbreviation
rename_file "src/devops/platform/kubernetes/k8s-sequenced-stories.tex" \
            "src/devops/platform/kubernetes/kubernetes-sequenced-user-stories.tex"

#===============================================================================
# DEVOPS - Secrets Management (fix concatenations)
#===============================================================================
log_section "DevOps - Secrets Management"

rename_file "src/devops/secrets-management/hashicorp-vault/vault-httpapiwith-postman.tex" \
            "src/devops/secrets-management/hashicorp-vault/vault-http-api-with-postman.tex"

#===============================================================================
# ELECTRONICS
#===============================================================================
log_section "Electronics"

rename_file "src/electronics/main.tex" \
            "src/electronics/art-of-electronics-curriculum.tex"

rename_file "src/electronics/main-2.tex" \
            "src/electronics/art-of-electronics-x-chapters-lab-course.tex"

#===============================================================================
# GAME DEVELOPMENT
#===============================================================================
log_section "Game Development"

# Generic main.tex
rename_file "src/game-development/design-documents/main.tex" \
            "src/game-development/design-documents/game-design-document-overview.tex"

# Fix concatenations in asset pipelines
rename_file "src/game-development/asset-pipelines/ai-assisted3dmodel-generation-pipeline.tex" \
            "src/game-development/asset-pipelines/ai-assisted-3d-model-generation-pipeline.tex"

rename_file "src/game-development/asset-pipelines/aisprite-generation-pipeline.tex" \
            "src/game-development/asset-pipelines/ai-sprite-generation-pipeline.tex"

#===============================================================================
# MATHEMATICS
#===============================================================================
log_section "Mathematics"

# Generic main.tex
rename_file "src/mathematics/geometry/main.tex" \
            "src/mathematics/geometry/computational-geometry-in-c-study-plan.tex"

# Fix concatenations in algebra
rename_file "src/mathematics/algebra/how-matricesand-polynomials-relateto-algebraic-operations.tex" \
            "src/mathematics/algebra/matrices-and-polynomials-algebraic-operations.tex"

rename_file "src/mathematics/algebra/polynomial-data-structuresin-cand-c.tex" \
            "src/mathematics/algebra/polynomial-data-structures-in-c-and-cpp.tex"

# Fix concatenations in geometry
rename_file "src/mathematics/geometry/polygon-data-structuresin-cand-c.tex" \
            "src/mathematics/geometry/polygon-data-structures-in-c-and-cpp.tex"

# Expand abbreviations for clarity
rename_file "src/mathematics/geometry/cgc-study-plan-user-stories.tex" \
            "src/mathematics/geometry/computational-geometry-c-user-stories.tex"

rename_file "src/mathematics/geometry/cgc-study-plan-user-stories-2.tex" \
            "src/mathematics/geometry/computational-geometry-c-user-stories-v2.tex"

rename_file "src/mathematics/geometry/dcg-study-plan-user-stories.tex" \
            "src/mathematics/geometry/discrete-computational-geometry-user-stories.tex"

#===============================================================================
# PERSONAL - Finance
#===============================================================================
log_section "Personal - Finance"

# Normalize -2 suffix to -v2
rename_file "src/personal/finance/cd-guide-2.tex" \
            "src/personal/finance/cd-guide-v2.tex"

#===============================================================================
# PERSONAL - Recipes (misnamed compilations)
#===============================================================================
log_section "Personal - Recipes"

# These are individual recipes misnamed as main-*.tex
rename_file "src/personal/recipes/compilations/main.tex" \
            "src/personal/recipes/compilations/zucchini-soup.tex"

rename_file "src/personal/recipes/compilations/main-v2.tex" \
            "src/personal/recipes/compilations/southwest-salad.tex"

rename_file "src/personal/recipes/compilations/main-v3.tex" \
            "src/personal/recipes/compilations/vegetable-soup.tex"

rename_file "src/personal/recipes/compilations/main-v4.tex" \
            "src/personal/recipes/compilations/shrimp-po-boys.tex"

# Normalize -v2 suffix in soups-stews
rename_file "src/personal/recipes/soups-stews/cioppino-seafood-stew-v2.tex" \
            "src/personal/recipes/soups-stews/cioppino-seafood-stew-detailed.tex"

rename_file "src/personal/recipes/soups-stews/creamy-vegetable-soup-v2.tex" \
            "src/personal/recipes/soups-stews/creamy-vegetable-soup-detailed.tex"

rename_file "src/personal/recipes/soups-stews/vegetable-soup-v2.tex" \
            "src/personal/recipes/soups-stews/vegetable-soup-detailed.tex"

rename_file "src/personal/recipes/soups-stews/zucchini-soup-v2.tex" \
            "src/personal/recipes/soups-stews/zucchini-soup-detailed.tex"

# Normalize in salads
rename_file "src/personal/recipes/salads/southwest-salad-v2.tex" \
            "src/personal/recipes/salads/southwest-salad-detailed.tex"

# Normalize in entrees
rename_file "src/personal/recipes/entrees/shrimp-po-boys-v2.tex" \
            "src/personal/recipes/entrees/shrimp-po-boys-detailed.tex"

#===============================================================================
# PROGRAMMING - Languages
#===============================================================================
log_section "Programming - Languages"

# Fix concatenation
rename_file "src/programming/languages/c-cpp/benefitsof-simulating-object-oriented-programmingin-cfor-embedded-systems.tex" \
            "src/programming/languages/c-cpp/oop-simulation-in-c-for-embedded-systems.tex"

# Fix "type-script" → "typescript"
rename_file "src/programming/languages/typescript/effective-type-script-user-stories.tex" \
            "src/programming/languages/typescript/effective-typescript-user-stories.tex"

rename_file "src/programming/languages/typescript/type-script-cookbook-user-stories.tex" \
            "src/programming/languages/typescript/typescript-cookbook-user-stories.tex"

#===============================================================================
# PROGRAMMING - Web Frontend
#===============================================================================
log_section "Programming - Web Frontend"

# Fix concatenation
rename_file "src/programming/web/frontend/designof-sites-user-stories.tex" \
            "src/programming/web/frontend/design-of-sites-user-stories.tex"

# Generic user-stories.tex files
rename_file "src/programming/web/frontend/user-stories.tex" \
            "src/programming/web/frontend/micro-frontends-board-user-stories.tex"

rename_file "src/programming/web/frontend/user-stories-2.tex" \
            "src/programming/web/frontend/dynamic-project-board-user-stories.tex"

#===============================================================================
# SECURITY - Application Security
#===============================================================================
log_section "Security - Application Security"

# Generic user-stories.tex
rename_file "src/security/application-security/fundamentals/user-stories.tex" \
            "src/security/application-security/fundamentals/ci-cd-github-actions-user-stories.tex"

#===============================================================================
# SECURITY - Certifications (fix concatenations)
#===============================================================================
log_section "Security - Certifications"

rename_file "src/security/certifications/ciso/cisouser-stories.tex" \
            "src/security/certifications/ciso/ciso-user-stories.tex"

rename_file "src/security/certifications/cissp/cisspuser-stories.tex" \
            "src/security/certifications/cissp/cissp-user-stories.tex"

#===============================================================================
# SECURITY - GHAS References (normalize cheatsheet naming)
#===============================================================================
log_section "Security - GHAS References"

rename_file "src/security/github-advanced-security/references/ghas-dependabot-cheatsheet-v2.tex" \
            "src/security/github-advanced-security/references/ghas-dependabot-cheatsheet-detailed.tex"

#===============================================================================
# SECURITY - OWASP (fix concatenations and improve naming)
#===============================================================================
log_section "Security - OWASP Standards"

# Generic user-stories.tex
rename_file "src/security/standards/owasp/user-stories.tex" \
            "src/security/standards/owasp/owasp-api-security-user-stories.tex"

# Fix concatenation in API security
rename_file "src/security/standards/owasp/owaspapisecurity-top10.tex" \
            "src/security/standards/owasp/owasp-api-security-top10.tex"

# Fix concatenations in OWASP Top 10 items
rename_file "src/security/standards/owasp/a012025-broken-access-control.tex" \
            "src/security/standards/owasp/owasp-a01-2025-broken-access-control.tex"

rename_file "src/security/standards/owasp/a022025-security-misconfiguration.tex" \
            "src/security/standards/owasp/owasp-a02-2025-security-misconfiguration.tex"

rename_file "src/security/standards/owasp/a032025-software-supply-chain-failures.tex" \
            "src/security/standards/owasp/owasp-a03-2025-software-supply-chain-failures.tex"

rename_file "src/security/standards/owasp/a042025-cryptographic-failures.tex" \
            "src/security/standards/owasp/owasp-a04-2025-cryptographic-failures.tex"

rename_file "src/security/standards/owasp/a052025-injection.tex" \
            "src/security/standards/owasp/owasp-a05-2025-injection.tex"

rename_file "src/security/standards/owasp/a062025-insecure-design.tex" \
            "src/security/standards/owasp/owasp-a06-2025-insecure-design.tex"

rename_file "src/security/standards/owasp/a072025-authentication-failures.tex" \
            "src/security/standards/owasp/owasp-a07-2025-authentication-failures.tex"

rename_file "src/security/standards/owasp/a082025-softwareor-data-integrity-failures.tex" \
            "src/security/standards/owasp/owasp-a08-2025-software-data-integrity-failures.tex"

rename_file "src/security/standards/owasp/a092025-security-logging-alerting-failures.tex" \
            "src/security/standards/owasp/owasp-a09-2025-security-logging-alerting-failures.tex"

rename_file "src/security/standards/owasp/a102025-mishandlingof-exceptional-conditions.tex" \
            "src/security/standards/owasp/owasp-a10-2025-mishandling-exceptional-conditions.tex"

#===============================================================================
# SUMMARY
#===============================================================================
echo ""
echo "============================================================"
echo "  Summary"
echo "============================================================"
if $DRY_RUN; then
    echo -e "  Mode:        ${YELLOW}DRY-RUN${NC}"
    echo -e "  Would rename: ${GREEN}$RENAMED${NC} files"
else
    echo -e "  Renamed:     ${GREEN}$RENAMED${NC} files"
fi
echo -e "  Skipped:     ${YELLOW}$SKIPPED${NC} files"
echo -e "  Errors:      ${RED}$ERRORS${NC} files"
echo "============================================================"
echo ""

if $DRY_RUN; then
    log_info "To execute the renames, run without --dry-run:"
    echo "  ./rename-latex-files.sh"
else
    if [[ $RENAMED -gt 0 ]]; then
        log_success "File renaming complete!"
        echo ""
        echo "Next steps:"
        echo "  1. Review the changes: git status"
        echo "  2. Update any cross-references (\\input, \\include) in .tex files"
        echo "  3. Stage changes: git add -A"
        echo "  4. Commit: git commit -m 'refactor: rename files to descriptive, consistent names'"
    else
        log_info "No files were renamed."
    fi
fi

exit 0
