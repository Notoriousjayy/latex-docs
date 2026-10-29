#!/usr/bin/env python3
"""Migrate the 2026-10-12 repository-root document intake into src/.

The repository root accumulated 164 standalone .tex uploads and one multi-
diagram PlantUML legend. This script classifies every intake file, applies
the per-family transformations required by the repository's style contracts,
writes the results to their categorized src/ destinations, and records a
hash-based provenance manifest at
tooling/manifests/top-level-document-intake.json.

Usage:
  python3 tooling/scripts/migrate_top_level_intake.py --dry-run   # mapping + collision report
  python3 tooling/scripts/migrate_top_level_intake.py --apply     # perform migration
  python3 tooling/scripts/migrate_top_level_intake.py --cleanup   # remove verified originals

The script is idempotent: re-running --apply recomputes each transform from
the recorded original content (kept in the manifest by hash) and only writes
when the target is missing or stale. Originals are only removed by an
explicit --cleanup after every target has been written and verified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "tooling" / "manifests" / "top-level-document-intake.json"

# ---------------------------------------------------------------------------
# Mapping tables
# ---------------------------------------------------------------------------

# Byte-identical duplicates of files integrated under src/ by commit
# 499cef81 ("Integrates new documents"). Verified with cmp before recording.
DUPLICATES_OF_EXISTING = {
    "42010-ad-template-polished.tex": "src/architecture/templates/42010-ad-template-polished.tex",
    "42010-vp-template-polished.tex": "src/architecture/templates/42010-vp-template-polished.tex",
    "viewpoint-section.tex": "src/architecture/templates/viewpoint-section.tex",
    "viewpoint-template-polished.tex": "src/architecture/templates/viewpoint-template-polished.tex",
}

# Content-equivalent duplicate: template.tex differs from
# kubernetes-from-first-principles.tex only by two typographic fixes
# ($$..$$ -> $..$ inside \raisebox postbreak hooks); the named file is the
# corrected canonical copy.
CONTENT_DUPLICATES = {
    "template.tex": "kubernetes-from-first-principles.tex",
}

CCOE_PHASES = {
    "1": "initiation",
    "2": "planning",
    "3": "execution",
    "4": "monitoring-and-control",
    "5": "closure",
}

CLOUD_SUITE_DIR = "src/architecture/cloud/engineering-suite"
CLOUD_CHAPTERS_DIR = "src/architecture/cloud/concepts-technology-architecture"
CORNELL_CLOUD_DIR = "src/cornell-notes/architecture/cloud-computing"
CORNELL_CALC_DIR = "src/cornell-notes/mathematics/calculus"

# filename -> (target relpath, family, transform)
EXPLICIT_MAP: dict[str, tuple[str, str, str]] = {
    # --- enterprise open-source security platform report (flagship) --------
    "enterprise_oss_security.tex": (
        "src/security/enterprise-security/open-source-enterprise-security-platform.tex",
        "enterprise-security", "enterprise"),
    # --- CCoE master guide ---------------------------------------------------
    "CCoE_Master_Governance_Guide.tex": (
        "src/architecture/governance/ccoe/ccoe-master-governance-guide.tex",
        "ccoe-governance", "identity"),
    # --- cloud engineering deliverables (cloudsuite module) ------------------
    "01_cloud_engineering_guide.tex": (f"{CLOUD_SUITE_DIR}/01-cloud-engineering-guide.tex", "cloud-engineering", "cloudsuite"),
    "02_cloud_architecture_curriculum.tex": (f"{CLOUD_SUITE_DIR}/02-cloud-architecture-curriculum.tex", "cloud-engineering", "cloudsuite"),
    "03_cloud_mechanisms_catalog.tex": (f"{CLOUD_SUITE_DIR}/03-cloud-mechanisms-catalog.tex", "cloud-engineering", "cloudsuite"),
    "04_cloud_architecture_catalog.tex": (f"{CLOUD_SUITE_DIR}/04-cloud-architecture-catalog.tex", "cloud-engineering", "cloudsuite"),
    "05_architecture_documentation_templates.tex": (f"{CLOUD_SUITE_DIR}/05-architecture-documentation-templates.tex", "cloud-engineering", "cloudsuite"),
    "06_security_governance_templates.tex": (f"{CLOUD_SUITE_DIR}/06-security-governance-templates.tex", "cloud-engineering", "cloudsuite"),
    "07_finops_sla_templates.tex": (f"{CLOUD_SUITE_DIR}/07-finops-sla-templates.tex", "cloud-engineering", "cloudsuite"),
    # --- cloud chapter companions ch01-ch18 (cloudsuite module) --------------
    "ch01_introduction.tex": (f"{CLOUD_CHAPTERS_DIR}/ch01-introduction.tex", "cloud-chapters", "cloudsuite"),
    "ch02_case_study_background.tex": (f"{CLOUD_CHAPTERS_DIR}/ch02-case-study-background.tex", "cloud-chapters", "cloudsuite"),
    "ch03_understanding_cloud_computing.tex": (f"{CLOUD_CHAPTERS_DIR}/ch03-understanding-cloud-computing.tex", "cloud-chapters", "cloudsuite"),
    "ch04_fundamental_concepts_and_models.tex": (f"{CLOUD_CHAPTERS_DIR}/ch04-fundamental-concepts-and-models.tex", "cloud-chapters", "cloudsuite"),
    "ch05_cloud_enabling_technology.tex": (f"{CLOUD_CHAPTERS_DIR}/ch05-cloud-enabling-technology.tex", "cloud-chapters", "cloudsuite"),
    "ch06_understanding_containerization.tex": (f"{CLOUD_CHAPTERS_DIR}/ch06-understanding-containerization.tex", "cloud-chapters", "cloudsuite"),
    "ch07_understanding_cloud_security_and_cybersecurity.tex": (f"{CLOUD_CHAPTERS_DIR}/ch07-cloud-security-and-cybersecurity.tex", "cloud-chapters", "cloudsuite"),
    "ch08_cloud_infrastructure_mechanisms.tex": (f"{CLOUD_CHAPTERS_DIR}/ch08-cloud-infrastructure-mechanisms.tex", "cloud-chapters", "cloudsuite"),
    "ch09_specialized_cloud_mechanisms.tex": (f"{CLOUD_CHAPTERS_DIR}/ch09-specialized-cloud-mechanisms.tex", "cloud-chapters", "cloudsuite"),
    "ch10_cloud_security_and_cybersecurity_access_oriented_mechanisms.tex": (f"{CLOUD_CHAPTERS_DIR}/ch10-access-oriented-security-mechanisms.tex", "cloud-chapters", "cloudsuite"),
    "ch11_cloud_security_and_cybersecurity_data_oriented_mechanisms.tex": (f"{CLOUD_CHAPTERS_DIR}/ch11-data-oriented-security-mechanisms.tex", "cloud-chapters", "cloudsuite"),
    "ch12_cloud_management_mechanisms.tex": (f"{CLOUD_CHAPTERS_DIR}/ch12-cloud-management-mechanisms.tex", "cloud-chapters", "cloudsuite"),
    "ch13_fundamental_cloud_architectures.tex": (f"{CLOUD_CHAPTERS_DIR}/ch13-fundamental-cloud-architectures.tex", "cloud-chapters", "cloudsuite"),
    "ch14_advanced_cloud_architectures.tex": (f"{CLOUD_CHAPTERS_DIR}/ch14-advanced-cloud-architectures.tex", "cloud-chapters", "cloudsuite"),
    "ch15_specialized_cloud_architectures.tex": (f"{CLOUD_CHAPTERS_DIR}/ch15-specialized-cloud-architectures.tex", "cloud-chapters", "cloudsuite"),
    "ch16_cloud_delivery_model_considerations.tex": (f"{CLOUD_CHAPTERS_DIR}/ch16-cloud-delivery-model-considerations.tex", "cloud-chapters", "cloudsuite"),
    "ch17_cost_metrics_and_pricing_models.tex": (f"{CLOUD_CHAPTERS_DIR}/ch17-cost-metrics-and-pricing-models.tex", "cloud-chapters", "cloudsuite"),
    "ch18_service_quality_metrics_and_slas.tex": (f"{CLOUD_CHAPTERS_DIR}/ch18-service-quality-metrics-and-slas.tex", "cloud-chapters", "cloudsuite"),
    # --- cloud Cornell notes (cornell-notes module adapter) -------------------
    "01-introduction-cornell-notes.tex": (f"{CORNELL_CLOUD_DIR}/01-introduction-cornell-notes.tex", "cornell-cloud", "cornell_cloud"),
    "02-case-study-background-cornell-notes.tex": (f"{CORNELL_CLOUD_DIR}/02-case-study-background-cornell-notes.tex", "cornell-cloud", "cornell_cloud"),
    "03-understanding-cloud-computing-cornell-notes.tex": (f"{CORNELL_CLOUD_DIR}/03-understanding-cloud-computing-notes.tex", "cornell-cloud", "cornell_cloud"),
    "04-fundamental-concepts-and-models-cornell-notes.tex": (f"{CORNELL_CLOUD_DIR}/04-fundamental-concepts-and-models-notes.tex", "cornell-cloud", "cornell_cloud"),
    "05-cloud-enabling-technology-cornell-notes.tex": (f"{CORNELL_CLOUD_DIR}/05-cloud-enabling-technology-notes.tex", "cornell-cloud", "cornell_cloud"),
    "06-understanding-containerization-cornell-notes.tex": (f"{CORNELL_CLOUD_DIR}/06-understanding-containerization-notes.tex", "cornell-cloud", "cornell_cloud"),
    "07-understanding-cloud-security-and-cybersecurity-cornell-notes.tex": (f"{CORNELL_CLOUD_DIR}/07-cloud-security-and-cybersecurity-notes.tex", "cornell-cloud", "cornell_cloud"),
    "08-cloud-infrastructure-mechanisms-cornell-notes.tex": (f"{CORNELL_CLOUD_DIR}/08-cloud-infrastructure-mechanisms-notes.tex", "cornell-cloud", "cornell_cloud"),
    "09-specialized-cloud-mechanisms-cornell-notes.tex": (f"{CORNELL_CLOUD_DIR}/09-specialized-cloud-mechanisms-notes.tex", "cornell-cloud", "cornell_cloud"),
    "10-cloud-security-and-cybersecurity-access-oriented-mechanisms-cornell-notes.tex": (f"{CORNELL_CLOUD_DIR}/10-access-oriented-security-mechanisms-notes.tex", "cornell-cloud", "cornell_cloud"),
    "11-cloud-security-and-cybersecurity-data-oriented-mechanisms-cornell-notes.tex": (f"{CORNELL_CLOUD_DIR}/11-data-oriented-security-mechanisms-notes.tex", "cornell-cloud", "cornell_cloud"),
    "12-cloud-management-mechanisms-cornell-notes.tex": (f"{CORNELL_CLOUD_DIR}/12-cloud-management-mechanisms-notes.tex", "cornell-cloud", "cornell_cloud"),
    "13-fundamental-cloud-architectures-cornell-notes.tex": (f"{CORNELL_CLOUD_DIR}/13-fundamental-cloud-architectures-notes.tex", "cornell-cloud", "cornell_cloud"),
    "14-advanced-cloud-architectures-cornell-notes.tex": (f"{CORNELL_CLOUD_DIR}/14-advanced-cloud-architectures-notes.tex", "cornell-cloud", "cornell_cloud"),
    "15-specialized-cloud-architectures-cornell-notes.tex": (f"{CORNELL_CLOUD_DIR}/15-specialized-cloud-architectures-notes.tex", "cornell-cloud", "cornell_cloud"),
    "16-cloud-delivery-model-considerations-cornell-notes.tex": (f"{CORNELL_CLOUD_DIR}/16-cloud-delivery-model-considerations-notes.tex", "cornell-cloud", "cornell_cloud"),
    "17-cost-metrics-and-pricing-models-cornell-notes.tex": (f"{CORNELL_CLOUD_DIR}/17-cost-metrics-and-pricing-models-notes.tex", "cornell-cloud", "cornell_cloud"),
    "18-service-quality-metrics-and-slas-cornell-notes.tex": (f"{CORNELL_CLOUD_DIR}/18-service-quality-metrics-slas-notes.tex", "cornell-cloud", "cornell_cloud"),
    # --- calculus Cornell notes (cornell-notes module adapter) ----------------
    "00-preparation-for-calculus-cornell-notes.tex": (f"{CORNELL_CALC_DIR}/00-preparation-for-calculus-cornell-notes.tex", "cornell-calculus", "cornell_calc"),
    "01-limits-and-their-properties-cornell-notes.tex": (f"{CORNELL_CALC_DIR}/01-limits-and-their-properties-cornell-notes.tex", "cornell-calculus", "cornell_calc"),
    "02-differentiation-cornell-notes.tex": (f"{CORNELL_CALC_DIR}/02-differentiation-cornell-notes.tex", "cornell-calculus", "cornell_calc"),
    "03-applications-of-differentiation-cornell-notes.tex": (f"{CORNELL_CALC_DIR}/03-applications-of-differentiation-notes.tex", "cornell-calculus", "cornell_calc"),
    "04-integration-cornell-notes.tex": (f"{CORNELL_CALC_DIR}/04-integration-cornell-notes.tex", "cornell-calculus", "cornell_calc"),
    "05-logarithmic-exponential-and-transcendental-functions-cornell-notes.tex": (f"{CORNELL_CALC_DIR}/05-transcendental-functions-cornell-notes.tex", "cornell-calculus", "cornell_calc"),
    "06-differential-equations-cornell-notes.tex": (f"{CORNELL_CALC_DIR}/06-differential-equations-cornell-notes.tex", "cornell-calculus", "cornell_calc"),
    "07-applications-of-integration-cornell-notes.tex": (f"{CORNELL_CALC_DIR}/07-applications-of-integration-cornell-notes.tex", "cornell-calculus", "cornell_calc"),
    "08-integration-techniques-and-improper-integrals-cornell-notes.tex": (f"{CORNELL_CALC_DIR}/08-integration-techniques-cornell-notes.tex", "cornell-calculus", "cornell_calc"),
    "09-infinite-series-cornell-notes.tex": (f"{CORNELL_CALC_DIR}/09-infinite-series-cornell-notes.tex", "cornell-calculus", "cornell_calc"),
    "10-conics-parametric-equations-and-polar-coordinates-cornell-notes.tex": (f"{CORNELL_CALC_DIR}/10-conics-parametric-polar-cornell-notes.tex", "cornell-calculus", "cornell_calc"),
    "11-vectors-and-the-geometry-of-space-cornell-notes.tex": (f"{CORNELL_CALC_DIR}/11-vectors-geometry-of-space-cornell-notes.tex", "cornell-calculus", "cornell_calc"),
    "12-vector-valued-functions-cornell-notes.tex": (f"{CORNELL_CALC_DIR}/12-vector-valued-functions-cornell-notes.tex", "cornell-calculus", "cornell_calc"),
    "13-functions-of-several-variables-cornell-notes.tex": (f"{CORNELL_CALC_DIR}/13-functions-of-several-variables-notes.tex", "cornell-calculus", "cornell_calc"),
    "14-advanced-cloud-architectures-cornell-notes.tex": (f"{CORNELL_CLOUD_DIR}/14-advanced-cloud-architectures-notes.tex", "cornell-cloud", "cornell_cloud"),
    # --- secure coding standards ------------------------------------------------
    "secure-coding-standard-c.tex": ("src/programming/languages/c-cpp/secure-coding/secure-coding-standard-c.tex", "secure-coding", "identity"),
    "secure-coding-standard-cpp.tex": ("src/programming/languages/c-cpp/secure-coding/secure-coding-standard-cpp.tex", "secure-coding", "identity"),
    "secure-coding-standard-csharp.tex": ("src/programming/languages/csharp/secure-coding-standard-csharp.tex", "secure-coding", "identity"),
    "secure-coding-standard-go.tex": ("src/programming/languages/go/secure-coding-standard-go.tex", "secure-coding", "identity"),
    "secure-coding-standard-java.tex": ("src/programming/languages/java/secure-coding/secure-coding-standard-java.tex", "secure-coding", "identity"),
    "secure-coding-standard-javascript.tex": ("src/programming/languages/ecmascript/secure-coding-standard-javascript.tex", "secure-coding", "identity"),
    "secure-coding-standard-kotlin.tex": ("src/programming/languages/kotlin/secure-coding-standard-kotlin.tex", "secure-coding", "identity"),
    "secure-coding-standard-python.tex": ("src/programming/languages/python/secure-coding-standard-python.tex", "secure-coding", "identity"),
    "secure-coding-standard-ruby.tex": ("src/programming/languages/ruby/secure-coding-standard-ruby.tex", "secure-coding", "identity"),
    "secure-coding-standard-rust.tex": ("src/programming/languages/rust/secure-coding-standard-rust.tex", "secure-coding", "identity"),
    "secure-coding-standard-swift.tex": ("src/programming/languages/swift/secure-coding-standard-swift.tex", "secure-coding", "identity"),
    "secure-coding-standard-typescript.tex": ("src/programming/languages/typescript/secure-coding-standard-typescript.tex", "secure-coding", "identity"),
    # --- GHAS and workflow hardening ---------------------------------------------
    "ghas-codeql-secure-coding-crosswalk.tex": ("src/security/github-advanced-security/references/ghas-codeql-secure-coding-crosswalk.tex", "ghas", "identity"),
    "ghas-secure-coding-standards-handout.tex": ("src/security/github-advanced-security/references/ghas-secure-coding-standards-handout.tex", "ghas", "identity"),
    "secure-workflow-standard-github-actions.tex": ("src/security/github-advanced-security/references/secure-workflow-standard-github-actions.tex", "ghas", "identity"),
    # --- appsec tooling, auditing, catalogs ------------------------------------
    "burp-suite-appsec-engineering-guide.tex": ("src/security/application-security/dast/burp-suite/burp-suite-appsec-engineering-guide.tex", "appsec-tools", "burp"),
    "pentagi-technical-handout.tex": ("src/security/application-security/pentesting/pentagi-technical-handout.tex", "appsec-tools", "identity"),
    "code-audit-strategy-catalog.tex": ("src/security/application-security/auditing/code-audit-strategy-catalog.tex", "code-audit", "identity"),
    "code-audit-techniques-catalog.tex": ("src/security/application-security/auditing/code-audit-techniques-catalog.tex", "code-audit", "identity"),
    "catalog-textual-data-string-processing-vulnerabilities.tex": ("src/security/application-security/auditing/textual-data-string-vulnerabilities-catalog.tex", "code-audit", "identity"),
    "application-review-analysis-template.tex": ("src/security/application-security/processes/application-review-analysis-template.tex", "appsec-process", "identity"),
    # --- BABOK business analysis -------------------------------------------------
    "BABOK_v3_Technical_Guide.tex": ("src/business-analysis/babok/babok-v3-technical-guide.tex", "babok", "identity"),
    "BABOK_v3_Knowledge_Areas_and_Tasks.tex": ("src/business-analysis/babok/babok-v3-knowledge-areas-and-tasks.tex", "babok", "identity"),
    "BABOK_v3_50_Techniques_Catalog.tex": ("src/business-analysis/babok/babok-v3-50-techniques-catalog.tex", "babok", "identity"),
    "BABOK_v3_Cornell_Chapter_Notes.tex": ("src/business-analysis/babok/babok-v3-cornell-chapter-notes.tex", "babok", "identity"),
    "BABOK_v3_Requirements_Traceability_Templates.tex": ("src/business-analysis/babok/babok-v3-requirements-traceability-templates.tex", "babok", "identity"),
    "BABOK_v3_Engineering_AppSec_Agile_UML_BPMN_EA_Crosswalk.tex": ("src/business-analysis/babok/babok-v3-appsec-agile-uml-bpmn-ea-crosswalk.tex", "babok", "identity"),
    # --- intelligent investor suite -----------------------------------------------
    "01_intelligent_investor_technical_guide.tex": ("src/personal/finance/intelligent-investor/01-intelligent-investor-technical-guide.tex", "intelligent-investor", "identity"),
    "02_cornell_chapter_notes.tex": ("src/personal/finance/intelligent-investor/02-cornell-chapter-notes.tex", "intelligent-investor", "identity"),
    "03_framework_and_formulas.tex": ("src/personal/finance/intelligent-investor/03-framework-and-formulas.tex", "intelligent-investor", "identity"),
    "04_defensive_enterprising_playbooks.tex": ("src/personal/finance/intelligent-investor/04-defensive-enterprising-playbooks.tex", "intelligent-investor", "identity"),
    "05_valuation_and_margin_of_safety_worksheets.tex": ("src/personal/finance/intelligent-investor/05-valuation-margin-of-safety-worksheets.tex", "intelligent-investor", "identity"),
    "06_modern_brokerage_portfolio_framework.tex": ("src/personal/finance/intelligent-investor/06-modern-brokerage-portfolio-framework.tex", "intelligent-investor", "identity"),
    # --- cleaning-services operations ----------------------------------------------
    "Residential_Cleaning_Operations_Guide.tex": ("src/startups/cleaning-services/residential-cleaning-operations-guide.tex", "cleaning-operations", "engine_lualatex"),
    "Residential_Cleaning_Training_Curriculum.tex": ("src/startups/cleaning-services/residential-cleaning-training-curriculum.tex", "cleaning-operations", "engine_lualatex"),
    "Budget_Cleaning_Supply_Catalog.tex": ("src/startups/cleaning-services/budget-cleaning-supply-catalog.tex", "cleaning-operations", "engine_lualatex"),
    "JAN_PRO_Atlanta_Pre_Purchase_Roadmap.tex": ("src/startups/cleaning-services/jan-pro-atlanta-pre-purchase-roadmap.tex", "cleaning-operations", "identity"),
    # --- mathematics -----------------------------------------------------------------
    "mathematical-techniques-proofs-complete.tex": ("src/mathematics/proofs/mathematical-techniques-proofs-complete.tex", "mathematics", "identity"),
    "mathematical-techniques-proofs-modular.tex": ("src/mathematics/proofs/mathematical-techniques-proofs-modular.tex", "mathematics", "identity"),
    "calculus-applications-companion-workbook.tex": ("src/mathematics/calculus/calculus-applications-companion-workbook.tex", "mathematics", "identity"),
    "calculus-applications-companion-workbook-solutions.tex": ("src/mathematics/calculus/calculus-applications-workbook-solutions.tex", "mathematics", "identity"),
    # --- programming / algorithms / game dev ------------------------------------------
    "desk-check-algorithm-workbook.tex": ("src/programming/algorithms/desk-check-algorithm-workbook.tex", "programming", "identity"),
    "synchronization-object-scoreboard.tex": ("src/programming/concurrency/synchronization-object-scoreboard.tex", "programming", "identity"),
    "game-programming-pattern-catalog.tex": ("src/game-development/patterns/game-programming-pattern-catalog.tex", "game-development", "identity"),
    # --- platform / web / electronics ---------------------------------------------------
    "kubernetes-from-first-principles.tex": ("src/devops/platform/kubernetes/kubernetes-from-first-principles.tex", "kubernetes", "identity"),
    "kubernetes-cloud-architecture-technical-guide.tex": ("src/devops/platform/kubernetes/kubernetes-cloud-architecture-technical-guide.tex", "kubernetes", "identity"),
    "http_headers_reference.tex": ("src/programming/web/http-headers-reference.tex", "web", "engine_lualatex"),
    "http_request_metadata_technical_guide.tex": ("src/programming/web/http-request-metadata-technical-guide.tex", "web", "identity"),
    "Gamified_DevOps_Security_Learning_Guide.tex": ("src/devops/foundations/gamified-devops-security-learning-guide.tex", "devops-learning", "engine_lualatex"),
    "Orange_Pi_Zero_Engineering_Guide.tex": ("src/electronics/orange-pi-zero-engineering-guide.tex", "electronics", "identity"),
    # --- PlantUML legend ------------------------------------------------------------------
    "uml-2.5.1-legend.puml": ("src/architecture/uml/uml-2-5-1-legend", "uml-notation", "puml_legend"),
}

PUML_BLOCK_STYLES = [
    "structural/class-diagram-style.iuml",
    "structural/package-diagram-style.iuml",
    "structural/composite-structure-diagram-style.iuml",
    "structural/deployment-diagram-style.iuml",
    "behavioral/usecase-diagram-style.iuml",
    "behavioral/activity-diagram-style.iuml",
    "behavioral/statemachine-diagram-style.iuml",
    "interaction/sequence-diagram-style.iuml",
    "interaction/communication-diagram-style.iuml",
    "interaction/timing-diagram-style.iuml",
    "interaction/interaction-overview-diagram-style.iuml",
    "structural/class-diagram-style.iuml",
]


def ccoe_entry(name: str) -> tuple[str, str, str] | None:
    match = re.match(r"^([1-5])\.(\d{1,2}) (.+)\.tex$", name)
    if not match:
        return None
    major, minor, title = match.groups()
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    target = f"src/architecture/governance/ccoe/{CCOE_PHASES[major]}/{major}-{minor}-{slug}.tex"
    return (target, "ccoe-governance", "identity")


def lookup(name: str) -> tuple[str, str, str] | None:
    if name in EXPLICIT_MAP:
        return EXPLICIT_MAP[name]
    return ccoe_entry(name)


# ---------------------------------------------------------------------------
# Transforms
# ---------------------------------------------------------------------------

def t_identity(text: str) -> str:
    return text


def t_cloudsuite(text: str) -> str:
    return text.replace("\\usepackage{styles/cloudsuite}", "\\usepackage{cloudsuite}")


CORNELL_DROP_PACKAGES = (
    r"\usepackage[T1]{fontenc}",
    r"\usepackage[utf8]{inputenc}",
    r"\usepackage{lmodern}",
    r"\usepackage{microtype}",
    r"\usepackage[letterpaper,margin=0.72in,headheight=15pt]{geometry}",
    r"\usepackage{amsmath,amssymb,mathtools}",
    r"\usepackage{booktabs,longtable,tabularx,array}",
    r"\usepackage{array,booktabs,longtable,tabularx}",
    r"\usepackage{adjustbox}",
    r"\usepackage[table]{xcolor}",
    r"\usepackage[most]{tcolorbox}",
    r"\usepackage{enumitem}",
    r"\usepackage{fancyhdr}",
    r"\usepackage{titlesec}",
    r"\usepackage{needspace}",
    r"\usepackage{tikz}",
    r"\usetikzlibrary{arrows.meta,positioning}",
    r"\usepackage{hyperref}",
    r"\usepackage{bookmark}",
    r"\usepackage{lastpage}",
    r"\usepackage{ragged2e}",
)


def _rename_env(text: str, old: str, new: str) -> str:
    text = text.replace(f"\\newtcolorbox{{{old}}}", f"\\newtcolorbox{{{new}}}")
    text = text.replace(f"\\begin{{{old}}}", f"\\begin{{{new}}}")
    text = text.replace(f"\\end{{{old}}}", f"\\end{{{new}}}")
    return text


def _cornell_adapter(text: str, collection: str, extra_lines: list[str]) -> str:
    # Derive unit metadata for the module's cover renderer from the document's
    # own title ("Chapter N: Title" across both collections; "Preparation" is
    # chapter P in the calculus source's numbering).
    meta_lines: list[str] = []
    title_match = re.search(r"\\title\{(?:\\textcolor\{Navy\}\{)?([^\\}]+?)(?:\})?\\\\", text)
    if title_match:
        title_value = title_match.group(1).strip()
        chapter = re.match(r"Chapter (\d+): (.+)$", title_value)
        if chapter:
            meta_lines = [
                "\\setCornellUnitType{Chapter}",
                f"\\setCornellUnitNumber{{{chapter.group(1)}}}",
                f"\\setCornellUnitTitle{{{chapter.group(2)}}}",
            ]
        elif title_value.startswith("Preparation: "):
            meta_lines = [
                "\\setCornellUnitType{Chapter}",
                "\\setCornellUnitNumber{P}",
                f"\\setCornellUnitTitle{{{title_value.split(': ', 1)[1]}}}",
            ]
    lines = text.splitlines()
    out: list[str] = []
    inserted = False
    for line in lines:
        stripped = line.strip()
        if stripped in CORNELL_DROP_PACKAGES:
            continue
        # Module supplies the C and N Cornell column types.
        if re.match(r"\\newcolumntype\{[CN]\}", stripped):
            continue
        out.append(line)
        if not inserted and stripped.startswith("\\documentclass"):
            adapter = [
                "\\usepackage{cornell-notes}",
                "\\usepackage{mathtools}",
                "\\usepackage{needspace}",
                "\\usepackage{ragged2e}",
                *extra_lines,
                "\\tcbuselibrary{most}",
                "\\geometry{letterpaper,margin=0.72in,headheight=15pt}",
                f"\\setCornellCollection{{{collection}}}",
                *meta_lines,
            ]
            out.extend(adapter)
            inserted = True
    return "\n".join(out) + "\n"


def t_cornell_calc(text: str) -> str:
    # cornell-notes.sty ships legacy `summarybox`, `\cornellhead` and
    # `\cornellrow` compatibility definitions, so the collection's own
    # versions need non-colliding names.
    text = _rename_env(text, "summarybox", "sectionsummarybox")
    text = text.replace("\\cornellhead", "\\cornellcuehead")
    text = text.replace("\\cornellrow", "\\cornellcuerow")
    return _cornell_adapter(
        text,
        "Calculus Cornell Notes",
        ["\\usepackage{adjustbox}", "\\usepackage{tikz}", "\\usetikzlibrary{arrows.meta,positioning}"],
    )


def t_cornell_cloud(text: str) -> str:
    # `notebox` collides with the house callout; `summarybox` collides with the
    # cornell-notes legacy compatibility environment.
    text = _rename_env(text, "notebox", "scopenotebox")
    text = _rename_env(text, "summarybox", "sectionsummarybox")
    # The module renders the title itself; the nested \textcolor wrapper breaks
    # the repository validator's brace-free \title{...} contract.
    text = re.sub(r"\\title\{\\textcolor\{Navy\}\{([^{}]*)\}", r"\\title{\1", text)
    return _cornell_adapter(text, "Cloud Architecture Cornell Notes", [])


def t_engine_lualatex(text: str) -> str:
    # fontspec documents: declare a reproducible Unicode engine for the build
    # system's magic-comment detection (fonts verified via luaotfload).
    if not text.startswith("% !TeX program"):
        text = "% !TeX program = lualatex\n" + text
    return text


def t_burp(text: str) -> str:
    # Latent source bug: `diamond/.style={diamond,...}` self-references the
    # TikZ key and loops until TeX's input stack overflows. Rename the local
    # style; the diamond *shape* semantics are unchanged.
    text = text.replace(
        "diamond/.style={diamond, draw=accent, fill=accentlight, aspect=2, align=center}",
        "decisionnode/.style={diamond, draw=accent, fill=accentlight, aspect=2, align=center}",
    )
    text = text.replace("\\node[diamond,", "\\node[decisionnode,")
    return text


ENTERPRISE_LISTING_LANGS = ["json", "yaml", "json", "bash"]


def t_enterprise(text: str) -> str:
    # 1. Reproducible engine declaration: the source requires fontspec with
    #    Linux Libertine O / Lato / DejaVu Sans Mono.
    if not text.startswith("% !TeX program"):
        text = "% !TeX program = lualatex\n" + text
    # 2. minted migration (repository code-rendering contract).
    text = text.replace(
        "\\usepackage{listings}",
        "\\usepackage[cache=false]{minted}\n"
        "\\setminted{fontsize=\\footnotesize,breaklines=true,breakanywhere=true,"
        "frame=single,framesep=5pt,rulecolor=\\color{linegray}}",
    )
    text = re.sub(r"\\lstdefinestyle\{tech\}\{[^\n]*\}\n", "", text)
    text = text.replace("\\lstset{style=tech}\n", "")
    langs = iter(ENTERPRISE_LISTING_LANGS)

    def _begin(match: re.Match[str]) -> str:
        return f"\\begin{{minted}}{{{next(langs)}}}"

    text = re.sub(r"\\begin\{lstlisting\}(\[[^\]]*\])?", _begin, text)
    text = text.replace("\\end{lstlisting}", "\\end{minted}")
    return text


PUML_BLOCK_FILES = [
    "01-core-structure.puml",
    "02-instances-packages-profiles.puml",
    "03-components-composite-structure.puml",
    "04-deployment.puml",
    "05-use-cases.puml",
    "06-activities.puml",
    "07-state-machines.puml",
    "08-interactions-sequence.puml",
    "09-communication-approximation.puml",
    "10-timing.puml",
    "11-interaction-overview-approximation.puml",
    "12-compatibility-notes.puml",
]

# skinparams owned by the shared style modules (plantuml_lint HOUSE_OWNED).
HOUSE_OWNED_SKINPARAM = re.compile(
    r"^\s*skinparam\s+[A-Za-z]*(Color|FontSize|FontStyle|FontName|BackgroundColor|BorderColor|RoundCorner|Shadowing)\b",
    re.I,
)


def t_puml_legend(text: str) -> dict[str, str]:
    """Split the 12-block legend into per-diagram files.

    The repository's PlantUML lint contract requires exactly one leaf style
    include per .puml file and forbids locally restating colour/typography
    skinparams, so the multi-type legend cannot stay a single file. Blocks
    keep their original order, traceability comments, layout skinparams and
    the deliberate monochrome/strictuml notation settings.
    """
    # Pinned PlantUML 1.2026.7 syntax compatibility (see t_puml notes).
    text = text.replace('namespace "com.example.billing" {', "namespace com.example.billing {")
    text = re.sub(r'^(\s*)(package "[^"]+" as \w+)(\s*)$', r"\1\2 {\n\1}", text, flags=re.M)
    text = re.sub(r"^(\s*):([^;\n]+);\n\s*<<(\w+)>>[ \t]*$", r"\1:\2\n«\3»;", text, flags=re.M)

    blocks = re.findall(r"(@startuml[^\n]*\n.*?@enduml)", text, re.S)
    if len(blocks) != len(PUML_BLOCK_FILES):
        raise SystemExit(f"legend split expected {len(PUML_BLOCK_FILES)} blocks, found {len(blocks)}")
    outputs: dict[str, str] = {}
    for block, filename, style in zip(blocks, PUML_BLOCK_FILES, PUML_BLOCK_STYLES):
        lines = block.splitlines()
        out: list[str] = []
        for index, line in enumerate(lines):
            if index == 0:
                name = line.removeprefix("@startuml").strip()
                # Bare @startuml so the rendered output takes the kebab-case
                # file stem; keep the original block name for traceability.
                out.append("@startuml")
                out.append(f"' Source block: {name} (uml-2.5.1-legend.puml intake)")
                out.append(f"!include ../../../../tooling/styles/plantuml/{style}")
                continue
            if HOUSE_OWNED_SKINPARAM.match(line):
                continue
            if line.startswith("!include ../../../tooling/styles/plantuml/"):
                continue
            out.append(line)
        outputs[filename] = "\n".join(out) + "\n"
    return outputs


TRANSFORMS = {
    "identity": t_identity,
    "cloudsuite": t_cloudsuite,
    "cornell_calc": t_cornell_calc,
    "cornell_cloud": t_cornell_cloud,
    "enterprise": t_enterprise,
    "engine_lualatex": t_engine_lualatex,
    "burp": t_burp,
    "puml_legend": t_puml_legend,
}


# ---------------------------------------------------------------------------
# Inventory helpers
# ---------------------------------------------------------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_title(text: str) -> str:
    for pattern in (r"\\title\{(.{1,120}?)\}", r"pdftitle=\{([^}]{1,120})\}", r"\\coverpage\{([^}]{1,120})\}"):
        match = re.search(pattern, text)
        if match:
            raw = re.sub(r"\\[a-zA-Z]+", " ", match.group(1))
            raw = raw.replace("{", " ").replace("}", " ")
            return re.sub(r"\s+", " ", raw).strip()
    return ""


def detect_engine(text: str) -> str:
    if re.search(r"^\s*%\s*!TeX\s+program\s*=\s*lualatex", text, re.M):
        return "lualatex"
    if re.search(r"^\s*%\s*!TeX\s+program\s*=\s*xelatex", text, re.M):
        return "xelatex"
    return "pdflatex"


def detect_class(text: str) -> str:
    match = re.search(r"\\documentclass(?:\[[^\]]*\])?\{([^}]+)\}", text)
    return match.group(1) if match else ""


def semantic_module(text: str, name: str) -> str:
    match = re.search(
        r"\\usepackage(?:\[[^\]]*\])?\{(cloudsuite|cornell-notes|technical[a-z-]*|business-admin|financial|hr|legal|personal-official)\}",
        text,
    )
    if match:
        return match.group(1)
    return "self-contained" if name.endswith(".tex") else "plantuml"


def intake_files() -> list[Path]:
    files = sorted(ROOT.glob("*.tex")) + sorted(ROOT.glob("*.puml"))
    return [path for path in files if path.is_file()]


# ---------------------------------------------------------------------------
# Main flows
# ---------------------------------------------------------------------------

def build_records(apply: bool) -> tuple[list[dict], list[str]]:
    errors: list[str] = []
    records: list[dict] = []
    seen_targets: dict[str, str] = {}

    for path in intake_files():
        name = path.name
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        record: dict = {
            "original_path": name,
            "original_sha256": sha256_bytes(raw),
            "source_type": "plantuml" if name.endswith(".puml") else "standalone-latex",
            "document_title": extract_title(text) if name.endswith(".tex") else "UML 2.5.1 PlantUML Legend and Notation Reference",
            "latex_class": detect_class(text) if name.endswith(".tex") else "",
        }

        if name in DUPLICATES_OF_EXISTING:
            canonical = DUPLICATES_OF_EXISTING[name]
            canonical_raw = (ROOT / canonical).read_bytes()
            if canonical_raw != raw:
                errors.append(f"expected byte-identical duplicate differs: {name} vs {canonical}")
                continue
            record.update({
                "duplicate_status": "byte-identical-duplicate-of-existing",
                "canonical_path": canonical,
                "migration_status": "duplicate-dropped",
                "family": "already-integrated",
            })
            records.append(record)
            continue

        if name in CONTENT_DUPLICATES:
            record.update({
                "duplicate_status": "content-equivalent-duplicate",
                "canonical_path": CONTENT_DUPLICATES[name],
                "migration_status": "duplicate-dropped",
                "family": "kubernetes",
                "notes": "Identical content to kubernetes-from-first-principles.tex except two "
                         "$$..$$ -> $..$ typographic corrections present in the canonical copy.",
            })
            records.append(record)
            continue

        mapped = lookup(name)
        if mapped is None:
            errors.append(f"unmapped intake file: {name}")
            continue
        target_rel, family, transform_name = mapped
        target = ROOT / target_rel
        target_name = target.name
        if len(target_name) > 50:
            errors.append(f"target filename too long ({len(target_name)}): {target_rel}")
        if target_rel in seen_targets:
            errors.append(f"target collision: {target_rel} <- {name} and {seen_targets[target_rel]}")
        seen_targets[target_rel] = name
        if target.exists() and target.is_file():
            existing = target.read_bytes()
            transformed_preview = TRANSFORMS[transform_name](text)
            if isinstance(transformed_preview, str) and existing != transformed_preview.encode("utf-8"):
                # A stale or conflicting file already sits at the target.
                if not apply:
                    errors.append(f"target exists with different content: {target_rel}")

        transformed = TRANSFORMS[transform_name](text)
        if isinstance(transformed, dict):
            record.update({
                "duplicate_status": "unique",
                "family": family,
                "transform": transform_name,
                "target_path": target_rel,
                "target_files": {
                    child: sha256_bytes(content.encode("utf-8"))
                    for child, content in transformed.items()
                },
                "pdf_path": "",
                "engine": "",
                "style_module": "plantuml-leaf-styles",
                "migration_status": "planned",
            })
            if apply:
                target.mkdir(parents=True, exist_ok=True)
                for child, content in transformed.items():
                    child_path = target / child
                    payload = content.encode("utf-8")
                    if not child_path.exists() or child_path.read_bytes() != payload:
                        child_path.write_bytes(payload)
                record["migration_status"] = "migrated"
            records.append(record)
            continue
        record.update({
            "duplicate_status": "unique",
            "family": family,
            "transform": transform_name,
            "target_path": target_rel,
            "pdf_path": ("public/pdfs/" + str(Path(target_rel).relative_to("src").with_suffix(".pdf")))
                        if name.endswith(".tex") else "",
            "engine": detect_engine(transformed) if name.endswith(".tex") else "",
            "style_module": semantic_module(transformed, name),
            "target_sha256": sha256_bytes(transformed.encode("utf-8")),
            "migration_status": "planned",
        })

        if apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            payload = transformed.encode("utf-8")
            if not target.exists() or target.read_bytes() != payload:
                target.write_bytes(payload)
            record["migration_status"] = "migrated"
        records.append(record)

    return records, errors


def write_manifest(records: list[dict]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "intake": "repository-root top-level documents, recorded 2026-10-12",
        "note": (
            "Counts reflect the files actually present in the live checkout: 164 .tex "
            "sources and 1 .puml source (165 intake files). The externally described "
            "inventory of 176 uploads (including (2)-(4) duplicate suffixes, a .log "
            "diagnostic, and a repository snapshot export) does not match this checkout; "
            "those extra files were never present here and are recorded as absent."
        ),
        "files": records,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def cleanup(records: list[dict]) -> int:
    failures = 0
    for record in records:
        source = ROOT / record["original_path"]
        if not source.exists():
            continue
        status = record.get("migration_status")
        if status == "duplicate-dropped":
            source.unlink()
            continue
        target = ROOT / record.get("target_path", "")
        if "target_files" in record:
            ok = True
            for child, expected in record["target_files"].items():
                child_path = target / child
                if not child_path.exists() or sha256_bytes(child_path.read_bytes()) != expected:
                    print(f"cleanup blocked, split target mismatch: {record['original_path']} -> {child}")
                    ok = False
            if ok:
                source.unlink()
            else:
                failures += 1
            continue
        if not target.exists():
            print(f"cleanup blocked, target missing: {record['original_path']}")
            failures += 1
            continue
        expected = record.get("target_sha256")
        actual = sha256_bytes(target.read_bytes())
        if expected != actual:
            print(f"cleanup blocked, target hash mismatch: {record['original_path']}")
            failures += 1
            continue
        source.unlink()
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--apply", action="store_true")
    group.add_argument("--cleanup", action="store_true")
    args = parser.parse_args()

    if args.cleanup:
        if not MANIFEST_PATH.exists():
            print("manifest missing; run --apply first", file=sys.stderr)
            return 1
        records = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["files"]
        return 1 if cleanup(records) else 0

    records, errors = build_records(apply=args.apply)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    families: dict[str, int] = {}
    for record in records:
        families[record["family"]] = families.get(record["family"], 0) + 1
    print(f"intake files: {len(records)}")
    for family in sorted(families):
        print(f"  {family}: {families[family]}")

    if args.dry_run:
        for record in records:
            target = record.get("target_path") or f"(duplicate of {record.get('canonical_path')})"
            print(f"{record['original_path']} -> {target} [{record.get('transform', 'drop')}]")
    if errors:
        return 1
    if args.apply:
        write_manifest(records)
        print(f"manifest written: {MANIFEST_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
