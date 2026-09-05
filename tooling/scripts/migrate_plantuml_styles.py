#!/usr/bin/env python3
"""Migrate first-party PlantUML sources onto the shared house style system.

The corpus predates the shared modules: 179 of 259 diagrams carried their own
hex palette and 103 re-themed themselves with local skinparams. This script
moves every such source onto the tokens and role classes defined in
tooling/plantuml/house-tokens.iuml so that one authoritative definition owns
each visual decision. It is idempotent: a migrated file is left untouched.

What it does per renderable diagram under src/:

* drops `!theme` directives and duplicate `!include` lines;
* removes single-line skinparams that set colour, typography or corner
  rounding (layout hints such as nodesep/ranksep/linetype/direction stay);
* removes colour/typography lines inside `skinparam X { ... }` blocks and
  deletes the block when nothing else is left;
* replaces every six-digit hex literal with the nearest house role token,
  choosing $line_* for arrow/text contexts and $fill_*/$deep_* for element
  fills, and resolving per-diagram collisions so two colours that were
  distinct in the source stay distinct after migration;
* rewrites `;text:white` / `<color:white>` to the on-dark token.

Semantic corrections that need a human reading of the diagram (choosing
role stereotypes, adding legends, converting to C4) are deliberately not
automated here; the report lists what still needs attention.

Usage:
    python3 tooling/scripts/migrate_plantuml_styles.py            # apply
    python3 tooling/scripts/migrate_plantuml_styles.py --check    # report only
    python3 tooling/scripts/migrate_plantuml_styles.py --report out.json
"""

from __future__ import annotations

import argparse
import colorsys
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

HEX = re.compile(r"#([0-9A-Fa-f]{6})\b")
THEME = re.compile(r"^\s*!theme\b", re.I)
INCLUDE = re.compile(r"^\s*!include(?:sub)?\s+\S+\s*$")
STARTUML = re.compile(r"^@startuml", re.M)
# Single-line skinparams owned by the shared modules (colour, typography, rounding, shadow, background).
OWNED_SINGLE = re.compile(
    r"^\s*skinparam\s+(?!\w*<<)[A-Za-z]*(Color|FontSize|FontStyle|FontName|RoundCorner|Shadowing|backgroundColor|BackgroundColor)\b",
    re.I,
)
BLOCK_OPEN = re.compile(r"^\s*skinparam\s+([A-Za-z]+)(<<[^>]+>>)?\s*\{\s*$")
BLOCK_OWNED_LINE = re.compile(r"^\s*[A-Za-z]*(Color|FontSize|FontStyle|FontName|RoundCorner|Shadowing)\b", re.I)
ARROW_COLOR = re.compile(r"(-\[)(#[0-9A-Fa-f]{6})")
INLINE_COLOR = re.compile(r"(<color:)(#[0-9A-Fa-f]{6})(>)")
LEGEND_SWATCH = re.compile(r"(\|\s*<)(#[0-9A-Fa-f]{6})(>)")
TEXT_SUFFIX = re.compile(r";text:(white|#FFFFFF|#ffffff)\b")
INLINE_WHITE = re.compile(r"<color:(white|#FFFFFF|#ffffff)>")
DEFINE_COLOR = re.compile(r"^\s*!(define\s+\w+|\$\w+\s*=)\s*\"?(#[0-9A-Fa-f]{6})\"?\s*$")

ROLES = ("primary", "dynamic", "ok", "caution", "invalid", "alt", "neutral")
# Hue buckets (degrees) -> role. Boundaries chosen on the corpus's Material-style palette.
HUE_BUCKETS = (
    (0, 22, "invalid"),
    (22, 70, "caution"),
    (70, 160, "ok"),
    (160, 200, "dynamic"),
    (200, 255, "primary"),
    (255, 335, "alt"),
    (335, 361, "invalid"),
)
DEPTHS = ("fill", "deep", "line")


def _hsl(hex6: str) -> tuple[float, float, float]:
    r, g, b = (int(hex6[i : i + 2], 16) / 255 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, s, l


def classify(hex6: str) -> tuple[str, str]:
    """Return (role, depth) for a hex colour; depth is fill/deep/line."""
    hue, sat, light = _hsl(hex6)
    # Blue-grey charcoals (#37474F, #455A64, #546E7A) sit just above a strict grey threshold but were
    # used as "dark header" fills, so they are treated as neutral-dark and land on the navy stroke.
    if sat < 0.12 or (sat < 0.22 and light < 0.45):
        if light > 0.93:
            return "surface", "fill"
        if light > 0.80:
            return "neutral", "fill"
        if light > 0.55:
            return "neutral", "deep"
        if light > 0.30:
            return "neutral", "line"
        # Dark slate/charcoal fills read as the emphasised element; keep them in-palette as navy.
        return "primary", "line"
    role = next(role for lo, hi, role in HUE_BUCKETS if lo <= hue < hi)
    if light > 0.80:
        depth = "fill"
    elif light > 0.62:
        depth = "deep"
    else:
        depth = "line"
    return role, depth


def token(role: str, depth: str) -> str:
    if role == "surface":
        return "$theme_surface" if depth == "fill" else "$theme_surface_2"
    return f"${depth}_{role}"


def _alternatives(role: str, depth: str) -> list[tuple[str, str]]:
    """Fallback tokens when two source colours collapse onto one token: same role other depth, then neighbours."""
    order: list[tuple[str, str]] = []
    if role == "surface":
        order += [("surface", "deep"), ("neutral", "fill"), ("neutral", "deep")]
        return order
    other_depths = [d for d in DEPTHS if d != depth and d != "line"] if depth != "line" else []
    order += [(role, d) for d in other_depths]
    idx = ROLES.index(role) if role in ROLES else 0
    for step in (1, -1, 2, -2, 3, -3):
        neighbour = ROLES[(idx + step) % len(ROLES)]
        order.append((neighbour, depth if depth != "line" else "line"))
        if depth != "line":
            order += [(neighbour, d) for d in other_depths]
    return order


def build_color_map(text: str) -> tuple[dict[str, str], list[str]]:
    """Map every hex in a diagram to a token; keep source distinctions by resolving collisions."""
    counts = Counter(m.group(1).upper() for m in HEX.finditer(text))
    # `!define NAME #hex` aliases hide the real usage context; classify by where the alias is used.
    aliases = {m.group(1): m.group(2)[1:].upper() for m in re.finditer(r"^\s*!define\s+(\w+)\s+(#[0-9A-Fa-f]{6})\s*$", text, re.M)}
    fill_contexts: Counter[str] = Counter()
    line_contexts: Counter[str] = Counter()
    for line in text.splitlines():
        if re.match(r"\s*(skinparam|!)", line):
            continue
        hexes = [h.upper() for h in HEX.findall(line)]
        for alias, value in aliases.items():
            if re.search(rf"\b{re.escape(alias)}\b", line):
                hexes.append(value)
        if not hexes:
            continue
        alias_edge = bool(aliases) and bool(re.search(r"-\[(" + "|".join(map(re.escape, aliases)) + r")\b", line))
        is_edge = bool(ARROW_COLOR.search(line) or INLINE_COLOR.search(line)) or alias_edge
        # A legend row that draws an arrow glyph describes an edge colour, not a fill.
        if line.lstrip().startswith("|") and re.search(r"[→←─┄~]|-->|->|\.\.>", line):
            is_edge = True
        for h in hexes:
            (line_contexts if is_edge else fill_contexts)[h] += 1
    mapping: dict[str, str] = {}
    used_fill_tokens: dict[str, str] = {}
    notes: list[str] = []
    # Most frequent colours claim their natural token first.
    for hex6, _ in counts.most_common():
        role, depth = classify(hex6)
        is_fill = fill_contexts.get(hex6, 0) > 0
        # A saturated mid-tone used as an element fill kept dark text legible in the source; a stroke
        # token would not, so fills never go darker than the deep tint (white-text headers are
        # restored to the stroke token by the ;text: pass below).
        if is_fill and depth == "line":
            depth = "deep"
        natural = token(role, depth)
        if not is_fill:
            mapping[hex6] = natural
            continue
        if natural not in used_fill_tokens:
            mapping[hex6] = natural
            used_fill_tokens[natural] = hex6
            continue
        for alt_role, alt_depth in _alternatives(role, depth):
            candidate = token(alt_role, alt_depth)
            if candidate not in used_fill_tokens:
                mapping[hex6] = candidate
                used_fill_tokens[candidate] = hex6
                notes.append(f"#{hex6} -> {candidate} (natural {natural} already taken by #{used_fill_tokens[natural]})")
                break
        else:
            mapping[hex6] = natural
            notes.append(f"#{hex6} -> {natural} COLLIDES with #{used_fill_tokens[natural]} (no free token)")
    return mapping, notes


def _line_token(tok: str) -> str:
    """Arrows and inline text must use a stroke colour even when the source hex was a tint."""
    if tok.startswith("$fill_") or tok.startswith("$deep_"):
        return "$line_" + tok.split("_", 1)[1]
    if tok.startswith("$theme_surface"):
        return "$line_neutral"
    return tok


def migrate_text(text: str) -> tuple[str, dict]:
    stats: dict = {"removed_lines": 0, "hex_replaced": 0, "notes": []}
    lines = text.splitlines()
    out: list[str] = []
    seen_includes: set[str] = set()
    in_block: str | None = None
    block_buffer: list[str] = []
    block_kept_any = False

    def flush_block() -> None:
        nonlocal in_block, block_buffer, block_kept_any
        if block_kept_any:
            out.extend(block_buffer)
        else:
            stats["removed_lines"] += len(block_buffer)
        in_block, block_buffer, block_kept_any = None, [], False

    for line in lines:
        if in_block is not None:
            stripped = line.strip()
            if stripped == "}":
                block_buffer.append(line)
                flush_block()
                continue
            if BLOCK_OWNED_LINE.match(line) or not stripped:
                if stripped:
                    stats["removed_lines"] += 1
                continue
            block_buffer.append(line)
            block_kept_any = True
            continue
        if THEME.match(line):
            stats["removed_lines"] += 1
            continue
        if INCLUDE.match(line):
            key = line.strip()
            if key in seen_includes:
                stats["removed_lines"] += 1
                continue
            seen_includes.add(key)
            out.append(line)
            continue
        if OWNED_SINGLE.match(line):
            stats["removed_lines"] += 1
            continue
        opened = BLOCK_OPEN.match(line)
        if opened and opened.group(2) is None:
            in_block = opened.group(1)
            block_buffer = [line]
            block_kept_any = False
            continue
        out.append(line)
    if in_block is not None:
        out.extend(block_buffer)

    body = "\n".join(out)
    mapping, notes = build_color_map(body)
    stats["notes"] = notes

    def sub_line_ctx(match: re.Match) -> str:
        tok = _line_token(mapping[match.group(2)[1:].upper()])
        stats["hex_replaced"] += 1
        return match.group(1) + tok + (match.group(3) if match.lastindex and match.lastindex >= 3 else "")

    body = ARROW_COLOR.sub(lambda m: sub_line_ctx(m), body)
    body = INLINE_COLOR.sub(lambda m: sub_line_ctx(m), body)

    def sub_fill(match: re.Match) -> str:
        stats["hex_replaced"] += 1
        return mapping[match.group(1).upper()]

    body = HEX.sub(sub_fill, body)
    # An alias that landed on a tint but is used to colour an edge gets the matching stroke token
    # at the edge; the alias itself keeps the fill token for the elements that use it.
    alias_tokens = {m.group(1): m.group(2) for m in re.finditer(r"^\s*!define\s+(\w+)\s+(\$(?:fill|deep)_\w+|\$theme_surface(?:_2)?)\s*$", body, re.M)}
    for alias, tok in alias_tokens.items():
        body = re.sub(rf"(-\[){re.escape(alias)}\b", lambda m, t=_line_token(tok): m.group(1) + t, body)
        body = re.sub(rf"(<color:){re.escape(alias)}(>)", lambda m, t=_line_token(tok): m.group(1) + t + m.group(2), body)
    body = TEXT_SUFFIX.sub(";text:$theme_on_dark", body)
    body = INLINE_WHITE.sub("<color:$theme_on_dark>", body)
    # White text was chosen for a dark fill: keep the dark stroke tone rather than the clamped tint.
    body = re.sub(r"\$(?:deep|fill)_(\w+);text:\$theme_on_dark", r"$line_\1;text:$theme_on_dark", body)
    # `A -down-> B : "label" #hex` never coloured the edge: PlantUML appended the hex to the label
    # (rendered as a diamond glyph plus the digits). Move the colour into the arrow where it belongs.
    body = re.sub(
        r'^(\s*\S+\s+)(<?-+)([a-z]*)(-*>?)(\s+\S+\s*:\s*"[^"]*")\s+\$(?:line|deep|fill)_(\w+)\s*$',
        lambda m: f"{m.group(1)}{m.group(2)[:1]}[$line_{m.group(6)}]{m.group(2)[1:]}{m.group(3)}{m.group(4)}{m.group(5)}",
        body,
        flags=re.M,
    )
    # A container (line ending in `{`) filled with a solid stroke colour becomes a dark slab around its
    # children; keep containers at the deep tint of the same role with ordinary ink text.
    body = re.sub(
        r"^(\s*(?:rectangle|package|frame|node|folder|cloud|card)\b[^\n]*?)\$line_(\w+)(;text:\$theme_on_dark)?(\s*\{\s*)$",
        lambda m: m.group(1) + ("$deep_primary" if m.group(2) == "secondary" else f"$deep_{m.group(2)}") + m.group(4),
        body,
        flags=re.M,
    )
    # Collapse the blank-line runs left behind by removed skinparam lines.
    body = re.sub(r"\n{3,}", "\n\n", body)
    if text.endswith("\n") and not body.endswith("\n"):
        body += "\n"
    return body, stats


def migrate_file(path: Path, *, check: bool) -> dict:
    original = path.read_text(encoding="utf-8", errors="replace")
    if not STARTUML.search(original):
        return {"path": str(path.relative_to(ROOT)), "skipped": "not renderable"}
    migrated, stats = migrate_text(original)
    changed = migrated != original
    if changed and not check:
        path.write_text(migrated, encoding="utf-8")
    remaining_hex = len(HEX.findall(migrated))
    return {
        "path": str(path.relative_to(ROOT)),
        "changed": changed,
        "removed_lines": stats["removed_lines"],
        "hex_replaced": stats["hex_replaced"],
        "remaining_hex": remaining_hex,
        "collision_notes": stats["notes"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="report without writing")
    parser.add_argument("--report", type=Path, default=None, help="write a JSON report here")
    parser.add_argument("paths", nargs="*", type=Path, help="files or directories (default: src/)")
    args = parser.parse_args(argv)
    targets: list[Path] = []
    for given in args.paths or [SRC]:
        given = given if given.is_absolute() else ROOT / given
        targets += sorted(given.rglob("*.puml")) if given.is_dir() else [given]
    results = [migrate_file(path, check=args.check) for path in targets]
    changed = [r for r in results if r.get("changed")]
    collisions = [r for r in results if any("COLLIDES" in n for n in r.get("collision_notes", []))]
    summary = {
        "files": len(results),
        "changed": len(changed),
        "removed_lines": sum(r.get("removed_lines", 0) for r in results),
        "hex_replaced": sum(r.get("hex_replaced", 0) for r in results),
        "remaining_hex": sum(r.get("remaining_hex", 0) for r in results),
        "unresolved_collisions": len(collisions),
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps({"summary": summary, "files": results}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary), file=sys.stderr)
    for r in collisions:
        for note in r["collision_notes"]:
            if "COLLIDES" in note:
                print(f"{r['path']}: {note}", file=sys.stderr)
    return 1 if (args.check and changed) else 0


if __name__ == "__main__":
    raise SystemExit(main())
