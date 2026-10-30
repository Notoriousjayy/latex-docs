"""Bounded Pratt parser / AST evaluator for signed-integer expression subset."""
from dataclasses import dataclass
from lexer import tokenize, LexError, Token

MAX_DEPTH = 128

class ParseError(ValueError):
    pass

@dataclass(frozen=True)
class Number:
    value: int

@dataclass(frozen=True)
class Unary:
    op: str
    operand: object

@dataclass(frozen=True)
class Binary:
    op: str
    lhs: object
    rhs: object

PREC = {'+':10,'-':10,'*':20,'/':20}

class Parser:
    def __init__(self, text):
        self.tokens=tokenize(text)
        self.index=0

    def current(self): return self.tokens[self.index]

    def eat(self,kind):
        t=self.current()
        if t.kind != kind:
            raise ParseError(f'expected {kind}, found {t.kind} at {t.start}')
        self.index+=1
        return t

    def expression(self,min_prec=0,depth=0):
        if depth>=MAX_DEPTH:
            raise ParseError('nesting limit exceeded')
        t=self.current()
        if t.kind=='INT':
            self.eat('INT')
            lhs=Number(int(t.value))
        elif t.kind=='-':
            self.eat('-')
            lhs=Unary('-', self.expression(30,depth+1))
        elif t.kind=='(':
            self.eat('(')
            lhs=self.expression(0,depth+1)
            self.eat(')')
        else:
            raise ParseError(f'unexpected {t.kind} at {t.start}')
        while self.current().kind in PREC and PREC[self.current().kind]>=min_prec:
            op=self.current().kind
            self.eat(op)
            rhs=self.expression(PREC[op]+1,depth+1)
            lhs=Binary(op,lhs,rhs)
        return lhs

def parse(text):
    p=Parser(text)
    node=p.expression()
    p.eat('EOF')
    return node

def eval_ast(node):
    if isinstance(node,Number):return node.value
    if isinstance(node,Unary): return -eval_ast(node.operand)
    if isinstance(node,Binary):
        a,b=eval_ast(node.lhs),eval_ast(node.rhs)
        if node.op=='+':return a+b
        if node.op=='-':return a-b
        if node.op=='*':return a*b
        if node.op=='/':
            if b==0:raise ZeroDivisionError('division by zero')
            # deliberately defined integer truncation toward zero
            q=abs(a)//abs(b)
            return -q if (a<0)!=(b<0) else q
    raise TypeError(f'unknown AST node: {type(node)}')
