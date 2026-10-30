import random
import unittest
from lexer import tokenize,LexError
from parser import parse,eval_ast,ParseError,Number,Binary
from dataflow import Block,liveness
from optimizer import fold
from ir import lower,execute

class CompilerTests(unittest.TestCase):
    def test_tokens(self):
        t=tokenize(' 12 + (3*4)')
        self.assertEqual([x.kind for x in t],['INT','+','(','INT','*','INT',')','EOF'])
        self.assertEqual((t[0].start,t[0].end),(1,3))

    def test_errors(self):
        with self.assertRaises(LexError):tokenize('1 + @')
        with self.assertRaises(LexError):tokenize('1'*19)
        with self.assertRaises(ParseError):parse('1 + )')
        with self.assertRaises(ParseError):parse('(' * 200 + '1' + ')' * 200)
        with self.assertRaises(ParseError):parse('1 2')

    def test_precedence(self):
        cases={'1+2*3':7,'(1+2)*3':9,'8-3-2':3,'-3*4':-12,'7/(-3)':-2}
        for expr,expected in cases.items():
            self.assertEqual(eval_ast(parse(expr)),expected)
            self.assertEqual(eval_ast(fold(parse(expr))),expected)
            inst,ret=lower(parse(expr))
            self.assertEqual(execute(inst,ret),expected)
        with self.assertRaises(ZeroDivisionError):eval_ast(fold(parse('1/0')))

    def test_liveness_diamond(self):
        blocks=[Block('entry',('left','right'),frozenset(),frozenset({'x'})),
                Block('left',('join',),frozenset({'x'}),frozenset()),
                Block('right',('join',),frozenset({'x'}),frozenset()),
                Block('join',(),frozenset(),frozenset())]
        inn,out,it=liveness(blocks)
        self.assertEqual(inn['entry'],set())
        self.assertEqual(out['entry'],{'x'})
        self.assertGreaterEqual(it,2)
        with self.assertRaises(ValueError):liveness([Block('x',('missing',),frozenset(),frozenset())])

    def test_differential_random(self):
        rng=random.Random(42)
        def make(depth):
            if depth==0:return Number(rng.randint(-100,100))
            return Binary(rng.choice(['+','-','*']), make(depth-1),make(depth-1))
        for _ in range(250):
            expr=make(3)
            self.assertEqual(eval_ast(expr),eval_ast(fold(expr)))
            inst,ret=lower(expr)
            self.assertEqual(eval_ast(expr),execute(inst,ret))

if __name__=='__main__':unittest.main()
