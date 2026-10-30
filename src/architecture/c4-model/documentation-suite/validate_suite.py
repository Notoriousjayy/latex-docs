#!/usr/bin/env python3
"""Validate suite files and Template-Blank lifecycle; optionally compile LaTeX."""
from pathlib import Path
import argparse, subprocess, tempfile, re, sys
base=Path(__file__).resolve().parent
p=argparse.ArgumentParser(); p.add_argument('--compile',action='store_true'); args=p.parse_args()
errors=[]
for area in ['templates','workbooks','scorecards']:
    folder=base/area
    stems={x.name.rsplit('-',1)[0] for x in folder.glob('*-template.tex')}
    blanks={x.name.rsplit('-',1)[0] for x in folder.glob('*-blank.tex')}
    if area=='templates':
        blanks={x.name.rsplit('-',1)[0] for x in (base/'blanks').glob('*-blank.tex')}
    for missing in sorted(stems-blanks):errors.append(f'Missing blank {area}/{missing}')
    for missing in sorted(blanks-stems):errors.append(f'Missing template {area}/{missing}')
    blankdir=base/'blanks' if area=='templates' else folder
    for file in blankdir.glob('*-blank.tex'):
        raw=file.read_text(encoding='utf-8')
        if re.search(r'\[(?:To complete|Enter|Describe|Example|Insert|Fill)\b',raw,re.I):errors.append(f'Bracketed visible placeholder: {file}')
for folder in [base]+[x for x in base.iterdir() if x.is_dir() and x.name!='build']:
    if not (folder/'README.md').exists():errors.append(f'Missing README: {folder}')
for file in base.rglob('*.tex'):
    raw=file.read_text(encoding='utf-8')
    if r'\documentclass' not in raw or r'\end{document}' not in raw:errors.append(f'Non-root TeX: {file}')
if args.compile:
    pdfs=base/'build'; pdfs.mkdir(exist_ok=True)
    for source in sorted(base.rglob('*.tex')):
        if 'build' in source.parts:continue
        with tempfile.TemporaryDirectory() as td:
            c=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory',td,source.name],cwd=source.parent,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=45,text=True)
            if c.returncode:errors.append('Compilation failed: '+str(source.relative_to(base))+'\n'+c.stdout[-1000:])
            else:
                pdf=Path(td)/(source.stem+'.pdf')
                if pdf.exists():
                    dest=pdfs/(source.parent.name+'-'+pdf.name)
                    dest.write_bytes(pdf.read_bytes())
print(f'Validation: {sum(1 for _ in base.rglob("*.tex"))} LaTeX roots, {sum(1 for _ in (base/"examples").glob("*.puml"))} PlantUML examples')
if errors:
    for err in errors:print('ERROR:',err)
    sys.exit(1)
print('PASS: structure, pairing, blank placeholder rules'+(' and PDF compilation' if args.compile else ''))
