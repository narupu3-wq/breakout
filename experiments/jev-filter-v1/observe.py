"""Continuous Jev observation loop: one decision per closed 15m candle per symbol.

Reads public Kraken data via the existing market_data module, asks Jev one
allow/skip question per new closed candle, and records everything in this
experiment's own SQLite ledger. It never writes to the main research DB and
never places orders. API cost is capped by config budget_usd.
"""
import argparse
import json
import os
import signal as os_signal
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import market_data
import jev  # noqa: E402


def load_config(path):
    cfg = json.loads(Path(path).read_text())
    required = {'version', 'model', 'budget_usd', 'duration_days',
                'input_usd_per_million', 'reservation_usd_per_request',
                'max_request_bytes', 'request_timeout_seconds', 'entry_probability'}
    if not required.issubset(cfg):
        raise ValueError('Missing config keys')
    if cfg['budget_usd'] <= 0 or cfg['duration_days'] <= 0:
        raise ValueError('Budget and duration must be positive')
    return cfg


def candle_state(symbol, candles):
    """Compact state built only from completed candles."""
    last = candles[-40:]
    closes = [b['close'] for b in last]
    return {
        'symbol': symbol,
        'candle_interval_minutes': 15,
        'candles': [{'ts': b['ts'], 'open': b['open'], 'high': b['high'],
                     'low': b['low'], 'close': b['close'], 'volume': b['volume']}
                    for b in last],
        'last_close': closes[-1],
        'question': 'Will the next 15m candle move more than 0.1% from the last close?',
    }


def observe_once(db, cfg, dry_run):
    results = []
    for symbol in ('BTCUSD', 'ETHUSD'):
        market = market_data.fetch_market(symbol)
        last_closed = market['candles'][-1]['ts']
        candle_key = '{}:{}'.format(symbol, last_closed)
        try:
            decision, cost = jev.evaluate(candle_key, candle_state(symbol, market['candles']),
                                          cfg, db, dry_run=dry_run)
        except ValueError as exc:
            if 'Duplicate' in str(exc):
                continue
            raise
        results.append({'symbol': symbol, 'candle_ts': last_closed,
                        'decision': decision, 'cost_usd': cost,
                        'bid': market['bid'], 'ask': market['ask'],
                        'observed_at': market['observed_at']})
    return results


def main():
    parser = argparse.ArgumentParser(description='Continuous Jev observation (no orders).')
    parser.add_argument('--config', default=str(Path(__file__).resolve().parent / 'config.json'))
    parser.add_argument('--db', default=str(Path(__file__).resolve().parent / 'data' / 'ledger.sqlite3'))
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--dry-run', action='store_true', help='Mock decisions, no API cost')
    parser.add_argument('--duration', type=int, default=0, help='Seconds to run (0 = until 30d deadline or Ctrl-C)')
    args = parser.parse_args()
    cfg = load_config(args.config)
    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    db = jev.open_ledger(args.db)
    started = time.time()
    deadline_days = cfg['duration_days'] * 86400
    stop = [False]

    def shutdown(*_):
        stop[0] = True

    os_signal.signal(os_signal.SIGTERM, shutdown)
    os_signal.signal(os_signal.SIGINT, shutdown)
    print(json.dumps({'mode': 'dry_run' if args.dry_run else 'live',
                      'budget_usd': cfg['budget_usd'],
                      'duration_days': cfg['duration_days']}), flush=True)
    try:
        while not stop[0]:
            if time.time() - started >= deadline_days:
                print(json.dumps({'status': 'duration_reached'}), flush=True)
                break
            try:
                for row in observe_once(db, cfg, dry_run=args.dry_run):
                    print(json.dumps(row), flush=True)
            except Exception as exc:
                print(json.dumps({'error': str(exc)}), flush=True)
            if stop[0] or args.once:
                break
            for _ in range(60):
                if stop[0]:
                    break
                time.sleep(1)
    finally:
        remaining = jev.budget_remaining(db, cfg['budget_usd'])
        print(json.dumps({'budget_remaining': str(remaining)}), flush=True)
        db.close()


if __name__ == '__main__':
    main()
