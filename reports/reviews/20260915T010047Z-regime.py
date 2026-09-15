import sqlite3,json,statistics
from pathlib import Path
c=sqlite3.connect('file:experiments/resume-20260914-v1/data/research.sqlite3?mode=ro',uri=True);c.execute('BEGIN')
rows=[]
for t,p in c.execute("select ts,payload from events where candidate='mean_reversion-cautious' and kind='intent' and ts<=? order by id",(1789434047.757516,)):
 p=json.loads(p)
 if p['symbol']!='BTCUSD':continue
 ts=p['signal']['signal_ts'];bars=[json.loads(x[0]) for x in c.execute('select payload from candles where symbol=? and ts<=? order by ts desc limit 33',('BTCUSD',ts))][::-1]
 prev=[b['close'] for b in bars[:-1]];cur=bars[-1]['close']
 rows.append(dict(intent=t,signal_ts=ts,side=p['signal']['side'],planned_risk=p['planned_risk'],z=(cur-statistics.mean(prev))/statistics.pstdev(prev),return_8h=cur/prev[0]-1,close=cur))
prior=[json.loads(x[0]) for x in c.execute('select payload from candles where symbol=? and ts<? order by ts',('BTCUSD',1789380000))]
zshort=[]
for i in range(32,len(prior)-16):
 h=[x['close'] for x in prior[i-32:i]];sd=statistics.pstdev(h)
 if sd and (prior[i]['close']-statistics.mean(h))/sd>=2:
  zshort.append(dict(ts=prior[i]['ts'],return_next_4h=prior[i+16]['close']/prior[i]['close']-1))
out=dict(forward_intents=rows,exploratory_prior_signals=len(zshort),prior_up_after_4h=sum(x['return_next_4h']>0 for x in zshort),prior_down_after_4h=sum(x['return_next_4h']<0 for x in zshort),prior_examples=zshort,note='Overlapping 15m signals, gross close-to-close returns, no costs or stop simulation; exploratory diagnostic, not independent trades or validation.')
with Path(__file__).with_name('20260915T010047Z-regime.json').open('x') as f:json.dump(out,f,indent=2)
print(json.dumps({k:v for k,v in out.items() if k!='prior_examples'},indent=2))
