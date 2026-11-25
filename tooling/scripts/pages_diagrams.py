"""Reference-aware static Pages image cards. No basename-only associations."""
from __future__ import annotations

import html
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

FORMATS = ("png", "svg", "jpeg", "jpg")
SUFFIXES = {"." + fmt for fmt in FORMATS}
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
    return related


def render_card(key: Path, variants: list[Path], *, standalone: bool = False) -> str:
    ordered = sorted(variants, key=lambda p: (FORMATS.index(p.suffix.lower()[1:]), p.as_posix()))
    default = ordered[0]
    escape = lambda value: html.escape(value, quote=True)

    def href(path: Path) -> str:
        return escape("images/" + quote(path.as_posix(), safe="/:@-._~"))

    def label(path: Path) -> str:
        return "JPG (legacy)" if path.suffix.lower() == ".jpg" else path.suffix[1:].upper()

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
