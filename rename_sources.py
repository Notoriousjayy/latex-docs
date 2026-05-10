#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rename_sources.py
=================

Recursively rename ``.tex`` and ``.puml`` source files to intuitive,
content-derived, kebab-case filenames while preserving each file's
directory location and extension.

Why this exists
---------------
Over time, LaTeX/PlantUML libraries accumulate filenames that are:

  * slugified from raw ``\\title{...}`` macros and end up containing
    spacing-macro residue (``0.75em``, ``1cm-primaryblue-...``, ``12pt``);
  * generic (``main.tex``, ``activity-example.puml``, ``untitled.tex``);
  * snake_case (``admin_it_security_system_guide.tex``);
  * burdened with disambiguating numeric suffixes that no longer reflect
    the actual document subject (``...-comprehensive-gu-2.tex``).

This script reads each source file, derives a clean, meaningful slug
from its **internal content** (titles, headings, header comments,
PlantUML ``title`` directives), and proposes a rename when the new
slug is materially better than what is already on disk.

Design priorities
-----------------
1. **Safety first** – dry-run by default; never overwrite; idempotent.
2. **Correctness** – LaTeX macros stripped before slugification,
   balanced-brace parsing for ``\\title{...}``.
3. **Repository awareness** – preserves numbered PlantUML series in
   directories that obviously use ordered prefixes.
4. **Stdlib only** – no third-party dependencies.

Usage
-----
    # dry-run from the default root (./src), pretty report
    python3 rename_sources.py

    # explicit root, verbose dry-run
    python3 rename_sources.py --root /path/to/repo/src --verbose

    # actually apply the renames
    python3 rename_sources.py --root /path/to/repo/src --apply

    # apply across a different file set
    python3 rename_sources.py --apply --include-ext .tex

Exit codes
----------
    0  success, with or without renames
    1  invalid arguments
    2  fatal I/O error
    3  one or more files failed extraction in --apply mode
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Filename slugs of this length or shorter are kept; longer slugs are
#: truncated at a hyphen boundary near this length.
MAX_SLUG_LEN = 80

#: Number of bytes read from each file when looking for a title.  Almost
#: every LaTeX preamble + ``\\title{}`` lives in the first ~16 KB; PlantUML
#: ``title`` directives sit well within the first 4 KB.  We read more than
#: strictly needed so multi-line ``\\title{...}`` blocks with deeply nested
#: braces always close before the cutoff.
HEAD_BYTES = 32 * 1024

#: Generic title words that should *not* by themselves drive a rename when
#: encountered as a section heading – they reveal nothing about the
#: document's subject.
GENERIC_TITLE_WORDS = frozenset({
    "introduction", "overview", "content", "contents", "notes", "note",
    "document", "abstract", "summary", "preface", "foreword", "appendix",
    "references", "bibliography", "acknowledgments", "acknowledgements",
    "conclusion", "conclusions", "table of contents", "the document",
    "untitled", "main", "scratch", "draft", "purpose", "background",
    "diagram", "view", "example", "demo", "test", "sample", "todo",
    "readme", "index",
})

#: Filename stems we consider categorically poor and which therefore
#: *always* benefit from a content-driven rename, even if the proposed
#: slug is mediocre.
ALWAYS_REPLACE_STEMS = frozenset({
    "main", "doc", "document", "untitled", "scratch", "draft", "tmp",
    "temp", "test", "new", "copy", "file", "untitled-1",
})

#: LaTeX size / weight / shape macros whose argument we want to keep but
#: which themselves carry no semantic content for naming.  These are
#: matched as standalone tokens (not as wrappers) and stripped.
LATEX_FONT_TOKENS = frozenset({
    r"\tiny", r"\scriptsize", r"\footnotesize", r"\small",
    r"\normalsize", r"\large", r"\Large", r"\LARGE", r"\huge", r"\Huge",
    r"\bfseries", r"\itshape", r"\slshape", r"\scshape", r"\sffamily",
    r"\rmfamily", r"\ttfamily", r"\mdseries", r"\upshape", r"\em",
    r"\noindent", r"\raggedright", r"\raggedleft", r"\centering",
    r"\par", r"\smallskip", r"\medskip", r"\bigskip",
    r"\linebreak", r"\newline", r"\newpage", r"\clearpage",
    r"\maketitle", r"\thispagestyle", r"\pagestyle",
    r"\LaTeX", r"\TeX",
})

#: LaTeX wrapper macros of the form ``\macro{argument}`` whose argument
#: should be kept (the macro itself is purely visual).
LATEX_UNWRAP_MACROS = frozenset({
    "textbf", "textit", "textsl", "textsc", "textsf", "texttt",
    "textup", "textmd", "textnormal", "emph", "underline", "uline",
    "mbox", "hbox", "fbox", "framebox", "boldmath", "mathbf", "mathit",
    "mathrm", "mathsf", "mathtt", "mathcal", "uppercase", "lowercase",
    "MakeUppercase", "MakeLowercase", "ensuremath",
})

#: LaTeX macros whose argument should be *dropped* entirely.
LATEX_DROP_ARG_MACROS = frozenset({
    "vspace", "hspace", "vspace*", "hspace*", "rule", "label", "ref",
    "eqref", "cite", "citep", "citet", "footnote", "footnotemark",
    "footnotetext", "marginpar", "index", "addcontentsline",
    "phantomsection", "include", "input", "usepackage", "documentclass",
    "thispagestyle", "pagestyle", "setlength", "setcounter",
    "definecolor", "color", "hypersetup", "tcbset",
})

#: LaTeX macros of the form ``\macro{key}{value}`` where we want to keep
#: the *second* argument and drop the first (e.g. ``\textcolor{red}{X}``).
LATEX_KEEP_SECOND_ARG_MACROS = frozenset({
    "textcolor", "colorbox", "fcolorbox",
})

#: Length-spec regex (matches things like ``0.75em``, ``-1.2cm``, ``12pt``,
#: ``+3in``) that survive macro stripping if we are not careful.
LENGTH_SPEC_RE = re.compile(
    r"(?<![A-Za-z])[+\-]?\d+(?:\.\d+)?\s*"
    r"(?:em|ex|pt|pc|cm|mm|in|bp|dd|sp|mu|px)\b",
    re.IGNORECASE,
)

#: Numeric prefix used in PlantUML ordered series, e.g. ``14.1-foo`` or
#: ``07_bar`` or ``1.-baz``.
NUMERIC_PREFIX_RE = re.compile(r"^(?P<prefix>\d+(?:[.\-_]\d+)*)[\.\-_]\s*")


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class RenamePlan:
    """A single proposed rename action for one file."""

    path: Path                    #: absolute current path
    new_name: str                 #: proposed new filename (basename only)
    title: Optional[str]          #: extracted title text (None on failure)
    reason: str                   #: short, human-readable justification

    @property
    def old_name(self) -> str:
        return self.path.name

    @property
    def new_path(self) -> Path:
        return self.path.with_name(self.new_name)

    @property
    def changed(self) -> bool:
        return self.new_name != self.old_name


@dataclass
class Report:
    """Aggregated report of what the run did or would do."""

    renamed: List[RenamePlan] = field(default_factory=list)
    unchanged: List[RenamePlan] = field(default_factory=list)
    skipped: List[Tuple[Path, str]] = field(default_factory=list)
    conflicts: List[Tuple[Path, str, str]] = field(default_factory=list)
    failures: List[Tuple[Path, str]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Slugification
# ---------------------------------------------------------------------------

def slugify(text: str, *, max_len: int = MAX_SLUG_LEN) -> str:
    """Convert ``text`` into a safe, lowercase, kebab-case slug.

    The pipeline is:

    1. Unicode-normalise (NFKD) and drop combining marks so ``é`` → ``e``.
    2. Replace a small set of meaningful symbols with words
       (``&`` → ``and``, ``+`` → ``plus``, ``%`` → ``percent``).
    3. Lowercase.
    4. Replace any run of non ``[a-z0-9]`` characters with a single hyphen.
    5. Collapse repeated hyphens, strip leading/trailing hyphens.
    6. Truncate at a hyphen boundary near ``max_len``.

    >>> slugify("OWASP API Security Top 10 — 2023 Edition")
    'owasp-api-security-top-10-2023-edition'
    """
    if not text:
        return ""

    # 1. Normalise away accents and width variants.
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))

    # 2. Symbol substitutions BEFORE stripping non-alphanum, so the
    #    information they carry survives.
    substitutions = (
        ("&", " and "),
        ("+", " plus "),
        ("%", " percent "),
        ("@", " at "),
        ("#", " number "),
    )
    for src, dst in substitutions:
        text = text.replace(src, dst)

    # 3. ASCII fold and lowercase.
    text = text.encode("ascii", "ignore").decode("ascii").lower()

    # 4. Non-alphanum runs → single hyphen.
    text = re.sub(r"[^a-z0-9]+", "-", text)

    # 5. Tidy hyphens.
    text = re.sub(r"-{2,}", "-", text).strip("-")

    # 6. Length cap with hyphen-boundary preference.
    if len(text) > max_len:
        cut = text.rfind("-", 0, max_len)
        if cut <= 0 or cut < max_len - 20:
            cut = max_len
        text = text[:cut].rstrip("-")

    return text


# ---------------------------------------------------------------------------
# LaTeX content cleaning
# ---------------------------------------------------------------------------

def _drop_brace_arg(text: str, start: int) -> int:
    """Given ``text`` with a brace at index ``start``, return the index of
    the matching closing brace + 1.  Returns ``len(text)`` on imbalance."""
    depth = 0
    i = start
    n = len(text)
    while i < n:
        c = text[i]
        if c == "\\" and i + 1 < n:
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n


def clean_latex_text(text: str) -> str:
    """Strip LaTeX markup from a raw title fragment, preserving its
    semantic content so it can be slugified.

    Handles, in order:

      * Macros that take an argument we want to **drop**
        (``\\vspace{0.75em}`` → removed entirely).
      * Two-argument macros where we keep the **second** arg
        (``\\textcolor{red}{X}`` → ``X``).
      * Wrapper macros where we keep the **first** arg
        (``\\textbf{X}`` → ``X``).
      * Standalone visual tokens (``\\Large``, ``\\bfseries``) → removed.
      * Line-break-with-optional-arg constructs ``\\\\[1em]`` → space.
      * Stray ``\\\\`` linebreaks → space.
      * Non-breaking ``~`` → space.
      * LaTeX-escaped ASCII (``\\&`` → ``&``, ``\\_`` → ``_``).
      * Bare length specs that survived (``0.75em``, ``-1cm``) → removed.
      * Em/en dashes → hyphens.
    """
    if not text:
        return ""

    # ---- 0. Strip LaTeX line comments.  In LaTeX, an unescaped ``%``
    #         eats from itself through the end-of-line (and the newline
    #         itself).  Multi-line ``\title{...}`` blocks routinely use
    #         this to suppress unwanted whitespace, e.g.::
    #
    #             \title{%
    #               \textbf{Real Title}\\
    #               Subtitle
    #             }
    #
    #         If we don't strip these, ``%`` survives slugification as
    #         the literal word "percent".
    text = re.sub(r"(?<!\\)%[^\n]*", "", text)

    # ---- 1. Drop macros whose argument we never want.
    for macro in LATEX_DROP_ARG_MACROS:
        # match \macro{...} (balanced) or \macro[opt]{...}
        text = _expand_macro(text, macro, mode="drop")

    # ---- 2. Keep the second arg of {key}{value}-style macros.
    for macro in LATEX_KEEP_SECOND_ARG_MACROS:
        text = _expand_macro(text, macro, mode="second")

    # ---- 3. Unwrap ``\macro{X}`` → ``X``.
    for macro in LATEX_UNWRAP_MACROS:
        text = _expand_macro(text, macro, mode="first")

    # ---- 4. Drop standalone visual tokens.  Match whole-word so we don't
    #         eat ``\Largeword`` (rare but possible).
    for token in LATEX_FONT_TOKENS:
        text = re.sub(re.escape(token) + r"(?![A-Za-z])", " ", text)

    # ---- 5. ``\\[1em]`` and ``\\*[1em]`` line-break-with-spacing.
    text = re.sub(r"\\\\\*?\s*\[[^\]]*\]", " ", text)
    # Bare ``\\`` line-break.
    text = text.replace(r"\\", " ")
    # Non-breaking space.
    text = text.replace("~", " ")

    # ---- 6. Common LaTeX escapes back to their literal char.
    for esc, lit in (
        (r"\&", "&"), (r"\%", "%"), (r"\$", "$"),
        (r"\#", "#"), (r"\_", "_"), (r"\{", "{"), (r"\}", "}"),
    ):
        text = text.replace(esc, lit)

    # ---- 7. Any *other* leftover ``\command`` (no argument) – drop.
    text = re.sub(r"\\[A-Za-z@]+\*?", " ", text)

    # ---- 8. Bare length specs that escaped (``0.75em``, ``-1.2cm``).
    text = LENGTH_SPEC_RE.sub(" ", text)

    # ---- 9. Em-dash, en-dash, smart quotes → hyphens / blanks.
    text = text.replace("\u2014", "-").replace("\u2013", "-")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')

    # ---- 10. Collapse whitespace.
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _expand_macro(text: str, macro: str, *, mode: str) -> str:
    """Locate every occurrence of ``\\macro`` in ``text`` and replace it
    according to ``mode``:

      * ``"drop"``   – remove the macro and its argument(s) entirely.
      * ``"first"``  – keep the contents of the first ``{...}`` arg.
      * ``"second"`` – keep the contents of the *second* ``{...}`` arg.

    Optional ``[...]`` arguments are tolerated and discarded.
    The function is intentionally hand-written rather than regex-based so
    that nested braces in the argument are correctly balanced.
    """
    name = macro.rstrip("*")
    star = macro.endswith("*")
    pat = re.compile(r"\\" + re.escape(name) + (r"\*" if star else r"\*?")
                     + r"(?![A-Za-z])")

    out: List[str] = []
    i = 0
    n = len(text)
    while i < n:
        m = pat.search(text, i)
        if not m:
            out.append(text[i:])
            break
        out.append(text[i:m.start()])
        j = m.end()

        # Skip optional [...] arguments.
        while j < n and text[j] == "[":
            close = text.find("]", j)
            if close == -1:
                break
            j = close + 1

        # Capture first {...}.
        first_arg = ""
        if j < n and text[j] == "{":
            end = _drop_brace_arg(text, j)
            first_arg = text[j + 1:end - 1]
            j = end
        else:
            # Macro with no argument – leave a space and continue.
            out.append(" ")
            i = j
            continue

        # Capture optional second {...}.
        second_arg = ""
        if j < n and text[j] == "{":
            end = _drop_brace_arg(text, j)
            second_arg = text[j + 1:end - 1]
            j = end

        if mode == "drop":
            out.append(" ")
        elif mode == "first":
            out.append(first_arg)
        elif mode == "second":
            out.append(second_arg if second_arg else first_arg)
        i = j

    return "".join(out)


# ---------------------------------------------------------------------------
# Title extraction – LaTeX
# ---------------------------------------------------------------------------

def extract_tex_title(content: str) -> Optional[str]:
    """Extract the most descriptive title-like string from a LaTeX file.

    Priority order (per the project spec):

      1. ``\\title{...}``
      2. Custom title-like macros: ``\\<word>Title{...}``,
         ``\\<word>title{...}`` (e.g. ``\\docTitle{...}{...}``).
      3. ``\\chapter{...}`` or first non-generic
         ``\\section[*]{...}``.
      4. Strong header comments: ``% Title:`` or ``% File:`` near the top.
      5. First non-generic heading-like phrase.

    Returns ``None`` if nothing usable is found.
    """
    # ----- 1. \title{...}
    title = _find_braced_macro(content, r"\\title")
    if title:
        cleaned = clean_latex_text(title)
        if cleaned and not _is_generic(cleaned):
            return cleaned

    # ----- 2. Custom \xxxTitle{...} or \xxxtitle{...}
    custom = re.search(
        r"\\([A-Za-z]+[Tt]itle)\b\s*\*?\s*(?:\[[^\]]*\])?\s*\{",
        content,
    )
    if custom:
        start = custom.end() - 1  # position of '{'
        end = _drop_brace_arg(content, start)
        candidate = content[start + 1:end - 1]
        cleaned = clean_latex_text(candidate)
        if cleaned and not _is_generic(cleaned):
            return cleaned

    # ----- 3. \chapter / \section
    for macro in (r"\\chapter", r"\\section"):
        for m in re.finditer(macro + r"\*?\s*(?:\[[^\]]*\])?\s*\{", content):
            start = m.end() - 1
            end = _drop_brace_arg(content, start)
            candidate = content[start + 1:end - 1]
            cleaned = clean_latex_text(candidate)
            if cleaned and not _is_generic(cleaned):
                return cleaned

    # ----- 4. Strong header comment.
    for m in re.finditer(
        r"^[ \t]*%[ \t]*(?:Title|File|Subject|Document)\s*[:\-]\s*(.+)$",
        content,
        flags=re.MULTILINE | re.IGNORECASE,
    ):
        candidate = m.group(1).strip()
        # If the comment names a path, extract the basename and drop ext.
        if "/" in candidate or "\\" in candidate:
            candidate = candidate.replace("\\", "/").rsplit("/", 1)[-1]
            candidate = re.sub(r"\.[A-Za-z0-9]+$", "", candidate)
            candidate = candidate.replace("-", " ").replace("_", " ")
        cleaned = clean_latex_text(candidate)
        if cleaned and not _is_generic(cleaned):
            return cleaned

    return None


def _find_braced_macro(content: str, macro_pattern: str) -> Optional[str]:
    """Find ``macro_pattern{...}`` in ``content`` and return the brace
    contents with proper balancing.  ``macro_pattern`` is a regex
    fragment, e.g. ``r"\\title"``."""
    m = re.search(macro_pattern + r"\b\s*\*?\s*(?:\[[^\]]*\])?\s*\{",
                  content)
    if not m:
        return None
    start = m.end() - 1
    end = _drop_brace_arg(content, start)
    return content[start + 1:end - 1]


# ---------------------------------------------------------------------------
# Title extraction – PlantUML
# ---------------------------------------------------------------------------

def extract_puml_title(content: str) -> Optional[str]:
    """Extract a meaningful title from a PlantUML source.

    Priority order:

      1. ``title <text>`` (single line) or ``title\\n...\\nend title``.
      2. ``caption <text>``.
      3. Strong header comments: ``' Diagram:`` / ``' Title:`` /
         ``/' Diagram: '/`` near the top.
      4. The first non-skinparam, non-include, non-stereotype meaningful
         label – e.g. the first class name, actor name or note text.

    Boilerplate (``@startuml``, ``@enduml``, ``!include ...``,
    ``skinparam ...``, ``hide ...``, ``scale ...``) is ignored throughout.
    """
    # ---- 1. ``title ... end title`` block.
    block = re.search(
        r"^\s*title\s*\n(?P<body>.*?)\n\s*end\s*title\s*$",
        content,
        flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    if block:
        body = _clean_puml_text(block.group("body"))
        if body and not _is_generic(body):
            return body

    # ---- 1b. Single-line ``title ...``.
    line = re.search(
        r"^[ \t]*title[ \t]+(?P<body>.+)$",
        content,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    if line:
        body = _clean_puml_text(line.group("body"))
        if body and not _is_generic(body):
            return body

    # ---- 2. ``caption ...``.
    cap = re.search(
        r"^[ \t]*caption[ \t]+(?P<body>.+)$",
        content,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    if cap:
        body = _clean_puml_text(cap.group("body"))
        if body and not _is_generic(body):
            return body

    # ---- 3. Header comments: ``' Diagram: ...``, ``' Title: ...``, etc.
    for m in re.finditer(
        r"^[ \t]*'[ \t]*(?:Diagram|Title|Subject|Document|Section|Topic)"
        r"[ \t]*[:\-][ \t]*(?P<body>.+)$",
        content,
        flags=re.MULTILINE | re.IGNORECASE,
    ):
        body = _clean_puml_text(m.group("body"))
        if body and not _is_generic(body):
            return body

    # ---- 4. First meaningful identifier (class / actor / package / note).
    for m in re.finditer(
        r'^[ \t]*(?:class|interface|enum|abstract|actor|usecase|package'
        r'|component|node|database|participant|boundary|control|entity'
        r'|state|object|rectangle|note\s+(?:over|left|right|top|bottom)?'
        r'|together|frame|cloud|folder)\s+'
        r'(?:"(?P<quoted>[^"]+)"|(?P<bare>[A-Za-z][A-Za-z0-9_]*))',
        content,
        flags=re.MULTILINE | re.IGNORECASE,
    ):
        candidate = (m.group("quoted") or m.group("bare") or "").strip()
        if candidate:
            cleaned = _clean_puml_text(candidate)
            if cleaned and not _is_generic(cleaned):
                return cleaned

    return None


def _clean_puml_text(text: str) -> str:
    """Remove PlantUML formatting artefacts from a title fragment."""
    if not text:
        return ""
    # Decode escaped newlines.
    text = text.replace(r"\n", " ").replace(r"\r", " ")
    text = text.replace(r"\t", " ").replace(r"\l", " ")
    # Strip <b>, <i>, <color:#abc>, <size:14> etc.
    text = re.sub(r"<[^>]+>", " ", text)
    # Strip surrounding quotes.
    text = text.strip().strip('"').strip("'")
    # Drop trailing colour spec like ``#FFAA00``.
    text = re.sub(r"#[0-9A-Fa-f]{3,8}\b", " ", text)
    # Em/en dashes, smart quotes.
    text = text.replace("\u2014", "-").replace("\u2013", "-")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    # Collapse whitespace.
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ---------------------------------------------------------------------------
# Genericity check
# ---------------------------------------------------------------------------

def _is_generic(text: str) -> bool:
    """True if ``text`` is too generic to identify a document."""
    if not text:
        return True
    norm = text.strip().lower()
    # Strip a leading section number like ``1.``, ``1.2``, ``A.1``.
    norm = re.sub(r"^[\dA-Za-z]+(?:\.\d+)*\.?\s+", "", norm)
    if norm in GENERIC_TITLE_WORDS:
        return True
    # A single very short word is unlikely to be informative.
    if len(norm) <= 2:
        return True
    return False


# ---------------------------------------------------------------------------
# Numbered-series detection (PlantUML)
# ---------------------------------------------------------------------------

def detect_series_prefix(path: Path, peers: Iterable[Path]) -> Optional[str]:
    """If ``path`` is part of a numbered series in its directory, return
    the numeric prefix (without the trailing separator), else ``None``.

    A "series" is defined as **3 or more** sibling files of the same
    extension whose names begin with ``\\d+(?:\\.\\d+)*[\\.\\-_]``.  The
    threshold of 3 prevents accidentally treating a one-off ``14.1-foo``
    as ordered.
    """
    m = NUMERIC_PREFIX_RE.match(path.name)
    if not m:
        return None
    own_prefix = m.group("prefix")

    same_ext = [p for p in peers if p.suffix == path.suffix and p != path]
    matches = sum(1 for p in same_ext if NUMERIC_PREFIX_RE.match(p.name))
    if matches + 1 >= 3:  # include self
        return own_prefix
    return None


# ---------------------------------------------------------------------------
# Reading files safely
# ---------------------------------------------------------------------------

def read_head(path: Path, limit: int = HEAD_BYTES) -> str:
    """Read up to ``limit`` bytes of ``path`` as text, decoding leniently.

    Returns ``""`` on I/O error.
    """
    try:
        with path.open("rb") as f:
            data = f.read(limit)
    except OSError:
        return ""
    # Try UTF-8 first; fall back to latin-1 which never fails.
    for enc in ("utf-8", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Decision logic – is the new name materially better?
# ---------------------------------------------------------------------------

# Markers in an existing filename suggesting it was poorly derived and
# should be replaced even if the proposed slug is only marginally better.
_BAD_NAME_MARKERS = (
    re.compile(r"\b\d+(?:\.\d+)?(em|ex|pt|pc|cm|mm|in|bp)\b", re.IGNORECASE),
    re.compile(r"primaryblue|softbg|accent\b", re.IGNORECASE),
    re.compile(r"_"),
    re.compile(r"[A-Z]"),
    re.compile(r"-{2,}"),
    re.compile(r"^[\-\.]"),
    re.compile(r"\.[a-z]+\.[a-z]+$"),  # double extensions
)


def is_materially_better(old_stem: str, new_slug: str) -> Tuple[bool, str]:
    """Return ``(better, reason)``.

    ``old_stem`` is the current filename without extension.
    ``new_slug`` is the proposed kebab-case slug.
    """
    if not new_slug:
        return False, "empty proposed slug"

    if old_stem == new_slug:
        return False, "names identical"

    old_norm = slugify(old_stem.replace("_", "-").lower())
    if old_norm == new_slug:
        return False, "slugified equivalent"

    # Always prefer to fix categorically poor stems.
    base = old_stem.lower()
    if base in ALWAYS_REPLACE_STEMS or base.startswith("untitled"):
        return True, "generic stem replaced"

    # Always replace if the existing name shows clear pathologies.
    for pat in _BAD_NAME_MARKERS:
        if pat.search(old_stem):
            return True, f"old name has bad marker: {pat.pattern}"

    # Truncation suffix like ``-gu``, ``-im``, ``-2`` after a long stem.
    if len(old_stem) >= MAX_SLUG_LEN - 5 and re.search(r"-[a-z]{1,3}$", old_stem):
        return True, "old name appears truncated"

    # Significantly more informative? (more distinct word stems).
    old_words = {w for w in re.split(r"[-_.]", old_stem.lower()) if len(w) > 2}
    new_words = {w for w in new_slug.split("-") if len(w) > 2}
    if len(new_words) >= len(old_words) + 2 and old_words.issubset(new_words):
        return True, "new name strictly more informative"

    if len(new_words & old_words) / max(1, len(old_words)) < 0.4:
        return True, "old name substantively different from content"

    return False, "old name already adequate"


# ---------------------------------------------------------------------------
# Main planning routine
# ---------------------------------------------------------------------------

def plan_renames(root: Path, exts: Set[str], verbose: bool) -> Report:
    """Scan ``root`` recursively and build a :class:`Report` of proposed
    renames without touching the filesystem."""

    report = Report()
    # First, gather every candidate file grouped by directory so we can
    # do per-directory series detection cheaply.
    by_dir: Dict[Path, List[Path]] = defaultdict(list)
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip dotfile directories (.git, .github, etc.) and node_modules.
        dirnames[:] = [d for d in dirnames
                       if not d.startswith(".") and d != "node_modules"]
        d = Path(dirpath)
        for name in filenames:
            p = d / name
            if p.suffix.lower() in exts:
                by_dir[d].append(p)

    # Plan renames per file.  Track planned new names per directory to
    # detect intra-batch conflicts and assign deterministic suffixes.
    planned_per_dir: Dict[Path, Set[str]] = defaultdict(set)

    for d in sorted(by_dir):
        peers = by_dir[d]
        for path in sorted(peers):
            try:
                plan = _plan_one(path, peers, planned_per_dir[d])
            except Exception as exc:  # noqa: BLE001 – we want a complete run
                report.failures.append((path, f"{type(exc).__name__}: {exc}"))
                if verbose:
                    print(f"[FAIL] {path}: {exc}", file=sys.stderr)
                continue

            if plan is None:
                continue

            if not plan.changed:
                report.unchanged.append(plan)
                continue

            # Final on-disk safety net (some CI runs may have raced files).
            if plan.new_path.exists():
                report.conflicts.append(
                    (path, plan.new_name,
                     "target already exists on disk after disambiguation"))
                continue

            planned_per_dir[d].add(plan.new_name)
            report.renamed.append(plan)

    return report


def _plan_one(path: Path,
              peers: List[Path],
              already_planned: Set[str]) -> Optional[RenamePlan]:
    """Compute the rename plan for a single file, or ``None`` when we
    have no opinion."""

    content = read_head(path)
    if not content:
        # Empty file or unreadable – never invent a name.
        return RenamePlan(path, path.name, None,
                          reason="file empty or unreadable")

    suffix = path.suffix.lower()
    if suffix == ".tex":
        title = extract_tex_title(content)
    elif suffix == ".puml":
        title = extract_puml_title(content)
    else:
        return None  # filtered earlier, but defensive

    if not title:
        return RenamePlan(path, path.name, None,
                          reason="no title-like content found")

    new_slug = slugify(title)
    if not new_slug:
        return RenamePlan(path, path.name, None,
                          reason="title slugified to empty string")

    # PlantUML: preserve a numbered-series prefix when one is in use.
    if suffix == ".puml":
        series = detect_series_prefix(path, peers)
        if series:
            # Strip any prefix already in the proposed slug to avoid
            # double-prefixing, then re-attach the canonical one.
            new_slug = re.sub(r"^" + re.escape(slugify(series)) + r"-?", "",
                              new_slug)
            new_slug = f"{series}-{new_slug}".strip("-")
            new_slug = re.sub(r"-{2,}", "-", new_slug)

    new_name = f"{new_slug}{path.suffix}"

    # Materiality check.
    better, reason = is_materially_better(path.stem, new_slug)
    if not better:
        return RenamePlan(path, path.name, title, reason=reason)

    # Deterministic disambiguation: append ``-2``, ``-3``, ... if the
    # target name already exists or has been planned for this directory.
    final_name = _disambiguate(new_name, path, already_planned)
    return RenamePlan(path, final_name, title, reason=reason)


def _disambiguate(candidate: str, path: Path,
                  already_planned: Set[str]) -> str:
    """If ``candidate`` would collide on disk or in the planned set,
    append ``-2``, ``-3``, ... before the extension until unique."""
    parent = path.parent
    stem, ext = candidate.rsplit(".", 1)
    ext = "." + ext

    def is_taken(name: str) -> bool:
        # The current file does not count as taking its own slot.
        target = parent / name
        if target.exists() and target.resolve() != path.resolve():
            return True
        if name in already_planned:
            return True
        return False

    if not is_taken(candidate):
        return candidate

    n = 2
    while True:
        attempt = f"{stem}-{n}{ext}"
        if not is_taken(attempt):
            return attempt
        n += 1
        if n > 999:
            raise RuntimeError(
                f"Could not disambiguate {candidate!r} in {parent}")


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------

def apply_plan(report: Report, *, verbose: bool) -> int:
    """Perform the renames in ``report.renamed``.  Returns count of
    successful renames."""
    done = 0
    for plan in report.renamed:
        try:
            plan.path.rename(plan.new_path)
            done += 1
            if verbose:
                print(f"[OK]   {plan.path} → {plan.new_name}")
        except OSError as exc:
            print(f"[FAIL] {plan.path}: {exc}", file=sys.stderr)
            report.failures.append((plan.path, str(exc)))
    return done


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _bar(title: str, width: int = 76) -> str:
    pad = max(0, width - len(title) - 2)
    return f"== {title} " + ("=" * pad)


def print_report(report: Report, *, root: Path, dry_run: bool,
                 verbose: bool) -> None:
    """Pretty-print the rename report to stdout."""
    print(_bar("rename report"))
    print(f"  root         : {root}")
    print(f"  mode         : {'DRY-RUN' if dry_run else 'APPLY'}")
    print(f"  renamed      : {len(report.renamed)}")
    print(f"  unchanged    : {len(report.unchanged)}")
    print(f"  conflicts    : {len(report.conflicts)}")
    print(f"  failures     : {len(report.failures)}")
    print()

    if report.renamed:
        print(_bar("proposed renames" if dry_run else "renames"))
        for plan in report.renamed:
            rel = plan.path.relative_to(root) if _is_within(plan.path, root) \
                else plan.path
            print(f"  {rel}")
            print(f"      → {plan.new_name}")
            if verbose:
                print(f"        title : {plan.title!r}")
                print(f"        why   : {plan.reason}")
        print()

    if report.conflicts:
        print(_bar("conflicts (NOT renamed)"))
        for path, name, why in report.conflicts:
            rel = path.relative_to(root) if _is_within(path, root) else path
            print(f"  {rel}")
            print(f"      target: {name}")
            print(f"      reason: {why}")
        print()

    if report.failures:
        print(_bar("failures"))
        for path, why in report.failures:
            rel = path.relative_to(root) if _is_within(path, root) else path
            print(f"  {rel}: {why}")
        print()

    if verbose and report.unchanged:
        print(_bar("unchanged (kept as-is)"))
        for plan in report.unchanged:
            rel = plan.path.relative_to(root) if _is_within(plan.path, root) \
                else plan.path
            print(f"  {rel}  ({plan.reason})")
        print()


def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="rename_sources.py",
        description=(
            "Rename .tex and .puml files to content-derived, kebab-case "
            "filenames.  Dry-run by default."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python3 rename_sources.py\n"
            "  python3 rename_sources.py --root src --verbose\n"
            "  python3 rename_sources.py --root src --apply\n"
        ),
    )
    p.add_argument("--root", default="src", type=Path,
                   help="repository root to scan recursively (default: ./src)")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", default=True,
                      help="show proposed renames without changing anything "
                           "(default)")
    mode.add_argument("--apply", action="store_true", default=False,
                      help="actually perform the renames")
    p.add_argument("--verbose", "-v", action="store_true", default=False,
                   help="print extra detail (titles, reasons, kept files)")
    p.add_argument("--include-ext", nargs="+",
                   default=[".tex", ".puml"],
                   help="file extensions to consider (default: .tex .puml)")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    root: Path = args.root.resolve()

    if not root.exists():
        print(f"error: --root {root} does not exist", file=sys.stderr)
        return 1
    if not root.is_dir():
        print(f"error: --root {root} is not a directory", file=sys.stderr)
        return 1

    exts: Set[str] = {e.lower() if e.startswith(".") else "." + e.lower()
                      for e in args.include_ext}

    dry_run = not args.apply

    report = plan_renames(root, exts, verbose=args.verbose)

    if not dry_run:
        apply_plan(report, verbose=args.verbose)

    print_report(report, root=root, dry_run=dry_run, verbose=args.verbose)

    if not dry_run and report.failures:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
