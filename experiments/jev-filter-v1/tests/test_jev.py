import importlib.util
from pathlib import Path
import unittest


SPEC = importlib.util.spec_from_file_location('jev', Path(__file__).resolve().parents[1] / 'jev.py')
jev = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(jev)


def response(allow=0.7, skip=0.3, choice='allow'):
    return {'answers': {'entry': {'type': 'choice', 'choice': choice,
                                'probabilities': {'allow': allow, 'skip': skip}}}}


class DecisionTests(unittest.TestCase):
    def test_allows_only_at_fixed_threshold(self):
        self.assertTrue(jev.parse_decision(response(0.6, 0.4)))
        self.assertFalse(jev.parse_decision(response(0.59, 0.41)))
        self.assertFalse(jev.parse_decision(response(0.2, 0.8, 'skip')))

    def test_invalid_or_missing_response_is_rejected(self):
        for value in (None, {}, response(float('nan'), 0.3), response(0.8, 0.8),
                      response(0.7, 0.3, 'buy'), response(0.7, 0.3, 'skip'),
                      response(True, 0.0)):
            with self.subTest(value=value), self.assertRaises(ValueError):
                jev.parse_decision(value)


if __name__ == '__main__':
    unittest.main()
