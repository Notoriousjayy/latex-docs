"""Original three-address IR lowering and pure interpreter for a small expression language."""
from dataclasses import dataclass
from parser import Number,Unary,Binary

@dataclass(frozen=True)
class Instruction:
    op: str
    dest: str
    args: tuple

def lower(node):
    instructions=[]
    def emit(op,*args):
        name=f'v{len(instructions)}'
        instructions.append(Instruction(op,name,tuple(args)))
        return name
    def visit(n):
        if isinstance(n,Number):return emit('const',n.value)
        if isinstance(n,Unary):return emit('neg',visit(n.operand))
        if isinstance(n,Binary):
            left=visit(n.lhs)
            right=visit(n.rhs)
            return emit({'+':'add','-':'sub','*':'mul','/':'div'}[n.op],left,right)
        raise TypeError('unsupported AST node')
    output=visit(node)
    return instructions,output

def execute(instructions,output):
    env={}
    for index,insn in enumerate(instructions):
        if insn.dest in env: raise ValueError('SSA-style virtual name reused')
        if insn.dest!=f'v{index}':raise ValueError('non-canonical temporary')
        a=insn.args
        if insn.op=='const': value=a[0]
        elif insn.op=='neg':value=-env[a[0]]
        else:
            x,y=env[a[0]],env[a[1]]
            if insn.op=='add':value=x+y
            elif insn.op=='sub':value=x-y
            elif insn.op=='mul':value=x*y
            elif insn.op=='div':
                if y==0:raise ZeroDivisionError('division by zero')
                q=abs(x)//abs(y)
                value=-q if (x<0)!=(y<0) else q
            else:raise ValueError('unsupported opcode')
        env[insn.dest]=value
    return env[output]
