"""Small-instance correctness and theorem-checking tests."""
import itertools
import math
import unittest
from collections import Counter
from instrumented_analysis import (merge_sort, quick_sort_first_pivot,
    insertion_sort, count_inversions, expected_quick_comparisons)
from combinatorial_models import (catalan, ordered_binary_tree_shapes,
    bst_shape_distribution, internal_path_length, trie_statistics, bucket_trial)

class ModelsTest(unittest.TestCase):
    def test_sort_inversions_and_shift_identity(self):
        for n in range(7):
            for p in itertools.permutations(range(n)):
                for fn in (merge_sort, quick_sort_first_pivot, insertion_sort):
                    self.assertEqual(fn(p).values, tuple(range(n)))
                self.assertEqual(insertion_sort(p).shifts, count_inversions(p))

    def test_quicksort_exact_mean(self):
        for n in range(1, 7):
            counts = [quick_sort_first_pivot(p).comparisons
                      for p in itertools.permutations(range(n))]
            self.assertAlmostEqual(sum(counts)/len(counts),
                                   expected_quick_comparisons(n), places=10)

    def test_catalan_enumeration(self):
        self.assertEqual([catalan(n) for n in range(6)], [1, 1, 2, 5, 14, 42])
        for n in range(7):
            self.assertEqual(len(ordered_binary_tree_shapes(n)), catalan(n))

    def test_bst_exact_mean(self):
        for n in range(1, 7):
            counts = bst_shape_distribution(n)
            mean = sum(internal_path_length(s)*freq for s,freq in counts.items()) / math.factorial(n)
            target = 2*(n+1)*sum(1/k for k in range(1, n+1))-4*n
            self.assertAlmostEqual(mean, target, places=10)

    def test_occupancy_and_trie_invariants(self):
        counts, collisions = bucket_trial(512, 16, 9)
        self.assertEqual(sum(counts), 512)
        self.assertEqual(collisions, sum(x*(x-1)//2 for x in counts))
        a,_ = trie_statistics(["aa0", "aa1", "aa2"])
        b,_ = trie_statistics(["a00", "b00", "c00"])
        self.assertLess(a, b)

if __name__ == "__main__":
    unittest.main()
