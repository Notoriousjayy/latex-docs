#!/usr/bin/env python3
"""Publish a complete, searchable PNG grammar gallery in the existing Pages site.

All image paths are checked against the verified staged raster corpus. This
never copies or generates a React application. The complete grammar definition
is displayed beside each factory-derived or explicitly schematic PNG.
"""
from __future__ import annotations

import argparse
import html
from pathlib import Path
from urllib.parse import quote

import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.scripts.generate_railroad_ebnf import (
    COLLECTION, LANGUAGES, rule_path, source_data, grammar_parts, build_rule,
)

IMAGE_ROOT = Path("src/programming/languages/syntax-diagrams/railroad-generated")
HOME_NAV_MARKER = '</nav></section><section class="library" aria-label="Published documents">'
EXPECTED_TOTAL = 1166


def asset_path(language: str, index: int, rule: str) -> Path:
    original = rule_path(language, index, rule)
    return IMAGE_ROOT / original.parent / "png" / (original.stem + ".png")


def template(title: str, body: str, extra_script: str = "") -> str:
    return """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>""" + html.escape(title) + """ - Documentation Library</title>
<style>
:root { color-scheme: light dark; font-family: system-ui,-apple-system,Segoe UI,sans-serif; line-height:1.55 }
body { margin:0; background:Canvas; color:CanvasText }
main { max-width:1100px; padding:2rem 1rem 4rem; margin:0 auto }
a { color:LinkText }
h1 { font-size:clamp(1.8rem,4vw,2.9rem);line-height:1.2 }
h2 { font-size:1.45rem }
p { max-width:90ch }
.summary { color:GrayText }
.stats { display:flex;flex-wrap:wrap;gap:1rem }
.pill { border:1px solid GrayText;border-radius:8px;padding:.45rem .8rem }
.grid { display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:1rem;margin-top:2rem }
.card { border:1px solid GrayText;border-radius:10px;padding:1rem;min-width:0 }
.card h2 { margin:.2rem 0 }
.card img { display:block;width:100%;height:auto;max-height:300px;object-fit:contain;background:#fff;border-radius:5px }
.card p { font-size:.92rem }
.search { width:100%;box-sizing:border-box;font:inherit;padding:.75rem;border:1px solid GrayText;border-radius:6px;background:Canvas;color:CanvasText }
.rule { margin:1.2rem 0;padding:1rem;border:1px solid GrayText;border-radius:8px;scroll-margin-top:1rem }
.rule h3 { margin:0 0 .4rem;overflow-wrap:anywhere }
.rule img { display:block;max-width:100%;height:auto;background:white;border:1px solid #bbb;padding:.5rem;border-radius:5px }
.rule a { display:inline-block;margin:.5rem 0 }
.rule pre { overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere;padding:1rem;border:1px solid GrayText;border-radius:6px }
.notice { border-left:4px solid #987b29;padding:.5rem 1rem }
.sections { margin:1.5rem 0;display:flex;flex-wrap:wrap;gap:.6rem }
.sections a { border:1px solid GrayText;padding:.25rem .65rem;border-radius:999px }
section.grammar-section { margin-top:2rem }
section.grammar-section > h2 { padding-bottom:.5rem;border-bottom:1px solid GrayText }
[hidden] { display:none !important }
footer { margin-top:3rem;border-top:1px solid GrayText;padding-top:1rem;font-size:.9rem }
</style>
</head><body><main>""" + body + """<footer>
<a href="../">Documentation home</a> ·
<a href="./">All syntax languages</a> ·
<a href="https://github.com/Notoriousjayy/latex-docs/tree/main/src/programming/languages/syntax-diagrams">LaTeX source collection</a>
</footer></main>
""" + extra_script + "</body></html>\n"


SEARCH_SCRIPT = """
<script>
(function() {
 const input = document.getElementById('rule-search');
 const counter = document.getElementById('match-count');
 if (!input) return;
 const rules = Array.from(document.querySelectorAll('[data-rule]'));
 const sections = Array.from(document.querySelectorAll('.grammar-section'));
 function filter() {
  const q = input.value.trim().toLocaleLowerCase();
  let count = 0;
  for (const rule of rules) {
   const visible = !q || rule.dataset.rule.includes(q);
   rule.hidden = !visible;
   if (visible) count++;
  }
  for (const section of sections) {
   section.hidden = !section.querySelector('.rule:not([hidden])');
  }
  counter.textContent = String(count) + ' of ' + rules.length + ' rules shown';
 }
 input.addEventListener('input', filter);
 input.addEventListener('keydown', function(event) {
  if (event.key === 'Escape') { input.value = ''; filter(); }
 });
 filter();
}());
</script>
"""


def language_page(site: Path, language: str, title: str) -> tuple[str, int]:
    data = source_data(language)
    module = COLLECTION / "data/upstream" / (language + "-factory-source.txt")
    factories = grammar_parts(module.read_text(encoding="utf-8"))
    if len(factories) != data["sourceFactoryCount"]:
        raise ValueError("Pinned factory count mismatch for " + language)
    name_to_entry = {entry["name"]: entry for entry in data["rules"]}
    index_by_name = {entry["name"]: i for i, entry in enumerate(data["rules"], 1)}
    missing: list[str] = []
    fragments: list[str] = []
    rendered_names: set[str] = set()

    def add_rule(name: str) -> None:
        if name in rendered_names:
            raise ValueError("Duplicate grammar section entry: " + name)
        if name not in name_to_entry:
            raise ValueError("Missing grammar text: " + name)
        entry = name_to_entry[name]
        index = index_by_name[name]
        relative = asset_path(language, index, name)
        asset = site / "images" / relative
        if not asset.is_file() or asset.stat().st_size < 8:
            missing.append(relative.as_posix())
        else:
            with asset.open("rb") as stream:
                if stream.read(8) != b"\x89PNG\r\n\x1a\n":
                    raise ValueError("Invalid PNG diagram: " + relative.as_posix())
        rendered_names.add(name)
        _, mode = build_rule(language, name, factories.get(name))
        safe_name = html.escape(name)
        url = "../images/" + quote(relative.as_posix(), safe="/-._~")
        caption = "Factory-derived diagram" if mode == "factory-derived" else "Text-only schematic (factory not convertible)"
        fragments.append(
            '<article class="rule" id="rule-' + format(index, "04d") +
            '" data-rule="' + html.escape((name + " " + entry["text"]).casefold(), quote=True) + '">'
            + "<h3>" + safe_name + "</h3>"
            + '<p class="summary">' + html.escape(caption) + "</p>"
            + '<a href="' + html.escape(url, quote=True) + '" title="View original PNG">'
            + '<img loading="lazy" src="' + html.escape(url, quote=True)
            + '" alt="' + html.escape(title + " railroad diagram for " + name, quote=True) + '"></a>'
            + "<details><summary>Full textual grammar definition</summary><pre>"
            + html.escape(entry["text"])
            + "</pre></details></article>"
        )

    pieces = []
    sections = data["sections"]
    nav = []
    for sidx, section in enumerate(sections, 1):
        sid = "section-" + format(sidx, "02d")
        nav.append('<a href="#' + sid + '">' + html.escape(section["id"].replace("_", " ").replace("-", " "))
                   + " (" + str(len(section["ruleNames"])) + ")</a>")
        start = len(fragments)
        for name in section["ruleNames"]:
            add_rule(name)
        parts = "".join(fragments[start:])
        pieces.append('<section class="grammar-section" id="' + sid + '"><h2>'
                      + html.escape(section["id"].replace("_", " ").replace("-", " "))
                      + "</h2>" + parts + "</section>")
    extra = [entry["name"] for entry in data["rules"] if entry["name"] not in rendered_names]
    if extra:
        start = len(fragments)
        for name in extra:
            add_rule(name)
        pieces.append('<section class="grammar-section" id="section-extra"><h2>Additional textual productions</h2>'
                      + "".join(fragments[start:]) + "</section>")
        nav.append('<a href="#section-extra">Additional productions (' + str(len(extra)) + ")</a>")
    if missing:
        raise FileNotFoundError(str(len(missing)) + " required grammar PNGs missing for " + language
                                + "; examples: " + ", ".join(missing[:8]))
    if len(rendered_names) != len(data["rules"]):
        raise ValueError("Gallery omitted grammar productions")
    body = (
        '<p><a href="./">All syntax diagrams</a> / ' + html.escape(title) + "</p>"
        + "<h1>" + html.escape(title) + " Grammar Railroad Diagrams</h1>"
        + '<p>All <strong>' + str(len(rendered_names)) + "</strong> imported textual productions are indexed below. "
        + "Each has a PNG rendered by the repository-owned PlantUML pipeline, plus the complete original grammar text.</p>"
        + '<p class="notice">Diagram syntax is a visual interpretation of source railroad factories, not a normative language specification. '
        + "Factory conversion gaps are explicitly marked. PEG ordered choice, contextual rules and semantic restrictions "
        + "must be checked against the language specification.</p>"
        + '<label for="rule-search"><strong>Search rule names or definitions</strong></label>'
        + '<input id="rule-search" class="search" type="search" placeholder="Search productions..." autocomplete="off">'
        + '<p id="match-count" aria-live="polite"></p>'
        + '<nav class="sections" aria-label="Grammar categories">' + "".join(nav) + "</nav>"
        + "".join(pieces)
    )
    return template(title + " grammar", body, SEARCH_SCRIPT), len(rendered_names)


def stage_gallery(site: Path) -> Path:
    site = site.resolve()
    homepage = site / "index.html"
    if not homepage.is_file():
        raise FileNotFoundError("Run the canonical stage-pages command before publishing syntax diagrams")
    index_pieces: list[str] = []
    gallery = site / "syntax-diagrams"
    expected = 0
    # Verify every production and every actual PNG before writing any gallery page.
    generated_pages = {}
    for language, title in LANGUAGES:
        page, count = language_page(site, language, title)
        generated_pages[language + ".html"] = page
        expected += count
        first = source_data(language)["rules"][0]["name"]
        png = asset_path(language, 1, first)
        image_url = "../images/" + quote(png.as_posix(), safe="/-._~")
        index_pieces.append(
            '<article class="card"><h2><a href="' + language + '.html">'
            + html.escape(title) + "</a></h2>"
            + '<p>' + str(count) + " grammar productions</p>"
            + '<a href="' + language + '.html"><img loading="lazy" src="'
            + html.escape(image_url, quote=True) + '" alt="Example '
            + html.escape(title, quote=True) + ' railroad diagram"></a></article>'
        )
    if expected != EXPECTED_TOTAL:
        raise ValueError("Incomplete PNG publication: " + str(expected) + "/" + str(EXPECTED_TOTAL))
    body = (
        '<p><a href="../">Documentation library</a> / Programming grammars</p>'
        + "<h1>Programming Language Railroad Diagrams</h1>"
        + "<p>Explore <strong>1,166 grammar productions</strong> across five language specifications. "
        + "The diagrams are PNG images generated by the repository's pinned PlantUML pipeline. "
        + "The complete textual rules remain available alongside every image.</p>"
        + '<div class="stats"><span class="pill">5 languages</span>'
        + '<span class="pill">1,166 productions</span>'
        + '<span class="pill">Static HTML and PNG</span></div>'
        + '<div class="grid">' + "".join(index_pieces) + "</div>"
        + '<p class="notice">Railroad visualizations are educational companions, not conformance '
        + 'certifications or guarantees that PEG, contextual, and semantic constraints are represented.</p>'
    )
    generated_pages["index.html"] = template("Language grammar diagrams", body)
    original = homepage.read_text(encoding="utf-8")
    if HOME_NAV_MARKER not in original:
        raise ValueError("The canonical Pages home navigation has changed")
    new_home = original.replace(HOME_NAV_MARKER,
                                '<a href="syntax-diagrams/">Programming Syntax Diagrams (PNG)</a>'
                                + HOME_NAV_MARKER, 1)
    gallery.mkdir(parents=True, exist_ok=True)
    for name, content in generated_pages.items():
        (gallery / name).write_text(content, encoding="utf-8")
    homepage.write_text(new_home, encoding="utf-8")
    return gallery / "index.html"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-dir", type=Path, required=True)
    args = parser.parse_args()
    print("Staged all grammar PNGs at", stage_gallery(args.site_dir))


if __name__ == "__main__":
    main()
