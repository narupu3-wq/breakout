import sqlite3,json
from pathlib import Path
c=sqlite3.connect('file:data/research.sqlite3?mode=ro',uri=True);c.execute('BEGIN');result={}
for mode in ['paper']:
 rid,raw=c.execute('select id,manifest from runs where mode=? order by started desc limit 1',(mode,)).fetchone();cfg=json.loads(raw)['config'];rows=[]
 for name in ['mean_reversion-cautious','mean_reversion-cautious-stress','trend-cautious','trend-cautious-stress']:
  intent=fill=None;mult=2 if name.endswith('-stress') else 1;slip=cfg['costs']['slippage_bps']*mult/10000
  for ts,k,raw in c.execute("select ts,kind,payload from events where run=? and candidate=? and kind in ('intent','paper_fill','close') order by id",(rid,name)):
   p=json.loads(raw)
   if k=='intent':intent=p
   elif k=='paper_fill':fill=p
   elif fill and intent:
    gross=fill['qty']*fill['side']*(p['price']-fill['entry']);exit_quote=p['price']/(1-fill['side']*slip)
    rows.append(dict(candidate=name,symbol=p['symbol'],opened=fill['opened'],closed=ts,reason=p['reason'],net=p['net_pnl'],gross_after_slippage=gross,fees_carry=gross-p['net_pnl'],planned_risk=intent['planned_risk'],qty=fill['qty'],stop=fill['stop'],exit_quote=exit_quote,adverse_beyond_stop=(fill['stop']-exit_quote)*fill['side'],loss_above_planned=max(0,-p['net_pnl']-intent['planned_risk'])));fill=intent=None
 result[mode]={'run':rid,'rows':rows,'summary':[{'candidate':n,'closed':len(v),'above_budget_count':sum(x['loss_above_planned']>1e-8 for x in v),'max_loss_above_planned':max(x['loss_above_planned'] for x in v)} for n in sorted(set(x['candidate'] for x in rows)) for v in [[x for x in rows if x['candidate']==n]]]}
c.close()
p=Path(__file__).with_name('20260908T124716Z-evidence.json')
with p.open('x') as f:json.dump(result,f,indent=2)
print(json.dumps([r for r in result['paper']['rows'] if r['closed']>1788860849.007501],indent=2))
