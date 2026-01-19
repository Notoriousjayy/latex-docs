#!/bin/bash
#
# LaTeX Docs Repository Reorganization Script
# ============================================
# This script reorganizes the latex-docs repository by:
# 1. Creating a new category-based directory structure
# 2. Finding all .tex files and moving them to appropriate categories
# 3. Flattening the deeply nested structure
# 4. Updating .gitignore to exclude PDFs and LaTeX build artifacts
# 5. Removing tracked PDFs from git
# 6. Cleaning up empty directories and orphans
#
# Usage: ./reorganize-latex-docs.sh [--dry-run]
#
# Run with --dry-run first to see what changes will be made without executing them.

set -euo pipefail

# Configuration
REPO_ROOT="${REPO_ROOT:-$(pwd)}"
OLD_DOCS_DIR="$REPO_ROOT/docs/docs"
NEW_DOCS_DIR="$REPO_ROOT/src"
DRY_RUN=false
VERBOSE=true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --quiet)
            VERBOSE=false
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Logging functions
log_info() {
    if $VERBOSE; then
        echo -e "${BLUE}[INFO]${NC} $1"
    fi
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

log_action() {
    if $DRY_RUN; then
        echo -e "${YELLOW}[DRY-RUN]${NC} Would: $1"
    else
        echo -e "${GREEN}[ACTION]${NC} $1"
    fi
}

# Execute command (respects dry-run)
execute() {
    if $DRY_RUN; then
        log_action "$*"
    else
        "$@"
    fi
}

# Create directory (respects dry-run)
ensure_dir() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        execute mkdir -p "$dir"
    fi
}

# Move file with logging (respects dry-run)
move_file() {
    local src="$1"
    local dest="$2"
    local dest_dir
    dest_dir=$(dirname "$dest")
    
    ensure_dir "$dest_dir"
    
    if [[ -f "$src" ]]; then
        log_action "Move: $src -> $dest"
        if ! $DRY_RUN; then
            mv "$src" "$dest"
        fi
    else
        log_warning "Source file not found: $src"
    fi
}

# Determine category for a given path
get_category() {
    local path="$1"
    local lower_path
    lower_path=$(echo "$path" | tr '[:upper:]' '[:lower:]')
    
    # Security
    if [[ "$lower_path" =~ appsec|security-polic|modeling-application-security ]]; then
        echo "security/appsec"
    elif [[ "$lower_path" =~ ciso && ! "$lower_path" =~ cissp ]]; then
        echo "security/certifications/ciso"
    elif [[ "$lower_path" =~ cissp ]]; then
        echo "security/certifications/cissp"
    elif [[ "$lower_path" =~ computer-and-information-security-handbook|cish4e ]]; then
        echo "security/certifications/cish"
    elif [[ "$lower_path" =~ cloud-computing-security|secure-internal-apps|secure-internet-facing ]]; then
        echo "security/cloud-security"
    elif [[ "$lower_path" =~ /ghas/|ghas-|secret-scanning|codeql|dependabot|code-scanning ]]; then
        echo "security/ghas"
    elif [[ "$lower_path" =~ owasp ]]; then
        echo "security/owasp"
    
    # Architecture
    elif [[ "$lower_path" =~ documenting-software-architecture|allocation-style|module-style|component-and-connector|viewpoint|dodaf|iso.*42010|rozanski|rup.*views|spectrum.*style|stakeholder.*documentation|variab|architecture.*template|architecture.*beyond|interface.*documentation|primary.*presentation|element.*catalog|context.*diagram|rationale|architecture.*playbook|architecture.*overview|architecture.*review|architecture.*framework ]]; then
        echo "architecture/documenting-software-architecture"
    elif [[ "$lower_path" =~ togaf ]]; then
        echo "architecture/togaf"
    elif [[ "$lower_path" =~ enterprise-architecture ]]; then
        echo "architecture/enterprise"
    elif [[ "$lower_path" =~ confluence|build-system-facade ]]; then
        echo "architecture/system-design"
    elif [[ "$lower_path" =~ systems-engineering|systems-curriculum ]]; then
        echo "architecture/systems-engineering"
    elif [[ "$lower_path" =~ cloud.*governance.*control.*framework ]]; then
        echo "architecture/cloud-governance"
    
    # DevOps - GitHub Actions
    elif [[ "$lower_path" =~ github-actions|actions.*custom|actions.*input|cicd.*starter|workflow.*github|controlling.*job|github.*actions.*quick ]]; then
        echo "devops/github-actions"
    
    # DevOps - CI/CD
    elif [[ "$lower_path" =~ cicd|ci-cd|continuous-integration|continuous-delivery|release-engineering|analyze-sdlc|ci-toolkit|16.*gate|16-gate ]]; then
        echo "devops/ci-cd"
    
    # DevOps - Git/GitHub (non-actions)
    elif [[ "$lower_path" =~ /git/|exploregithub|github.*profile|github.*releases|github.*community|collaborating.*github|repository.*setup|github.*enforcement|github.*pr.*scale|servicenow.*ghas ]]; then
        echo "devops/github"
    
    # DevOps - GitOps
    elif [[ "$lower_path" =~ gitops ]]; then
        echo "devops/gitops"
    
    # DevOps - Vault
    elif [[ "$lower_path" =~ vault ]]; then
        echo "devops/hashicorp-vault"
    
    # DevOps - Kubernetes
    elif [[ "$lower_path" =~ kubernetes|k8s ]]; then
        echo "devops/kubernetes"
    
    # DevOps - NGINX
    elif [[ "$lower_path" =~ nginx ]]; then
        echo "devops/nginx"
    
    # Game Development
    elif [[ "$lower_path" =~ ai-assisted-3d|ai-sprite|3d.*model.*generation|sprite.*generation ]]; then
        echo "game-development/asset-pipelines"
    elif [[ "$lower_path" =~ game-design-document|gdd ]]; then
        echo "game-development/design-documents"
    elif [[ "$lower_path" =~ physics-engine ]]; then
        echo "game-development/physics"
    elif [[ "$lower_path" =~ computer-animation ]]; then
        echo "game-development/animation"
    elif [[ "$lower_path" =~ computer-graphics|cgpp ]]; then
        echo "game-development/graphics"
    elif [[ "$lower_path" =~ emscripten|webgl|wasm.*game ]]; then
        echo "game-development/webgl-wasm"
    
    # Mathematics
    elif [[ "$lower_path" =~ calculus|taocp.*nr ]]; then
        echo "mathematics/calculus"
    elif [[ "$lower_path" =~ geometry|polygon.*data|cgc.*study|dcg.*study|hdcg.*study ]]; then
        echo "mathematics/geometry"
    elif [[ "$lower_path" =~ matri.*polynomial|polynomial.*data ]]; then
        echo "mathematics/algebra"
    
    # Programming
    elif [[ "$lower_path" =~ typescript ]]; then
        echo "programming/typescript"
    elif [[ "$lower_path" =~ embedded.*system.*c|object-oriented.*c.*embedded|benefitsofsimulating ]]; then
        echo "programming/c-cpp"
    elif [[ "$lower_path" =~ microfront|web-site-design|design.*sites ]]; then
        echo "programming/web-frontend"
    
    # Data Systems
    elif [[ "$lower_path" =~ kafka ]]; then
        echo "data-systems/kafka"
    elif [[ "$lower_path" =~ llm.*design.*pattern ]]; then
        echo "data-systems/llm"
    
    # Electronics
    elif [[ "$lower_path" =~ art-of-electronics|electronics-curriculum|x-chapters|circuit.*simulator ]]; then
        echo "electronics"
    
    # Cloud
    elif [[ "$lower_path" =~ cloud-computing-architecture|cloud.*book.*mapping ]]; then
        echo "cloud/architecture"
    elif [[ "$lower_path" =~ cloud.*finops ]]; then
        echo "cloud/finops"
    
    # AI/ML
    elif [[ "$lower_path" =~ prompt.*engineering ]]; then
        echo "ai-ml/prompt-engineering"
    
    # Media
    elif [[ "$lower_path" =~ fast.*animation.*channel|fast.*programming.*bible ]]; then
        echo "media/fast-channels"
    
    # Physics Simulation
    elif [[ "$lower_path" =~ fluid.*simulation ]]; then
        echo "physics-simulation"
    
    # Personal - Recipes
    elif [[ "$lower_path" =~ recipe|food|baguette|beef.*stew|biscuit|salad|soup|chicken|curry|cioppino|gumbo|shrimp|bagel|cheesecake|parmesan|chili|cinnamon|kabob ]]; then
        echo "personal/recipes"
    
    # Personal - Finance
    elif [[ "$lower_path" =~ certificate.*deposit|cd.*guide|invest|algo.*trading ]]; then
        echo "personal/finance"
    
    # Personal - Hobbies
    elif [[ "$lower_path" =~ locks.*safes ]]; then
        echo "personal/hobbies"
    
    # Default/Uncategorized
    else
        echo "uncategorized"
    fi
}

# Generate a clean filename from a path
generate_filename() {
    local original_name="$1"
    local category="$2"
    
    # Remove .tex extension for processing
    local base_name="${original_name%.tex}"
    
    # Convert to kebab-case
    local clean_name
    clean_name=$(echo "$base_name" | \
        sed 's/[_]/-/g' | \
        sed 's/\([a-z]\)\([A-Z]\)/\1-\2/g' | \
        tr '[:upper:]' '[:lower:]' | \
        sed 's/[^a-z0-9-]/-/g' | \
        sed 's/--*/-/g' | \
        sed 's/^-//' | \
        sed 's/-$//')
    
    echo "${clean_name}.tex"
}

# Find all .tex files and create migration plan
create_migration_plan() {
    log_info "Scanning for .tex files..."
    
    local plan_file="$REPO_ROOT/migration_plan.txt"
    > "$plan_file"
    
    # Find all .tex files in docs/docs (excluding orphans)
    while IFS= read -r -d '' tex_file; do
        # Skip if in orphans directory
        if [[ "$tex_file" =~ /orphans/ ]]; then
            continue
        fi
        
        local relative_path="${tex_file#$OLD_DOCS_DIR/}"
        local filename
        filename=$(basename "$tex_file")
        local category
        category=$(get_category "$relative_path")
        local new_filename
        new_filename=$(generate_filename "$filename" "$category")
        local new_path="$NEW_DOCS_DIR/$category/$new_filename"
        
        echo "$tex_file|$new_path|$category" >> "$plan_file"
        
    done < <(find "$OLD_DOCS_DIR" -name "*.tex" -type f -print0 2>/dev/null || true)
    
    # Also check latex-docs/docs subdirectory
    local latex_docs_subdir="$OLD_DOCS_DIR/latex-docs/docs"
    if [[ -d "$latex_docs_subdir" ]]; then
        while IFS= read -r -d '' tex_file; do
            local relative_path="${tex_file#$latex_docs_subdir/}"
            local filename
            filename=$(basename "$tex_file")
            local category
            category=$(get_category "$relative_path")
            local new_filename
            new_filename=$(generate_filename "$filename" "$category")
            local new_path="$NEW_DOCS_DIR/$category/$new_filename"
            
            echo "$tex_file|$new_path|$category" >> "$plan_file"
            
        done < <(find "$latex_docs_subdir" -name "*.tex" -type f -print0 2>/dev/null || true)
    fi
    
    log_success "Migration plan created: $plan_file"
    echo "$plan_file"
}

# Execute the migration
execute_migration() {
    local plan_file="$1"
    
    log_info "Executing migration..."
    
    local count=0
    local skipped=0
    declare -A seen_destinations
    
    while IFS='|' read -r src dest category; do
        # Handle duplicate destinations by appending a number
        if [[ -n "${seen_destinations[$dest]:-}" ]]; then
            local base="${dest%.tex}"
            local counter=2
            while [[ -n "${seen_destinations[${base}-${counter}.tex]:-}" ]]; do
                ((counter++))
            done
            dest="${base}-${counter}.tex"
            log_warning "Duplicate detected, renaming to: $(basename "$dest")"
        fi
        seen_destinations[$dest]=1
        
        if [[ -f "$src" ]]; then
            move_file "$src" "$dest"
            ((count++))
        else
            log_warning "Skipping missing file: $src"
            ((skipped++))
        fi
    done < "$plan_file"
    
    log_success "Migrated $count files ($skipped skipped)"
}

# Update .gitignore
update_gitignore() {
    log_info "Updating .gitignore..."
    
    local gitignore="$REPO_ROOT/.gitignore"
    
    local gitignore_additions="
# ===========================================
# LaTeX build artifacts (PDFs compiled via GitHub Actions)
# ===========================================

# Compiled output
*.pdf

# LaTeX auxiliary files
*.aux
*.log
*.out
*.toc
*.lof
*.lot
*.fls
*.fdb_latexmk
*.synctex.gz
*.synctex(busy)
*.bbl
*.blg
*.bcf
*.run.xml
*.nav
*.snm
*.vrb
*.idx
*.ilg
*.ind
*.glo
*.gls
*.glg
*.acn
*.acr
*.alg
*.xdy

# LaTeX temporary directories
_minted-*/
auto/

# Editor files
*.swp
*.swo
*~
.DS_Store

# Build directories
build/
out/
"

    if $DRY_RUN; then
        log_action "Would append LaTeX ignores to .gitignore"
    else
        # Check if these rules already exist
        if ! grep -q "LaTeX build artifacts" "$gitignore" 2>/dev/null; then
            echo "$gitignore_additions" >> "$gitignore"
            log_success "Updated .gitignore"
        else
            log_info ".gitignore already contains LaTeX rules"
        fi
    fi
}

# Remove tracked PDFs from git
remove_tracked_pdfs() {
    log_info "Removing tracked PDF files from git..."
    
    if $DRY_RUN; then
        local pdf_count
        pdf_count=$(find "$REPO_ROOT" -name "*.pdf" -type f 2>/dev/null | wc -l)
        log_action "Would remove $pdf_count PDF files from git tracking"
    else
        # Remove PDFs from git index but keep local files
        find "$REPO_ROOT" -name "*.pdf" -type f -exec git rm --cached {} \; 2>/dev/null || true
        log_success "Removed PDFs from git tracking"
    fi
}

# Delete PDF files
delete_pdf_files() {
    log_info "Deleting PDF files..."
    
    if $DRY_RUN; then
        local pdf_count
        pdf_count=$(find "$REPO_ROOT/docs" -name "*.pdf" -type f 2>/dev/null | wc -l)
        log_action "Would delete $pdf_count PDF files"
    else
        find "$REPO_ROOT/docs" -name "*.pdf" -type f -delete 2>/dev/null || true
        log_success "Deleted PDF files"
    fi
}

# Clean up empty directories
cleanup_empty_dirs() {
    log_info "Cleaning up empty directories..."
    
    if $DRY_RUN; then
        log_action "Would remove empty directories"
    else
        # Remove empty directories recursively
        find "$REPO_ROOT/docs" -type d -empty -delete 2>/dev/null || true
        log_success "Cleaned up empty directories"
    fi
}

# Remove orphans directory
remove_orphans() {
    local orphans_dir="$REPO_ROOT/docs/orphans"
    
    if [[ -d "$orphans_dir" ]]; then
        log_info "Removing orphans directory (contains only PDFs)..."
        if $DRY_RUN; then
            log_action "Would remove: $orphans_dir"
        else
            rm -rf "$orphans_dir"
            log_success "Removed orphans directory"
        fi
    fi
}

# Remove old docs structure after migration
remove_old_structure() {
    log_info "Removing old directory structure..."
    
    if $DRY_RUN; then
        log_action "Would remove: $OLD_DOCS_DIR"
    else
        # Only remove if new structure exists and has files
        if [[ -d "$NEW_DOCS_DIR" ]] && [[ $(find "$NEW_DOCS_DIR" -name "*.tex" -type f | wc -l) -gt 0 ]]; then
            rm -rf "$OLD_DOCS_DIR"
            # Also remove the parent docs dir if empty
            rmdir "$REPO_ROOT/docs" 2>/dev/null || true
            log_success "Removed old directory structure"
        else
            log_error "New structure doesn't exist or is empty. Aborting removal of old structure."
        fi
    fi
}

# Generate summary report
generate_report() {
    local report_file="$REPO_ROOT/MIGRATION_REPORT.md"
    
    log_info "Generating migration report..."
    
    if $DRY_RUN; then
        log_action "Would generate report at: $report_file"
        return
    fi
    
    cat > "$report_file" << 'EOF'
# LaTeX Docs Repository Migration Report

## Migration Summary

This repository has been reorganized for better maintainability and discoverability.

## New Structure

```
src/
├── security/
│   ├── appsec/           # Application security programs, guides, user stories
│   ├── certifications/   # CISO, CISSP, CISH study materials
│   ├── cloud-security/   # Cloud security guides and user stories
│   ├── ghas/             # GitHub Advanced Security (CodeQL, Dependabot, Secret Scanning)
│   └── owasp/            # OWASP Top 10 (2025) and API Security
│
├── architecture/
│   ├── documenting-software-architecture/  # Views & Beyond styles and templates
│   ├── togaf/            # TOGAF user stories
│   ├── enterprise/       # Enterprise architecture curriculum
│   ├── systems-engineering/
│   └── system-design/    # Build patterns, Confluence structure
│
├── devops/
│   ├── github-actions/   # Workflows, custom actions, automation
│   ├── ci-cd/            # CI/CD pipelines, release engineering
│   ├── github/           # GitHub configuration, profiles, PRs
│   ├── gitops/           # GitOps stack blueprints
│   ├── hashicorp-vault/  # Vault guides
│   ├── kubernetes/       # K8s study materials
│   └── nginx/            # NGINX cookbook and HTTP server guides
│
├── game-development/
│   ├── asset-pipelines/  # AI 3D model and sprite generation
│   ├── design-documents/ # GDD templates
│   ├── physics/          # Physics engine analysis
│   ├── animation/        # Computer animation
│   ├── graphics/         # Computer graphics
│   └── webgl-wasm/       # Emscripten/WebGL guides
│
├── mathematics/
│   ├── calculus/         # Calculus handbooks
│   ├── geometry/         # Computational geometry
│   └── algebra/          # Matrices, polynomials
│
├── programming/
│   ├── typescript/       # Effective TypeScript, cookbook
│   ├── c-cpp/            # C/C++ for embedded systems
│   └── web-frontend/     # Microfrontends, web design
│
├── data-systems/
│   ├── kafka/            # Kafka guides
│   └── llm/              # LLM design patterns
│
├── electronics/          # Art of Electronics curriculum
│
├── cloud/
│   ├── architecture/     # Cloud computing architecture
│   └── finops/           # Cloud FinOps curriculum
│
├── ai-ml/
│   └── prompt-engineering/
│
├── physics-simulation/   # Fluid simulation curriculum
│
├── media/
│   └── fast-channels/    # FAST animation channels
│
└── personal/
    ├── recipes/          # All recipe .tex files
    ├── finance/          # CD guides, algo trading
    └── hobbies/          # Locks, safes, security
```

## Changes Made

1. **Flattened directory structure**: Removed deeply nested `hash-id/src/name/src/` patterns
2. **Removed PDF tracking**: PDFs are now compiled via GitHub Actions
3. **Consistent naming**: All files use kebab-case
4. **Logical grouping**: Documents organized by domain/topic
5. **Cleaned up duplicates**: Redundant files consolidated

## Building PDFs

PDFs are compiled automatically via GitHub Actions on push to main.

To build locally:
```bash
make all
# or
./tooling/scripts/build_all.sh
```

## File Naming Convention

- All `.tex` files use kebab-case: `my-document-name.tex`
- No spaces, underscores, or special characters
- Descriptive names that indicate content

EOF

    # Add list of files by category
    echo -e "\n## Files by Category\n" >> "$report_file"
    
    for category_dir in "$NEW_DOCS_DIR"/*/; do
        if [[ -d "$category_dir" ]]; then
            local category_name
            category_name=$(basename "$category_dir")
            echo -e "### $category_name\n" >> "$report_file"
            
            find "$category_dir" -name "*.tex" -type f | sort | while read -r f; do
                local rel_path="${f#$NEW_DOCS_DIR/}"
                echo "- \`$rel_path\`" >> "$report_file"
            done
            echo "" >> "$report_file"
        fi
    done
    
    log_success "Migration report generated: $report_file"
}

# Update Makefile for new structure
update_makefile() {
    log_info "Updating Makefile..."
    
    local makefile="$REPO_ROOT/Makefile"
    
    if $DRY_RUN; then
        log_action "Would update Makefile for new structure"
        return
    fi
    
    cat > "$makefile" << 'EOF'
# LaTeX Docs Makefile
# ===================

LATEX = pdflatex
LATEXFLAGS = -interaction=nonstopmode -halt-on-error
SRC_DIR = src
BUILD_DIR = build

# Find all .tex files
TEX_FILES := $(shell find $(SRC_DIR) -name '*.tex' -type f)
PDF_FILES := $(TEX_FILES:$(SRC_DIR)/%.tex=$(BUILD_DIR)/%.pdf)

.PHONY: all clean list

all: $(PDF_FILES)

$(BUILD_DIR)/%.pdf: $(SRC_DIR)/%.tex
	@mkdir -p $(dir $@)
	@echo "Building: $<"
	@cd $(dir $<) && $(LATEX) $(LATEXFLAGS) -output-directory=$(abspath $(dir $@)) $(notdir $<) > /dev/null 2>&1 || \
		(echo "Error building $<"; exit 1)
	@cd $(dir $<) && $(LATEX) $(LATEXFLAGS) -output-directory=$(abspath $(dir $@)) $(notdir $<) > /dev/null 2>&1

clean:
	rm -rf $(BUILD_DIR)
	find . -name '*.aux' -delete
	find . -name '*.log' -delete
	find . -name '*.out' -delete
	find . -name '*.toc' -delete

list:
	@echo "Source files:"
	@find $(SRC_DIR) -name '*.tex' -type f | sort
EOF

    log_success "Updated Makefile"
}

# Update build script
update_build_script() {
    log_info "Updating build script..."
    
    local script="$REPO_ROOT/tooling/scripts/build_all.sh"
    
    if $DRY_RUN; then
        log_action "Would update build script"
        return
    fi
    
    ensure_dir "$(dirname "$script")"
    
    cat > "$script" << 'EOF'
#!/bin/bash
#
# Build all LaTeX documents
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SRC_DIR="$REPO_ROOT/src"
BUILD_DIR="$REPO_ROOT/build"

echo "Building LaTeX documents..."
echo "Source: $SRC_DIR"
echo "Output: $BUILD_DIR"

# Create build directory
mkdir -p "$BUILD_DIR"

# Find and build all .tex files
find "$SRC_DIR" -name "*.tex" -type f | while read -r tex_file; do
    relative_path="${tex_file#$SRC_DIR/}"
    output_dir="$BUILD_DIR/$(dirname "$relative_path")"
    
    mkdir -p "$output_dir"
    
    echo "Building: $relative_path"
    
    # Run pdflatex twice for cross-references
    (
        cd "$(dirname "$tex_file")"
        pdflatex -interaction=nonstopmode -halt-on-error \
            -output-directory="$output_dir" \
            "$(basename "$tex_file")" > /dev/null 2>&1 || true
        pdflatex -interaction=nonstopmode -halt-on-error \
            -output-directory="$output_dir" \
            "$(basename "$tex_file")" > /dev/null 2>&1 || echo "  Warning: Build may have issues"
    )
done

echo "Build complete!"
echo "PDFs are in: $BUILD_DIR"
EOF

    chmod +x "$script"
    log_success "Updated build script"
}

# Main execution
main() {
    echo "========================================"
    echo "LaTeX Docs Repository Reorganization"
    echo "========================================"
    echo ""
    
    if $DRY_RUN; then
        echo -e "${YELLOW}Running in DRY-RUN mode - no changes will be made${NC}"
        echo ""
    fi
    
    # Verify we're in the right directory
    if [[ ! -d "$OLD_DOCS_DIR" ]]; then
        log_error "Directory not found: $OLD_DOCS_DIR"
        log_error "Please run this script from the latex-docs repository root"
        exit 1
    fi
    
    # Create migration plan
    local plan_file
    plan_file=$(create_migration_plan)
    
    # Show summary
    local total_files
    total_files=$(wc -l < "$plan_file")
    echo ""
    echo "Migration Plan Summary:"
    echo "  Total .tex files to migrate: $total_files"
    echo ""
    
    # Show category breakdown
    echo "Files by category:"
    awk -F'|' '{print $3}' "$plan_file" | sort | uniq -c | sort -rn | head -20
    echo ""
    
    if $DRY_RUN; then
        echo "To execute the migration, run without --dry-run"
        echo ""
        echo "Preview of first 10 migrations:"
        head -10 "$plan_file" | while IFS='|' read -r src dest category; do
            echo "  $(basename "$src") -> $category/$(basename "$dest")"
        done
        return
    fi
    
    # Confirm before proceeding
    read -p "Proceed with migration? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Migration cancelled"
        exit 0
    fi
    
    # Execute migration steps
    execute_migration "$plan_file"
    update_gitignore
    remove_tracked_pdfs
    delete_pdf_files
    remove_orphans
    cleanup_empty_dirs
    remove_old_structure
    update_makefile
    update_build_script
    generate_report
    
    echo ""
    echo "========================================"
    log_success "Migration complete!"
    echo "========================================"
    echo ""
    echo "Next steps:"
    echo "  1. Review the changes: git status"
    echo "  2. Review the report: cat MIGRATION_REPORT.md"
    echo "  3. Stage changes: git add -A"
    echo "  4. Commit: git commit -m 'Reorganize repository structure'"
    echo "  5. Push: git push"
}

# Run main
main "$@"
