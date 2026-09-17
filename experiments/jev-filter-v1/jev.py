import math
import json
import os
import sqlite3
import subprocess
import time
import urllib.request
from decimal import Decimal
from pathlib import Path


SCHEMA = '''
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY,
    ts REAL NOT NULL,
    candle_key TEXT NOT NULL UNIQUE,
    input_tokens INTEGER,
    cost_usd TEXT NOT NULL,
    decision TEXT NOT NULL,
    response_json TEXT NOT NULL
);
'''


def open_ledger(path):
    db = sqlite3.connect(str(path), timeout=10)
    db.execute('PRAGMA journal_mode=WAL')
    db.executescript(SCHEMA)
    db.commit()
    return db


def record_request(db, candle_key, response, input_tokens, cost_usd, threshold):
    decision = 'allow' if parse_decision(response, threshold) else 'skip'
    with db:
        db.execute('INSERT INTO requests(ts,candle_key,input_tokens,cost_usd,decision,response_json) VALUES(?,?,?,?,?,?)',
                   (time.time(), candle_key, input_tokens, str(Decimal(str(cost_usd)).quantize(Decimal('0.000001'))), decision, json.dumps(response, sort_keys=True, separators=(',', ':'))))
    return decision


def budget_remaining(db, budget_usd):
    spent = Decimal('0')
    for (value,) in db.execute('SELECT cost_usd FROM requests'):
        spent += Decimal(value)
    return Decimal(str(budget_usd)) - spent


def api_key():
    env = os.environ.get('TYPESAFE_AI_API_KEY')
    if env:
        return env.strip()
    result = subprocess.run(['security', 'find-generic-password', '-a', 'jev',
                             '-s', 'TYPESAFE_AI_API_KEY', '-w'],
                            capture_output=True, timeout=30)
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError('API key unavailable from keychain')
    return result.stdout.decode('utf-8').strip()


def evaluate(candle_key, state, cfg, db, dry_run=True):
    """One Jev evaluation with budget guard and ledger write.

    dry_run=True skips the network and uses a deterministic mock response so
    the pipeline can be exercised without cost or external calls.
    """
    if db.execute('SELECT 1 FROM requests WHERE candle_key=?', (candle_key,)).fetchone():
        raise ValueError('Duplicate candle_key: ' + candle_key)
    if budget_remaining(db, cfg['budget_usd']) < Decimal(str(cfg['reservation_usd_per_request'])):
        raise RuntimeError('Budget exhausted')
    if dry_run:
        response, tokens, cost = {'answers': {'entry': {
            'type': 'choice', 'choice': 'skip',
            'probabilities': {'allow': 0.4, 'skip': 0.6}}}}, 0, 0
    else:
        payload = json.dumps({
            'model': cfg['model'],
            'state': state,
            'questions': {'entry': {
                'type': 'choice',
                'instructions': 'Is there sufficient completed-candle evidence to consider a new paper entry? Missing evidence means skip.',
                'criteria': {'allow': 'Sufficient completed-candle evidence is present',
                             'skip': 'Evidence is missing or insufficient'}}},
        }).encode('utf-8')
        if len(payload) > cfg['max_request_bytes']:
            raise ValueError('Request exceeds max_request_bytes')
        request = urllib.request.Request(
            'https://api.typesafe.ai/v1/systemone', data=payload,
            headers={'Authorization': 'Bearer ' + api_key(),
                     'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(request, timeout=cfg['request_timeout_seconds']) as raw:
            response = json.loads(raw.read().decode('utf-8'))
        tokens = int(response.get('usage', {}).get('input_tokens') or 0)
        cost = Decimal(str(tokens)) * Decimal(str(cfg['input_usd_per_million'])) / Decimal('1000000')
    decision = record_request(db, candle_key, response, tokens, cost, cfg['entry_probability'])
    return decision, str(cost)


def parse_decision(response, threshold=0.6):
    if not isinstance(response, dict):
        raise ValueError('Response must be an object')
    answers = response.get('answers')
    if not isinstance(answers, dict) or not isinstance(answers.get('entry'), dict):
        raise ValueError('Missing entry answer')
    answer = answers['entry']
    if answer.get('type') != 'choice':
        raise ValueError('Expected choice answer')
    probabilities = answer.get('probabilities')
    if not isinstance(probabilities, dict) or set(probabilities) != {'allow', 'skip'}:
        raise ValueError('Expected allow/skip probabilities')
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or
           not math.isfinite(v) or not 0 <= v <= 1 for v in probabilities.values()):
        raise ValueError('Invalid probability')
    if not math.isclose(sum(probabilities.values()), 1.0, abs_tol=1e-6):
        raise ValueError('Probabilities must sum to one')
    choice = answer.get('choice')
    if not isinstance(choice, str) or choice not in probabilities:
        raise ValueError('Invalid choice')
    if probabilities[choice] < max(probabilities.values()):
        raise ValueError('Invalid choice')
    return choice == 'allow' and probabilities['allow'] >= threshold
