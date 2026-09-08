#!/usr/bin/env python3
"""Public-data comparison only. No orders, accounts, paid APIs or baseline writes."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import fcntl
import hashlib
import itertools
import json
import math
from pathlib import Path
import signal
import sqlite3
import statistics
import subprocess
import sys
import threading
import time
import urllib.request
import uuid
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
SYMBOLS=('XYZ100','SP500','BTC','ETH')

def encode(x): return json.dumps(x,ensure_ascii=False,allow_nan=False)
def request(url,body=None):
    req=urllib.request.Request(url,data=encode(body).encode() if body else None,
                               headers={'Content-Type':'application/json','User-Agent':'BreakOut-research/1'})
    with urllib.request.urlopen(req,timeout=10) as response:
        result=json.load(response)
    return result,time.time()

def normalize(symbol,raw,received,cfg):
    if symbol in ('XYZ100','SP500'):
        if raw['coin']!='xyz:'+symbol: raise ValueError('wrong instrument')
        bid,ask=(float(side[0]['px']) for side in raw['levels'])
        source=float(raw['time'])/1000
        if not math.isfinite(source) or not -5<=received-source<=cfg['max_source_age_seconds']:
            raise ValueError('stale/future source')
        venue='Hyperliquid xyz perpetual proxy'
    else:
        if raw['error']: raise ValueError(str(raw['error']))
        if len(raw['result'])!=1: raise ValueError('ambiguous Kraken pair')
        q=next(iter(raw['result'].values())); bid,ask=float(q['b'][0]),float(q['a'][0])
        source=None; venue='Kraken spot proxy'
    if not all(math.isfinite(v) and v>0 for v in (bid,ask)) or bid>ask: raise ValueError('invalid bid/ask')
    return dict(symbol=symbol,bid=bid,ask=ask,mid=(bid+ask)/2,spread_bps=(ask-bid)/((bid+ask)/2)*10000,
                received=received,source_time=source,venue=venue,raw=raw)

def fetch(symbol,cfg):
    if symbol in ('XYZ100','SP500'):
        raw,received=request('https://api.hyperliquid.xyz/info',{'type':'l2Book','coin':'xyz:'+symbol})
    else:
        raw,received=request('https://api.kraken.com/0/public/Ticker?pair='+('XBTUSD' if symbol=='BTC' else 'ETHUSD'))
    return normalize(symbol,raw,received,cfg)

def phase(ts,cfg):
    d=datetime.fromtimestamp(ts,ZoneInfo('America/New_York')); date=d.date().isoformat()
    if d.year!=2026: return 'calendar_unknown'
    if d.weekday()>=5 or date in cfg['holidays_2026']: return 'outside'
    end=13*60 if date in cfg['early_closes_2026'] else 16*60
    return 'regular' if 570<=d.hour*60+d.minute<end else 'outside'

def collect(cfg):
    quotes={}; errors={}
    with ThreadPoolExecutor(max_workers=4) as pool:
        pending={s:pool.submit(fetch,s,cfg) for s in SYMBOLS}
        for s,f in pending.items():
            try: quotes[s]=f.result()
            except Exception as exc: errors[s]=str(exc)
    ts=time.time(); times=[q['source_time'] if q['source_time'] is not None else q['received'] for q in quotes.values()]
    skew=max(times)-min(times) if times else None
    valid=len(quotes)==4 and skew<=cfg['max_skew_seconds']
    return dict(ts=ts,phase=phase(ts,cfg),valid=valid,quotes=quotes,errors=errors,skew_seconds=skew,origin='forward_observation')

def corr(xs,ys,minimum):
    if len(xs)<minimum: return None
    xbar,ybar=statistics.mean(xs),statistics.mean(ys)
    denom=math.sqrt(sum((x-xbar)**2 for x in xs)*sum((y-ybar)**2 for y in ys))
    return sum((x-xbar)*(y-ybar) for x,y in zip(xs,ys))/denom if denom else None

def summarize(rows,cfg):
    result={}
    for label in ('regular','outside','calendar_unknown'):
        subset=[r for r in rows if r['phase']==label and r['valid']]
        returns=[]
        for a,b in zip(rows,rows[1:]):
            if not (a['valid'] and b['valid'] and a['phase']==b['phase']==label and 45<=b['ts']-a['ts']<=90): continue
            if any(not 45<=b['quotes'][s]['received']-a['quotes'][s]['received']<=90 for s in SYMBOLS): continue
            returns.append({s:(b['quotes'][s]['mid']/a['quotes'][s]['mid']-1)*10000 for s in SYMBOLS})
        pairs={}
        for a,b in itertools.combinations(SYMBOLS,2):
            xs=[r[a] for r in returns];ys=[r[b] for r in returns]
            pairs[a+'/'+b]=dict(n=len(xs),correlation=corr(xs,ys,cfg['min_correlation_pairs']),
                both_down=sum(x<0 and y<0 for x,y in zip(xs,ys)))
        # Nonoverlapping 15-minute received-price ranges: diagnostics, not tradable profit.
        windows={}
        for r in subset: windows.setdefault(int(r['ts']//900),[]).append(r)
        ranges={s:[] for s in SYMBOLS}
        for group in windows.values():
            if len(group)<12 or group[-1]['ts']-group[0]['ts']<660:continue
            if any(b['ts']-a['ts']>90 for a,b in zip(group,group[1:])):continue
            for s in SYMBOLS:
                mids=[r['quotes'][s]['mid'] for r in group]
                span=(max(mids)-min(mids))/mids[0]*10000
                spread=statistics.mean(r['quotes'][s]['spread_bps'] for r in group)
                cost=cfg['fee_roundtrip_bps']+cfg['slippage_roundtrip_bps']+spread
                ranges[s].append(dict(range_bps=span,assumed_cost_bps=cost,range_to_cost=span/cost))
        result[label]=dict(samples=len(subset),return_pairs=len(returns),pairs=pairs,
            mean_spread_bps={s:statistics.mean(r['quotes'][s]['spread_bps'] for r in subset) if subset else None for s in SYMBOLS},
            index_moves_when_both_crypto_quiet={s:sum(abs(r[s])>=cfg['index_move_bps'] and max(abs(r['BTC']),abs(r['ETH']))<cfg['quiet_crypto_bps'] for r in returns) for s in ('XYZ100','SP500')},
            sampled_15m_ranges=ranges)
    return dict(observations=len(rows),invalid=sum(not r['valid'] for r in rows),phases=result,
        limitations=['proxy quotes, not Breakout fills','range is not realizable profit','cost assumes 8bps fees +10bps slippage +proxy spread; excludes swap','30 pairs only enables diagnostic, not acceptance','missing intervals not interpolated'])

def connect():
    db=sqlite3.connect(DATA/'observations.sqlite3');db.execute('PRAGMA journal_mode=WAL')
    db.executescript('CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY,started REAL,config TEXT); CREATE TABLE IF NOT EXISTS observations(id INTEGER PRIMARY KEY,run TEXT,payload TEXT);')
    return db

def report():
    db=sqlite3.connect((DATA/'observations.sqlite3').resolve().as_uri()+'?mode=ro',uri=True)
    try:
        db.execute('BEGIN'); run,started,config=db.execute('SELECT * FROM runs ORDER BY started DESC LIMIT 1').fetchone()
        rows=[json.loads(x[0]) for x in db.execute('SELECT payload FROM observations WHERE run=? ORDER BY id',(run,))]
    finally: db.close()
    r=dict(run=run,started=started,as_of=time.time(),**summarize(rows,json.loads(config)))
    out=ROOT/'reports';out.mkdir(exist_ok=True);dest=out/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8]+'.json')
    dest.write_text(encode(r)+'\n');print(encode({'report':str(dest),'observations':len(rows),'invalid':r['invalid']}))

def run(seconds):
    DATA.mkdir(exist_ok=True)
    with (DATA/'writer.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        cfg=json.loads((ROOT/'config.json').read_text());session=uuid.uuid4().hex
        archive=DATA/'runs'/session;archive.mkdir(parents=True)
        for name in ('monitor.py','config.json'): (archive/name).write_bytes((ROOT/name).read_bytes())
        raw,received=request('https://api.hyperliquid.xyz/info',{'type':'meta','dex':'xyz'})
        names={x['name'] for x in raw['universe'] if not x.get('isDelisted')}
        if not {'xyz:XYZ100','xyz:SP500'}<=names:raise ValueError('missing instruments')
        (archive/'metadata.json').write_text(encode({'received':received,'response':raw}))
        (archive/'manifest.json').write_text(encode({'python':sys.version,'fingerprint':hashlib.sha256((archive/'monitor.py').read_bytes()+(archive/'config.json').read_bytes()).hexdigest()}))
        db=connect()
        with db: db.execute('INSERT INTO runs VALUES(?,?,?)',(session,time.time(),encode(cfg)))
        stop=threading.Event();signal.signal(signal.SIGTERM,lambda *_:stop.set());signal.signal(signal.SIGINT,lambda *_:stop.set())
        started=time.monotonic(); last_report=None
        try:
            while not stop.is_set():
                cycle=time.monotonic();r=collect(cfg)
                with db: db.execute('INSERT INTO observations(run,payload) VALUES(?,?)',(session,encode(r)))
                status=dict(run=session,updated=time.time(),status='observing' if r['valid'] else 'data_error',last=r,orders_sent=0,ai_calls=0)
                tmp=DATA/'status.tmp';tmp.write_text(encode(status));tmp.replace(DATA/'status.json')
                if last_report is None or time.monotonic()-last_report>=3600:
                    report();last_report=time.monotonic()
                if seconds and time.monotonic()-started>=seconds:break
                while time.monotonic()-cycle<cfg['poll_seconds'] and not stop.is_set():
                    if (DATA/'stop.request').exists(): (DATA/'stop.request').unlink();stop.set()
                    if seconds and time.monotonic()-started>=seconds:stop.set()
                    stop.wait(0.5)
        finally:
            db.close()
            if (DATA/'status.json').exists():
                status['status']='stopped';status['updated']=time.time();(DATA/'status.json').write_text(encode(status))

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['run','start','stop','status','report']);p.add_argument('--seconds',type=float,default=0);args=p.parse_args()
    if args.command=='run':run(args.seconds)
    elif args.command=='report':report()
    elif args.command=='status':
        r=json.loads((DATA/'status.json').read_text()) if (DATA/'status.json').exists() else {'status':'not_started'}
        if 'updated' in r:
            r['age_seconds']=time.time()-r['updated']
            if r['age_seconds']>150:r['status']='stale'
        if 'last' in r:r['last']={k:v for k,v in r['last'].items() if k!='quotes'}
        print(encode(r))
    elif args.command=='stop':(DATA/'stop.request').write_text('stop')
    else:
        DATA.mkdir(exist_ok=True)
        with (DATA/'writer.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            (DATA/'stop.request').unlink(missing_ok=True)
        with (DATA/'service.log').open('ab') as log:
            child=subprocess.Popen([sys.executable,str(ROOT/'monitor.py'),'run'],stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
        time.sleep(1)
        if child.poll() is not None:raise RuntimeError('observer exited; inspect service.log')
        print(encode({'started_pid':child.pid}))

if __name__=='__main__':main()
