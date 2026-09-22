#!/usr/bin/env python3
"""Read-only, deterministic paper metrics; no market requests or strategy writes."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import shutil
import sqlite3
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parent
VERSION = 'hourly-report-v2'


def read_json(path):
    return json.loads(Path(path).read_text())


def seconds_summary(values):
    """Nearest-rank p95; empty samples stay unavailable, never zero."""
    values = sorted(values)
    if not values:
        return dict(count=0, mean=None, p95=None, maximum=None)
    return dict(count=len(values), mean=sum(values)/len(values),
                p95=values[math.ceil(len(values)*0.95)-1], maximum=values[-1])


def latency_metrics(events, cfg, now):
    """Recorded cycle timestamps, not CPU execution or network-only latency."""
    poll = cfg['poll_seconds']
    candle_seconds = cfg.get('interval_minutes', 15)*60
    beats = sorted(set(e['ts'] for e in events if e['kind']=='heartbeat'))
    errors = [e for e in events if e['kind']=='collection_error']
    intervals = [(end, end-start, any(start < e['ts'] <= end for e in errors))
                 for start, end in zip(beats, beats[1:])]
    # One observation per symbol/candle across strategy/cost variants.
    checks, signals = {}, {}
    invalid = []
    for e in events:
        if e['kind'] not in ('decision', 'no_signal'):
            continue
        p = e['payload']
        candle = p.get('signal', {}).get('signal_ts') if e['kind']=='decision' else p.get('candle_ts')
        if not isinstance(candle, (int, float)) or not math.isfinite(candle) or not p.get('symbol'):
            invalid.append(e['ts'])
            continue
        delay = e['ts']-(candle+candle_seconds)
        if delay < 0:
            invalid.append(e['ts'])
            continue
        key = (p['symbol'], candle)
        for target in ([checks, signals] if e['kind']=='decision' else [checks]):
            if key not in target or e['ts'] < target[key][0]:
                target[key] = (e['ts'], delay)
    result = {}
    for label, lower in [('total', float('-inf')), ('last_1h', now-3600)]:
        included = lambda ts: lower < ts <= now
        spans = [x for x in intervals if included(x[0])]
        delays = [d for ts,d in checks.values() if included(ts)]
        signal_delays = [d for ts,d in signals.values() if included(ts)]
        result[label] = dict(
            observation_interval_seconds=seconds_summary([d for _,d,_ in spans]),
            interval_excess_over_poll_seconds=seconds_summary([max(0,d-poll) for _,d,_ in spans]),
            intervals_with_collection_error=sum(error for _,_,error in spans),
            gaps_over_threshold=sum(d > poll*2.5 for _,d,_ in spans),
            candle_check_delay_seconds=seconds_summary(delays),
            signal_delay_seconds=seconds_summary(signal_delays),
            stale_signal_observations=sum(d > poll*2 for d in signal_delays),
            invalid_check_events=sum(included(ts) for ts in invalid),
            collection_errors=sum(included(e['ts']) for e in errors),
            error_messages=dict(Counter(e['payload'].get('error','unspecified') for e in errors if included(e['ts']))))
    return dict(poll_seconds=poll, gap_threshold_seconds=poll*2.5,
                signal_freshness_seconds=poll*2, api_duration_seconds=None,
                **result)


def collect(db_path, now, review=None):
    """One consistent DB snapshot. The hourly window is (now-3600, now]."""
    db = sqlite3.connect(Path(db_path).resolve().as_uri() + '?mode=ro', uri=True)
    try:
        db.execute('BEGIN')
        run_row = db.execute("SELECT id,manifest FROM runs WHERE mode='paper' ORDER BY started DESC LIMIT 1").fetchone()
        if not run_row:
            return dict(version=VERSION, as_of=now, status='no_paper_run', candidates=[], review_due=review is None or now-review['last_review_completed_at'] >= 10800)
        run, manifest = run_row
        cfg = json.loads(manifest)['config']
        stale_after = cfg['poll_seconds'] * 2.5
        events = [dict(candidate=c, ts=t, kind=k, payload=json.loads(p)) for c,t,k,p in db.execute('SELECT candidate,ts,kind,payload FROM events WHERE run=? AND ts<=? ORDER BY id', (run,now))]
        quotes = {s:json.loads(p) for s,p in db.execute('SELECT symbol,payload FROM snapshots WHERE id IN (SELECT max(id) FROM snapshots WHERE observed<=? GROUP BY symbol)', (now,))}
        states = [(c,json.loads(s)) for c,s in db.execute('SELECT candidate,state FROM states WHERE run=? ORDER BY candidate', (run,))]
    finally:
        db.close()
    recent = [e for e in events if now-3600 < e['ts'] <= now]
    totals, hourly = Counter(e['kind'] for e in events), Counter(e['kind'] for e in recent)
    beats = [e['ts'] for e in events if e['kind']=='heartbeat']
    age = now-max(beats) if beats else None
    warnings, rows = [], []
    for name,s in states:
        closed = [e for e in events if e['kind']=='close' and e['candidate']==name]
        hour = [e for e in recent if e['kind']=='close' and e['candidate']==name]
        p = s['position']; q = quotes.get(p['symbol']) if p else None
        quote_status, unrealized, mark = 'not_needed', 0.0, None
        quote_ts = q.get('observed_at') if q else None
        if p:
            unrealized = None
            quote_status = 'missing'
            if q:
                bid, ask = q.get('bid'), q.get('ask')
                valid = all(isinstance(v,(int,float)) and math.isfinite(v) for v in (bid,ask,quote_ts)) and 0 < bid <= ask
                if not valid:
                    quote_status = 'invalid'
                elif quote_ts > now or (p.get('opened') is not None and quote_ts < p['opened']):
                    quote_status = 'invalid_time'
                elif now-quote_ts > stale_after:
                    quote_status = 'stale'
                else:
                    quote_status = 'fresh'
                    mark = bid if p['side']==1 else ask
                    unrealized = p['qty']*p['side']*(mark-p['entry'])
        if quote_status not in ('fresh','not_needed'):
            warnings.append(name+': quote_'+quote_status)
        if len(closed) != s['closed']:
            warnings.append(name+': close_count_mismatch')
        if s.get('observed_at',now)>now:
            warnings.append(name+': state_after_report_time')
            unrealized = None
        rows.append(dict(candidate=name,closed_1h=len(hour),net_1h=sum(e['payload']['net_pnl'] for e in hour),closed_total=len(closed),net_total=sum(e['payload']['net_pnl'] for e in closed),balance=s['balance'],position=p,unrealized=unrealized,quote_ts=quote_ts,quote_status=quote_status,mark_price=mark,dd=s['max_drawdown'],halt=s['halt'],daily_halt=s['daily_halt'],unfilled_1h=sum(e['candidate']==name and e['kind']=='unfilled' for e in recent),unfilled_total=sum(e['candidate']==name and e['kind']=='unfilled' for e in events)))
    if not rows:
        warnings.append('no_candidate_states')
    if totals['collection_error'] or totals['data_gap']:
        warnings.append('recorded_data_quality_errors')
    if any(x['halt'] or x['daily_halt'] for x in rows):
        warnings.append('candidate_halted')
    if review and review['last_review_completed_at']>now:
        warnings.append('review_time_in_future')
    return dict(latency=latency_metrics(events,cfg,now),version=VERSION,as_of=now,run=run,status='observing' if age is not None and 0<=age<=stale_after and not warnings else 'attention_required',observed_hours=(max(beats)-min(beats))/3600 if beats else 0,heartbeat_age_seconds=age,stale_after_seconds=stale_after,events=dict(totals),events_1h=dict(hourly),errors=[e for e in events if e['kind'] in ('collection_error','data_gap')],error_count_1h=hourly['collection_error']+hourly['data_gap'],candidates=rows,quotes=quotes,warnings=warnings,last_review=review,review_due=review is None or now-review['last_review_completed_at']>=10800,orders_sent=0)


def monitoring_reference(root, now):
    paths = sorted((root/'reports/monitoring/sp500').glob('*.json'))
    if not paths:
        return dict(status='no_monitor_record')
    path = paths[-1]; data = read_json(path)
    ts = data.get('observed_at')
    if isinstance(ts,str):
        ts = datetime.fromisoformat(ts.replace('Z','+00:00')).timestamp()
    return dict(status='stored_reference_not_rechecked',file=str(path),record_age_seconds=now-ts if ts is not None else None,data=data)


def render(r):
    lines=['# BreakOut 毎時集計', '', '取得UTC: '+datetime.fromtimestamp(r['as_of'],timezone.utc).isoformat(), '状態: '+r['status'], '実発注0。公開代理価格による仮想結果。候補は別口座で合算しない。']
    if 'run' not in r:
        return '\n'.join(lines+['paper runなし。レビュー要否: '+str(r['review_due'])])+'\n'
    lines += ['',f'観測時間: {r["observed_hours"]:.2f} h / heartbeat経過秒: {r["heartbeat_age_seconds"]}', '直近1時間は取得時刻からの半開区間 (開始, 終了]。', 'イベント累積: '+json.dumps(r['events']), 'イベント直近1h: '+json.dumps(r['events_1h']), '', '| 候補 | 1h決済 | 1h確定USD | 累積決済 | 累積確定USD | 含みUSD | 最大DD USD |', '|---|---:|---:|---:|---:|---:|---:|']
    for x in r['candidates']:
        value='未評価' if x['unrealized'] is None else f'{x["unrealized"]:.4f}'
        lines.append(f'|{x["candidate"]}|{x["closed_1h"]}|{x["net_1h"]:.4f}|{x["closed_total"]}|{x["net_total"]:.4f}|{value}|{x["dd"]:.4f}|')
    lines += ['', '確定は決済取引の手数料・swap込み。含みは退出手数料・追加滑り前。古い/不正/欠損気配は未評価。']
    for x in r['candidates']:
        if x['position']:
            lines.append(f'- {x["candidate"]}: {x["position"]["symbol"]} side={x["position"]["side"]}, quote={x["quote_status"]}, quote_ts={x["quote_ts"]}')
    lines += ['', '## 観測・判断の遅延', '',
              '単位は秒。p95はnearest-rank。直近1hの間隔は終了時刻で集計し、開始が窓外でも含む。',
              '| 指標 | 累積 件数 / 平均 / p95 / 最大 | 直近1h 件数 / 平均 / p95 / 最大 |',
              '|---|---|---|']
    latency = r['latency']
    for key, label in [('observation_interval_seconds','観測間隔'),
                       ('interval_excess_over_poll_seconds','設定待機時間を超える分'),
                       ('candle_check_delay_seconds','足確定→条件確認'),
                       ('signal_delay_seconds','足確定→シグナル判断')]:
        cells = []
        for window in ('total','last_1h'):
            metric = latency[window][key]
            cells.append(str(metric['count'])+' / '+' / '.join('未計測' if metric[k] is None else f"{metric[k]:.2f}" for k in ('mean','p95','maximum')))
        lines.append('|'+label+'|'+'|'.join(cells)+'|')
    for window in ('total','last_1h'):
        x = latency[window]
        lines.append(f"- {window}: 収集エラー {x['collection_errors']}件、エラーを挟む観測間隔 {x['intervals_with_collection_error']}件、{latency['gap_threshold_seconds']}秒超の間隔 {x['gaps_over_threshold']}件、鮮度期限超のシグナル観測 {x['stale_signal_observations']}件、不正な判断イベント {x['invalid_check_events']}件。")
        if x['error_messages']:
            lines.append('  エラー内訳: '+json.dumps(x['error_messages'],ensure_ascii=False))
    lines += ['同じ銘柄・足は候補間で重複集計しない。初回起動時の古い足も含む。',
              '判断時刻は取得完了を基準としたイベント時刻。実際の計算終了時刻ではない。',
              'API通信時間・成功前の再試行回数は未記録。待機超過分は通信・処理・スケジュール・障害等を含み、通信遅延とは断定できない。',
              'collection_errorは取得以外の処理例外も含む。進行中の停止は上記heartbeat経過秒で確認。',
              'この診断だけでは遅延による損益影響や最適な取得間隔は判定できない。']
    lines += ['', '警告: '+str(r['warnings']), '停止: '+str([(x['candidate'],x['halt'],x['daily_halt']) for x in r['candidates'] if x['halt'] or x['daily_halt']]), '改善レビュー要否: '+str(r['review_due'])+'。この集計はレビューを実行せず、完了時刻も更新しない。', '前回レビュー: '+json.dumps(r['last_review'],ensure_ascii=False), '', 'S&P500: 保存済み監視記録の参照のみ。この実行では価格/営業状態の再確認なし。', json.dumps(r.get('sp500',{}),ensure_ascii=False), '', '回収実績は docs/recovery-goal.md と実受取の証拠で別途確認。仮想利益を実受取に算入しない。', '旧固定ゲートと期間可変の採用判断は別。戦略の有効性はこの集計だけでは判定しない。']
    return '\n'.join(lines)+'\n'


def save_bundle(out, report):
    """Publish a complete unique directory atomically; old reports are untouched."""
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    target=out/(datetime.fromtimestamp(report['as_of'],timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'-'+uuid.uuid4().hex[:8])
    stage=Path(tempfile.mkdtemp(prefix='.pending-',dir=out))
    try:
        source=Path(__file__).read_bytes()
        report={**report,'reporter_sha256':hashlib.sha256(source).hexdigest()}
        (stage/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False))
        (stage/'report.md').write_text(render(report))
        (stage/'reporter.py').write_bytes(source)
        stage.rename(target)
    except BaseException:
        shutil.rmtree(stage)
        raise
    return target


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',type=Path,default=ROOT/'data/research.sqlite3')
    parser.add_argument('--out',type=Path,default=ROOT/'reports/hourly')
    args=parser.parse_args()
    review_path=ROOT/'reports/reviews/schedule-state.json'
    review=read_json(review_path) if review_path.exists() else None
    now=time.time(); report=collect(args.db,now,review)
    report['sp500']=monitoring_reference(ROOT,now)
    report['experiments']=list(map(str,(ROOT/'experiments').glob('*')))
    bundle=save_bundle(args.out,report)
    print(json.dumps(dict(report=str(bundle/'report.md'),json=str(bundle/'report.json'),status=report['status'],review_due=report['review_due']),ensure_ascii=False))


if __name__=='__main__':
    main()
