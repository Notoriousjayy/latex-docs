#!/usr/bin/env bash
# =============================================================================
# restructure.sh
#
# Implements RESTRUCTURE-PROPOSAL.md sections 5 and 9 for the
# notoriousjayy-latex-docs repository.
#
# Run from the top level of the repository:
#
#   chmod +x ./restructure.sh
#   ./restructure.sh inventory                # Phase 1 — read-only inspection
#   ./restructure.sh shared-assets            # Phase 2 — move src/common to tooling/
#   ./restructure.sh rename-outliers          # Phase 3 — kebab-case the snake/Pascal files
#   ./restructure.sh structural-moves         # Phase 4 — VAB renames + security flatten
#   ./restructure.sh extract-templates        # Phase 5 — gdd-template into templates/
#   ./restructure.sh add-readmes              # Phase 6 — generate READMEs
#   ./restructure.sh validate                 # post-phase checklist (proposal §10)
#   ./restructure.sh all                      # all phases in order, with prompts
#
# Common flags:
#   --dry-run        Print actions without executing them.
#   --yes            Skip confirmation prompts.
#   --allow-dirty    Allow running with uncommitted changes (NOT recommended).
#   --with-build     For 'validate': also run `make build-all`.
#   -h | --help      Show usage.
#
# Idempotency: every step checks whether it has already been done. Re-running
# any phase is safe.
#
# Variant pairs (proposal §5.6) are NOT touched — those require owner review.
# The inventory phase lists them as warnings.
#
# Author: generated to accompany RESTRUCTURE-PROPOSAL.md
# License: same as repository
# =============================================================================

set -euo pipefail
shopt -s nullglob

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
readonly SCRIPT_NAME=$(basename "${BASH_SOURCE[0]}")
readonly SCRIPT_VERSION="1.0.0"

# -----------------------------------------------------------------------------
# Flags (set by parse_args)
# -----------------------------------------------------------------------------
DRY_RUN=0
ASSUME_YES=0
ALLOW_DIRTY=0
WITH_BUILD=0
CMD=""

# -----------------------------------------------------------------------------
# Color output (auto-disabled when not a TTY or NO_COLOR is set)
# -----------------------------------------------------------------------------
if [[ -t 1 ]] && [[ -z "${NO_COLOR:-}" ]]; then
  RED=$'\e[31m'; GREEN=$'\e[32m'; YELLOW=$'\e[33m'
  BLUE=$'\e[34m'; DIM=$'\e[2m'; BOLD=$'\e[1m'; RESET=$'\e[0m'
else
  RED=""; GREEN=""; YELLOW=""; BLUE=""; DIM=""; BOLD=""; RESET=""
fi

# -----------------------------------------------------------------------------
# Logging primitives
# -----------------------------------------------------------------------------
log()  { printf '%s[ INFO ]%s %s\n'  "$BLUE"   "$RESET" "$*"; }
ok()   { printf '%s[  OK  ]%s %s\n'  "$GREEN"  "$RESET" "$*"; }
warn() { printf '%s[ WARN ]%s %s\n'  "$YELLOW" "$RESET" "$*" >&2; }
err()  { printf '%s[ FAIL ]%s %s\n'  "$RED"    "$RESET" "$*" >&2; }
hdr()  { printf '\n%s== %s ==%s\n'   "$BOLD"   "$*"     "$RESET"; }
die()  { err "$*"; exit 1; }

# -----------------------------------------------------------------------------
# Core helpers
# -----------------------------------------------------------------------------

# run COMMAND ARGS...
# Executes a command, or prints it if --dry-run is set.
run() {
  if (( DRY_RUN )); then
    printf '%s[ DRY  ]%s %s\n' "$DIM" "$RESET" "$*"
  else
    "$@"
  fi
}

# git_mv SRC DST
# Moves SRC to DST under git, with skip-if-already-done semantics.
git_mv() {
  local src=$1 dst=$2
  if [[ ! -e "$src" ]]; then
    log "skip git mv (source missing — already moved?): $src"
    return 0
  fi
  if [[ -e "$dst" ]]; then
    warn "skip git mv (destination exists): $dst"
    return 0
  fi
  local parent
  parent=$(dirname "$dst")
  [[ -d "$parent" ]] || run mkdir -p "$parent"
  run git mv "$src" "$dst"
}

# confirm PROMPT
# Returns 0 on yes, 1 on no. --yes auto-confirms.
confirm() {
  local prompt=$1
  if (( ASSUME_YES )); then
    log "auto-confirm: $prompt"
    return 0
  fi
  local ans
  read -r -p "$(printf '%s%s%s [y/N] ' "$BOLD" "$prompt" "$RESET")" ans
  [[ "$ans" =~ ^[Yy]$ ]]
}

# ensure_repo_root
# cd to the git toplevel; abort if not in a repo.
ensure_repo_root() {
  local toplevel
  toplevel=$(git rev-parse --show-toplevel 2>/dev/null) \
    || die "not inside a git repository"
  cd "$toplevel"
}

# ensure_clean_tree
# Abort if working tree or index is dirty (overridable with --allow-dirty).
ensure_clean_tree() {
  if (( ALLOW_DIRTY )); then
    warn "running with uncommitted changes (--allow-dirty)"
    return 0
  fi
  if ! git diff --quiet HEAD -- 2>/dev/null; then
    die "working tree has uncommitted changes; commit/stash or pass --allow-dirty"
  fi
  if ! git diff --cached --quiet 2>/dev/null; then
    die "index has staged changes; commit/stash or pass --allow-dirty"
  fi
}

# in_place_sed PATTERN FILE...
# GNU sed -i wrapper that respects --dry-run.
in_place_sed() {
  local pattern=$1
  shift
  for f in "$@"; do
    if (( DRY_RUN )); then
      printf '%s[ DRY  ]%s sed -E -i %q %s\n' "$DIM" "$RESET" "$pattern" "$f"
    else
      sed -E -i "$pattern" "$f"
    fi
  done
}

# print_status_summary
# After mutations, print git status so the operator sees what changed.
print_status_summary() {
  if (( DRY_RUN )); then return 0; fi
  hdr "git status (post-phase)"
  git status --short --untracked-files=all || true
}

# =============================================================================
# Phase 1 — Inventory
# =============================================================================

cmd_inventory() {
  hdr "Phase 1 — Inventory and classification"

  # ---------------------------------------------------------------------------
  # Baseline metrics
  # ---------------------------------------------------------------------------
  local tex_root_count puml_count tex_total
  tex_total=$(find src -type f -name '*.tex' 2>/dev/null | wc -l | tr -d ' ')
  tex_root_count=$(grep -rl --include='*.tex' '^\\documentclass' src/ 2>/dev/null \
                   | wc -l | tr -d ' ')
  puml_count=$(find src tooling -type f -name '*.puml' 2>/dev/null | wc -l | tr -d ' ')

  log "Total .tex files:           $tex_total"
  log "Buildable .tex roots:       $tex_root_count"
  log "Total .puml files:          $puml_count"

  # ---------------------------------------------------------------------------
  # Legacy include references (proposal §8.3)
  # ---------------------------------------------------------------------------
  hdr "Legacy include references"

  echo
  echo "  -- LaTeX \\input/\\include/\\includegraphics pointing at common/:"
  if ! grep -rnE '\\(input|include|includegraphics|inputminted)\{[^}]*common/' \
       src/ tooling/ 2>/dev/null | sed 's/^/    /'; then
    echo "    (none found)"
  fi

  echo
  echo "  -- PlantUML !include pointing at common/:"
  if ! grep -rnE '!include[[:space:]]+[^[:space:]]*common/' \
       src/ tooling/ 2>/dev/null | sed 's/^/    /'; then
    echo "    (none found)"
  fi

  echo
  echo "  -- Hard-coded legacy paths in .github/:"
  if ! grep -rnE 'src/(common|architecture-overview|ci-cd-pipeline)' \
       .github/ 2>/dev/null | sed 's/^/    /'; then
    echo "    (none found)"
  fi

  echo
  echo "  -- Hard-coded legacy paths in Makefile/latexmkrc:"
  if ! grep -nE 'src/(common|architecture-overview|ci-cd-pipeline)' \
       Makefile latexmkrc 2>/dev/null | sed 's/^/    /'; then
    echo "    (none found)"
  fi

  echo
  echo "  -- Naming-outlier references (snake_case / PascalCase):"
  if ! grep -rnE 'sunlight_tools|oop_in_ansi_c|misra_cpp2023_cpp17|oracle_secure_coding_standard_java|AutomatingCISBenchmarks' \
       --exclude-dir=.git --exclude-dir=public --exclude-dir=node_modules \
       --exclude='*.log' --exclude='*.pdf' --exclude='RESTRUCTURE-PROPOSAL.md' \
       --exclude="$SCRIPT_NAME" \
       . 2>/dev/null | sed 's/^/    /'; then
    echo "    (none found)"
  fi

  echo
  echo "  -- application-security-v3 / appsec-plantuml-processes references:"
  if ! grep -rnE 'application-security-v3|appsec-plantuml-processes' \
       --exclude-dir=.git --exclude-dir=public \
       --exclude='*.log' --exclude='RESTRUCTURE-PROPOSAL.md' \
       --exclude="$SCRIPT_NAME" \
       . 2>/dev/null | sed 's/^/    /'; then
    echo "    (none found)"
  fi

  # ---------------------------------------------------------------------------
  # Variant pairs (proposal §5.6) — these block Phase 3 if unresolved
  # ---------------------------------------------------------------------------
  hdr "Variant pairs requiring owner review (proposal §5.6)"
  cat <<'EOF'

  These pairs are NOT touched by this script. Decide canonical/alternate
  manually (or merge), then commit, then run later phases.

   1. src/personal/finance/cd-guide.tex
      + src/personal/finance/cd-guide-v2.tex

   2. src/security/application-security/fundamentals/appsec-user-stories.tex
      + .../appsec-user-stories-resequenced.tex

   3. src/security/cloud-security/cloud-computing-security-user-stories.tex
      + .../cloud-computing-security-user-stories-resequenced.tex

   4. src/devops/platform/nginx/nginx-cookbook-user-stories.tex
      + .../nginx-cookbook-user-stories-alt.tex

   5. src/mathematics/geometry/computational-geometry-c-user-stories.tex
      + .../computational-geometry-c-user-stories-v2.tex

   6. src/security/github-advanced-security/administration/ghas-appsec-user-stories.tex
      + .../ghas-appsec-user-stories-tailored.tex

   7. src/security/github-advanced-security/references/ghas-dependabot-cheatsheet.tex
      + .../ghas-dependabot-cheatsheet-detailed.tex

   8. src/security/github-advanced-security/secret-scanning/secret-scanning-triage-sop.tex
      + .../ghas-secret-scanning-triage-sop.tex

EOF

  # ---------------------------------------------------------------------------
  # Existence probes (state of in-progress migration)
  # ---------------------------------------------------------------------------
  hdr "Migration state probe"
  _probe "src/common/"                                                "removed by Phase 2"
  _probe "src/architecture-overview.puml"                             "moved by Phase 2"
  _probe "src/ci-cd-pipeline.puml"                                    "moved by Phase 2"
  _probe "tooling/latex/ci-safe-macros.tex"                           "created by Phase 2" --want-present
  _probe "tooling/plantuml/config.puml"                               "created by Phase 2" --want-present
  _probe "src/personal/gardening/sunlight_tools.tex"                  "renamed by Phase 3"
  _probe "src/security/standards/cis/AutomatingCISBenchmarks.tex"    "renamed by Phase 3"
  _probe "src/architecture/views-and-beyond/architectural-style-catalog/" \
                                                                      "renamed by Phase 4"
  _probe "src/security/application-security/processes/application-security-v3/" \
                                                                      "removed by Phase 4"
  _probe "src/README.md"                                              "created by Phase 6" --want-present

  ok "inventory complete"
}

# _probe PATH MESSAGE [--want-present]
# Reports whether PATH currently exists; default expectation is "should be gone".
_probe() {
  local path=$1 msg=$2 want_present=0
  shift 2
  for arg in "$@"; do
    [[ "$arg" == "--want-present" ]] && want_present=1
  done
  if [[ -e "$path" ]]; then
    if (( want_present )); then
      ok "  present: $path  ($msg)"
    else
      log "  present: $path  ($msg) — pending"
    fi
  else
    if (( want_present )); then
      log "  absent:  $path  ($msg) — pending"
    else
      ok "  absent:  $path  ($msg) — done"
    fi
  fi
}

# =============================================================================
# Phase 2 — Shared assets
# =============================================================================

cmd_shared_assets() {
  hdr "Phase 2 — Move shared assets"
  ensure_clean_tree

  # 2.1 — Create target directories
  log "creating target directories"
  run mkdir -p tooling/plantuml \
               src/architecture/diagrams \
               src/devops/ci-cd/diagrams

  # 2.2 — Move src/common contents into tooling/
  log "moving shared LaTeX macros to tooling/latex/"
  git_mv src/common/ci-safe-macros.tex \
         tooling/latex/ci-safe-macros.tex

  log "moving shared PlantUML config to tooling/plantuml/"
  git_mv src/common/config.puml \
         tooling/plantuml/config.puml

  # 2.3 — Re-home orphan PUMLs at src/ root
  log "rehoming orphan PUMLs to domain diagrams/"
  git_mv src/architecture-overview.puml \
         src/architecture/diagrams/architecture-overview.puml
  git_mv src/ci-cd-pipeline.puml \
         src/devops/ci-cd/diagrams/ci-cd-pipeline.puml

  # 2.4 — Remove now-empty src/common
  if [[ -d src/common ]]; then
    if [[ -z "$(ls -A src/common 2>/dev/null)" ]]; then
      log "removing empty src/common/"
      run rmdir src/common
    else
      warn "src/common/ is not empty — leftover files require manual review:"
      ls -la src/common/ >&2
    fi
  fi

  # 2.5 — Normalize \input{*/common/ci-safe-macros} -> \input{ci-safe-macros}
  hdr "Normalizing LaTeX includes for ci-safe-macros"
  local tex_files=()
  while IFS= read -r f; do
    tex_files+=("$f")
  done < <(grep -rlE '\\(input|include|includegraphics|inputminted)\{[^}]*common/ci-safe-macros' \
           src/ tooling/ 2>/dev/null || true)

  if (( ${#tex_files[@]} == 0 )); then
    log "  no legacy LaTeX include references found"
  else
    log "  ${#tex_files[@]} file(s) to normalize:"
    for f in "${tex_files[@]}"; do
      log "    $f"
    done
    in_place_sed \
      's#\\input\{[^}]*common/ci-safe-macros[^}]*\}#\\input{ci-safe-macros}#g' \
      "${tex_files[@]}"
  fi

  # 2.6 — Normalize !include common/config.puml -> !include config.puml
  hdr "Normalizing PlantUML !include references"
  local puml_files=()
  while IFS= read -r f; do
    puml_files+=("$f")
  done < <(grep -rlE '!include[[:space:]]+[^[:space:]]*common/config\.puml' \
           src/ tooling/ 2>/dev/null || true)

  if (( ${#puml_files[@]} == 0 )); then
    log "  no legacy PlantUML !include references found"
  else
    log "  ${#puml_files[@]} file(s) to normalize:"
    for f in "${puml_files[@]}"; do
      log "    $f"
    done
    in_place_sed \
      's#!include[[:space:]]+[^[:space:]]*common/config\.puml#!include config.puml#g' \
      "${puml_files[@]}"
  fi

  # 2.7 — Render-action update notice
  hdr "PlantUML render action"
  local action_yml=.github/actions/render-plantuml/action.yml
  if [[ -f "$action_yml" ]]; then
    if grep -q 'tooling/plantuml' "$action_yml"; then
      ok "  $action_yml already references tooling/plantuml"
    else
      warn "  $action_yml does NOT include 'tooling/plantuml'"
      warn "  Add the following flag to the plantuml invocation manually:"
      cat <<'EOF' >&2

      plantuml -tpng -charset UTF-8 \
        -include-search-path tooling/plantuml \
        <input-glob>

EOF
    fi
  else
    warn "  $action_yml not found — skipping advisory"
  fi

  print_status_summary
  ok "Phase 2 complete"
}

# =============================================================================
# Phase 3 — Rename naming outliers
# =============================================================================

cmd_rename_outliers() {
  hdr "Phase 3 — Rename naming outliers"
  ensure_clean_tree

  # 3.1 — sunlight_tools.tex
  git_mv src/personal/gardening/sunlight_tools.tex \
         src/personal/gardening/sunlight-tools.tex

  # 3.2 — OOP in ANSI C rules
  git_mv src/programming/languages/c-cpp/oop_in_ansi_c_rules_checklists.tex \
         src/programming/languages/c-cpp/oop-in-ansi-c-rules-checklists.tex

  # 3.3 — MISRA C++ guideline index
  git_mv src/programming/languages/c-cpp/standards/misra/misra_cpp2023_cpp17_guideline_index.tex \
         src/programming/languages/c-cpp/standards/misra/misra-cpp-2023-cpp17-guideline-index.tex

  # 3.4 — Oracle Java rules catalog
  git_mv src/programming/languages/java/secure-coding/oracle_secure_coding_standard_java_rules_catalog.tex \
         src/programming/languages/java/secure-coding/oracle-secure-coding-standard-java-rules-catalog.tex

  # 3.5 — CIS benchmarks (PascalCase)
  git_mv src/security/standards/cis/AutomatingCISBenchmarks.tex \
         src/security/standards/cis/automating-cis-benchmarks.tex

  # 3.6 — Sanity check: nothing else with snake/Pascal under src/
  hdr "Verifying no remaining snake_case/PascalCase .tex/.puml under src/"
  local stragglers
  stragglers=$(find src -type f \( -name '*.tex' -o -name '*.puml' \) \
               2>/dev/null | grep -E '[A-Z]|_[a-zA-Z0-9]+\.[a-z]+$' || true)
  if [[ -n "$stragglers" ]]; then
    warn "  Stragglers detected — review and add explicit rename rules:"
    echo "$stragglers" | sed 's/^/    /' >&2
  else
    ok "  none"
  fi

  print_status_summary
  ok "Phase 3 complete"
}

# =============================================================================
# Phase 4 — Structural moves (views-and-beyond + security)
# =============================================================================

cmd_structural_moves() {
  hdr "Phase 4 — Structural moves"
  ensure_clean_tree

  local vab=src/architecture/views-and-beyond

  # 4.1 — architectural-style-catalog → style-catalogs
  if [[ -d "$vab/architectural-style-catalog" ]] && [[ ! -d "$vab/style-catalogs" ]]; then
    log "renaming $vab/architectural-style-catalog → style-catalogs/"
    git_mv "$vab/architectural-style-catalog" "$vab/style-catalogs"
  fi

  # 4.2 — *-catalog inner folders
  local sc=$vab/style-catalogs
  if [[ -d "$sc/allocation-catalog" ]] && [[ ! -d "$sc/allocation" ]]; then
    git_mv "$sc/allocation-catalog" "$sc/allocation"
  fi
  if [[ -d "$sc/component-connector-catalog" ]] && [[ ! -d "$sc/component-and-connector" ]]; then
    git_mv "$sc/component-connector-catalog" "$sc/component-and-connector"
  fi
  if [[ -d "$sc/module-catalog" ]] && [[ ! -d "$sc/module" ]]; then
    git_mv "$sc/module-catalog" "$sc/module"
  fi

  # 4.3 — pipe-and-filter → pipe-and-filter-style
  local cnc=$sc/component-and-connector
  if [[ -d "$cnc/pipe-and-filter" ]] && [[ ! -d "$cnc/pipe-and-filter-style" ]]; then
    git_mv "$cnc/pipe-and-filter" "$cnc/pipe-and-filter-style"
  fi

  # 4.4 — Collapse application-security-v3/appsec-plantuml-processes/puml/
  local proc=src/security/application-security/processes
  local old_root="$proc/application-security-v3"
  local old_dir="$old_root/appsec-plantuml-processes"
  local new_dir="$proc/appsec-process-diagrams"

  if [[ -d "$old_dir/puml" ]] && [[ ! -d "$new_dir" ]]; then
    log "collapsing $old_dir/{puml,README.md} → $new_dir/"
    run mkdir -p "$new_dir"

    # Move all .puml files from old puml/ folder
    local pf
    for pf in "$old_dir/puml/"*.puml; do
      [[ -e "$pf" ]] || continue
      git_mv "$pf" "$new_dir/$(basename "$pf")"
    done

    # Move README.md if present
    if [[ -f "$old_dir/README.md" ]]; then
      git_mv "$old_dir/README.md" "$new_dir/README.md"
    fi

    # Remove now-empty intermediate directories
    if [[ -d "$old_dir/puml" ]]; then
      if (( DRY_RUN )); then
        printf '%s[ DRY  ]%s rmdir %s\n' "$DIM" "$RESET" "$old_dir/puml"
      else
        rmdir "$old_dir/puml" 2>/dev/null \
          || warn "  $old_dir/puml not empty after move"
      fi
    fi
    if [[ -d "$old_dir" ]]; then
      if (( DRY_RUN )); then
        printf '%s[ DRY  ]%s rmdir %s\n' "$DIM" "$RESET" "$old_dir"
      else
        rmdir "$old_dir" 2>/dev/null \
          || warn "  $old_dir not empty after move"
      fi
    fi
    if [[ -d "$old_root" ]]; then
      if (( DRY_RUN )); then
        printf '%s[ DRY  ]%s rmdir %s\n' "$DIM" "$RESET" "$old_root"
      else
        rmdir "$old_root" 2>/dev/null \
          || warn "  $old_root not empty after move"
      fi
    fi
  fi

  # 4.5 — Field-guide flatten
  local fg_root=src/security/application-security/web-security/broken-access-control/field-guides
  local fg_old="$fg_root/user-id-controlled-by-param-with-password-disclosure"
  local fg_new="$fg_root/user-id-param-password-disclosure"
  local long_file="user-id-controlled-by-param-password-disclosure-field-guide.tex"

  if [[ -d "$fg_old" ]] && [[ ! -d "$fg_new" ]]; then
    log "shortening field-guide folder slug"
    git_mv "$fg_old" "$fg_new"
  fi
  if [[ -f "$fg_new/$long_file" ]] && [[ ! -f "$fg_new/field-guide.tex" ]]; then
    log "shortening field-guide filename"
    git_mv "$fg_new/$long_file" "$fg_new/field-guide.tex"
  fi

  # 4.6 — Cross-reference sweep
  hdr "Searching for stale references to renamed paths"
  local stale_patterns='architectural-style-catalog|allocation-catalog|component-connector-catalog|module-catalog|application-security-v3|appsec-plantuml-processes|user-id-controlled-by-param-with-password-disclosure|user-id-controlled-by-param-password-disclosure-field-guide'
  local stale_hits
  stale_hits=$(grep -rnE "$stale_patterns" src/ tooling/ .github/ Makefile latexmkrc \
       --exclude="$SCRIPT_NAME" 2>/dev/null \
       | grep -v 'RESTRUCTURE-PROPOSAL.md' || true)
  if [[ -n "$stale_hits" ]]; then
    warn "  Stale references found — manual fix-up required:"
    echo "$stale_hits" | sed 's/^/    /' >&2
    warn "  Run 'sed -i' against each file or use your editor's project-wide replace."
  else
    ok "  No stale references detected"
  fi

  print_status_summary
  ok "Phase 4 complete"
}

# =============================================================================
# Phase 5 — Templates extraction
# =============================================================================

cmd_extract_templates() {
  hdr "Phase 5 — Extract templates (optional)"
  ensure_clean_tree

  # 5.1 — gdd-template into design-documents/templates/
  local gd=src/game-development/design-documents
  if [[ -f "$gd/gdd-template.tex" ]] && [[ ! -f "$gd/templates/gdd-template.tex" ]]; then
    git_mv "$gd/gdd-template.tex" "$gd/templates/gdd-template.tex"
  fi

  # 5.2 — viewpoint-template (owner discretion, off by default)
  local vab=src/architecture/views-and-beyond
  if [[ -f "$vab/advanced-concepts/viewpoint-template.tex" ]] \
     && [[ ! -f "$vab/templates/viewpoint-template.tex" ]]; then
    if [[ "${VIEWPOINT_TEMPLATE_MOVE:-0}" == "1" ]]; then
      git_mv "$vab/advanced-concepts/viewpoint-template.tex" \
             "$vab/templates/viewpoint-template.tex"
    else
      log "  Note: viewpoint-template.tex stays under advanced-concepts/ by default."
      log "  To move it, set VIEWPOINT_TEMPLATE_MOVE=1 and re-run."
    fi
  fi

  print_status_summary
  ok "Phase 5 complete"
}

# =============================================================================
# Phase 6 — Add README files
# =============================================================================

cmd_add_readmes() {
  hdr "Phase 6 — Add READMEs"

  _write_readme src/README.md                                          _readme_root
  _write_readme src/architecture/README.md                             _readme_architecture
  _write_readme src/architecture/views-and-beyond/README.md            _readme_vab
  _write_readme src/data-systems/README.md                             _readme_data_systems
  _write_readme src/devops/README.md                                   _readme_devops
  _write_readme src/electronics/README.md                              _readme_electronics
  _write_readme src/game-development/README.md                         _readme_game_dev
  _write_readme src/mathematics/README.md                              _readme_mathematics
  _write_readme src/personal/README.md                                 _readme_personal
  _write_readme src/programming/README.md                              _readme_programming
  _write_readme src/security/README.md                                 _readme_security

  print_status_summary
  ok "Phase 6 complete"
}

# _write_readme PATH GENERATOR_FN
# Calls GENERATOR_FN to obtain content; writes only if PATH does not exist.
_write_readme() {
  local path=$1 generator=$2
  if [[ -f "$path" ]]; then
    log "skip (exists): $path"
    return 0
  fi
  if (( DRY_RUN )); then
    printf '%s[ DRY  ]%s would write %s\n' "$DIM" "$RESET" "$path"
    return 0
  fi
  mkdir -p "$(dirname "$path")"
  "$generator" > "$path"
  log "wrote $path"
}

# -- README content generators ------------------------------------------------

_readme_root() { cat <<'EOF'
# src/

LaTeX document sources, organized by domain. Every top-level folder is a
domain; within a domain, content is grouped by subdomain or by document
type. The repository builds standalone roots (`.tex` files containing
`\documentclass`); the `Makefile` discovers them automatically.

## Domains

| Folder | Contents |
|---|---|
| `architecture/` | Software & enterprise architecture, Views and Beyond, TOGAF, governance. |
| `data-systems/` | AI/ML, streaming (Kafka), and other data-platform documentation. |
| `devops/` | CI/CD, GitHub Actions, GitOps, platform (k8s, nginx), secrets management. |
| `electronics/` | Self-study electronics (Art of Electronics curriculum). |
| `game-development/` | Game design documents, animation, asset pipelines, physics engines. |
| `mathematics/` | Algebra, calculus, geometry — typeset references and study plans. |
| `personal/` | Personal/finance/gardening reference material. |
| `programming/` | Language references (C/C++, Java, TypeScript) and web/frontend. |
| `security/` | AppSec, GHAS, OWASP, certifications, cloud security, CIS standards. |

## Conventions

- **Naming:** lowercase kebab-case for every folder and file. See
  `RESTRUCTURE-PROPOSAL.md` §6 for the full rules.
- **House style:** every root document loads
  `\usepackage{latex-docs-style}` (resolved via `TEXINPUTS` to
  `tooling/latex/latex-docs-style.sty`).
- **Diagrams:** PlantUML co-locates with the document that owns it.
  Cross-cutting PlantUML config lives in `tooling/plantuml/`.
- **Generated artifacts:** PDFs and LaTeX aux files are git-ignored;
  CI publishes built PDFs under `public/`.

## Building

```bash
make list-roots                       # show every buildable .tex
make build-all                        # serial build of every root
make build-parallel JOBS=8            # parallel build
make build-category-architecture      # one category
```

For a single document, see the parent `README.md` of its folder.

## Document-type taxonomy

Within a domain, when ≥ 2 documents share a type, group them under one of
the following folder names:

| Folder | Use for |
|---|---|
| `fundamentals/` | Introductory and foundational explainers. |
| `references/` | Cheatsheets, indexes, cataloged rules. |
| `runbooks/` | SOPs, triage workflows, playbooks. |
| `study-plans/` | Curricula, ordered user-story sequences. |
| `templates/` | Reusable starting points (not meant to compile alone). |

Singletons live at the domain or subdomain root. The taxonomy is a
convention, not a mandate.

## Related

- `../README.md` — repository top-level README.
- `../tooling/latex/latex-docs-style.sty` — house style.
- `../RESTRUCTURE-PROPOSAL.md` — restructuring rationale.
EOF
}

_readme_architecture() { cat <<'EOF'
# Architecture

Software and enterprise architecture documentation: viewpoint
frameworks, governance, patterns, systems engineering, and TOGAF
adoption material.

## Scope

**Belongs here:**
- Architectural-viewpoint documentation (Views and Beyond, ISO/IEC/IEEE 42010, RUP, DoDAF).
- Enterprise framework material (TOGAF ADM, viewpoint mappings).
- Governance frameworks at the architectural layer (cloud governance, control frameworks).
- Architectural patterns (build-system facades, etc.).

**Does not belong here:**
- AppSec process flows — see `../security/application-security/processes/`.
- CI/CD pipeline details — see `../devops/ci-cd/`.
- Code-level patterns and language idioms — see `../programming/`.

## Contents

| Child | Purpose |
|---|---|
| `governance/` | Cloud governance and control frameworks; Confluence space rationale. |
| `patterns/` | Architectural patterns (build-system facade, etc.). |
| `systems-engineering/` | Systems-engineering perspective on software architecture. |
| `togaf/` | TOGAF ADM user stories and overviews. |
| `views-and-beyond/` | The largest subtree — Views and Beyond methodology, style catalogs, framework mappings. See child README. |
| `diagrams/` | Cross-cutting architecture diagrams not owned by any single document. |

## Conventions

- Diagrams co-locate with the document that owns them, except in
  `diagrams/` (cross-cutting only).
- Style catalogs sit under `views-and-beyond/style-catalogs/<aspect>/<style>-style/`.
- Framework mappings are named `mapping-to-<framework>.tex`.

## Building

```bash
make build-category-architecture
```

## Related

- `../README.md`
- `views-and-beyond/README.md`
- Upstream: *Documenting Software Architectures: Views and Beyond* (Clements et al., 2nd ed.).
EOF
}

_readme_vab() { cat <<'EOF'
# Views and Beyond

The Views and Beyond methodology for documenting software architecture
(Clements, Bachmann, Bass, Garlan, Ivers, Little, Merson, Nord, Stafford —
2nd ed.). This subtree is the spine of the architecture documentation.

## Scope

**Belongs here:**
- Foundational explanations of the methodology (`fundamentals/`).
- Advanced topics (`advanced-concepts/`): variation points, spectrum of style specializations, viewpoint templates.
- Framework mappings: how Views and Beyond aligns with DoDAF, ISO 42010, RUP, Rozanski & Woods.
- Style catalogs: per-style documentation with co-located PUML diagrams.

**Does not belong here:**
- Application-domain examples — those go in their owning domain folder (`../../security/`, etc.).
- Tools and CI — see `../../../tooling/` and `../../../.github/`.

## Contents

| Child | Purpose |
|---|---|
| `fundamentals/` | Stakeholder needs, effective diagrams, review across phases, beyond-views. |
| `advanced-concepts/` | Variation points, style specializations, viewpoint template. |
| `framework-mappings/` | Mappings to DoDAF, ISO 42010, RUP, Rozanski & Woods. |
| `style-catalogs/` | Style catalog grouped by viewpoint family (allocation, component-and-connector, module). |

## Style-catalog organization

```
style-catalogs/
├── allocation/                       # how software allocates to environment
│   ├── deployment-style/
│   ├── install-style/
│   └── work-assignment-style/
├── component-and-connector/          # runtime component/connector views
│   ├── client-server-style/
│   ├── component-and-connector-views/
│   ├── peer-to-peer-style/
│   ├── pipe-and-filter-style/
│   ├── publish-subscribe-style/
│   ├── service-oriented-architecture-style/
│   └── shared-data-style/
└── module/                           # static decomposition of code units
    ├── aspects-style/
    ├── data-model-style/
    ├── decomposition-style/
    ├── generalization-style/
    ├── layered-style/
    ├── module-views/
    └── uses-style/
```

Each `*-style/` folder contains numbered PUML diagrams and (typically)
one `.tex` document explaining the style.

## Conventions

- PUML files in a numbered series use 2-digit prefixes: `01-…`, `02-…`.
- Each style's `.tex` shares the folder slug: `decomposition-style/decomposition-style.tex`.
- `viewpoint-template.tex` (under `advanced-concepts/`) is the canonical
  starting point for a new style write-up.

## Building

```bash
make build-category-architecture
```

## Related

- `../README.md`
- `framework-mappings/mapping-to-iso42010.tex`
- Upstream: *Documenting Software Architectures: Views and Beyond* (2nd ed.).
EOF
}

_readme_data_systems() { cat <<'EOF'
# Data Systems

Data-platform documentation — AI/ML, streaming, and other system-level
data infrastructure topics. Currently sparse; structured in anticipation
of growth.

## Scope

**Belongs here:**
- LLM adoption and AI/ML system stories (`ai-ml/llm/`).
- Streaming-platform material (`streaming/kafka/`).
- Future: warehouses, lakes, lineage, contracts.

**Does not belong here:**
- Application-level data persistence patterns — see `../architecture/views-and-beyond/style-catalogs/module/data-model-style/`.
- Database security topics — see `../security/`.

## Contents

| Child | Purpose |
|---|---|
| `ai-ml/llm/` | LLM adoption user stories and AI/ML platform docs. |
| `streaming/kafka/` | Kafka adoption and platform user stories. |

## Conventions

- New AI/ML topics get their own folder under `ai-ml/<topic>/`.
- New streaming systems get their own folder under `streaming/<system>/`.
- Singleton folders are fine; this domain is intentionally
  forward-structured.

## Building

```bash
make build-category-data-systems
```

## Related

- `../README.md`
- Future expansion targets: warehouses, OLAP, data contracts.
EOF
}

_readme_devops() { cat <<'EOF'
# DevOps

Continuous delivery, version control, GitHub Actions, GitOps,
platform-engineering targets, and secrets management.

## Scope

**Belongs here:**
- CI/CD pipeline content, including GitHub Actions.
- SDLC, version-control, and GitHub-platform foundations.
- Platform targets (Kubernetes, Nginx).
- Secrets-management runbooks (HashiCorp Vault).

**Does not belong here:**
- AppSec gates inside CI — see `../security/application-security/`.
- GHAS-specific operational content — see `../security/github-advanced-security/`.

## Contents

| Child | Purpose |
|---|---|
| `ci-cd/` | CI/CD fundamentals, pipelines, and cross-cutting CI diagrams. |
| `foundations/` | SDLC fundamentals, Git, and base GitHub literacy. |
| `github-actions/` | GitHub Actions guides, workflow attribute references, custom actions. |
| `gitops/` | GitOps stack blueprints. |
| `platform/` | GitHub-platform hygiene, Kubernetes user stories, Nginx cookbooks. |
| `secrets-management/` | HashiCorp Vault primers and runbooks. |

## Conventions

- Workflow guides live under `github-actions/`; pipeline architecture
  lives under `ci-cd/pipelines/`. Don't mix the two.
- Cross-cutting CI diagrams (used by multiple roots) live in
  `ci-cd/diagrams/`; per-document diagrams co-locate.

## Building

```bash
make build-category-devops
```

## Related

- `../README.md`
- `../security/github-advanced-security/` (CI security gates).
- `../../tooling/plantuml/config.puml` (shared PlantUML config).
EOF
}

_readme_electronics() { cat <<'EOF'
# Electronics

Self-study electronics documentation, structured around *The Art of
Electronics* (Horowitz & Hill, 3rd ed.) and the companion *X-Chapters*
lab course.

## Scope

**Belongs here:**
- Curriculum maps for Art of Electronics and its lab companion.
- Future: lab notebooks, breadboarding diagrams, component data
  references that don't already live in the components reference DB.

**Does not belong here:**
- Embedded-software content — see `../programming/languages/c-cpp/`.
- Game-engine hardware notes — see `../game-development/`.

## Contents

| File | Purpose |
|---|---|
| `art-of-electronics-curriculum.tex` | Topic ordering and reading sequence for AoE 3rd ed. |
| `art-of-electronics-x-chapters-lab-course.tex` | Lab-course companion plan. |

## Conventions

- New textbook curricula become standalone roots named
  `<book-slug>-curriculum.tex`.
- Lab notebooks (when added) go under `lab-notebooks/<topic>/`.

## Building

```bash
make build-category-electronics
```

## Related

- `../README.md`
EOF
}

_readme_game_dev() { cat <<'EOF'
# Game Development

Game-engine and game-design documentation. Strong overlap with the
solo-authored AetherForge Engine project (C/C++, SDL3, OpenGL ES 3.0,
WebGL 2.0) — engine-internal docs live in the engine repository; this
folder hosts cross-cutting and study-plan material.

## Scope

**Belongs here:**
- Game-design documents (GDDs) and the GDD template.
- Animation and asset-pipeline notes.
- Physics-engine gap analyses and study plans.
- Cross-engine pipeline blueprints (AI-assisted asset generation, etc.).

**Does not belong here:**
- AetherForge Engine internal API documentation (lives in the engine repo).
- WebAssembly build-system docs — see `../programming/languages/c-cpp/wasm/`.

## Contents

| Child | Purpose |
|---|---|
| `animation/` | Computer animation user stories. |
| `asset-pipelines/` | AI-assisted 3D model and sprite pipelines. |
| `design-documents/` | GDD overview document and template (`templates/`). |
| `physics-engines/` | Physics-engine gap analyses. |

## Conventions

- The GDD template (`design-documents/templates/gdd-template.tex`)
  is the starting point for new GDDs; copy it before customizing.
- Asset-pipeline write-ups end with `-pipeline.tex`.

## Building

```bash
make build-category-game-development
```

## Related

- `../README.md`
- `../programming/languages/c-cpp/` for engine-language references.
EOF
}

_readme_mathematics() { cat <<'EOF'
# Mathematics

Typeset mathematics references and study plans. Most documents are
companion material to algorithmic implementations maintained in
sibling C/C++ projects.

## Scope

**Belongs here:**
- Algebra, calculus, and geometry user-story sequences.
- Study plans for algorithm-heavy texts (e.g., O'Rourke's *Computational Geometry in C*).
- Matrix/polynomial operation references that benefit from LaTeX typesetting.

**Does not belong here:**
- Implementation code — those live in domain-specific C/C++ libraries.
- Numerical-recipes implementations — separate project.

## Contents

| Child | Purpose |
|---|---|
| `algebra/` | Matrix and polynomial operations; data structures in C/C++. |
| `calculus/` | Handbook-of-calculus user stories. |
| `geometry/` | Computational-geometry user stories and study plans. |

## Conventions

- User-story sequences end with `-user-stories.tex`.
- Study plans end with `-study-plan.tex`.
- Companion data-structure notes end with `-data-structures-in-c-and-cpp.tex`.

## Building

```bash
make build-category-mathematics
```

## Related

- `../README.md`
- `../programming/languages/c-cpp/` (implementation companions).
- Upstream: O'Rourke, *Computational Geometry in C*; *Handbook of Discrete and Computational Geometry*, 3rd ed.
EOF
}

_readme_personal() { cat <<'EOF'
# Personal

Personal reference material — finance and gardening so far. Kept under
the same build pipeline as professional content for consistency.

## Scope

**Belongs here:**
- Personal-finance reference (e.g., CD ladder strategies).
- Gardening reference for the home garden.

**Does not belong here:**
- Hobby electronics — see `../electronics/`.
- Anything intended for public/professional consumption.

## Contents

| Child | Purpose |
|---|---|
| `finance/` | Personal-finance reference documents. |
| `gardening/` | Container/raised-bed gardening tools and references. |

## Conventions

- This domain is private-leaning. Do not link these docs from public
  README files or include them in customer-facing PDF releases.

## Building

```bash
make build-category-personal
```

## Related

- `../README.md`
EOF
}

_readme_programming() { cat <<'EOF'
# Programming

Programming-language references, language-standards documentation, and
web/frontend study plans.

## Scope

**Belongs here:**
- Language-specific guides (C/C++, Java, TypeScript).
- Language-standard references (MISRA C:2023, MISRA C++:2023, Oracle Secure Coding for Java).
- Web/frontend study plans and design-pattern user stories.

**Does not belong here:**
- AppSec language coverage — see `../security/application-security/`.
- CI/CD pipeline configuration — see `../devops/`.

## Contents

| Child | Purpose |
|---|---|
| `languages/c-cpp/` | C/C++ guides, embedded OOP, MISRA standards, WebAssembly. |
| `languages/java/` | Secure coding guidelines and Oracle catalog. |
| `languages/typescript/` | Effective TypeScript and cookbook user stories. |
| `web/frontend/` | Site-design study plans, micro-frontends, project-board UX. |

## Conventions

- Standards documents live under `<language>/standards/<standard>/`.
- Naming is strictly kebab-case; underscores and CamelCase are not allowed
  (the migration script enforces this on Phase 3).

## Building

```bash
make build-category-programming
```

## Related

- `../README.md`
- `../security/standards/owasp/` for application-layer rules.
EOF
}

_readme_security() { cat <<'EOF'
# Security

The largest documentation domain: AppSec, GitHub Advanced Security,
certifications, cloud security, and standards (CIS, OWASP).

## Scope

**Belongs here:**
- Application-security programs, processes, and field guides.
- GHAS operational SOPs, runbooks, and cheatsheets.
- Certification study plans (CISSP, CCSP, CISO, GH-500).
- Cloud-security user-story sequences.
- Standards mappings (CIS benchmarks, OWASP Top 10 / API Top 10).

**Does not belong here:**
- General CI/CD content — see `../devops/`.
- Language-level secure-coding rules — see `../programming/languages/<lang>/secure-coding/`.

## Contents

| Child | Purpose |
|---|---|
| `application-security/` | AppSec fundamentals, learning paths, processes, programs, web-security field guides. |
| `certifications/` | CISSP, CISO, GH-500 study plans. |
| `cloud-security/` | Cloud-computing security user-story sequences. |
| `github-advanced-security/` | GHAS administration, code scanning (CodeQL), Dependabot, references, secret scanning. |
| `standards/` | CIS benchmarks; OWASP Top 10 (2025) and API Security Top 10. |

## Conventions

- **Triage SOPs** end with `-triage-sop.tex`.
- **Closure runbooks** end with `-runbook.tex` or `-playbook.tex`.
- **Cheatsheets** live in the relevant `references/` folder, never
  alongside the operational SOP they reference.
- **Field guides** live under `web-security/<vuln-class>/field-guides/<short-slug>/field-guide.tex`.
- **Process diagrams** for AppSec sit in
  `application-security/processes/appsec-process-diagrams/`.

## Building

```bash
make build-category-security
```

## Related

- `../README.md`
- `../programming/languages/c-cpp/standards/misra/` for MISRA rules.
- `../programming/languages/java/secure-coding/` for Oracle CERT rules.
EOF
}

# =============================================================================
# Validation
# =============================================================================

cmd_validate() {
  hdr "Validation (proposal §10)"
  local fail=0

  # 10.3 — No legacy paths
  log "Checking for legacy paths..."
  local legacy_pattern='src/common|architectural-style-catalog|allocation-catalog|component-connector-catalog|module-catalog|application-security-v3|appsec-plantuml-processes'
  local hits
  hits=$(grep -rnE "$legacy_pattern" \
       --exclude="$SCRIPT_NAME" \
       --exclude='RESTRUCTURE-PROPOSAL.md' \
       --exclude-dir=public \
       --exclude-dir=.git \
       src/ tooling/ .github/ 2>/dev/null || true)
  if [[ -n "$hits" ]]; then
    err "  legacy paths still referenced:"
    echo "$hits" | sed 's/^/    /' >&2
    fail=1
  else
    ok "  no legacy paths in source/tooling/.github"
  fi

  # No snake_case or PascalCase in src/ for .tex/.puml
  log "Checking for snake_case/PascalCase in .tex/.puml under src/..."
  local outliers
  outliers=$(find src -type f \( -name '*.tex' -o -name '*.puml' \) 2>/dev/null \
             | grep -E '[A-Z]|_[a-zA-Z0-9]+\.[a-z]+$' || true)
  if [[ -n "$outliers" ]]; then
    err "  outlier filenames remain:"
    echo "$outliers" | sed 's/^/    /' >&2
    fail=1
  else
    ok "  all kebab-case"
  fi

  # No PDFs in src/
  log "Checking for committed PDFs in src/..."
  if find src -type f -name '*.pdf' -print -quit 2>/dev/null | grep -q .; then
    err "  PDFs found under src/ (should be gitignored):"
    find src -type f -name '*.pdf' 2>/dev/null | head -20 | sed 's/^/    /' >&2
    fail=1
  else
    ok "  no PDFs in src/"
  fi

  # No aux/log files in src/
  log "Checking for LaTeX aux files in src/..."
  if find src -type f \
       \( -name '*.aux' -o -name '*.fls' -o -name '*.fdb_latexmk' \
       -o -name '*.synctex.gz' -o -name '*.toc' -o -name '*.out' \) \
       -print -quit 2>/dev/null | grep -q .; then
    err "  aux files found under src/ (should be gitignored)"
    fail=1
  else
    ok "  no aux files in src/"
  fi

  # README presence
  log "Checking for required READMEs..."
  local missing=0
  for d in src \
           src/architecture src/architecture/views-and-beyond \
           src/data-systems src/devops src/electronics \
           src/game-development src/mathematics src/personal \
           src/programming src/security; do
    if [[ ! -f "$d/README.md" ]]; then
      err "  MISSING: $d/README.md"
      missing=$((missing+1))
    fi
  done
  if (( missing == 0 )); then
    ok "  all required READMEs present"
  else
    fail=1
  fi

  # Optional build
  if (( WITH_BUILD )); then
    log "Running 'make build-all' (this can take 10-20 minutes)..."
    if make build-all; then
      ok "  build green"
    else
      err "  build failed"
      fail=1
    fi
  fi

  if (( fail )); then
    die "validation FAILED"
  fi
  ok "validation passed"
}

# =============================================================================
# All — drive every phase with confirmation gates
# =============================================================================

cmd_all() {
  cmd_inventory
  echo

  warn "Variant pairs (proposal §5.6) must be resolved manually before continuing."
  warn "Re-read the inventory above and decide each canonical-vs-alternate."
  if ! confirm "Have you resolved the variant pairs?"; then
    die "aborted: resolve variants and re-run"
  fi

  hdr "About to run Phase 2 — shared assets"
  if confirm "Proceed with Phase 2?"; then
    cmd_shared_assets
  else
    die "aborted at Phase 2"
  fi
  echo

  hdr "About to run Phase 3 — rename naming outliers"
  if confirm "Proceed with Phase 3?"; then
    cmd_rename_outliers
  else
    die "aborted at Phase 3"
  fi
  echo

  hdr "About to run Phase 4 — structural moves (largest diff)"
  warn "This phase produces the bulk of the rename diff. Use a separate commit."
  if confirm "Proceed with Phase 4?"; then
    cmd_structural_moves
  else
    die "aborted at Phase 4"
  fi
  echo

  hdr "About to run Phase 5 — templates extraction (optional)"
  if confirm "Proceed with Phase 5?"; then
    cmd_extract_templates
  else
    log "skipping Phase 5"
  fi
  echo

  hdr "About to run Phase 6 — add READMEs"
  if confirm "Proceed with Phase 6?"; then
    cmd_add_readmes
  else
    die "aborted at Phase 6"
  fi
  echo

  cmd_validate
}

# =============================================================================
# Argument parsing
# =============================================================================

usage() {
  cat <<EOF
$SCRIPT_NAME $SCRIPT_VERSION — implements RESTRUCTURE-PROPOSAL.md

Usage: $SCRIPT_NAME [global flags] <command>

Commands (run in order, or use 'all'):
  inventory          Phase 1 — read-only repository inspection.
  shared-assets      Phase 2 — move src/common to tooling/, rehome orphan PUMLs.
  rename-outliers    Phase 3 — kebab-case the snake_case / PascalCase files.
  structural-moves   Phase 4 — VAB style-catalog renames + security path flatten.
  extract-templates  Phase 5 — split templates into templates/ subfolders.
  add-readmes        Phase 6 — write the eleven required READMEs.
  validate           Run the proposal §10 checklist (without --with-build,
                     no LaTeX is invoked).
  all                Run phases 1-6 in order, with confirmation gates,
                     then validate.

Global flags:
  --dry-run          Print actions without executing them.
  --yes              Skip confirmation prompts.
  --allow-dirty      Permit running with a dirty working tree (NOT recommended).
  --with-build       For 'validate': also run 'make build-all'.
  -h, --help         Show this help.

Examples:
  $SCRIPT_NAME inventory                       # what would I have to fix?
  $SCRIPT_NAME --dry-run shared-assets         # what would Phase 2 do?
  $SCRIPT_NAME --yes all                       # run everything end-to-end
  $SCRIPT_NAME validate --with-build           # full post-migration check

Environment overrides:
  VIEWPOINT_TEMPLATE_MOVE=1   In Phase 5, also move viewpoint-template.tex.
  NO_COLOR=1                  Disable ANSI color output.
EOF
}

parse_args() {
  while (( $# > 0 )); do
    case "$1" in
      --dry-run)      DRY_RUN=1; shift ;;
      --yes|-y)       ASSUME_YES=1; shift ;;
      --allow-dirty)  ALLOW_DIRTY=1; shift ;;
      --with-build)   WITH_BUILD=1; shift ;;
      -h|--help)      usage; exit 0 ;;
      --)             shift; break ;;
      -*)             err "unknown flag: $1"; usage >&2; exit 2 ;;
      *)
        if [[ -z "$CMD" ]]; then
          CMD=$1
        else
          err "unexpected positional argument: $1"
          usage >&2
          exit 2
        fi
        shift
        ;;
    esac
  done
  if [[ -z "$CMD" ]]; then
    usage
    exit 2
  fi
}

# =============================================================================
# Main
# =============================================================================

main() {
  parse_args "$@"
  ensure_repo_root

  case "$CMD" in
    inventory)         cmd_inventory ;;
    shared-assets)     cmd_shared_assets ;;
    rename-outliers)   cmd_rename_outliers ;;
    structural-moves)  cmd_structural_moves ;;
    extract-templates) cmd_extract_templates ;;
    add-readmes)       cmd_add_readmes ;;
    validate)          cmd_validate ;;
    all)               cmd_all ;;
    *)
      err "unknown command: $CMD"
      usage >&2
      exit 2
      ;;
  esac
}

main "$@"
