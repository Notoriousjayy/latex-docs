"""Restricted arithmetic expression lexer, Pratt parser and evaluator; no eval/exec.

Teaching demo only: integers, + - * /, parentheses and unary minus.
"""
from __future__ import annotations
from dataclasses import dataclass

class ParseError(ValueError):
    pass

@dataclass(frozen=True)
class Token:
    kind: str
    text: str
    offset: int

@dataclass(frozen=True)
class Node:
    kind: str
    value: object
    left: 'Node | None' = None
    right: 'Node | None' = None


def lex(source: str, *, max_chars=10_000, max_tokens=4_000) -> list[Token]:
    if len(source) > max_chars: raise ParseError("input limit exceeded")
    out: list[Token] = []
    i = 0
    while i < len(source):
        ch = source[i]
        if ch in ' \t\r\n':
            i += 1; continue
        if '0' <= ch <= '9':
            j = i + 1
            while j < len(source) and '0' <= source[j] <= '9': j += 1
            if j - i > 19: raise ParseError("integer literal too large")
            out.append(Token('INT', source[i:j], i)); i = j
        elif ch in '+-*/()':
            out.append(Token(ch, ch, i)); i += 1
        else:
            raise ParseError(f"unrecognized character at offset {i}")
        if len(out) > max_tokens: raise ParseError("token limit exceeded")
    out.append(Token('EOF','',len(source)))
    return out


def parse(source: str, *, max_depth=128, max_nodes=4_000) -> Node:
    toks = lex(source)
    pos = 0
    nodes = 0
    def node(kind, value, left=None, right=None):
        nonlocal nodes
        nodes += 1
        if nodes > max_nodes: raise ParseError("AST node limit exceeded")
        return Node(kind, value, left, right)
    def expression(min_bp=0, depth=0):
        nonlocal pos
        if depth >= max_depth: raise ParseError("nesting limit exceeded")
        token = toks[pos]; pos += 1
        if token.kind == 'INT':
            lhs = node('int', int(token.text))
        elif token.kind == '-':
            lhs = node('neg', '-', expression(5, depth + 1))
        elif token.kind == '(':
            lhs = expression(0, depth + 1)
            if toks[pos].kind != ')': raise ParseError(f"expected ')' at {toks[pos].offset}")
            pos += 1
        else:
            raise ParseError(f"expected atom at {token.offset}")
        while True:
            op = toks[pos].kind
            if op not in ('+', '-', '*', '/'): break
            left_bp, right_bp = (1,2) if op in ('+','-') else (3,4)
            if left_bp < min_bp: break
            pos += 1
            rhs = expression(right_bp, depth + 1)
            lhs = node('binop',op,lhs,rhs)
        return lhs
    result = expression()
    if toks[pos].kind != 'EOF':
        raise ParseError(f"trailing input at {toks[pos].offset}")
    return result


def evaluate(node: Node, *, max_magnitude=10**12) -> int:
    def rec(n: Node, depth=0):
        if depth > 256: raise ParseError("evaluation depth limit")
        if n.kind == 'int': value = n.value
        elif n.kind == 'neg': value = -rec(n.left, depth + 1)
        elif n.kind == 'binop':
            a = rec(n.left, depth + 1); b = rec(n.right, depth + 1)
            if n.value == '+': value = a+b
            elif n.value == '-': value = a-b
            elif n.value == '*': value = a*b
            else:
                if b == 0: raise ParseError("division by zero")
                if a % b: raise ParseError("division must be exact")
                value = a//b
        else: raise ParseError("invalid AST node")
        if abs(value) > max_magnitude: raise ParseError("integer magnitude limit")
        return value
    return rec(node)
