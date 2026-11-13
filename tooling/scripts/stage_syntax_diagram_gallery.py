#!/usr/bin/env python3
"""Stage native PlantUML railroad PNGs as a static GitHub Pages gallery.

The existing latex-pages.yml job calls this *after* stage-pages has copied the
verified PDF and raster corpora. No React, npm, or independent Pages publisher.
"""
from __future__ import annotations

import argparse
import html
from pathlib import Path

LANGUAGES = (
    ("ecmascript-2025", "ECMAScript 2025", 261),
    ("cpp23", "C++23", 351),
    ("c23", "C23", 96),
    ("java-25", "Java 25", 253),
    ("python-314", "Python 3.14", 205),
)

REPO_ASSET_PATH = Path(
    "src/programming/languages/syntax-diagrams/railroad-samples/png"
)
HOME_NAV_MARKER = '</nav></section><section class="library" aria-label="Published documents">'


def stage_gallery(site: Path) -> Path:
    """Only reference PNG files present in the verified staged raster corpus."""
    site = site.resolve()
    home = site / "index.html"
    if not home.is_file():
        raise FileNotFoundError("Stage the existing documentation site before the PNG gallery")
    fragments: list[str] = []
    missing: list[str] = []
    for slug, title, rules in LANGUAGES:
        asset = site / "images" / REPO_ASSET_PATH / (slug + ".png")
        if not asset.is_file() or asset.stat().st_size == 0:
            missing.append(str(asset))
            continue
        with asset.open("rb") as handle:
            if handle.read(8) != b"\x89PNG\r\n\x1a\n":
                raise ValueError("Invalid PNG diagram: " + str(asset))
        url = "../images/" + (REPO_ASSET_PATH / (slug + ".png")).as_posix()
        safe_title = html.escape(title, quote=True)
        safe_url = html.escape(url, quote=True)
        fragments.append(
            f'<article class="diagram-card" id="{html.escape(slug, quote=True)}">'
            f'<header><h2>{safe_title}</h2><p>{rules} preserved textual productions</p></header>'
            f'<a href="{safe_url}" aria-label="View full-size {safe_title} PNG">'
            f'<img src="{safe_url}" alt="PlantUML railroad diagram illustrating {safe_title} grammar" loading="lazy"></a>'
            f'<p class="small">Illustrative grammar rule. The complete grammar text is in the printable LaTeX collection.</p>'
            "</article>"
        )
    if missing:
        raise FileNotFoundError(
            "Native railroad PNG assets missing from the staged raster corpus: "
            + ", ".join(missing)
            + ". Ensure the existing pinned PlantUML render job runs before Pages staging."
        )

    gallery = site / "syntax-diagrams"
    gallery.mkdir(parents=True, exist_ok=True)
    content = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>Programming Language Syntax Diagrams — Documentation Library</title>
<style>
:root{color-scheme:light dark;font-family:system-ui,-apple-system,Segoe UI,sans-serif;line-height:1.55}
body{margin:0;background:Canvas;color:CanvasText}
main{max-width:1140px;padding:2rem 1.25rem 4rem;margin:auto}
h1{font-size:clamp(1.8rem,4vw,3rem);line-height:1.2}
a{color:LinkText}
.intro{max-width:78ch}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,330px),1fr));gap:1.25rem;margin-top:2rem}
.diagram-card{border:1px solid GrayText;border-radius:10px;padding:1.2rem;min-width:0}
.diagram-card h2{margin:0;font-size:1.35rem}
.diagram-card header p,.small{font-size:.9rem;opacity:.85}
.diagram-card img{display:block;width:100%;height:auto;max-height:360px;object-fit:contain;background:#fff;border-radius:6px}
footer{border-top:1px solid GrayText;margin-top:2.5rem;padding-top:1rem}
</style>
</head>
<body>
<main>
<p><a href="../">Documentation library</a> / Programming language grammars</p>
<h1>Programming Language Railroad Diagrams</h1>
<p class="intro">Illustrative diagrams rendered as <strong>PNG images</strong> using the same pinned PlantUML renderer as the repository's existing diagrams. The LaTeX technical references preserve all 1,166 textual grammar productions across five language versions. This gallery does not claim a rendered image for every production.</p>
<div class="grid">
""" + "\n".join(fragments) + """
</div>
<footer>Static HTML and PNG images. No React application, npm build, or additional deployment pipeline.</footer>
</main>
</body>
</html>
"""
    target = gallery / "index.html"
    target.write_text(content, encoding="utf-8")
    homepage = home.read_text(encoding="utf-8")
    if HOME_NAV_MARKER not in homepage:
        raise ValueError("Existing Pages index navigation contract changed")
    homepage = homepage.replace(
        HOME_NAV_MARKER,
        '<a href="syntax-diagrams/">Programming Syntax Diagrams (PNG)</a>'
        + HOME_NAV_MARKER,
        1,
    )
    home.write_text(homepage, encoding="utf-8")
    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-dir", type=Path, required=True)
    args = parser.parse_args()
    print("Staged native PNG grammar gallery:", stage_gallery(args.site_dir))


if __name__ == "__main__":
    main()
