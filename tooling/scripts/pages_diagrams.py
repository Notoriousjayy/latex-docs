"""Reference-aware static Pages image cards. No basename-only associations."""
from __future__ import annotations

import html
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

FORMATS = ("png", "svg")
SUFFIXES = {"." + fmt for fmt in FORMATS}
LEGACY_SUFFIXES = {".jpg", ".jpeg"}
GRAPHICS = re.compile(r"\\(?:includegraphics|safeincludegraphics)\*?\s*(?:\[[^\]]*\])?\s*\{([^{}]+)\}")
INPUTS = re.compile(r"\\(?:input|include|subfile|subfileinclude)\s*\{([^{}]+)\}")
GRAPHICSPATH = re.compile(r"\\graphicspath\s*\{((?:\s*\{[^}]*\}\s*)+)\}")
SHORTHAND = re.compile(r"\\diagram(?:\[[^\]]*\])?\s*\{([^{}]+)\}")
SHORTHAND_DEFINITION = re.compile(r"\\(?:re)?newcommand\s*\{\\diagram\}")
COMMENT = re.compile(r"(?<!\\)%[^\n]*")


def group_key(path: Path) -> Path:
    """Sibling format directories represent one logical image, not global stems."""
    parent = path.parent
    if parent.name.lower() in FORMATS:
        parent = parent.parent
    return parent / path.stem


def group_images(paths: list[Path]) -> dict[Path, list[Path]]:
    groups: dict[Path, list[Path]] = defaultdict(list)
    for path in sorted(paths):
        if path.suffix.lower() in SUFFIXES:
            groups[group_key(path)].append(path)
    return dict(sorted(groups.items()))


def document_diagrams(pdfs: list[Path], groups: dict[Path, list[Path]], source_root: Path) -> dict[Path, list[Path]]:
    """Resolve static graphic references, local TeX inputs and known diagram shorthand.

    Only staged asset paths are eligible. Dynamic paths and missing/ambiguous
    references stay in the separate gallery rather than being guessed by name.
    """
    source_root = source_root.resolve()
    aliases: dict[Path, set[Path]] = defaultdict(set)
    for key, variants in groups.items():
        for variant in variants:
            relative = Path(*variant.parts[1:]) if variant.parts[0] == source_root.name else variant
            aliases[relative].add(key)
            aliases[relative.with_suffix("")].add(key)
            # A format migration must not break the association of an explicitly
            # referenced legacy extension if a sibling format has been staged.
            for suffix in SUFFIXES:
                aliases[relative.with_suffix(suffix)].add(key)
    cache: dict[Path, str] = {}

    def safe_relative(path: Path) -> Path | None:
        try:
            return path.resolve().relative_to(source_root)
        except (ValueError, OSError):
            return None

    def lookup(path: Path) -> Path | None:
        relative = safe_relative(path)
        if relative is None:
            return None
        keys = aliases.get(relative, set())
        return next(iter(keys)) if len(keys) == 1 else None

    def read(path: Path) -> str:
        if path not in cache:
            try:
                cache[path] = COMMENT.sub("", path.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                cache[path] = ""
        return cache[path]

    related: dict[Path, list[Path]] = {}
    for pdf in pdfs:
        root = source_root / pdf.with_suffix(".tex")
        if not root.is_file():
            continue
        seen: set[Path] = set()
        stack = [root]
        sources: list[tuple[Path, str]] = []
        while stack:
            current = stack.pop().resolve()
            if current in seen or safe_relative(current) is None:
                continue
            seen.add(current)
            body = read(current)
            sources.append((current, body))
            for name in INPUTS.findall(body):
                if "\\" in name or "#" in name:
                    continue
                for directory in (current.parent, root.parent, source_root, source_root.parent):
                    base = directory / name.strip()
                    target = base if base.suffix else base.with_suffix(".tex")
                    if safe_relative(target) is not None and target.is_file():
                        stack.append(target)
                        break
        # TeX graphics paths can be declared in the root or a loaded fragment.
        declared: list[Path] = []
        for current, body in sources:
            for block in GRAPHICSPATH.findall(body):
                for entry in re.findall(r"\{([^{}]+)\}", block):
                    if "\\" not in entry and "#" not in entry:
                        declared.extend((current.parent / entry, root.parent / entry))
        allow_shorthand = any(SHORTHAND_DEFINITION.search(body) for _, body in sources)
        keys: set[Path] = set()
        for current, body in sources:
            names = GRAPHICS.findall(body)
            if allow_shorthand:
                names += ["png/" + name + ".png" for name in SHORTHAND.findall(body)]
            for name in names:
                name = name.strip()
                if not name or "\\" in name or "#" in name:
                    continue
                for directory in (current.parent, root.parent, *declared, source_root, source_root.parent):
                    hit = lookup(directory / name)
                    if hit is not None:
                        keys.add(hit)
                        break
        if keys:
            related[pdf] = sorted(keys)
    # Explicit references take precedence. Only unassigned images enter the
    # contextual pass; never associate across unrelated subject directories.
    inferred = infer_related(pdfs, groups, source_root, related)
    for pdf, keys in inferred.items():
        related[pdf] = sorted(set(related.get(pdf, [])) | set(keys))
    return related


GENERIC = {"architecture", "document", "documentation", "guide", "reference", "diagram",
           "diagrams", "style", "model", "system", "software", "technical", "views",
           "overview", "index", "notes", "design", "examples", "example", "patterns",
           "part", "chapter", "the", "and", "for", "with", "from"}
ASSET_FOLDERS = {"diagrams", "images", "figures", "assets", "examples", "railroad-samples"}


def terms(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9]+", text.casefold())
            if len(word) > 2 and word not in GENERIC and not word.isdigit()}


def infer_related(pdfs, groups, source_root, explicit):
    """Associate unreferenced images by bounded collection and topic evidence.

    A sole document in a dedicated diagram collection is a strong ownership
    signal. Otherwise require overlapping distinctive terms and a unique best
    candidate. Railroad diagrams have an exact language-to-document mapping.
    No fallback to a broad top-level category or arbitrary basename tie-break.
    """
    result = defaultdict(list)
    attached = {key for keys in explicit.values() for key in keys}
    by_parent = defaultdict(list)
    metadata = {}
    for pdf in pdfs:
        tex = source_root / pdf.with_suffix(".tex")
        if not tex.is_file():
            continue
        by_parent[pdf.parent].append(pdf)
        try:
            content = tex.read_text(encoding="utf-8", errors="replace")
        except OSError:
            content = ""
        titles = re.findall(r"\\(?:title|section|subsection|chapter)\*?\s*\{([^{}]+)\}", content)
        metadata[pdf] = (terms(pdf.stem + " " + " ".join(titles)), terms(content))
    for key in groups:
        if key in attached:
            continue
        relative = Path(*key.parts[1:]) if key.parts[0] == source_root.name else key
        parts = relative.parts
        # Generated grammar assets share a language-specific reference PDF.
        if "railroad-generated" in parts:
            pos = parts.index("railroad-generated")
            if pos + 1 < len(parts):
                target = Path(*parts[:pos]) / (parts[pos + 1] + "-syntax-reference.pdf")
                if target in metadata:
                    result[target].append(key)
                    continue
        if "railroad-samples" in parts:
            pos = parts.index("railroad-samples")
            for pdf in by_parent.get(Path(*parts[:pos]), []):
                if relative.stem == pdf.stem.removesuffix("-syntax-reference"):
                    result[pdf].append(key)
                    break
            else:
                pdf = None
            if pdf is not None and key in result.get(pdf, []):
                continue
        scope = relative.parent
        while scope.name in ASSET_FOLDERS:
            scope = scope.parent
        # Scope must be a real subject collection, not a category like security.
        if len(scope.parts) < 2:
            continue
        image_words = terms(relative.stem)
        candidates = by_parent.get(scope, [])
        # Detect an authored PlantUML collection even if the block output
        # filename differs from the source filename.
        diagram_dir = source_root / relative.parent
        authored = any(diagram_dir.glob("*.puml"))
        if len(candidates) == 1 and authored:
            result[candidates[0]].append(key)
            continue
        # Collection index may be next to a nested diagram library, not inside.
        # Permit at most two ancestors, require specific title/topic overlap.
        nearby = set(candidates)
        for ancestor in list(scope.parents)[:2]:
            if len(ancestor.parts) >= 2:
                nearby.update(by_parent.get(ancestor, []))
        ranked = []
        scope_words = terms(scope.name)
        for pdf in nearby:
            title, body = metadata[pdf]
            direct = image_words & title
            shared_scope = scope_words & title
            content_hits = image_words & body
            if len(direct) >= 2 or (len(shared_scope) >= 2 and len(content_hits) >= 1):
                ranked.append((4 * len(direct) + 3 * len(shared_scope) + min(3, len(content_hits)), pdf))
        ranked.sort(key=lambda row: (-row[0], row[1].as_posix()))
        if ranked and (len(ranked) == 1 or ranked[0][0] >= ranked[1][0] + 3):
            result[ranked[0][1]].append(key)
    return result


def render_card(key: Path, variants: list[Path], *, standalone: bool = False) -> str:
    ordered = sorted(variants, key=lambda p: (FORMATS.index(p.suffix.lower()[1:]), p.as_posix()))
    default = ordered[0]
    escape = lambda value: html.escape(value, quote=True)

    def href(path: Path) -> str:
        return escape("images/" + quote(path.as_posix(), safe="/:@-._~"))

    def label(path: Path) -> str:
        return path.suffix[1:].upper()

    search = escape(" ".join(p.as_posix() for p in ordered).casefold())
    title = escape(key.name)
    preview = href(default)
    links = []
    for index, path in enumerate(ordered):
        active = ' aria-current="true"' if index == 0 else ""
        links.append(f'<a href="{href(path)}" data-format-link{active}>{label(path)}</a>')
    marker = ' data-standalone' if standalone else ""
    return (
        f'<li class="image-card" data-search="{search}"{marker}>'
        f'<a href="{preview}" data-full-image target="_blank" rel="noopener noreferrer">'
        f'<img src="{preview}" alt="{title} diagram" loading="lazy" decoding="async"></a>'
        f'<div class="image-meta"><strong>{title}</strong> · <span data-selected-format aria-live="polite">{label(default)}</span></div>'
        f'<nav class="image-format-links" aria-label="Image format for {title}">{"".join(links)}</nav>'
        '</li>'
    )
