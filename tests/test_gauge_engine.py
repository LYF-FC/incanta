import unittest
from backend.gauge_engine import determine_emotion, get_current_gauges, update_gauges


class FixedVariation:
    def randint(self, low, high): return 0


class GaugeTests(unittest.TestCase):
    def test_reaches_three_non_neutral_emotions_with_explicit_precedence(self):
        for expected, values in [('Happy',{'Trust':80}), ('Confident',{'Confidence':80,'Affection':40,'Arousal':30}), ('Curious',{'Curiosity':80,'Affection':40,'Confidence':50})]:
            with self.subTest(expected=expected):
                gauges = get_current_gauges(); gauges.update(values)
                self.assertEqual(determine_emotion(gauges), expected)
        gauges = dict.fromkeys(get_current_gauges(), 40)
        gauges.update(Curiosity=20, Confidence=50, Intimacy=20)
        self.assertEqual(determine_emotion(gauges), 'Neutral')

    def test_updates_are_bounded_and_do_not_mutate_committed_input(self):
        gauges = dict.fromkeys(get_current_gauges(), 99)
        result = update_gauges('trust love kiss?', 'safe', gauges, rng=FixedVariation())
        self.assertEqual(gauges['Trust'], 99)
        self.assertTrue(all(0 <= value <= 100 for value in result.values()))
