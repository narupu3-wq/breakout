import json,datetime
from pathlib import Path
source=Path('experiments/realtime-v1/data/sessions/2026-09-08T03-55-29.089Z-314077c8/raw/2026-09-09T04.jsonl')
a,b=1788928860.779476,1788928922.851476
stop=78924.15877142859
accepted=[];rejected=0;last=-float('inf')
for line in source.open():
 r=json.loads(line);t=r['received']
 if t>b:break
 for q in r['message'].get('data',[]):
  if q.get('symbol')!='BTC/USD':continue
  s=datetime.datetime.fromisoformat(q['timestamp'].replace('Z','+00:00')).timestamp()
  valid=q['ask']>=q['bid']>0 and -5<=t-s<=30 and s>=last
  if valid:last=s
  if t<a:continue
  if not valid:rejected+=1;continue
  accepted.append(dict(received=t,source=s,bid=q['bid'],ask=q['ask']))
cross=next((r for r in accepted if r['ask']>=stop),None)
result=dict(source=str(source),window=[a,b],stop=stop,accepted=len(accepted),rejected=rejected,first_cross=cross,first=accepted[0],last=accepted[-1],max_gap_seconds=max(y['received']-x['received'] for x,y in zip(accepted,accepted[1:])),note='Historical diagnostic, no executable fill claim. Timestamp/quote filtering only; websocket ticker has no sequence guarantee.')
Path(__file__).with_name('20260914T220226Z-stress-replay.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
