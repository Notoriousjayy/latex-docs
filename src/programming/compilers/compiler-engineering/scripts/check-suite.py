"""Source-only suite consistency check; does not replace LaTeX compilation."""
from pathlib import Path
import re,sys
root=Path(__file__).resolve().parents[1]
files=list(root.rglob('*.tex'))
standalone=[f for f in files if f.parent.name!='shared']
assert len(standalone)>=40, len(standalone)
assert len(list((root/'study-guides').glob('chapter-*.tex')))==14
for f in standalone:
    s=f.read_text()
    assert '\\begin{document}' in s and '\\end{document}' in s,f
    assert '\\input{../shared/compiler-suite-style.tex}' in s,f
    assert s.count('\\begin{')==s.count('\\end{'),f
for f in (root/'templates').glob('*-template.tex'):
    peer=root/'blank'/f.name.replace('-template.tex','-blank.tex')
    assert peer.exists(),f
for f in (root/'workbooks').glob('*-template.tex'):
    peer=root/'blank'/f.name.replace('-template.tex','-blank.tex')
    assert peer.exists(),f
for f in (root/'blank').glob('*.tex'):
    s=f.read_text()
    assert 'Completion guidance:' not in s and 'Instruction:' not in s,f
    assert not re.search(r'\[[A-Za-z][^\]]{0,70}\]',s),f
print(f'PASS: {len(standalone)} standalone LaTeX sources, 14 chapter guides, all forms paired')
