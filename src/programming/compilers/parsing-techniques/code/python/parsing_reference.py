"""Teaching recognizers and grammar analysis. Original implementation, Python >=3.10.

Contracts:
- CYK requires nonempty CNF lexical tokens; no epsilon and no unit productions.
- Earley accepts epsilon and left recursion (items deduplicated).
- FIRST/FOLLOW and LL(1) operate on explicit tuple RHS, epsilon = empty tuple.
- Terminal/nonterminal disjointness is enforced.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from typing import Mapping, Sequence

Grammar = dict[str, tuple[tuple[str, ...], ...]]
END = "$"


def validate_grammar(grammar: Mapping[str, Sequence[Sequence[str]]], start: str) -> None:
    if start not in grammar:
        raise ValueError("undefined start symbol")
    if any(not isinstance(a, str) or not a for a in grammar):
        raise ValueError("invalid nonterminal")
    if any(not isinstance(x, str) or not x for rhses in grammar.values() for rhs in rhses for x in rhs):
        raise ValueError("invalid symbol")
    nt = set(grammar)
    terminals = {x for rhses in grammar.values() for rhs in rhses for x in rhs if x not in nt}
    if END in nt | terminals:
        raise ValueError("reserved end symbol")


def cyk_recognize(
    grammar: Mapping[str, Sequence[Sequence[str]]],
    start: str,
    tokens: Sequence[str],
    *,
    max_tokens: int = 256,
    max_cells: int = 65_536,
) -> bool:
    """Strict-CNF membership; nonempty input only; O(|P| n^3) naive bound."""
    validate_grammar(grammar, start)
    nt = set(grammar)
    if any(len(rhs) not in (1, 2) or (len(rhs) == 1 and rhs[0] in nt)
           or (len(rhs) == 2 and (rhs[0] not in nt or rhs[1] not in nt))
           for rhses in grammar.values() for rhs in rhses):
        raise ValueError("grammar must be in strict CNF without epsilon")
    n = len(tokens)
    if n > max_tokens or n * (n + 1) // 2 > max_cells:
        raise ValueError("resource limit exceeded")
    if not n:
        return False
    unary: dict[str, set[str]] = defaultdict(set)
    binary: dict[tuple[str, str], set[str]] = defaultdict(set)
    for lhs, rhses in grammar.items():
        for rhs in rhses:
            if len(rhs) == 1:
                unary[rhs[0]].add(lhs)
            else:
                binary[(rhs[0], rhs[1])].add(lhs)
    chart = [[set() for _ in range(n + 1)] for _ in range(n)]
    for i, token in enumerate(tokens):
        chart[i][i + 1].update(unary.get(token, ()))
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length
            for k in range(i + 1, j):
                for left in chart[i][k]:
                    for right in chart[k][j]:
                        chart[i][j].update(binary.get((left, right), ()))
    return start in chart[0][n]


@dataclass(frozen=True)
class Item:
    lhs: str
    rhs: tuple[str, ...]
    dot: int
    origin: int


def earley_recognize(
    grammar: Mapping[str, Sequence[Sequence[str]]],
    start: str,
    tokens: Sequence[str],
    *,
    max_tokens: int = 256,
    max_items: int = 100_000,
) -> bool:
    """Earley recognizer (not parse forest); nullable and recursion handled."""
    validate_grammar(grammar, start)
    n = len(tokens)
    if n > max_tokens:
        raise ValueError("resource limit exceeded")
    root = start + "'"
    while root in grammar:
        root += "'"
    chart: list[set[Item]] = [set() for _ in range(n + 1)]
    chart[0].add(Item(root, (start,), 0, 0))
    item_count = 1
    for pos in range(n + 1):
        agenda = list(chart[pos])
        ix = 0
        def add(target: int, item: Item) -> None:
            nonlocal item_count
            if item not in chart[target]:
                item_count += 1
                if item_count > max_items:
                    raise ValueError("resource limit exceeded")
                chart[target].add(item)
                if target == pos:
                    agenda.append(item)
        while ix < len(agenda):
            it = agenda[ix]
            ix += 1
            if it.dot == len(it.rhs):
                # completion; works for origin == position as agenda expands
                for waiting in tuple(chart[it.origin]):
                    if waiting.dot < len(waiting.rhs) and waiting.rhs[waiting.dot] == it.lhs:
                        add(pos, Item(waiting.lhs, waiting.rhs, waiting.dot + 1, waiting.origin))
            else:
                sym = it.rhs[it.dot]
                if sym in grammar:
                    for rule in grammar[sym]:
                        add(pos, Item(sym, tuple(rule), 0, pos))
                    # Nullable prediction may have completed before this item
                    # arrived; advance against any already-completed zero-span item.
                    for done in tuple(chart[pos]):
                        if done.lhs == sym and done.dot == len(done.rhs) and done.origin == pos:
                            add(pos, Item(it.lhs, it.rhs, it.dot + 1, it.origin))
                elif pos < n and sym == tokens[pos]:
                    add(pos + 1, Item(it.lhs, it.rhs, it.dot + 1, it.origin))
    return Item(root, (start,), 1, 0) in chart[n]


def grammar_sets(grammar: Mapping[str, Sequence[Sequence[str]]], start: str):
    """Return FIRST, FOLLOW, nullable for explicit symbol sequences."""
    validate_grammar(grammar, start)
    nt = set(grammar)
    first: dict[str, set[str]] = {a: set() for a in nt}
    nullable: set[str] = set()
    changed = True
    while changed:
        changed = False
        for lhs, rhses in grammar.items():
            for rhs in rhses:
                all_nullable = True
                for x in rhs:
                    additions = first[x] if x in nt else {x}
                    old = len(first[lhs]); first[lhs].update(additions)
                    changed |= len(first[lhs]) != old
                    if x not in nullable:
                        all_nullable = False
                        break
                if all_nullable and lhs not in nullable:
                    nullable.add(lhs); changed = True
    follow: dict[str, set[str]] = {a: set() for a in nt}
    follow[start].add(END)
    changed = True
    while changed:
        changed = False
        for lhs, rhses in grammar.items():
            for rhs in rhses:
                trailer = follow[lhs].copy()
                for sym in reversed(rhs):
                    if sym in nt:
                        old = len(follow[sym]); follow[sym].update(trailer)
                        changed |= len(follow[sym]) != old
                        trailer = trailer | first[sym] if sym in nullable else first[sym].copy()
                    else:
                        trailer = {sym}
    return first, follow, nullable


def first_of_sequence(rhs: Sequence[str], first: Mapping[str, set[str]], nullable: set[str]):
    result: set[str] = set()
    for symbol in rhs:
        result.update(first[symbol] if symbol in first else {symbol})
        if symbol not in nullable:
            return result, False
    return result, True


def ll1_table(grammar: Grammar, start: str) -> dict[tuple[str, str], tuple[str, ...]]:
    first, follow, nullable = grammar_sets(grammar, start)
    table: dict[tuple[str, str], tuple[str, ...]] = {}
    for lhs, rhses in grammar.items():
        for rhs in rhses:
            choices, is_nullable = first_of_sequence(rhs, first, nullable)
            if is_nullable:
                choices |= follow[lhs]
            for tok in choices:
                key = (lhs, tok)
                if key in table and table[key] != tuple(rhs):
                    raise ValueError(f"LL(1) conflict at {key}")
                table[key] = tuple(rhs)
    return table


def ll1_recognize(grammar: Grammar, start: str, tokens: Sequence[str], *, max_steps: int=100_000):
    table = ll1_table(grammar, start)
    stack = [END, start]
    stream = list(tokens) + [END]
    cursor = 0
    steps = 0
    while stack:
        steps += 1
        if steps > max_steps:
            raise ValueError("resource limit exceeded")
        top = stack.pop()
        look = stream[cursor]
        if top in grammar:
            rule = table.get((top, look))
            if rule is None:
                return False
            stack.extend(reversed(rule))
        elif top == look:
            cursor += 1
        else:
            return False
    return cursor == len(stream)
