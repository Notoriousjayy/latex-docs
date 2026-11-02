import unittest
from flow_observations import (
    deliberately_leaky_output,
    find_low_observation_differences,
    safe_public_output,
)


class ObservationTests(unittest.TestCase):
    def test_no_sampled_difference_in_public_function(self):
        self.assertEqual(
            find_low_observation_differences(
                safe_public_output, range(6), range(-2, 3)
            ),
            [],
        )

    def test_leak_produces_counterexample(self):
        self.assertTrue(
            find_low_observation_differences(
                deliberately_leaky_output, [0, 1], [3]
            )
        )

    def test_empty_high_sample_is_inconclusive(self):
        self.assertEqual(
            find_low_observation_differences(
                deliberately_leaky_output, [], [3]
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
