"""Run locally from any directory to audit delivered source organization and form pairs."""
from pathlib import Path
import json, re, sys
root=Path(__file__).resolve().parents[1]
pairs=json.loads((root/'PAIR_REGISTER.json').read_text())['pairs']
issues=[]
for item in pairs:
    tmpl=root/'templates'/(item['family']+'-template.tex')
    blank=root/'blank-forms'/(item['family']+'-blank.tex')
    if not tmpl.exists() or not blank.exists():
        issues.append('missing '+item['family']);continue
    text=blank.read_text()
    body=text.split(r'\begin{document}',1)[-1]
    if re.search(r'(?<!\\)\[[^\]]+\]',body):
        issues.append('bracketed fill text '+blank.name)
    if 'Example (' in body or 'Authoring prompt' in body or 'To complete' in body:
        issues.append('example or prompt in blank '+blank.name)
    heads=lambda p: re.findall(r'\\section\{([^}]+)\}',p.read_text())
    if heads(tmpl)!=heads(blank):issues.append('headings mismatch '+item['family'])
for p in root.rglob('*.tex'):
    if not re.search(r'\\documentclass(?:\[.*?\])?\{article\}',p.read_text()): issues.append('missing root '+str(p))
for p in root.rglob('*'):
    if p.is_dir() and p != root and not any(part in {'__pycache__','.pytest_cache','.mypy_cache','.venv','out','build','target'} for part in p.relative_to(root).parts) and not (p/'README.md').exists():issues.append('missing leaf readme '+str(p.relative_to(root)))
if issues:
    print('SUITE CHECK FAILED:\n'+'\n'.join(issues));sys.exit(1)
print(f'SUITE CHECK OK: {len(list(root.rglob("*.tex")))} compilable LaTeX roots, {len(pairs)} complete Template-Blank pairs.')
