#!/usr/bin/env python3
"""Migrate the 2026-10-18 repository-root documentation-suite intake into src/.

The repository root accumulated 171 untracked upload files representing the
ten-batch "latex-root-integration-intake-final" manifest: 168 manifest
artifacts (164 standalone documents, one .sty style package and three shared
.tex preambles across 22 documentation families), plus two ECMAScript 2025
suite documents (volumes 06 and 07) that the external manifest missed, plus
one byte-identical duplicate upload copy.

This script classifies every intake file by SHA-256 (upload filenames are not
authoritative), applies the per-suite transformations required by the
repository's style and naming contracts, writes the results to their
categorized src/ destinations, and records a hash-based provenance manifest at
tooling/manifests/suite-intake-2026-10-18.json.

Usage:
  python3 tooling/scripts/migrate_suite_intake.py --dry-run   # mapping + collision report
  python3 tooling/scripts/migrate_suite_intake.py --apply     # perform migration
  python3 tooling/scripts/migrate_suite_intake.py --cleanup   # remove verified originals

The script is idempotent: re-running --apply recomputes each transform from
the root source (while it exists) and only rewrites a target when it is
missing or stale. Originals are only removed by an explicit --cleanup after
every target has been written and verified.

Style decisions implemented here (see the intake manifest for the registry):
  * suite-style.sty (ISO/IEC/IEEE 42010 suite) is namespaced to
    tooling/styles/latex/ad42010-suite.sty; suite documents import
    ad42010-suite. The generic package name "suite-style" never enters a
    TEXINPUTS tree.
  * The C++23 suite's common-preamble.tex collides by name with the
    build-injected tooling/latex/common-preamble.tex helper. It is renamed to
    cpp23-common-preamble.tex and co-located with the suite; the helper is
    untouched.
  * The CMake/WebAssembly suite's preamble.tex (referenced as
    ../latex/preamble.tex) is renamed to cmake-wasm-preamble.tex and
    co-located with the suite.
  * The MISRA C suite's misra_style.tex stays an \\input preamble (it is not
    a package: no \\ProvidesPackage, loaded mid-preamble) and is renamed to
    the kebab-case, suite-scoped misra-c-style.tex. MISRA C and MISRA C++
    keep separate style identities.
  * The ISO 27000 and Design-of-Sites suites referenced style.tex (and
    references.tex) files that were never uploaded and do not exist anywhere
    in repository history. Documented reconstructions live at
    src/security/standards/iso-27000/isms-27000-style.tex and
    src/programming/web/design-of-sites/design-of-sites-{style,references}.tex.
  * The SOC 2 suite referenced soc2style.sty, also never uploaded; a
    documented reconstruction lives at tooling/styles/latex/soc2style.sty.
  * The seven security-assessment curricula carried byte-identical inline
    preambles except for \\hypersetup{pdftitle} and \\title; the common lines
    are extracted verbatim into assessment-curricula-common.tex.
  * The cpython suite's Pandoc-style \\ifPDFTeX conditionals carried a
    unicode-math/fontspec else-branch; the else branch becomes a
    \\PackageError guard (same approach the uploaded appsec-assessment suite
    already uses), which keeps pdfLaTeX behaviour byte-identical.
  * enterprise_oss_security(2).tex is the pre-remediation source of the
    already-integrated
    src/security/enterprise-security/open-source-enterprise-security-platform.tex
    (differences: fontspec->libertine/lato/DejaVuSansMono, listings->minted,
    xelatex->pdf in a verbatim build note). Recorded as a content duplicate;
    nothing is overwritten.
  * 05_cornell_study_notes.tex (Design of Sites) is a genuine Cornell Notes
    study document; it publishes under src/cornell-notes/ using the
    cornell-notes module title contract while keeping its suite-local
    callouts and the shared suite references file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "tooling" / "manifests" / "suite-intake-2026-10-18.json"

# ---------------------------------------------------------------------------
# Mapping tables (keyed by source SHA-256; upload filenames are evidence only)
# ---------------------------------------------------------------------------

# sha256 -> (target repo-relative path, suite id, transform name)
DOCUMENTS: dict[str, tuple[str, str, str]] = {}

# Loaded from the adjacent data file to keep this module reviewable; the data
# file is generated from the final intake manifest plus the two unmanifested
# ECMAScript volumes and is part of the audit trail.
_DATA_PATH = Path(__file__).with_name("suite_intake_2026_10_18_map.json")


def _load_documents() -> None:
    data = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    for sha, target, suite, transform in data["documents"]:
        DOCUMENTS[sha] = (target, suite, transform)


# Support files, keyed by sha: (target path, suite, transform)
SUPPORT_FILES: dict[str, tuple[str, str, str]] = {}

# Special dispositions keyed by sha.
SPECIAL: dict[str, dict] = {}

TRANSFORM_NOTES = {
    "t_identity": "content unchanged; canonical rename only",
    "t_ad42010": "\\usepackage{suite-style} -> \\usepackage{ad42010-suite}",
    "t_cmake_wasm": "\\input{../latex/preamble.tex} -> \\input{cmake-wasm-preamble.tex}",
    "t_cpp23": "\\input{common-preamble.tex} -> \\input{cpp23-common-preamble.tex}",
    "t_cpython": "unicode-math/fontspec else-branch replaced with a pdfLaTeX-only \\PackageError guard; xcolor [table] option clash fixed",
    "t_pandoc_xcolor": "latent xcolor [table] option clash fixed via top-of-file \\PassOptionsToPackage",
    "t_support_cmake_preamble": "suite rename plus guarded \\lstinputlisting fallback for the missing ../reference/ asset tree",
    "t_isms": "\\input{style.tex} -> \\input{isms-27000-style.tex} (reconstructed dependency)",
    "t_misra_c": "\\input{misra_style.tex} -> \\input{misra-c-style.tex}",
    "t_curricula": "byte-identical shared preamble lines replaced with \\input{assessment-curricula-common.tex}",
    "t_dos": "\\input{style.tex}/\\input{references.tex} -> suite-named reconstructed dependencies",
    "t_dos_cornell": "adapted to the cornell-notes module title contract; suite callouts kept document-local",
    "t_support_ad42010": "package renamed suite-style -> ad42010-suite (\\ProvidesPackage updated)",
    "t_support_verbatim": "content unchanged; suite-scoped rename only",
}


# ---------------------------------------------------------------------------
# Transforms
# ---------------------------------------------------------------------------

def t_identity(text: str) -> str:
    return text


def t_ad42010(text: str) -> str:
    return text.replace("\\usepackage{suite-style}", "\\usepackage{ad42010-suite}")


def t_cmake_wasm(text: str) -> str:
    return text.replace("\\input{../latex/preamble.tex}", "\\input{cmake-wasm-preamble.tex}")


def t_cpp23(text: str) -> str:
    return text.replace("\\input{common-preamble.tex}", "\\input{cpp23-common-preamble.tex}")


_CPYTHON_ELSE_BLOCK = (
    "\\else % if luatex or xetex\n"
    "  \\usepackage{unicode-math} % this also loads fontspec\n"
    "  \\defaultfontfeatures{Scale=MatchLowercase}\n"
    "  \\defaultfontfeatures[\\rmfamily]{Ligatures=TeX,Scale=1}\n"
    "\\fi"
)
_CPYTHON_GUARD_BLOCK = (
    "\\else % if luatex or xetex\n"
    "  % pdfLaTeX-only repository policy: the original unicode-math/fontspec\n"
    "  % branch is unreachable under pdfLaTeX and is replaced with a guard.\n"
    "  \\PackageError{cpython-suite}{Compile with pdfLaTeX only}{}\n"
    "\\fi"
)


def t_pandoc_xcolor(text: str) -> str:
    """Fix the latent xcolor option clash in the Pandoc-derived preambles.

    The sources load ``\\usepackage{xcolor}`` (Pandoc) and later
    ``\\usepackage[table]{xcolor}`` (document theme), which is a fatal option
    clash on every LaTeX engine; the intake manifest records these documents
    as never compiled. The ``table`` option moves to a top-of-file
    \\PassOptionsToPackage so both loads succeed with identical semantics.
    """
    marker = "\\PassOptionsToPackage{hyphens}{url}"
    clash = "\\usepackage[table]{xcolor}"
    if marker not in text or clash not in text:
        raise RuntimeError("expected Pandoc xcolor pattern not found; refusing to guess")
    text = text.replace(marker, marker + "\n\\PassOptionsToPackage{table}{xcolor}", 1)
    return text.replace(clash, "\\usepackage{xcolor} % [table] passed at top of file (option-clash fix)", 1)


def t_cpython(text: str) -> str:
    if _CPYTHON_ELSE_BLOCK not in text:
        raise RuntimeError("cpython engine conditional not found; refusing to guess")
    text = text.replace(_CPYTHON_ELSE_BLOCK, _CPYTHON_GUARD_BLOCK, 1)
    return t_pandoc_xcolor(text)


def t_isms(text: str) -> str:
    return text.replace("\\input{style.tex}", "\\input{isms-27000-style.tex}")


def t_misra_c(text: str) -> str:
    return text.replace("\\input{misra_style.tex}", "\\input{misra-c-style.tex}")


def t_dos(text: str) -> str:
    text = text.replace("\\input{style.tex}", "\\input{design-of-sites-style.tex}")
    return text.replace("\\input{references.tex}", "\\input{design-of-sites-references.tex}")


# The curricula docs share preamble lines 2-10 and 12-27 byte-for-byte; the
# hypersetup (line 11) and title/author/date (lines 28-30) are doc-specific.
_CURRICULA_COMMON_INPUT = "\\input{assessment-curricula-common.tex}"


def t_curricula(text: str) -> str:
    lines = text.splitlines()
    common_file = ROOT / "src/security/application-security/learning/assessment-curricula/assessment-curricula-common.tex"
    common_lines = [
        line for line in common_file.read_text(encoding="utf-8").splitlines()
        if not line.startswith("%")
    ]
    head = lines[:31]
    expected_common = head[1:10] + head[11:27]
    if expected_common != common_lines:
        raise RuntimeError("curricula preamble does not match the extracted common file; refusing to transform")
    out = [
        head[0],
        _CURRICULA_COMMON_INPUT,
        head[10],   # \hypersetup (doc-specific pdftitle)
        *head[27:31],  # \title, \author, \date, \begin{document}
        *lines[31:],
    ]
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


_DOS_CORNELL_PREAMBLE = r"""\usepackage{cornell-notes}
% Suite identity: Web Design Patterns / Design of Sites (document DOS-05).
% This study document publishes under the Cornell Notes tree; the callout
% environments and provenance marker below are document-local mirrors of the
% suite's reconstructed style (see
% src/programming/web/design-of-sites/design-of-sites-style.tex).
\usepackage{booktabs}
\usepackage{enumitem}
\definecolor{Ink}{HTML}{1E2A36}
\definecolor{Ocean}{HTML}{0F4C72}
\definecolor{Mint}{HTML}{0E7E6B}
\definecolor{Amber}{HTML}{B07A1E}
\definecolor{Faint}{HTML}{F2F7F9}
\newtcolorbox{groundedbox}[1][]{enhanced,breakable,colback=Faint,colframe=Mint,boxrule=0.5pt,arc=1.5mm,title={Grounded in the public record},fonttitle=\bfseries\small,#1}
\newtcolorbox{dosnotebox}[1][]{enhanced,breakable,colback=Faint,colframe=Amber,boxrule=0.5pt,arc=1.5mm,#1}
\newcommand{\Provenance}{\par\noindent{\footnotesize\sffamily\color{Amber}\bfseries Provenance:}~{\footnotesize\color{Ink}\itshape claims grounded in the public bibliographic record are boxed and cited; everything else is newly authored interpretation.}\par\smallskip}
\setCornellCollection{Web Design Patterns Cornell Notes}
\setCornellSourceTitle{The Design of Sites}
\setCornellSourceEdition{2nd edition}
\setCornellSourceAuthor{van Duyne, Landay and Hong}
\title{The Design of Sites: Cornell Study Notes}
\author{Web Design Patterns Engineering Suite (DOS-05)}
\date{}"""


def t_dos_cornell(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("\\newcommand{\\DocTitle}") or stripped.startswith("\\newcommand{\\DocSubtitle}") or stripped.startswith("\\newcommand{\\DocID}"):
            continue
        if stripped == "\\input{style.tex}":
            out.append(_DOS_CORNELL_PREAMBLE)
            continue
        if stripped == "\\MakeFront":
            out.append("\\maketitle")
            continue
        if stripped == "\\input{references.tex}":
            out.append("\\input{../../../programming/web/design-of-sites/design-of-sites-references.tex}")
            continue
        # The module ships no plain `notebox`; keep the suite callout under a
        # non-colliding, document-local name.
        line = line.replace("\\begin{notebox}", "\\begin{dosnotebox}").replace("\\end{notebox}", "\\end{dosnotebox}")
        out.append(line)
    return "\n".join(out) + "\n"


def t_support_ad42010(text: str) -> str:
    return text.replace(
        "\\ProvidesPackage{suite-style}",
        "\\ProvidesPackage{ad42010-suite}",
    )


_CMAKE_WASM_FALLBACK = r"""
% Integration note (2026-10-18): five suite volumes reference a companion
% ../reference/ source tree (CMakeLists.txt, CMakePresets.json, scripts,
% tests, browser/web clients) that was not part of the documentation upload
% batches and could not be recovered. \lstinputlisting falls back to a
% clearly marked notice when a referenced file is absent so the volumes stay
% buildable; restoring the files next to the suite re-enables the listings.
\makeatletter
\let\cmakewasm@lstinputlisting\lstinputlisting
\renewcommand{\lstinputlisting}[2][]{%
  \IfFileExists{#2}{\cmakewasm@lstinputlisting[#1]{#2}}{%
    \begin{tcolorbox}[colback=light,colframe=navy!60]\small
      \textbf{Referenced listing not included in this repository:}
      \texttt{\detokenize{#2}}. The companion reference tree was not part of
      the documentation upload; the surrounding guidance is unaffected.
    \end{tcolorbox}}}
\makeatother
"""


def t_support_cmake_preamble(text: str) -> str:
    return text + _CMAKE_WASM_FALLBACK


TRANSFORMS = {
    "t_identity": t_identity,
    "t_ad42010": t_ad42010,
    "t_cmake_wasm": t_cmake_wasm,
    "t_cpp23": t_cpp23,
    "t_cpython": t_cpython,
    "t_isms": t_isms,
    "t_misra_c": t_misra_c,
    "t_curricula": t_curricula,
    "t_dos": t_dos,
    "t_dos_cornell": t_dos_cornell,
    "t_pandoc_xcolor": t_pandoc_xcolor,
    "t_support_ad42010": t_support_ad42010,
    "t_support_cmake_preamble": t_support_cmake_preamble,
    "t_support_verbatim": t_identity,
}

# Reconstructed / extracted first-party dependencies that must exist before
# the migrated documents can build. Authored directly in the repository; the
# migration only verifies their presence.
RECONSTRUCTED_DEPENDENCIES = (
    "src/security/standards/iso-27000/isms-27000-style.tex",
    "src/programming/web/design-of-sites/design-of-sites-style.tex",
    "src/programming/web/design-of-sites/design-of-sites-references.tex",
    "tooling/styles/latex/soc2style.sty",
    "src/security/application-security/learning/assessment-curricula/assessment-curricula-common.tex",
)


# ---------------------------------------------------------------------------
# Intake discovery
# ---------------------------------------------------------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def intake_files() -> dict[str, list[Path]]:
    """Hash every candidate intake file sitting at the repository root."""
    by_sha: dict[str, list[Path]] = {}
    for path in sorted(ROOT.glob("*.tex")) + sorted(ROOT.glob("*.sty")):
        if not path.is_file():
            continue
        digest = sha256_bytes(path.read_bytes())
        by_sha.setdefault(digest, []).append(path)
    return by_sha


def _setup_tables() -> None:
    _load_documents()
    data = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    for sha, target, suite, transform in data["support_files"]:
        SUPPORT_FILES[sha] = (target, suite, transform)
    for entry in data["special"]:
        SPECIAL[entry["sha256"]] = entry


# ---------------------------------------------------------------------------
# Migration
# ---------------------------------------------------------------------------

def build_records(apply: bool) -> tuple[list[dict], list[str]]:
    by_sha = intake_files()
    records: list[dict] = []
    errors: list[str] = []

    for rel in RECONSTRUCTED_DEPENDENCIES:
        if not (ROOT / rel).exists():
            errors.append(f"missing reconstructed dependency: {rel}")

    planned: dict[str, tuple[str, str, str, str]] = {}
    for sha, (target, suite, transform) in DOCUMENTS.items():
        planned[sha] = (target, suite, transform, "document")
    for sha, (target, suite, transform) in SUPPORT_FILES.items():
        planned[sha] = (target, suite, transform, "support")

    for sha, (target, suite, transform, role) in sorted(planned.items(), key=lambda kv: kv[1][0]):
        sources = by_sha.get(sha, [])
        target_path = ROOT / target
        record = {
            "sha256": sha,
            "original_paths": [p.name for p in sources],
            "suite": suite,
            "role": role,
            "transform": transform,
            "transform_note": TRANSFORM_NOTES.get(transform, ""),
            "target_path": target,
        }
        if not sources and not target_path.exists():
            errors.append(f"source for {sha[:16]} ({target}) not found at root and target missing")
            record["migration_status"] = "missing-source"
            records.append(record)
            continue
        if sources:
            source_text = sources[0].read_text(encoding="utf-8")
            try:
                result = TRANSFORMS[transform](source_text)
            except RuntimeError as exc:
                errors.append(f"{sources[0].name}: {exc}")
                record["migration_status"] = "transform-failed"
                records.append(record)
                continue
            record["target_sha256"] = sha256_bytes(result.encode("utf-8"))
            if apply:
                current = target_path.read_text(encoding="utf-8") if target_path.exists() else None
                if current != result:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    target_path.write_text(result, encoding="utf-8")
                record["migration_status"] = "migrated"
            else:
                record["migration_status"] = "planned"
        else:
            # Source already cleaned up; verify the target is present.
            record["target_sha256"] = sha256_bytes(target_path.read_bytes())
            record["migration_status"] = "migrated"
        records.append(record)

    for sha, entry in SPECIAL.items():
        sources = by_sha.get(sha, [])
        records.append(
            {
                "sha256": sha,
                "original_paths": [p.name for p in sources],
                "suite": entry["suite"],
                "role": entry["role"],
                "transform": "none",
                "transform_note": entry["note"],
                "target_path": entry.get("existing_path", ""),
                "migration_status": entry["status"],
            }
        )

    return records, errors


def write_manifest(records: list[dict]) -> None:
    payload = {
        "intake": "repository-root documentation-suite uploads, final manifest 2026-10-18",
        "note": (
            "171 root upload files: 168 externally manifested artifacts plus the two "
            "ECMAScript 2025 volumes (06, 07) the external manifest omitted plus one "
            "byte-identical duplicate upload copy. All artifacts matched by SHA-256; "
            "upload (n) suffixes and live filenames were reconciled by hash, never by name. "
            "Reconstructed dependencies (isms-27000-style.tex, design-of-sites-style.tex, "
            "design-of-sites-references.tex, soc2style.sty) are documented inferences; the "
            "original files were never uploaded and are absent from repository history."
        ),
        "files": records,
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")


def cleanup() -> int:
    """Remove root originals whose canonical targets are verified in place."""
    by_sha = intake_files()
    removed = 0
    failures = 0
    planned: dict[str, str] = {sha: target for sha, (target, _s, _t) in DOCUMENTS.items()}
    planned.update({sha: target for sha, (target, _s, _t) in SUPPORT_FILES.items()})

    for sha, sources in by_sha.items():
        if sha in planned:
            target_path = ROOT / planned[sha]
            if not target_path.exists():
                print(f"NOT removing {sources[0].name}: target {planned[sha]} missing")
                failures += 1
                continue
            source_text = sources[0].read_text(encoding="utf-8")
            _, _, transform = DOCUMENTS.get(sha) or SUPPORT_FILES[sha]
            expected = TRANSFORMS[transform](source_text)
            if target_path.read_text(encoding="utf-8") != expected:
                print(f"NOT removing {sources[0].name}: target {planned[sha]} does not match transform output")
                failures += 1
                continue
            for path in sources:
                path.unlink()
                removed += 1
        elif sha in SPECIAL:
            entry = SPECIAL[sha]
            ok = True
            if entry.get("verify_against"):
                ok = (ROOT / entry["verify_against"]).exists()
            if ok:
                for path in sources:
                    path.unlink()
                    removed += 1
            else:
                print(f"NOT removing {sources[0].name}: verification target missing")
                failures += 1
        else:
            print(f"NOT removing unrecognized root file: {[p.name for p in sources]} ({sha[:16]})")
            failures += 1
    print(f"removed {removed} intake files, {failures} left in place")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--cleanup", action="store_true")
    args = parser.parse_args()

    _setup_tables()

    if args.cleanup:
        return cleanup()

    records, errors = build_records(apply=args.apply)
    migrated = sum(1 for r in records if r["migration_status"] in {"migrated", "planned"})
    print(f"{migrated} artifacts mapped, {len(SPECIAL)} special dispositions, {len(errors)} errors")
    for error in errors:
        print(f"ERROR: {error}")
    if args.apply and not errors:
        write_manifest(records)
        print(f"manifest written: {MANIFEST_PATH.relative_to(ROOT)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
