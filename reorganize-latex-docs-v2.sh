#!/usr/bin/env bash
#===============================================================================
# reorganize-latex-docs-v2.sh
# 
# Refined hierarchical reorganization of the latex-docs repository
# 
# ANALYSIS SUMMARY:
# -----------------
# The current structure has several organizational issues:
#   1. architecture/documenting-software-architecture/ is a mega-folder (27 files)
#      mixing styles, viewpoints, mappings, and governance docs
#   2. devops/ci-cd/ conflates version control, SDLC, and deployment topics
#   3. uncategorized/ contains GHAS content that belongs in security/
#   4. personal/recipes/ has many duplicate files (-2, -3, -4 suffixes)
#   5. security/ghas/ has duplicate cheatsheets and SOPs
#   6. No distinction between learning materials vs reference documentation
#
# NEW HIERARCHY RATIONALE:
# ------------------------
# - architecture/views-and-beyond/: Organized by viewtype (module, C&C, allocation)
#   plus fundamentals, advanced concepts, and framework mappings
# - devops/: Split into foundations, ci-cd, platform, gitops, secrets-management
# - security/: Clear separation of appsec, GHAS (with sub-domains), cloud, standards
# - personal/recipes/: Organized by meal type (breads, soups, entrees, etc.)
# - Duplicate files are preserved but consolidated with clear naming
#
# USAGE:
#   chmod +x reorganize-latex-docs-v2.sh
#   ./reorganize-latex-docs-v2.sh [--dry-run]
#
# OPTIONS:
#   --dry-run    Show what would be done without making changes
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
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

# Counters
MOVED=0
CREATED=0
SKIPPED=0

#-------------------------------------------------------------------------------
# Utility functions
#-------------------------------------------------------------------------------

log_info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $*"; }
log_move()    { echo -e "${CYAN}[MOVE]${NC} $1 ${YELLOW}→${NC} $2"; }

ensure_dir() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        if $DRY_RUN; then
            log_info "[DRY-RUN] Would create directory: $dir"
        else
            mkdir -p "$dir"
            log_success "Created directory: $dir"
        fi
        ((CREATED++)) || true
    fi
}

move_file() {
    local src="$1"
    local dst="$2"
    
    if [[ ! -f "$src" ]]; then
        log_warn "Source not found: $src"
        ((SKIPPED++)) || true
        return 0
    fi
    
    local dst_dir
    dst_dir="$(dirname "$dst")"
    ensure_dir "$dst_dir"
    
    if [[ -f "$dst" ]]; then
        log_warn "Destination exists, skipping: $dst"
        ((SKIPPED++)) || true
        return 0
    fi
    
    if $DRY_RUN; then
        log_move "$src" "$dst"
        log_info "[DRY-RUN] Would move file"
    else
        mv "$src" "$dst"
        log_move "$src" "$dst"
    fi
    ((MOVED++)) || true
}

move_dir() {
    local src="$1"
    local dst="$2"
    
    if [[ ! -d "$src" ]]; then
        log_warn "Source directory not found: $src"
        ((SKIPPED++)) || true
        return 0
    fi
    
    ensure_dir "$(dirname "$dst")"
    
    if [[ -d "$dst" ]]; then
        # Merge contents
        log_info "Merging $src into existing $dst"
        if $DRY_RUN; then
            log_info "[DRY-RUN] Would merge directories"
        else
            cp -rn "$src"/* "$dst"/ 2>/dev/null || true
            rm -rf "$src"
        fi
    else
        if $DRY_RUN; then
            log_move "$src" "$dst"
            log_info "[DRY-RUN] Would move directory"
        else
            mv "$src" "$dst"
            log_move "$src" "$dst"
        fi
    fi
    ((MOVED++)) || true
}

cleanup_empty_dirs() {
    log_info "Cleaning up empty directories..."
    if $DRY_RUN; then
        find src -type d -empty 2>/dev/null | while read -r d; do
            log_info "[DRY-RUN] Would remove empty dir: $d"
        done
    else
        find src -type d -empty -delete 2>/dev/null || true
    fi
}

#===============================================================================
# MAIN REORGANIZATION LOGIC
#===============================================================================

main() {
    echo ""
    echo "============================================================"
    echo "  LaTeX Documentation Repository Reorganization v2"
    echo "============================================================"
    echo ""
    
    if $DRY_RUN; then
        log_warn "Running in DRY-RUN mode - no changes will be made"
        echo ""
    fi
    
    # Verify we're in the right place
    if [[ ! -d "src" ]]; then
        log_error "No 'src' directory found. Run this script from the repository root."
        exit 1
    fi
    
    #---------------------------------------------------------------------------
    # PHASE 1: ARCHITECTURE REORGANIZATION
    #---------------------------------------------------------------------------
    echo ""
    log_info "=== Phase 1: Reorganizing Architecture ==="
    
    local arch_src="src/architecture/documenting-software-architecture"
    local vb_base="src/architecture/views-and-beyond"
    
    # 1.1 Views and Beyond - Fundamentals
    ensure_dir "$vb_base/fundamentals"
    move_file "$arch_src/architecture-overview-presentation.tex" \
              "$vb_base/fundamentals/architecture-overview-presentation.tex"
    move_file "$arch_src/stakeholder-documentation-needs.tex" \
              "$vb_base/fundamentals/stakeholder-documentation-needs.tex"
    move_file "$arch_src/architecture-documentation-beyond-views.tex" \
              "$vb_base/fundamentals/architecture-documentation-beyond-views.tex"
    move_file "$arch_src/architecture-documentation-review-across-project-phases.tex" \
              "$vb_base/fundamentals/architecture-documentation-review-across-project-phases.tex"
    
    # 1.2 Views and Beyond - Module Viewtype
    ensure_dir "$vb_base/module-viewtype"
    move_file "$arch_src/module-views.tex" \
              "$vb_base/module-viewtype/module-views.tex"
    move_file "$arch_src/decomposition-style.tex" \
              "$vb_base/module-viewtype/decomposition-style.tex"
    move_file "$arch_src/uses-style.tex" \
              "$vb_base/module-viewtype/uses-style.tex"
    move_file "$arch_src/generalization-style.tex" \
              "$vb_base/module-viewtype/generalization-style.tex"
    move_file "$arch_src/layered-style.tex" \
              "$vb_base/module-viewtype/layered-style.tex"
    
    # 1.3 Views and Beyond - Component & Connector Viewtype
    ensure_dir "$vb_base/component-connector-viewtype"
    move_file "$arch_src/component-and-connector-views.tex" \
              "$vb_base/component-connector-viewtype/component-and-connector-views.tex"
    move_file "$arch_src/pipe-and-filter-style.tex" \
              "$vb_base/component-connector-viewtype/pipe-and-filter-style.tex"
    move_file "$arch_src/shared-data-style.tex" \
              "$vb_base/component-connector-viewtype/shared-data-style.tex"
    move_file "$arch_src/publish-subscribe-style.tex" \
              "$vb_base/component-connector-viewtype/publish-subscribe-style.tex"
    move_file "$arch_src/service-oriented-architecture-style.tex" \
              "$vb_base/component-connector-viewtype/service-oriented-architecture-style.tex"
    
    # 1.4 Views and Beyond - Allocation Viewtype
    ensure_dir "$vb_base/allocation-viewtype"
    move_file "$arch_src/deployment-style.tex" \
              "$vb_base/allocation-viewtype/deployment-style.tex"
    move_file "$arch_src/data-model-style.tex" \
              "$vb_base/allocation-viewtype/data-model-style.tex"
    
    # 1.5 Views and Beyond - Advanced Concepts
    ensure_dir "$vb_base/advanced-concepts"
    move_file "$arch_src/aspects-style.tex" \
              "$vb_base/advanced-concepts/aspects-style.tex"
    move_file "$arch_src/variation-points.tex" \
              "$vb_base/advanced-concepts/variation-points.tex"
    move_file "$arch_src/spectrumof-style-specializations.tex" \
              "$vb_base/advanced-concepts/spectrum-of-style-specializations.tex"
    move_file "$arch_src/viewpointtemplate-2.tex" \
              "$vb_base/advanced-concepts/viewpoint-template.tex"
    
    # 1.6 Views and Beyond - Framework Mappings
    ensure_dir "$vb_base/framework-mappings"
    move_file "$arch_src/relating-viewsand-beyondto-rup.tex" \
              "$vb_base/framework-mappings/mapping-to-rup.tex"
    move_file "$arch_src/relating-viewsand-beyondtothe-rozanskiand-woodsviewpointset.tex" \
              "$vb_base/framework-mappings/mapping-to-rozanski-woods.tex"
    move_file "$arch_src/rozanskiwoodsviewsandbeyond.tex" \
              "$vb_base/framework-mappings/rozanski-woods-comparison.tex"
    move_file "$arch_src/iso42010information-requirement-viewsand-beyond-location.tex" \
              "$vb_base/framework-mappings/mapping-to-iso42010.tex"
    move_file "$arch_src/do-dafand-viewsand-beyond.tex" \
              "$vb_base/framework-mappings/mapping-to-dodaf.tex"
    
    # 1.7 Architecture - Governance
    ensure_dir "src/architecture/governance"
    move_file "$arch_src/cloud-governance-control-framework-architecture.tex" \
              "src/architecture/governance/cloud-governance-control-framework.tex"
    move_file "$arch_src/confluence-space-structureand-directory-rationale.tex" \
              "src/architecture/governance/confluence-space-structure-rationale.tex"
    
    # 1.8 Architecture - Patterns (from system-design)
    ensure_dir "src/architecture/patterns"
    move_file "src/architecture/system-design/build-system-facade-pattern.tex" \
              "src/architecture/patterns/build-system-facade-pattern.tex"
    
    #---------------------------------------------------------------------------
    # PHASE 2: DEVOPS REORGANIZATION
    #---------------------------------------------------------------------------
    echo ""
    log_info "=== Phase 2: Reorganizing DevOps ==="
    
    # 2.1 Foundations - Version Control
    ensure_dir "src/devops/foundations/version-control"
    move_file "src/devops/ci-cd/git.tex" \
              "src/devops/foundations/version-control/git-fundamentals.tex"
    
    # 2.2 Foundations - SDLC
    ensure_dir "src/devops/foundations/sdlc"
    move_file "src/devops/ci-cd/analyze-sdlc.tex" \
              "src/devops/foundations/sdlc/analyze-sdlc.tex"
    move_file "src/devops/ci-cd/explore-git-hub.tex" \
              "src/devops/foundations/sdlc/explore-github.tex"
    
    # 2.3 CI/CD - Fundamentals
    ensure_dir "src/devops/ci-cd/fundamentals"
    move_file "src/devops/ci-cd/release-engineering-quick-start.tex" \
              "src/devops/ci-cd/fundamentals/release-engineering-quick-start.tex"
    move_file "src/devops/ci-cd/ci-toolkit.tex" \
              "src/devops/ci-cd/fundamentals/ci-toolkit.tex"
    
    # 2.4 CI/CD - Pipelines
    ensure_dir "src/devops/ci-cd/pipelines"
    move_file "src/devops/ci-cd/quick-start-git-hub-to-aws-app-runner.tex" \
              "src/devops/ci-cd/pipelines/github-to-aws-app-runner.tex"
    
    # 2.5 Platform - GitHub (from github/)
    ensure_dir "src/devops/platform/github"
    move_file "src/devops/github/collaboratingwith-your-communityon-git-hub.tex" \
              "src/devops/platform/github/collaborating-with-community.tex"
    move_file "src/devops/github/git-hub-profile.tex" \
              "src/devops/platform/github/github-profile.tex"
    move_file "src/devops/github/git-hub-releases-practical-quick-reference.tex" \
              "src/devops/platform/github/releases-quick-reference.tex"
    move_file "src/devops/github/repository-setup-guide.tex" \
              "src/devops/platform/github/repository-setup-guide.tex"
    
    # 2.6 Platform - Kubernetes
    ensure_dir "src/devops/platform/kubernetes"
    move_file "src/devops/kubernetes/k8s-sequenced-stories.tex" \
              "src/devops/platform/kubernetes/k8s-sequenced-stories.tex"
    
    # 2.7 Platform - Nginx
    ensure_dir "src/devops/platform/nginx"
    move_file "src/devops/nginx/nginx-cookbook-user-stories.tex" \
              "src/devops/platform/nginx/nginx-cookbook-user-stories.tex"
    move_file "src/devops/nginx/nginxcookbook-user-stories.tex" \
              "src/devops/platform/nginx/nginx-cookbook-user-stories-alt.tex"
    move_file "src/devops/nginx/user-stories.tex" \
              "src/devops/platform/nginx/user-stories.tex"
    
    # 2.8 Secrets Management - Vault
    ensure_dir "src/devops/secrets-management/hashicorp-vault"
    move_dir "src/devops/hashicorp-vault" "src/devops/secrets-management/hashicorp-vault"
    
    # 2.9 GitOps (keep as-is but move up)
    ensure_dir "src/devops/gitops"
    move_file "src/devops/gitops/git-ops-stack-blueprint.tex" \
              "src/devops/gitops/gitops-stack-blueprint.tex"
    
    #---------------------------------------------------------------------------
    # PHASE 3: SECURITY REORGANIZATION
    #---------------------------------------------------------------------------
    echo ""
    log_info "=== Phase 3: Reorganizing Security ==="
    
    # 3.1 Application Security - Fundamentals
    ensure_dir "src/security/application-security/fundamentals"
    move_file "src/security/appsec/app-sec-user-stories.tex" \
              "src/security/application-security/fundamentals/appsec-user-stories.tex"
    move_file "src/security/appsec/app-sec-user-stories-resequenced.tex" \
              "src/security/application-security/fundamentals/appsec-user-stories-resequenced.tex"
    move_file "src/security/appsec/user-stories.tex" \
              "src/security/application-security/fundamentals/user-stories.tex"
    
    # 3.2 Application Security - Programs
    ensure_dir "src/security/application-security/programs"
    move_file "src/security/appsec/application-security-program-ghas.tex" \
              "src/security/application-security/programs/application-security-program-ghas.tex"
    move_file "src/security/appsec/programs-and-systems.tex" \
              "src/security/application-security/programs/programs-and-systems.tex"
    move_file "src/security/appsec/appsec-architecture-backlog.tex" \
              "src/security/application-security/programs/appsec-architecture-backlog.tex"
    
    # 3.3 Application Security - Processes
    ensure_dir "src/security/application-security/processes"
    move_file "src/security/appsec/modeling-application-security-processes.tex" \
              "src/security/application-security/processes/modeling-appsec-processes.tex"
    move_file "src/security/appsec/mappingthe-five-app-sec-core-processestoa16-gate-cicdpipeline0.tex" \
              "src/security/application-security/processes/appsec-cicd-pipeline-mapping.tex"
    move_file "src/security/appsec/security-policies-github.tex" \
              "src/security/application-security/processes/security-policies-github.tex"
    
    # 3.4 Application Security - Learning
    ensure_dir "src/security/application-security/learning"
    move_file "src/security/appsec/appsec-certification-guide.tex" \
              "src/security/application-security/learning/appsec-certification-guide.tex"
    move_file "src/security/appsec/appsec-course-priority-sequence.tex" \
              "src/security/application-security/learning/appsec-course-priority-sequence.tex"
    move_file "src/security/appsec/appsec-reading-sequence.tex" \
              "src/security/application-security/learning/appsec-reading-sequence.tex"
    
    # 3.5 GHAS - Administration
    local ghas_base="src/security/github-advanced-security"
    ensure_dir "$ghas_base/administration"
    move_file "src/security/ghas/administring-ghas.tex" \
              "$ghas_base/administration/administering-ghas.tex"
    move_file "src/security/ghas/git-hub-advanced-security-ghasbest-practices.tex" \
              "$ghas_base/administration/ghas-best-practices.tex"
    move_file "src/security/ghas/git-hub-advanced-security-ghasand-its-roleina16-gate-cicdpipeline.tex" \
              "$ghas_base/administration/ghas-cicd-pipeline-role.tex"
    move_file "src/security/ghas/ghas-study-plan-user-stories.tex" \
              "$ghas_base/administration/ghas-study-plan-user-stories.tex"
    
    # 3.6 GHAS - Code Scanning
    ensure_dir "$ghas_base/code-scanning"
    move_file "src/security/ghas/applying-codeql-scanning.tex" \
              "$ghas_base/code-scanning/applying-codeql-scanning.tex"
    move_file "src/security/ghas/code-qlcapabilities.tex" \
              "$ghas_base/code-scanning/codeql-capabilities.tex"
    move_file "src/security/ghas/codeql-triage-sop.tex" \
              "$ghas_base/code-scanning/codeql-triage-sop.tex"
    move_file "src/security/ghas/git-hub-code-scanning-quickstart.tex" \
              "$ghas_base/code-scanning/code-scanning-quickstart.tex"
    move_file "src/security/ghas/external-scanning-sarif-upload.tex" \
              "$ghas_base/code-scanning/sarif-upload.tex"
    
    # 3.7 GHAS - Secret Scanning
    ensure_dir "$ghas_base/secret-scanning"
    move_file "src/security/ghas/enable-secret-protection-secret-scanning-alertsfora-git-hub-repository.tex" \
              "$ghas_base/secret-scanning/enable-secret-scanning.tex"
    move_file "src/security/ghas/secret-scanning-triage-sequence.tex" \
              "$ghas_base/secret-scanning/secret-scanning-triage-sequence.tex"
    move_file "src/security/ghas/secret-scanning-triage-sop.tex" \
              "$ghas_base/secret-scanning/secret-scanning-triage-sop.tex"
    move_file "src/security/ghas/ghas-secret-scanning-sop.tex" \
              "$ghas_base/secret-scanning/ghas-secret-scanning-sop.tex"
    move_file "src/security/ghas/ghas-secret-scanning-triage-sop.tex" \
              "$ghas_base/secret-scanning/ghas-secret-scanning-triage-sop.tex"
    move_file "src/security/ghas/viewingandfilteringalertsfromsecretscanning.tex" \
              "$ghas_base/secret-scanning/viewing-filtering-alerts.tex"
    move_file "src/security/ghas/notification-decision-matrixfor-monitoring-secret-scanning-alerts.tex" \
              "$ghas_base/secret-scanning/notification-decision-matrix.tex"
    move_file "src/security/ghas/role-scope-access-matrixfor-metricsfor-custom-patterns.tex" \
              "$ghas_base/secret-scanning/role-scope-access-matrix.tex"
    
    # 3.8 GHAS - Dependabot
    ensure_dir "$ghas_base/dependabot"
    move_file "src/security/ghas/dependabot-alerts.tex" \
              "$ghas_base/dependabot/dependabot-alerts.tex"
    
    # 3.9 GHAS - Cheatsheets & References (consolidated)
    ensure_dir "$ghas_base/references"
    move_file "src/security/ghas/ghas-cheatsheet.tex" \
              "$ghas_base/references/ghas-cheatsheet.tex"
    move_file "src/security/ghas/code-scanning-cheatsheet.tex" \
              "$ghas_base/references/code-scanning-cheatsheet.tex"
    move_file "src/security/ghas/codeql-cheatsheet.tex" \
              "$ghas_base/references/codeql-cheatsheet.tex"
    move_file "src/security/ghas/dependabot-cheatsheet.tex" \
              "$ghas_base/references/dependabot-cheatsheet.tex"
    move_file "src/security/ghas/ghas-dependabot-cheatsheet.tex" \
              "$ghas_base/references/ghas-dependabot-cheatsheet.tex"
    move_file "src/security/ghas/ghas-dependabot-cheatsheet-2.tex" \
              "$ghas_base/references/ghas-dependabot-cheatsheet-v2.tex"
    move_file "src/security/ghas/ghas-secret-scanning-cheat-sheet.tex" \
              "$ghas_base/references/secret-scanning-cheatsheet.tex"
    
    # 3.10 Move uncategorized GHAS doc
    move_file "src/uncategorized/practical-overviewof-git-hub-advanced-security.tex" \
              "$ghas_base/administration/practical-overview-ghas.tex"
    
    # 3.11 Standards - OWASP (rename parent for clarity)
    ensure_dir "src/security/standards/owasp"
    move_dir "src/security/owasp" "src/security/standards/owasp"
    
    #---------------------------------------------------------------------------
    # PHASE 4: PERSONAL/RECIPES REORGANIZATION
    #---------------------------------------------------------------------------
    echo ""
    log_info "=== Phase 4: Reorganizing Personal/Recipes ==="
    
    local recipes="src/personal/recipes"
    
    # 4.1 Breads
    ensure_dir "$recipes/breads"
    move_file "$recipes/baguette.tex" "$recipes/breads/baguette.tex"
    move_file "$recipes/biscuits.tex" "$recipes/breads/biscuits.tex"
    move_file "$recipes/cinnamon-rolls.tex" "$recipes/breads/cinnamon-rolls.tex"
    move_file "$recipes/new-york-style-bagel.tex" "$recipes/breads/new-york-style-bagel.tex"
    
    # 4.2 Soups & Stews
    ensure_dir "$recipes/soups-stews"
    move_file "$recipes/beef-stew.tex" "$recipes/soups-stews/beef-stew.tex"
    move_file "$recipes/chicken-tortilla-soup.tex" "$recipes/soups-stews/chicken-tortilla-soup.tex"
    move_file "$recipes/chilli.tex" "$recipes/soups-stews/chilli.tex"
    move_file "$recipes/cioppino-fishermans-stew.tex" "$recipes/soups-stews/cioppino-fishermans-stew.tex"
    move_file "$recipes/cioppino-seafood-stew.tex" "$recipes/soups-stews/cioppino-seafood-stew.tex"
    move_file "$recipes/cioppino-seafood-stew-2.tex" "$recipes/soups-stews/cioppino-seafood-stew-v2.tex"
    move_file "$recipes/creamy-potato-celery-soup.tex" "$recipes/soups-stews/creamy-potato-celery-soup.tex"
    move_file "$recipes/creamy-vegetable-soup.tex" "$recipes/soups-stews/creamy-vegetable-soup.tex"
    move_file "$recipes/creamy-vegetable-soup-2.tex" "$recipes/soups-stews/creamy-vegetable-soup-v2.tex"
    move_file "$recipes/irish-vegetable-soup.tex" "$recipes/soups-stews/irish-vegetable-soup.tex"
    move_file "$recipes/roasted-celeryand-potato-soup.tex" "$recipes/soups-stews/roasted-celery-potato-soup.tex"
    move_file "$recipes/seafood-gumbo.tex" "$recipes/soups-stews/seafood-gumbo.tex"
    move_file "$recipes/seafood-stewwith-shrimpand-lobster.tex" "$recipes/soups-stews/seafood-stew-shrimp-lobster.tex"
    move_file "$recipes/vegetable-soup.tex" "$recipes/soups-stews/vegetable-soup.tex"
    move_file "$recipes/vegetable-soup-2.tex" "$recipes/soups-stews/vegetable-soup-v2.tex"
    move_file "$recipes/zucchini-soup.tex" "$recipes/soups-stews/zucchini-soup.tex"
    move_file "$recipes/zucchini-soup-2.tex" "$recipes/soups-stews/zucchini-soup-v2.tex"
    
    # 4.3 Entrees (Main Dishes)
    ensure_dir "$recipes/entrees"
    move_file "$recipes/chicken-curry.tex" "$recipes/entrees/chicken-curry.tex"
    move_file "$recipes/chicken-parmesan.tex" "$recipes/entrees/chicken-parmesan.tex"
    move_file "$recipes/eggplant-parmesan.tex" "$recipes/entrees/eggplant-parmesan.tex"
    move_file "$recipes/indian-chicken-curry-murgh-kari.tex" "$recipes/entrees/indian-chicken-curry-murgh-kari.tex"
    move_file "$recipes/grilled-shrimp-kabobs.tex" "$recipes/entrees/grilled-shrimp-kabobs.tex"
    move_file "$recipes/shrimp-po-boys.tex" "$recipes/entrees/shrimp-po-boys.tex"
    move_file "$recipes/shrimp-po-boys-2.tex" "$recipes/entrees/shrimp-po-boys-v2.tex"
    
    # 4.4 Salads
    ensure_dir "$recipes/salads"
    move_file "$recipes/chef-salad.tex" "$recipes/salads/chef-salad.tex"
    move_file "$recipes/cobb-salad.tex" "$recipes/salads/cobb-salad.tex"
    move_file "$recipes/southwest-salad.tex" "$recipes/salads/southwest-salad.tex"
    move_file "$recipes/southwest-salad-2.tex" "$recipes/salads/southwest-salad-v2.tex"
    
    # 4.5 Desserts
    ensure_dir "$recipes/desserts"
    move_file "$recipes/peanut-butter-cheesecake.tex" "$recipes/desserts/peanut-butter-cheesecake.tex"
    
    # 4.6 Recipe Compilations (main.tex files)
    ensure_dir "$recipes/compilations"
    move_file "$recipes/main.tex" "$recipes/compilations/main.tex"
    move_file "$recipes/main-2.tex" "$recipes/compilations/main-v2.tex"
    move_file "$recipes/main-3.tex" "$recipes/compilations/main-v3.tex"
    move_file "$recipes/main-4.tex" "$recipes/compilations/main-v4.tex"
    
    #---------------------------------------------------------------------------
    # PHASE 5: PROGRAMMING REORGANIZATION
    #---------------------------------------------------------------------------
    echo ""
    log_info "=== Phase 5: Reorganizing Programming ==="
    
    # 5.1 Languages structure
    ensure_dir "src/programming/languages/c-cpp"
    move_dir "src/programming/c-cpp" "src/programming/languages/c-cpp"
    
    ensure_dir "src/programming/languages/typescript"
    move_dir "src/programming/typescript" "src/programming/languages/typescript"
    
    # 5.2 Web development
    ensure_dir "src/programming/web/frontend"
    move_dir "src/programming/web-frontend" "src/programming/web/frontend"
    
    #---------------------------------------------------------------------------
    # PHASE 6: DATA SYSTEMS REORGANIZATION
    #---------------------------------------------------------------------------
    echo ""
    log_info "=== Phase 6: Reorganizing Data Systems ==="
    
    ensure_dir "src/data-systems/streaming/kafka"
    move_dir "src/data-systems/kafka" "src/data-systems/streaming/kafka"
    
    ensure_dir "src/data-systems/ai-ml/llm"
    move_dir "src/data-systems/llm" "src/data-systems/ai-ml/llm"
    
    #---------------------------------------------------------------------------
    # PHASE 7: GAME DEVELOPMENT CLEANUP
    #---------------------------------------------------------------------------
    echo ""
    log_info "=== Phase 7: Reorganizing Game Development ==="
    
    # Rename physics to physics-engines for clarity
    ensure_dir "src/game-development/physics-engines"
    move_file "src/game-development/physics/physics-engine-gap-analysis.tex" \
              "src/game-development/physics-engines/physics-engine-gap-analysis.tex"
    
    #---------------------------------------------------------------------------
    # PHASE 8: CLEANUP
    #---------------------------------------------------------------------------
    echo ""
    log_info "=== Phase 8: Cleanup ==="
    
    cleanup_empty_dirs
    
    #---------------------------------------------------------------------------
    # SUMMARY
    #---------------------------------------------------------------------------
    echo ""
    echo "============================================================"
    echo "  Reorganization Complete"
    echo "============================================================"
    echo ""
    log_info "Directories created: $CREATED"
    log_info "Files/directories moved: $MOVED"
    log_info "Skipped (missing/exists): $SKIPPED"
    echo ""
    
    if $DRY_RUN; then
        log_warn "This was a DRY RUN. No actual changes were made."
        log_info "Run without --dry-run to apply changes."
    else
        log_success "Reorganization applied successfully!"
        log_info "Review the new structure with: find src -type d | head -50"
    fi
}

#-------------------------------------------------------------------------------
# Display new structure summary
#-------------------------------------------------------------------------------

show_new_structure() {
    cat << 'EOF'

NEW DIRECTORY STRUCTURE
=======================

src/
├── architecture/
│   ├── views-and-beyond/
│   │   ├── fundamentals/           # Core V&B concepts
│   │   ├── module-viewtype/        # Decomposition, uses, layered, generalization
│   │   ├── component-connector-viewtype/  # Pipe-filter, pub-sub, shared-data, SOA
│   │   ├── allocation-viewtype/    # Deployment, data model
│   │   ├── advanced-concepts/      # Aspects, variations, specializations
│   │   └── framework-mappings/     # RUP, Rozanski-Woods, ISO42010, DoDAF
│   ├── enterprise/
│   │   ├── togaf/
│   │   └── systems-engineering/
│   ├── governance/                 # Cloud governance, Confluence structure
│   └── patterns/                   # Design patterns
│
├── devops/
│   ├── foundations/
│   │   ├── version-control/        # Git fundamentals
│   │   └── sdlc/                   # SDLC analysis, GitHub exploration
│   ├── ci-cd/
│   │   ├── fundamentals/           # Release engineering, CI toolkit
│   │   ├── github-actions/         # All GHA workflows and guides
│   │   └── pipelines/              # Pipeline implementations
│   ├── platform/
│   │   ├── github/                 # GitHub platform guides
│   │   ├── kubernetes/             # K8s stories
│   │   └── nginx/                  # Nginx cookbook
│   ├── gitops/                     # GitOps blueprints
│   └── secrets-management/
│       └── hashicorp-vault/        # All Vault docs
│
├── security/
│   ├── application-security/
│   │   ├── fundamentals/           # AppSec user stories
│   │   ├── programs/               # Security programs
│   │   ├── processes/              # Security processes, CI/CD mapping
│   │   └── learning/               # Certifications, courses, reading
│   ├── github-advanced-security/
│   │   ├── administration/         # GHAS admin, best practices
│   │   ├── code-scanning/          # CodeQL, SARIF
│   │   ├── secret-scanning/        # Secret scanning SOPs
│   │   ├── dependabot/             # Dependabot alerts
│   │   └── references/             # All cheatsheets
│   ├── cloud-security/             # Cloud security stories
│   ├── standards/
│   │   └── owasp/                  # OWASP Top 10 2025
│   └── certifications/
│       ├── ciso/
│       └── cissp/
│
├── programming/
│   ├── languages/
│   │   ├── c-cpp/
│   │   └── typescript/
│   └── web/
│       └── frontend/
│
├── game-development/
│   ├── design/                     # GDD template
│   ├── animation/
│   ├── asset-pipelines/            # AI sprite/model generation
│   └── physics-engines/            # Physics engine analysis
│
├── mathematics/
│   ├── algebra/
│   ├── calculus/
│   └── geometry/
│
├── data-systems/
│   ├── streaming/
│   │   └── kafka/
│   └── ai-ml/
│       └── llm/
│
├── electronics/
│
├── personal/
│   ├── finance/
│   └── recipes/
│       ├── breads/
│       ├── soups-stews/
│       ├── entrees/
│       ├── salads/
│       ├── desserts/
│       └── compilations/
│
└── common/

EOF
}

# Show structure when asked
if [[ "${1:-}" == "--show-structure" ]]; then
    show_new_structure
    exit 0
fi

# Run main
main "$@"