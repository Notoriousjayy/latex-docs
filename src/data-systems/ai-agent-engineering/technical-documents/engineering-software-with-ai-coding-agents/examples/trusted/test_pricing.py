import unittest
from pricing import discount

class PricingTests(unittest.TestCase):
    def test_boundaries(self):
        self.assertEqual(discount(101, 0), 101)
        self.assertEqual(discount(101, 100), 0)
        self.assertEqual(discount(101, 50), 50)
    def test_invalid(self):
        for args in [(-1, 10), (10, -1), (10, 101), (True, 1), (10, 0.5)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                discount(*args)
