#!/usr/bin/env python3
"""Fast source-level package self-check; does not replace PDF rendering or CI."""
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
chapters=json.loads((ROOT/'chapter-index.json').read_text())['chapters']
pairs=json.loads((ROOT/'PAIR_REGISTER.json').read_text())
errors=[]
tex=list(ROOT.rglob('*.tex'))
if len(chapters)!=82 or set(x['number'] for x in chapters)!=set(range(1,83)):
    errors.append('invalid original TOC chapter coverage')
for x in chapters:
    found=list((ROOT/'study-guides').glob(f"chapter-{x['number']:02d}-*.tex"))
    if len(found)!=1: errors.append(f"guide for chapter {x['number']} has {len(found)} files")
if len(pairs)!=14: errors.append('unexpected registered pair count')
for pair in pairs:
    for kind in ('template','blank'):
        p=ROOT/pair[kind]
        if not p.exists(): errors.append(f'missing {p}')
    if (ROOT/pair['blank']).exists():
        source=(ROOT/pair['blank']).read_text()
        body=source.split(r'\begin{document}',1)[-1]
        if re.search(r'\[(?:To complete|TODO|Insert|Example|TBD|Fill in)[^\]]*\]',body,re.I):
            errors.append(f'bracketed response prompt in {pair["blank"]}')
        if not any(x in body for x in (r'\hrulefill',r'\rule')):
            errors.append(f'blank has no response area: {pair["blank"]}')
for p in tex:
    s=p.read_text()
    if s.count(r'\begin{document}')!=1 or s.count(r'\end{document}')!=1:
        errors.append(f'not standalone: {p}')
    if r'\setDocTitle{' not in s or r'\usepackage{technical-' not in s:
        errors.append(f'house style missing: {p}')
    if r'\n\section' in s or r'\n\rule' in s:
        errors.append(f'literal escaped newline: {p}')
for kind in ('README.md','SOURCE_PROVENANCE.md','code/python/test_animation.py',
             'code/cpp/CMakeLists.txt'):
    if not (ROOT/kind).exists(): errors.append(f'missing {kind}')
print(f"Chapter guides: {len(chapters)} | LaTeX roots: {len(tex)} | Pairs: {len(pairs)}")
if errors:
    print('\n'.join('ERROR '+e for e in errors));sys.exit(1)
print('PASS: package source and pair validation (not a full typeset or PDF audit)')
