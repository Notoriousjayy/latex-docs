import unittest
from parsing_reference import cyk_recognize,earley_recognize,grammar_sets,ll1_table,ll1_recognize
from mini_compiler import lex,parse,evaluate,ParseError

class ParsingReferenceTests(unittest.TestCase):
    def setUp(self):
        self.cnf={'S':(('A','B'),),'A':(('a',),),'B':(('b',),)}
        self.balanced={'S':(('a','S','b'),())}
        self.ll={'S':(('a','A'),),'A':(('b','A'),())}

    def test_cyk_positive_negative(self):
        for tokens,expected in [(('a','b'),True),(('b','a'),False),(('a',),False),((),False)]:
            self.assertEqual(cyk_recognize(self.cnf,'S',tokens),expected)
    def test_cyk_validation(self):
        with self.assertRaisesRegex(ValueError,'strict CNF'):
            cyk_recognize(self.balanced,'S',('a','b'))
        with self.assertRaisesRegex(ValueError,'resource'):
            cyk_recognize(self.cnf,'S',('a','b'),max_tokens=1)
    def test_earley(self):
        for tokens,expected in [((),True),(('a','b'),True),(('a','a','b','b'),True),
                                (('a','b','b'),False),(('a','a','b'),False)]:
            self.assertEqual(earley_recognize(self.balanced,'S',tokens),expected)
    def test_cyk_earley_equivalence_bounded(self):
        # Equivalent CNF and CFG representations of {a^n b^n : n>=1}.
        cnf={'S':(('A','B'),('A','C')),'C':(('S','B'),),
             'A':(('a',),),'B':(('b',),)}
        cfg={'S':(('a','S','b'),('a','b'))}
        import itertools
        for n in range(1,7):
            for t in itertools.product('ab', repeat=n):
                self.assertEqual(cyk_recognize(cnf,'S',t),
                                 earley_recognize(cfg,'S',t),
                                 msg=f"different result for {t}")

    def test_nullable_cycle(self):
        g={'S':(('A',),),'A':(('A',),())}
        self.assertTrue(earley_recognize(g,'S',()))
        self.assertFalse(earley_recognize(g,'S',('a',)))
    def test_nullable_prior_completion(self):
        g={'S':(('A','A'),),'A':((),)}
        self.assertTrue(earley_recognize(g,'S',()))
    def test_first_follow(self):
        first,follow,nullable=grammar_sets(self.ll,'S')
        self.assertEqual(first['S'],{'a'})
        self.assertEqual(first['A'],{'b'})
        self.assertIn('A',nullable)
        self.assertEqual(follow['A'],{'$'})
    def test_predictive_accepts_and_rejects(self):
        for tokens,expected in [(('a',),True),(('a','b','b'),True),(('b',),False), (('a','b','a'),False)]:
            self.assertEqual(ll1_recognize(self.ll,'S',tokens),expected)
    def test_conflicting_table(self):
        g={'S':(('a','A'),('a','B')),'A':(('b',),),'B':(('c',),)}
        with self.assertRaisesRegex(ValueError,'conflict'):ll1_table(g,'S')

class MiniCompilerTests(unittest.TestCase):
    def test_precedence(self):self.assertEqual(evaluate(parse('2 + 3 * 4')),14)
    def test_associativity(self):self.assertEqual(evaluate(parse('9-4-2')),3)
    def test_nested(self):self.assertEqual(evaluate(parse(' -(3 + 4)*2')), -14)
    def test_invalid(self):
        for expr in ('2+', '(1+2', '1&&2', '2 3', '0x10', '3 / 0'):
            with self.assertRaises(ParseError): evaluate(parse(expr))
    def test_limit(self):
        with self.assertRaisesRegex(ParseError,'integer literal too large'): parse('1' * 1001,max_nodes=1)
        with self.assertRaisesRegex(ParseError,'AST node limit'): parse('1+2',max_nodes=1)
    def test_unicode_rejection(self):
        with self.assertRaisesRegex(ParseError,'unrecognized'): lex('１+２')

if __name__=='__main__': unittest.main()
