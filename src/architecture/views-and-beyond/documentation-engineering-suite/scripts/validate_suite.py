#!/usr/bin/env python3
"""Validate document structure and paired printable blank forms."""
from pathlib import Path
import re
import sys
root = Path(__file__).resolve().parents[1]
base = root
errors = []
for folder in sorted(base.iterdir()):
    if folder.is_dir() and not (folder / 'README.md').is_file():
        errors.append(f'Missing leaf README: {folder}')
for folder, other in [('templates', 'blanks'), ('workbooks', 'workbooks'), ('scorecards', 'scorecards')]:
    for t in (base / folder).glob('*_Template.tex'):
        blank = base / other / t.name.replace('_Template.tex', '_Blank.tex')
        if not blank.is_file():
            errors.append(f'Missing blank counterpart: {t}')
for folder in ['blanks', 'workbooks', 'scorecards']:
    for blank in (base / folder).glob('*_Blank.tex'):
        s = blank.read_text(encoding='utf-8')
        s = s.split(r'\begin{document}', 1)[-1]
        s = '\n'.join(line.split('%', 1)[0] for line in s.splitlines())
        s = re.sub(r'\\(?:[A-Za-z@]+\*?|begin\{[^{}\n]+\})\s*\[[^\]\n]*\]', '', s)
        if re.search(r'(?<!\\)\[[^\]\n]{1,160}\]', s):
            errors.append(f'Bracketed placeholder: {blank}')
        if re.search(r'(?i)\b(to complete|insert here|enter here|tbd|your answer)\b', s):
            errors.append(f'Instructional placeholder: {blank}')
for t in base.rglob('*.tex'):
    if t.parent.name == 'shared': continue
    s = t.read_text(encoding='utf-8')
    if r'\begin{document}' not in s or r'\end{document}' not in s:
        errors.append(f'Missing standalone document wrapper: {t}')
    if r'\input{../shared/architecture-style.tex}' not in s:
        errors.append(f'Missing standard style import: {t}')
count = len([p for p in base.rglob('*.tex') if p.parent.name != 'shared'])
print(f'Validated {count} standalone LaTeX documents, directories and blank-template pairs: {len(errors)} errors.')
for e in errors: print('ERROR:', e)
sys.exit(1 if errors else 0)
