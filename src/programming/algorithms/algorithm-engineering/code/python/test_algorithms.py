"""Run: cd code/python && python -m unittest -v"""
import bisect
import itertools
import math
import random
import unittest
from algorithms import (RingBuffer, Record, combinations, dpll, euclid_gcd, exact_cover,
                        fisher_yates, insertion_sort, lcg, lower_bound, n_queens,
                        permutations, stable_merge_sort, cnf_satisfied)

class AlgorithmTests(unittest.TestCase):
    def test_ring_buffer(self):
        b = RingBuffer(2)
        with self.assertRaises(IndexError): b.dequeue()
        b.enqueue(1); b.enqueue(2)
        with self.assertRaises(OverflowError): b.enqueue(3)
        self.assertEqual(b.dequeue(), 1)
        b.enqueue(3)
        self.assertEqual([b.dequeue(), b.dequeue()], [2, 3])

    def test_gcd(self):
        for a in range(-25, 26):
            for b in range(-25, 26):
                self.assertEqual(euclid_gcd(a,b), math.gcd(a,b))

    def test_lcg(self):
        self.assertEqual(lcg(0,4,1,9,9), [1,5,3,4,8,6,7,2,0])
        with self.assertRaises(ValueError): lcg(0,1,1,0,5)

    def test_shuffle(self):
        original = list(range(20))
        result = fisher_yates(original, random.Random(17))
        self.assertEqual(sorted(result), original)
        self.assertEqual(original, list(range(20)))

    def test_sorting_stability(self):
        rng = random.Random(5)
        for n in (0,1,2,3,17,128):
            records = [Record(rng.randrange(4),i) for i in range(n)]
            expected = sorted(records, key=lambda r:r.key)
            self.assertEqual(insertion_sort(records), expected)
            self.assertEqual(stable_merge_sort(records), expected)

    def test_lower_bound(self):
        for seq in ([], [1], [1,1,2,4,4,6], list(range(-10,11))):
            for x in range(-12,14):
                self.assertEqual(lower_bound(seq,x), bisect.bisect_left(seq,x))

    def test_combinations(self):
        for n in range(7):
            for k in range(n+1):
                self.assertEqual(list(combinations(n,k)), list(itertools.combinations(range(n),k)))
        self.assertEqual(list(combinations(2,3)),[])

    def test_permutations(self):
        for n in range(6):
            self.assertEqual(list(permutations(tuple(range(n)))),
                             list(itertools.permutations(range(n))))

    def test_n_queens(self):
        self.assertEqual([n_queens(n) for n in range(9)], [1,1,0,0,2,10,4,40,92])

    def test_exact_cover(self):
        p={'A','B','C','D'}
        options=[{'A','B'},{'C','D'},{'A','C'},{'B','D'}]
        actual=exact_cover(p,options)
        self.assertEqual(len(actual),2)
        for indices in actual:
            seen=[]
            for index in indices: seen += list(options[index])
            self.assertEqual(set(seen),p)
            self.assertEqual(len(seen),len(p))
        self.assertEqual(exact_cover(set(),[]),[()])
        self.assertEqual(exact_cover({'A'},[]),[])

    def test_dpll_exhaustive_small(self):
        rng=random.Random(23)
        for vars_count in range(1,5):
            universe=[v for v in range(1,vars_count+1)]
            for _ in range(100):
                clauses=[]
                for _ in range(rng.randrange(7)):
                    clause=[rng.choice(universe)*rng.choice([-1,1])
                            for _ in range(rng.randrange(4))]
                    clauses.append(clause)
                actual=dpll(clauses)
                exhaustive=any(cnf_satisfied(clauses,dict(zip(universe, bits)))
                               for bits in itertools.product([False,True],repeat=vars_count))
                self.assertEqual(actual is not None,exhaustive, clauses)
                if actual is not None:
                    self.assertTrue(cnf_satisfied(clauses,actual))

if __name__ == '__main__': unittest.main()
