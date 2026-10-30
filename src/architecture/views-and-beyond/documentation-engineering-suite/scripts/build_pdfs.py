#!/usr/bin/env python3
"""Parallel, isolated PDF builds; source remains untouched."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess
import os
import sys
root = Path(__file__).resolve().parents[1]
base = root
outroot = root / 'build'
files = [p for p in sorted(base.rglob('*.tex')) if p.parent.name != 'shared']

def run(src):
    outdir = outroot / src.stem
    outdir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(['pdflatex', '-halt-on-error', '-interaction=batchmode',
        f'-output-directory={outdir}', src.name], cwd=src.parent, capture_output=True, timeout=90)
    success = result.returncode == 0 and (outdir / f'{src.stem}.pdf').exists()
    log = outdir / f'{src.stem}.log'
    detail = log.read_text(errors='replace')[-1400:] if log.exists() else result.stdout.decode(errors='replace')[-1400:]
    return src.name, success, detail
with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 2)) as ex:
    results = list(ex.map(run, files))
failures = [(name, tail) for name, passed, tail in results if not passed]
print(f'Compiled {len(results) - len(failures)} / {len(results)} PDFs into {outroot}')
for name, tail in failures:
    print(f'ERROR: {name}\n{tail}\n')
sys.exit(1 if failures else 0)
