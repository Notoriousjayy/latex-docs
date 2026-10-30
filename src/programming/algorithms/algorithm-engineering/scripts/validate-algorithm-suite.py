#!/usr/bin/env python3
"""Dependency-free static checks for the LaTeX documentation suite."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
source = root
tex = sorted(source.rglob('*.tex'))
standalone = [p for p in tex if p.parent.name != 'shared']
errors: list[str] = []
if len(standalone) != 33:
    errors.append(f'Expected 33 standalone files; found {len(standalone)}')
if len([p for p in tex if p.parent.name == 'shared']) != 1:
    errors.append('Expected exactly one shared LaTeX style file')
for p in standalone:
    body = p.read_bytes()
    bad = sorted({f'0x{b:02x}' for b in body if b < 32 and b not in (9, 10, 13)})
    if bad:
        errors.append(f'{p}: unexpected control characters {bad}')
    text = body.decode('utf8')
    for required in [r'\documentclass', r'\input{../shared/algorithm-style.tex}', r'\DocTitle', r'\end{document}']:
        if required not in text:
            errors.append(f'{p}: missing {required}')
    if p.parent.name == 'blank':
        for placeholder in ['[To complete]', '[TODO]', '[Enter', '[Insert', '[Fill in', '[Your ']:
            if placeholder.lower() in text.lower():
                errors.append(f'{p}: bracketed placeholder {placeholder}')
        if r'\AnswerLines' not in text and r'\FormField' not in text:
            errors.append(f'{p}: blank form has no writing areas')
for p in (source/'templates').glob('*-template.tex'):
    partner = source/'blank'/(p.name.replace('-template.tex','-blank.tex'))
    if not partner.exists():
        errors.append(f'Missing blank companion for {p.name}')
for p in (source/'workbooks').glob('*.tex'):
    partner = source/'blank'/(p.stem + '-blank.tex')
    if not partner.exists():
        errors.append(f'Missing workbook blank for {p.name}')
lines = (root / 'MANIFEST.txt').read_text().splitlines()
found = [str(p.relative_to(root)) for p in tex]
if sorted(lines) != sorted(found):
    errors.append('MANIFEST.txt does not match generated source files')

print(f'Validated {len(standalone)} standalone documents, {len(tex)} .tex files overall.')
if errors:
    for error in errors:
        print('ERROR:', error, file=sys.stderr)
    sys.exit(1)
print('Template/blank pairs, workbook companions, source inventory and basic source hygiene passed.')
