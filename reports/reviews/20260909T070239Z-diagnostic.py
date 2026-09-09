import sqlite3,json
from pathlib import Path
c=sqlite3.connect('file:data/research.sqlite3?mode=ro',uri=True)
c.execute('BEGIN')
rows=[dict(ts=t,kind=k,candidate=n,payload=json.loads(p)) for t,k,n,p in c.execute("select ts,kind,candidate,payload from events where run=? and ts>? and ts<=? and kind in ('intent','paper_fill','close','collection_error') order by id",('paper-a933e913646055c5',1788915400,1788937359.367079))]
positions={};out=[]
for r in rows:
 n=r['candidate'];p=r['payload']
 if r['kind']=='paper_fill':positions[n]=p
 if r['kind']!='close' or '-cautious' not in n:continue
 e=positions[n];mult=2 if n.endswith('stress') else 1
 gross=e['qty']*e['side']*(p['price']-e['entry']);fee=e['qty']*p['price']*.0004*mult
 carry=gross-fee-e['entry_fee']-p['net_pnl']
 raw=p['price']/(1-e['side']*.0005*mult)
 ideal=e['stop']*(1-e['side']*.0005*mult)
 ideal_net=e['qty']*e['side']*(ideal-e['entry'])-e['qty']*ideal*.0004*mult-e['entry_fee']-carry
 snapshots=[dict(observed=t,payload=json.loads(v)) for t,v in c.execute('select observed,payload from snapshots where symbol=? and observed<=? order by observed desc limit 2',(e['symbol'],r['ts']))]
 out.append(dict(candidate=n,entry=e,close=p,gross_pnl=gross,exit_fee=fee,carry_inferred=carry,raw_exit_quote=raw,net_if_observed_at_exact_stop_same_carry=ideal_net,extra_loss_beyond_exact_stop=ideal_net-p['net_pnl'],snapshots=snapshots))
c.close()
result=dict(events=rows,exit_decomposition=out,note='Counterfactual exact-stop quote holds carry fixed; no claim of executable fill or faster-poll benefit. Carry inferred from frozen accounting identity.')
with Path(__file__).with_name('20260909T070239Z-evidence.json').open('x') as f:json.dump(result,f,indent=2)
for x in out:print(json.dumps({k:v for k,v in x.items() if k not in ('entry','close','snapshots')},indent=2))
