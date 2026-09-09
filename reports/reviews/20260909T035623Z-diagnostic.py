import sqlite3,json
from pathlib import Path
c=sqlite3.connect('file:data/research.sqlite3?mode=ro',uri=True)
c.execute('BEGIN')
rows=[]
for ts,kind,candidate,payload in c.execute("select ts,kind,candidate,payload from events where run=? and ts>? and ts<=? and kind in ('intent','paper_fill','close','collection_error') order by id",('paper-a933e913646055c5',1788915276.257656,1788926183.122655)):
 rows.append(dict(ts=ts,kind=kind,candidate=candidate,payload=json.loads(payload)))
c.close()
p=Path(__file__).with_name('20260909T035623Z-evidence.json')
with p.open('x') as f:json.dump(rows,f,indent=2)
print(json.dumps(rows[:2],indent=2))
