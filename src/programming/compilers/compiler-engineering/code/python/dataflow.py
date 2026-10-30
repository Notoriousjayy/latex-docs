"""Finite-set liveness solver. All block uses are upward-exposed by contract."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Block:
    name: str
    successors: tuple[str, ...]
    uses: frozenset[str]
    defs: frozenset[str]

def liveness(blocks: list[Block]):
    by_name={b.name:b for b in blocks}
    if len(by_name)!=len(blocks):raise ValueError('duplicate block')
    if not blocks: return {},{},0
    for b in blocks:
        if any(s not in by_name for s in b.successors):
            raise ValueError(f'unknown successor for {b.name}')
    live_in={b.name:set() for b in blocks}
    live_out={b.name:set() for b in blocks}
    changed=True;iterations=0
    while changed:
        changed=False
        iterations+=1
        for b in reversed(blocks):
            out=set().union(*(live_in[s] for s in b.successors))
            inn=set(b.uses)|(out-set(b.defs))
            if live_out[b.name]!=out or live_in[b.name]!=inn:
                live_out[b.name]=out
                live_in[b.name]=inn
                changed=True
    return live_in,live_out,iterations
