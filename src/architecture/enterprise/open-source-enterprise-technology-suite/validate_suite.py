#!/usr/bin/env python3
"""Validate local cross-domain suite content and optionally compile all TeX roots."""
from pathlib import Path
import argparse,csv,json,re,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parent
PARSER=argparse.ArgumentParser()
PARSER.add_argument('--compile',action='store_true',help='Run pdfLaTeX in isolated temporary directories')
a=PARSER.parse_args()
manifest=json.loads((ROOT/'manifest.json').read_text())
paths=[ROOT/x['path'] for x in manifest['files']]
assert all(p.is_file() for p in paths), 'Missing file from manifest'
texs=sorted(ROOT.rglob('*.tex'))
templates=sorted((ROOT/'templates').glob('*-template.tex'))
blanks=sorted((ROOT/'blanks').glob('*-blank.tex'))
assert len(templates)==len(blanks)==11
for p in templates:
 b=ROOT/'blanks'/(p.name[:-13]+'-blank.tex')
 assert b.is_file(),f'Missing blank pair for {p}'
 assert r'\documentclass' in p.read_text() and r'\documentclass' in b.read_text()
 assert r'\writearea' in b.read_text(), f'Not a printable blank: {b}'
 assert not re.search(r'\[(?:TODO|To complete|Example|Insert|Enter|Sample)',b.read_text(),re.I),f'Filled placeholder in {b}'
for p in texs:
 s=p.read_text()
 assert s.count(r'\begin{document}')==1 and s.count(r'\end{document}')==1,p
 assert 'fontspec' not in s and 'setmainfont' not in s,p
for f in ['tool-capability-register.csv','integration-register.csv','control-matrix.csv','roadmap.csv','source-of-truth-matrix.csv']:
 with (ROOT/'registers'/f).open() as h:
  rows=list(csv.DictReader(h));assert rows and all(all(v for v in r.values()) for r in rows),f
assert len(list(csv.DictReader((ROOT/'registers'/'control-matrix.csv').open())))==20
if a.compile:
 for i,p in enumerate(texs,1):
  with tempfile.TemporaryDirectory() as d:
   cmd=['pdflatex','-halt-on-error','-interaction=nonstopmode','-output-directory',d,str(p)]
   out=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
   if out.returncode:
    print('FAILED:',p.relative_to(ROOT));print(out.stdout[-2500:]);sys.exit(1)
 print(f'PASS: {len(texs)} TeX roots compile')
print(f'PASS: {len(texs)} independent PDFLaTeX documents; {len(templates)} Template/Blank pairs; {len(paths)} registered files')
