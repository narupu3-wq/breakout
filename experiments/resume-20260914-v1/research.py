#!/usr/bin/env python3
"""BreakOut research CLI: public data and simulated orders only."""
import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import random
import shutil
import signal as os_signal
import sqlite3
import statistics
import sys
import tempfile
import time

from engine import Account, signal
from market_data import fetch_market

ROOT = Path(__file__).resolve().parent


def encoded(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False)


def load_config(path):
    cfg = json.loads(Path(path).read_text())
    def finite(obj):
        if isinstance(obj, dict):
            for v in obj.values(): finite(v)
        elif isinstance(obj, list):
            for v in obj: finite(v)
        elif isinstance(obj, (int, float)) and not math.isfinite(obj):
            raise ValueError('Nonfinite configuration')
    finite(cfg)
    a = cfg['account']
    if cfg['mode'] != 'paper_only' or cfg['breakout_execution_verified'] is not False:
        raise ValueError('This build supports paper_only; live execution does not exist')
    if a != {'initial_balance':5000.0, 'target_profit':450.0, 'daily_loss_fraction':0.03, 'static_loss':150.0, 'reset_utc_seconds':1800}:
        raise ValueError('Only verified provisional Turbo 5K account rules supported')
    if cfg['symbols'] != ['BTCUSD', 'ETHUSD'] or cfg['interval_minutes'] != 15 or cfg['poll_seconds'] < 30:
        raise ValueError('Unsupported market/interval/poll configuration')
    for r in cfg['risk_candidates']:
        if not 0 < r['trade_risk'] < r['daily_stop'] <= r['total_stop'] < a['static_loss']:
            raise ValueError('Invalid risk limits')
    if len({r['name'] for r in cfg['risk_candidates']}) != len(cfg['risk_candidates']):
        raise ValueError('Duplicate risk names')
    c, s, g = cfg['costs'], cfg['strategy'], cfg['gates']
    if not all(c[k] > 0 for k in ('fee_per_side','slippage_bps','backtest_spread_bps','swap_per_day')):
        raise ValueError('Costs must be positive')
    if not all(s[k] > 0 for k in s) or s['lookback'] < s['atr_period']:
        raise ValueError('Invalid strategy parameters')
    if not all(g[k] > 0 for k in g) or g['required_stress_cost_multiplier'] < 2:
        raise ValueError('Invalid research gates')
    return cfg


def fingerprint(cfg):
    h = hashlib.sha256(encoded(cfg).encode())
    for name in ('engine.py', 'market_data.py', 'research.py'):
        h.update((ROOT/name).read_bytes())
    return h.hexdigest()


def connect(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(path), timeout=10)
    db.execute('PRAGMA journal_mode=WAL')
    db.executescript('''
    CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, mode TEXT, started REAL, manifest TEXT);
    CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, run TEXT, candidate TEXT, ts REAL, kind TEXT, payload TEXT);
    CREATE TABLE IF NOT EXISTS states (run TEXT, candidate TEXT, state TEXT, PRIMARY KEY(run,candidate));
    CREATE TABLE IF NOT EXISTS snapshots (id INTEGER PRIMARY KEY, observed REAL, symbol TEXT, payload TEXT);
    CREATE TABLE IF NOT EXISTS candles (symbol TEXT, ts INTEGER, payload TEXT, PRIMARY KEY(symbol,ts));
    CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT,'append only'); END;
    CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT,'append only'); END;
    CREATE TRIGGER IF NOT EXISTS runs_no_update BEFORE UPDATE ON runs BEGIN SELECT RAISE(ABORT,'immutable manifest'); END;
    CREATE TRIGGER IF NOT EXISTS runs_no_delete BEFORE DELETE ON runs BEGIN SELECT RAISE(ABORT,'immutable manifest'); END;
    CREATE TRIGGER IF NOT EXISTS candles_no_update BEFORE UPDATE ON candles BEGIN SELECT RAISE(ABORT,'immutable candles'); END;
    CREATE TRIGGER IF NOT EXISTS candles_no_delete BEFORE DELETE ON candles BEGIN SELECT RAISE(ABORT,'immutable candles'); END;
    CREATE TRIGGER IF NOT EXISTS snapshots_no_update BEFORE UPDATE ON snapshots BEGIN SELECT RAISE(ABORT,'immutable snapshots'); END;
    CREATE TRIGGER IF NOT EXISTS snapshots_no_delete BEFORE DELETE ON snapshots BEGIN SELECT RAISE(ABORT,'immutable snapshots'); END;
    ''')
    return db


@contextlib.contextmanager
def writer_lock(path):
    lock = open(str(path)+'.lock', 'a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock.close()
        raise RuntimeError('Another writer is running; use status or report')
    try:
        yield
    finally:
        lock.close()


def record(db, run, candidate, event):
    db.execute('INSERT INTO events(run,candidate,ts,kind,payload) VALUES(?,?,?,?,?)',
               (run, candidate, event['ts'], event['kind'], encoded(event)))


def create_run(db, cfg, mode, resume=False):
    digest = fingerprint(cfg)
    run = mode + '-' + digest[:16]
    if not resume:
        run += '-' + str(time.time_ns())
    manifest = {'fingerprint': digest, 'config':cfg, 'source':'Kraken spot public API proxy',
                'limitations':['Breakout execution unverified','sampled quotes cannot establish continuous equity compliance',
                               'OHLC intrabar sequence unknown; adverse-first approximation',
                               'fills, slippage, swap timing and market depth unvalidated'],
                'live_enabled':False}
    with db:
        db.execute('INSERT OR IGNORE INTO runs VALUES(?,?,?,?)', (run,mode,time.time(),encoded(manifest)))
    # Preserve the actual source as well as hashes so old evidence stays reproducible.
    archive = Path(db.execute('PRAGMA database_list').fetchone()[2]).parent/'runs'/run
    if not archive.exists():
        archive.parent.mkdir(parents=True,exist_ok=True)
        staging=Path(tempfile.mkdtemp(prefix='.snapshot-',dir=str(archive.parent)))
        try:
            (staging/'manifest.json').write_text(json.dumps(manifest,indent=2))
            for name in ('engine.py','market_data.py','research.py'):
                shutil.copyfile(ROOT/name,staging/name)
            os.replace(str(staging),str(archive))
        finally:
            if staging.exists(): shutil.rmtree(staging)
    if json.loads((archive/'manifest.json').read_text())!=manifest:
        raise ValueError('Archived manifest mismatch; do not resume')
    archived_hash=hashlib.sha256(encoded(cfg).encode())
    for name in ('engine.py','market_data.py','research.py'):
        archived_hash.update((archive/name).read_bytes())
    if archived_hash.hexdigest()!=digest:
        raise ValueError('Archived source mismatch; do not resume')
    return run


def candidates(cfg, stress=False):
    for risk in cfg['risk_candidates']:
        for kind in ('trend', 'mean_reversion'):
            for mult in ([1.0, cfg['gates']['required_stress_cost_multiplier']] if stress else [1.0]):
                yield kind+'-'+risk['name']+('-stress' if mult > 1 else ''), kind, risk, mult


def acquire(db, cfg):
    markets = {}
    for symbol in cfg['symbols']:
        m = fetch_market(symbol, interval=cfg['interval_minutes'])
        markets[symbol] = m
    if max(m['observed_at'] for m in markets.values())-min(m['observed_at'] for m in markets.values()) > 30:
        raise ValueError('Market snapshot skew exceeds 30s')
    with db:
        for symbol,m in markets.items():
            for b in m['candles']:
                previous=db.execute('SELECT payload FROM candles WHERE symbol=? AND ts=?',(symbol,b['ts'])).fetchone()
                if previous and previous[0]!=encoded(b):
                    raise ValueError('Closed candle revised by source: {} {}'.format(symbol,b['ts']))
                db.execute('INSERT OR IGNORE INTO candles VALUES(?,?,?)',(symbol,b['ts'],encoded(b)))
            quote={k:v for k,v in m.items() if k!='candles'}
            quote['last_candle_ts']=m['candles'][-1]['ts']
            db.execute('INSERT INTO snapshots(observed,symbol,payload) VALUES(?,?,?)', (m['observed_at'],symbol,encoded(quote)))
    return markets


def cached_markets(db,cfg):
    markets={}
    for symbol in cfg['symbols']:
        row=db.execute('SELECT payload FROM snapshots WHERE symbol=? ORDER BY id DESC LIMIT 1',(symbol,)).fetchone()
        if not row: raise ValueError('No stored snapshot: '+symbol)
        m=json.loads(row[0])
        m['candles']=[json.loads(r[0]) for r in db.execute('SELECT payload FROM candles WHERE symbol=? AND ts<=? ORDER BY ts',(symbol,m['last_candle_ts']))]
        markets[symbol]=m
    return markets


def history_run(db, cfg, markets):
    run = create_run(db, cfg, 'backtest')
    histories = {s: m['candles'] for s,m in markets.items()}
    indices = {s: {b['ts']:i for i,b in enumerate(bars)} for s,bars in histories.items()}
    common = sorted(set.intersection(*(set(ix) for ix in indices.values())))
    if len(common) < cfg['strategy']['lookback']+2:
        raise ValueError('Insufficient shared history')
    if any(b-a != 900 for a,b in zip(common, common[1:])):
        raise ValueError('Shared history has a gap')
    results = {}
    # Report each candidate, never automatically choose a winner from this sample.
    for name,kind,risk,mult in candidates(cfg, stress=True):
        account = Account(cfg,risk,cost_multiplier=mult)
        for ts in common:
            account.reset_day(ts)
            p = account.s['position']
            if p:
                account.bar(histories[p['symbol']][indices[p['symbol']][ts]])
            else:
                for symbol in cfg['symbols']:
                    i = indices[symbol][ts]
                    sig = signal(histories[symbol][:i],kind,cfg['strategy'])
                    b = histories[symbol][i]
                    if sig:
                        half = cfg['costs']['backtest_spread_bps']*mult/20000
                        # Prior completed bar volume cap, never current/future bar volume.
                        available=histories[symbol][i-1]['volume']*0.01 if i else 0
                        if account.open(ts,symbol,sig,b['open']*(1-half),b['open']*(1+half),available):
                            account.bar(b)
                            break
            for ev in account.events:
                record(db,run,name,ev)
            account.events = []
        if account.s['position']:
            p = account.s['position']
            b = histories[p['symbol']][indices[p['symbol']][common[-1]]]
            half = cfg['costs']['backtest_spread_bps']*mult/20000
            account.close(common[-1]+899,b['close']*(1-half*p['side']),'end_of_sample')
            for ev in account.events: record(db,run,name,ev)
        results[name] = account.summary()
        db.execute('INSERT INTO states VALUES(?,?,?)', (run,name,encoded(account.s)))
    record(db,run,'system',{'kind':'history_window','ts':time.time(),
                           'first':common[0], 'last':common[-1], 'bars':len(common),
                           'purpose':'pipeline smoke / exploratory only; not a promotion test'})
    db.commit()
    return run,results


def paper_cycle(db,cfg,run,markets):
    now = max(m['observed_at'] for m in markets.values())
    with db:
        for name,kind,risk,mult in candidates(cfg,stress=True):
            row = db.execute('SELECT state FROM states WHERE run=? AND candidate=?',(run,name)).fetchone()
            state = json.loads(row[0]) if row else None
            account = Account(cfg,risk,state,mult)
            previous = account.s.get('observed_at')
            gap = previous is not None and now-previous > cfg['poll_seconds']*2.5
            if gap:
                account.event('data_gap',now,seconds=now-previous)
                # Existing positions get a visible delayed close at first observed quote.
                # This session cannot qualify; no invented fills during outage.
                account.s['halt'] = 'data_gap_requires_new_version'
            account.reset_day(now)
            p = account.s['position']
            if p:
                m = markets[p['symbol']]
                account.quote(now,m['bid'],m['ask'])
                if gap and account.s['position']:
                    p = account.s['position']
                    account.close(now,m['bid'] if p['side']==1 else m['ask'],'delayed_close_after_gap')
            last = account.s.setdefault('last_signals',{})
            for symbol in cfg['symbols']:
                m = markets[symbol]
                candle_ts = m['candles'][-1]['ts']
                if last.get(symbol) == candle_ts:
                    continue
                last[symbol] = candle_ts
                sig = signal(m['candles'],kind,cfg['strategy'])
                fresh = 0 <= now-(candle_ts+900) <= cfg['poll_seconds']*2
                if sig:
                    account.event('decision',now,symbol=symbol,signal=sig,fresh=fresh,
                                  blocked=bool(account.s['position'] or account.s['halt'] or account.s['daily_halt'] or not fresh))
                    if fresh:
                        available=m['ask_size'] if sig['side']==1 else m['bid_size']
                        account.open(now,symbol,sig,m['bid'],m['ask'],available)
                else:
                    account.event('no_signal',now,symbol=symbol,candle_ts=candle_ts)
            account.s['observed_at'] = now
            for ev in account.events: record(db,run,name,ev)
            db.execute('INSERT OR REPLACE INTO states VALUES(?,?,?)',(run,name,encoded(account.s)))
        record(db,run,'system',{'kind':'heartbeat','ts':now,'source':'Kraken spot proxy','orders_sent':0})


def run_paper(db,cfg,once=False,duration=0):
    run = create_run(db,cfg,'paper',resume=True)
    started, stop = time.monotonic(), [False]
    def shutdown(*_): stop[0]=True
    os_signal.signal(os_signal.SIGTERM,shutdown)
    os_signal.signal(os_signal.SIGINT,shutdown)
    print(encoded({'run':run,'mode':'paper_only','pid':__import__('os').getpid()}),flush=True)
    while not stop[0]:
        try:
            markets = acquire(db,cfg)
            paper_cycle(db,cfg,run,markets)
            print(encoded({'at':time.time(),'status':'observed','run':run}),flush=True)
        except Exception as exc:
            with db:
                record(db,run,'system',{'kind':'collection_error','ts':time.time(),'error':str(exc)})
            print(encoded({'at':time.time(),'status':'collection_error','error':str(exc)}),flush=True)
            if once: raise
        if once or (duration and time.monotonic()-started >= duration): break
        deadline = time.monotonic()+cfg['poll_seconds']
        while not stop[0] and time.monotonic()<deadline:
            time.sleep(min(1,deadline-time.monotonic()))
    return run


def bootstrap_daily_lower(events, started, ended, cfg):
    days = int((ended-started)//86400)
    if days < 2: return None
    pnl = [0.0]*days
    for ev in events:
        i = int((ev['ts']-started)//86400)
        if 0<=i<days: pnl[i] += ev['net_pnl']
    rng = random.Random(cfg['gates']['bootstrap_seed'])
    # Day-block resampling is a diagnostic, not a guarantee or a multiple-testing correction.
    means = sorted(statistics.mean(rng.choices(pnl,k=days)) for _ in range(cfg['gates']['bootstrap_samples']))
    return means[int(len(means)*0.05)]


def report(db,out):
    records = []
    for run,mode,started,manifest in db.execute('SELECT * FROM runs ORDER BY started'):
        manifest = json.loads(manifest); cfg=manifest['config']
        errors = db.execute("SELECT count(*) FROM events WHERE run=? AND kind IN ('collection_error','data_gap')",(run,)).fetchone()[0]
        heartbeat = db.execute("SELECT max(ts) FROM events WHERE run=? AND kind='heartbeat'",(run,)).fetchone()[0]
        first_heartbeat = db.execute("SELECT min(ts) FROM events WHERE run=? AND kind='heartbeat'",(run,)).fetchone()[0]
        for name,raw in db.execute('SELECT candidate,state FROM states WHERE run=? ORDER BY candidate',(run,)):
            s=json.loads(raw)
            risk=next(r for r in cfg['risk_candidates'] if name.split('-')[1]==r['name'])
            summary=Account(cfg,risk,s).summary()
            closed=[json.loads(r[0]) for r in db.execute("SELECT payload FROM events WHERE run=? AND candidate=? AND kind='close' ORDER BY id",(run,name))]
            lower=bootstrap_daily_lower(closed,first_heartbeat or started,heartbeat or started,cfg) if mode=='paper' else None
            elapsed=(heartbeat-first_heartbeat)/86400 if heartbeat is not None and first_heartbeat is not None else 0
            reasons=[]
            if mode!='paper': reasons.append('exploratory_history_only')
            if elapsed<cfg['gates']['min_forward_days']: reasons.append('insufficient_forward_days')
            if s['closed']<cfg['gates']['min_closed_trades']: reasons.append('insufficient_trades')
            if lower is None or lower<=0: reasons.append('daily_bootstrap_lower_not_positive')
            if summary['profit_factor'] is None or summary['profit_factor']<cfg['gates']['min_profit_factor']: reasons.append('profit_factor_not_established')
            if s['max_drawdown']>cfg['gates']['max_peak_drawdown'] or s['halt'] not in (None,'simulated_target_reached'): reasons.append('risk_stop_or_breach')
            if errors: reasons.append('data_quality_errors')
            if s['position']: reasons.append('open_position_not_final')
            stress_name=name if name.endswith('-stress') else name+'-stress'
            stress_row=db.execute('SELECT state FROM states WHERE run=? AND candidate=?',(run,stress_name)).fetchone()
            stress_state=json.loads(stress_row[0]) if stress_row else None
            if not stress_state or stress_state['balance']<=cfg['account']['initial_balance']:
                reasons.append('double_cost_profit_not_established')
            if stress_state and (stress_state['halt'] not in (None,'simulated_target_reached') or
                                 stress_state['max_drawdown']>cfg['gates']['max_peak_drawdown'] or stress_state['position']):
                reasons.append('double_cost_risk_or_unclosed_position')
            records.append({'run':run,'candidate':name,'mode':mode,'forward_days':elapsed,
                            **summary,'bootstrap_daily_mean_lower':lower,
                            'research_gate':'PASS' if not reasons else 'NOT_PASSED','reasons':reasons,
                            'live_ready':False,'live_blockers':['Breakout connection unverified','proxy fills and continuous equity unvalidated']})
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    payload={'generated_at':time.time(),'orders_sent':0,'results':records}
    (out/'latest.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False))
    lines=['# BreakOut 無発注検証レポート','', '実発注：0件。Kraken現物価格を代理データとして使用。Breakoutの実績ではありません。','',
           '| 実行版 | モード | 候補 | 確定残高* | 決済数 | 最大観測DD | 判定 |','|---|---|---|---:|---:|---:|---|']
    for r in records:
        lines.append('| {} | {} | {} | {:.2f} | {} | {:.2f} | {} |'.format(r['run'].split('-')[1],r['mode'],r['candidate'],r['balance'],r['closed_trades'],r['max_drawdown'],r['research_gate']))
    lines += ['', '*残高は含み損益を除きます。保有中の建玉はJSONを参照。', '',
              '過去検証は直近最大720本の探索・動作確認です。全候補を報告し、勝者の自動採用はしません。',
              '無発注検証の最低期間60日・決済100件に加え、日次損益ブートストラップ、コスト2倍、損失・データ品質基準を評価します。',
              '短い履歴、OHLCの順序不明、60秒間隔の価格観測、代理価格、約定・swap時刻の近似により本番適合性は別途確認が必要です。',
              '研究基準を満たしても、このプログラムに実発注機能はありません。']
    (out/'latest.md').write_text('\n'.join(lines)+'\n')
    return payload


def status(db):
    runs=db.execute("SELECT id,started FROM runs WHERE mode='paper' ORDER BY started DESC LIMIT 1").fetchone()
    if not runs: return {'status':'not_started','orders_sent':0}
    row=db.execute("SELECT max(ts) FROM events WHERE run=? AND kind='heartbeat'",(runs[0],)).fetchone()
    age=time.time()-row[0] if row[0] else None
    return {'run':runs[0],'last_heartbeat':row[0],'age_seconds':age,
            'status':'observing' if age is not None and age<150 else 'stale_or_stopped','orders_sent':0,
            'states':{name:json.loads(raw) for name,raw in db.execute('SELECT candidate,state FROM states WHERE run=?',(runs[0],))}}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',default=str(ROOT/'config/research-v1.json'))
    parser.add_argument('--db',default=str(ROOT/'data/research.sqlite3'))
    sub=parser.add_subparsers(dest='command',required=True)
    backtest=sub.add_parser('backtest'); backtest.add_argument('--cached',action='store_true')
    sub.add_parser('collect'); sub.add_parser('status'); sub.add_parser('report')
    paper=sub.add_parser('paper'); paper.add_argument('--once',action='store_true'); paper.add_argument('--duration',type=int,default=0)
    args=parser.parse_args(); cfg=load_config(args.config); db=connect(args.db)
    try:
        if args.command=='status': print(json.dumps(status(db),indent=2)); return
        if args.command=='report': print(encoded({'report':str(ROOT/'reports/latest.md'),'rows':len(report(db,ROOT/'reports')['results'])})); return
        with writer_lock(args.db):
            if args.command=='collect':
                m=acquire(db,cfg); print(encoded({s:len(v['candles']) for s,v in m.items()}))
            elif args.command=='backtest':
                markets=cached_markets(db,cfg) if args.cached else acquire(db,cfg)
                run,results=history_run(db,cfg,markets); report(db,ROOT/'reports')
                print(json.dumps({'run':run,'results':results},indent=2))
            else:
                run_paper(db,cfg,args.once,args.duration)
                report(db,ROOT/'reports')
    finally: db.close()


if __name__=='__main__':
    main()
