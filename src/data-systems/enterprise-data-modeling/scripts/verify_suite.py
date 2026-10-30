#!/usr/bin/env python3
"""Validate the enterprise modeling suite's local structural contracts."""
from pathlib import Path
import re, sys
suite=Path(__file__).resolve().parents[1]
problems=[]
for d in ('curriculum','study-guides','references','laboratories','laboratories/sql',
          'laboratories/diagrams','workbooks','case-studies','governance','scorecards','templates'):
    if not (suite/d/'README.md').exists():problems.append('Missing leaf README: '+d)
roots=list(suite.rglob('*.tex'))
for p in roots:
    data=p.read_text(encoding='utf8')
    if '\\documentclass' not in data or '\\end{document}' not in data:
        problems.append('Incomplete LaTeX root: '+str(p.relative_to(suite)))
    if p.name.endswith('-template.tex') and not p.with_name(p.name.replace('-template.tex','-blank.tex')).exists():
        problems.append('Unpaired template: '+p.name)
    if p.name.endswith('-blank.tex'):
        body=data.split('\\begin{document}',1)[-1]
        if re.search(r'\[(?:to complete|todo|insert|enter|example|placeholder|tbd)[^]]*\]',body,re.I):
            problems.append('Bracketed completion token in Blank: '+p.name)
        if 'Author guidance:' in body or 'Example response:' in body:
            problems.append('Template instructions leaked into Blank: '+p.name)
for p in (suite/'templates').glob('*-blank.tex'):
    if not p.with_name(p.name.replace('-blank.tex','-template.tex')).exists():
        problems.append('Orphan Blank: '+p.name)
chapters=sorted((suite/'study-guides').glob('chapter-*.tex'))
if len(chapters)!=10:problems.append(f'Expected 10 chapter guides, found {len(chapters)}')
for filename in ('01-party-and-agreements.sql','02-manufacturing-bom.sql',
                 '03-marketplace-checkout.sql','04-financial-double-entry.sql',
                 '05-expand-contract-migration.sql','06-smoke-and-negative-tests.sql'):
    if not (suite/'laboratories'/'sql'/filename).exists():problems.append('SQL missing: '+filename)
if problems:
    print('FAIL\n'+'\n'.join(' - '+x for x in problems));sys.exit(1)
print('PASS | LaTeX roots:',len(roots),'| Chapter guides:',len(chapters),
      '| Blank companions:',len(list(suite.rglob('*-blank.tex'))))
