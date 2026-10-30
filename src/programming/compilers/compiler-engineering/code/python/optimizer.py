"""Pure-AST constant folding; division by zero retains runtime failure."""
from parser import Number,Unary,Binary,eval_ast

def fold(node):
    if isinstance(node,Number):return node
    if isinstance(node,Unary):
        child=fold(node.operand)
        folded=Unary(node.op,child)
        return Number(eval_ast(folded)) if isinstance(child,Number) else folded
    if isinstance(node,Binary):
        l,r=fold(node.lhs),fold(node.rhs)
        result=Binary(node.op,l,r)
        if isinstance(l,Number) and isinstance(r,Number):
            try: return Number(eval_ast(result))
            except ZeroDivisionError: pass
        return result
    raise TypeError('unsupported AST node')
