import importlib.util
from pathlib import Path
import json
import sqlite3
import tempfile
import unittest
from decimal import Decimal
from unittest.mock import patch


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

    def test_ledger_records_unique_key_and_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            db = jev.open_ledger(Path(directory) / 'ledger.sqlite3')
            try:
                first = jev.record_request(db, 'BTC-1000', response(), 250, 0.00001, 0.6)
                self.assertEqual(first, 'allow')
                with self.assertRaises(sqlite3.IntegrityError):
                    jev.record_request(db, 'BTC-1000', response(), 250, 0.00001, 0.6)
                self.assertEqual(jev.budget_remaining(db, 1.0).quantize(Decimal('0.000001')),
                                 Decimal('0.999990'))
                skip = jev.record_request(db, 'ETH-1000', response(0.3, 0.7, 'skip'), 250, 0.00002, 0.6)
                self.assertEqual(skip, 'skip')
                self.assertEqual(jev.budget_remaining(db, 1.0).quantize(Decimal('0.000001')),
                                 Decimal('0.999970'))
            finally:
                db.close()

    def test_budget_exhaustion_blocks_request(self):
        with tempfile.TemporaryDirectory() as directory:
            db = jev.open_ledger(Path(directory) / 'ledger.sqlite3')
            try:
                jev.record_request(db, 'BTC-1', response(), 250, 0.999, 0.6)
                self.assertLess(jev.budget_remaining(db, 1.0), Decimal('0.01'))
            finally:
                db.close()

    def test_invalid_or_missing_response_is_rejected(self):
        for value in (None, {}, response(float('nan'), 0.3), response(0.8, 0.8),
                      response(0.7, 0.3, 'buy'), response(0.7, 0.3, 'skip'),
                      response(True, 0.0)):
            with self.subTest(value=value), self.assertRaises(ValueError):
                jev.parse_decision(value)


class EvaluateTests(unittest.TestCase):
    def setUp(self):
        self.cfg = {'model': 'jev-latest', 'budget_usd': 1.0,
                    'reservation_usd_per_request': 0.01,
                    'input_usd_per_million': 0.042, 'max_request_bytes': 16000,
                    'request_timeout_seconds': 10, 'entry_probability': 0.6}

    def test_dry_run_writes_ledger_without_network(self):
        with tempfile.TemporaryDirectory() as directory:
            db = jev.open_ledger(Path(directory) / 'ledger.sqlite3')
            try:
                decision, cost = jev.evaluate('BTC-1', {'close': 100}, self.cfg, db, dry_run=True)
                self.assertEqual(decision, 'skip')
                self.assertEqual(cost, '0')
                with self.assertRaises(ValueError):
                    jev.evaluate('BTC-1', {'close': 100}, self.cfg, db, dry_run=True)
            finally:
                db.close()

    def test_budget_guard_blocks_before_network(self):
        with tempfile.TemporaryDirectory() as directory:
            db = jev.open_ledger(Path(directory) / 'ledger.sqlite3')
            try:
                db.execute("INSERT INTO requests(ts,candle_key,input_tokens,cost_usd,decision,response_json) VALUES(?,?,?,?,?,?)",
                           (0, 'BTC-0', 0, '0.999', 'skip', '{}'))
                db.commit()
                with patch.object(jev, 'api_key') as key:
                    with self.assertRaises(RuntimeError):
                        jev.evaluate('BTC-2', {}, self.cfg, db, dry_run=False)
                    key.assert_not_called()
            finally:
                db.close()

    def test_live_call_records_cost(self):
        with tempfile.TemporaryDirectory() as directory:
            db = jev.open_ledger(Path(directory) / 'ledger.sqlite3')
            try:
                http_response = json.dumps({'model': 'jev-latest', 'usage': {'input_tokens': 250},
                                            'answers': {'entry': {'type': 'choice', 'choice': 'allow',
                                                                  'probabilities': {'allow': 0.8, 'skip': 0.2}}}}).encode()
                context = unittest.mock.Mock()
                context.__enter__ = unittest.mock.Mock(return_value=unittest.mock.Mock(read=lambda: http_response))
                context.__exit__ = unittest.mock.Mock(return_value=False)
                with patch.object(jev.urllib.request, 'urlopen', return_value=context), \
                     patch.object(jev, 'api_key', return_value='test'):
                    decision, cost = jev.evaluate('BTC-3', {}, self.cfg, db, dry_run=False)
                self.assertEqual(decision, 'allow')
                self.assertEqual(Decimal(cost), Decimal('250') * Decimal('0.042') / Decimal('1000000'))
            finally:
                db.close()


if __name__ == '__main__':
    unittest.main()
