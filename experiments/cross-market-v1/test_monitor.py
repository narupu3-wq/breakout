import unittest
import json
from datetime import datetime
from pathlib import Path
from monitor import normalize, phase, summarize
CFG=json.loads((Path(__file__).parent/'config.json').read_text())
def ts(x):return datetime.fromisoformat(x).timestamp()
def row(t, x, valid=True):
 return dict(ts=t,valid=valid,phase='regular',quotes={s:dict(mid=100+x*k,spread_bps=2,received=t) for s,k in [('BTC',1),('ETH',2),('XYZ100',-1),('SP500',-2)]})
class Tests(unittest.TestCase):
 def test_calendar(self):
  for date,expected in [('2026-09-08T13:30:00+00:00','regular'),('2026-09-07T14:00:00+00:00','outside'),('2026-11-27T18:00:00+00:00','outside'),('2026-12-24T17:59:00+00:00','regular'),('2027-01-04T15:00:00+00:00','calendar_unknown')]: self.assertEqual(phase(ts(date),CFG),expected)
 def test_bad_quotes(self):
  raw={'coin':'xyz:XYZ100','time':100000,'levels':[[{'px':'100'}],[{'px':'101'}]]}
  self.assertEqual(normalize('XYZ100',raw,101,CFG)['mid'],100.5)
  with self.assertRaises(ValueError):normalize('XYZ100',raw,120,CFG)
  raw['levels'][0][0]['px']='NaN'
  with self.assertRaises(ValueError):normalize('XYZ100',raw,101,CFG)
 def test_minimum_and_gaps(self):
  rows=[row(i*60,(i%2)/10) for i in range(32)]
  p=summarize(rows,CFG)['phases']['regular'];self.assertEqual(p['return_pairs'],31)
  self.assertLess(p['pairs']['XYZ100/BTC']['correlation'],-0.99)
  rows[10]['valid']=False
  p=summarize(rows,CFG)['phases']['regular'];self.assertEqual(p['return_pairs'],29)
  self.assertIsNone(p['pairs']['XYZ100/BTC']['correlation'])
 def test_ranges_are_separate_from_profit(self):
  p=summarize([row(i*60,i/10) for i in range(15)],CFG)['phases']['regular']
  self.assertEqual(len(p['sampled_15m_ranges']['BTC']),1)
  self.assertEqual(p['sampled_15m_ranges']['BTC'][0]['assumed_cost_bps'],20)
 def test_empty(self):self.assertEqual(summarize([],CFG)['phases']['regular']['pairs']['XYZ100/BTC']['correlation'],None)
if __name__=='__main__':unittest.main()
