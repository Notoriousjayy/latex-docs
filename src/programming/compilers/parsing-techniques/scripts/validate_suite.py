"""Verify suite structure, standalone LaTeX roots and printable blank form contract."""
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=['technical-references','study-guides','curricula','laboratories','workbooks','procedures','templates','blank','assessments','shared','code/python','code/cpp','code/cpp/tests','scripts','integration']
errors=[]
for d in REQUIRED:
    if not (ROOT/d/'README.md').is_file(): errors.append('missing leaf README '+d)
chapters=list((ROOT/'study-guides').glob('*.tex'))
if len(chapters)!=18:errors.append('expected 18 study guides, found '+str(len(chapters)))
forms=list((ROOT/'templates').glob('*-template.tex'))+list((ROOT/'workbooks').glob('*-template.tex'))
for p in forms:
    blank=ROOT/'blank'/p.name.replace('-template.tex','-blank.tex')
    if not blank.exists():errors.append('missing blank '+str(blank))
for p in (ROOT/'blank').glob('*.tex'):
    s=p.read_text()
    rendered_text=s.split(r'\begin{document}',1)[-1]
    if re.search(r'\[(To complete|TODO|Insert|Example|Enter|TBD)[^]]*\]',rendered_text,re.I):
        errors.append('printed bracketed placeholder '+str(p))
    if r'\PTLines' not in s: errors.append('no handwriting area '+str(p))
for p in ROOT.rglob('*.tex'):
    if p.parent.name=='shared': continue
    s=p.read_text()
    if not s.startswith(r'\documentclass'):errors.append('not standalone '+str(p))
    if s.count(r'\usepackage{technical-')!=1:errors.append('wrong semantic module '+str(p))
    if '\\n\\setDoc' in s:errors.append('literal newline bug '+str(p))
print('chapters:',len(chapters),'template pairs:',len(forms),'TeX roots:',len(list(ROOT.rglob('*.tex')))-1)
if errors:
    print('\n'.join(errors));sys.exit(1)
print('Suite structure and template/blank pairs validated')
