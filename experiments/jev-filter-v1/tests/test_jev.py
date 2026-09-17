import importlib.util
from pathlib import Path
import sqlite3
import tempfile
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

    def test_decision_round_trip_through_temporary_sqlite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'decision.sqlite3'
            with sqlite3.connect(path) as db:
                db.execute('CREATE TABLE decisions (allowed INTEGER NOT NULL)')
                db.execute('INSERT INTO decisions VALUES (?)',
                           (int(jev.parse_decision(response())),))
            with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as db:
                self.assertEqual(db.execute('SELECT allowed FROM decisions').fetchall(), [(1,)])

    def test_non_string_choice_is_rejected_as_invalid_response(self):
        for choice in ([], {}, None, True, 1):
            with self.subTest(choice=choice), self.assertRaises(ValueError):
                jev.parse_decision(response(choice=choice))

    def test_invalid_or_missing_response_is_rejected(self):
        for value in (None, {}, response(float('nan'), 0.3), response(0.8, 0.8),
                      response(0.7, 0.3, 'buy'), response(0.7, 0.3, 'skip'),
                      response(True, 0.0)):
            with self.subTest(value=value), self.assertRaises(ValueError):
                jev.parse_decision(value)


if __name__ == '__main__':
    unittest.main()
