#!/usr/bin/env python3
"""Validate standalone LaTeX roots, chapter coverage, print form pairing and catalog presence."""
import re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
assert len(list((root/'study-guides').glob('*.tex')))==17, 'missing chapter guides'
assert len(list((root/'labs').glob('*.tex')))==11, 'missing labs'
assert len(list((root/'technical-references').glob('*.tex')))==8
for category in ('templates','workbooks','scorecards'):
    templates={p.name.removesuffix('-template.tex') for p in (root/category).glob('*-template.tex')}
    blanks={p.name.removesuffix('-blank.tex') for p in (root/category).glob('*-blank.tex')}
    assert templates==blanks, (category,templates.symmetric_difference(blanks))
    for p in (root/category).glob('*-blank.tex'):
        doc=p.read_text()
        body=doc.split('\\begin{document}',1)[-1]
        assert not any(w in body.casefold() for w in ('[to complete]','[enter','[insert','[example','[your','[tbd]')), p
        assert 'Guidance:' not in body and 'placeholder' not in body.lower(),p
for p in root.rglob('*.tex'):
    source=p.read_text()
    assert '\\documentclass' in source and '\\begin{document}' in source and '\\end{document}' in source,p
for dirname in ('study-guides','curriculum','technical-references','labs','workbooks','templates','scorecards','architecture-specifications','benchmarking','code','code/cpp','code/python','code/python/tests','shared'):
    assert (root/dirname/'README.md').is_file(),dirname
print('Validated',len(list(root.rglob('*.tex'))),'standalone LaTeX files and',sum(1 for p in root.rglob('*.py')),'Python files')
