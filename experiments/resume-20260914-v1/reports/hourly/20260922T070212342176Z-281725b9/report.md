# BreakOut 毎時集計

取得UTC: 2026-09-22T07:02:12.342176+00:00
状態: attention_required
実発注0。公開代理価格による仮想結果。候補は別口座で合算しない。

観測時間: 188.98 h / heartbeat経過秒: 0.4306669235229492
直近1時間は取得時刻からの半開区間 (開始, 終了]。
イベント累積: {"daily_reset": 72, "decision": 1360, "no_signal": 10752, "heartbeat": 10965, "intent": 341, "paper_fill": 341, "close": 339, "collection_error": 3, "risk_budget_exhausted": 3}
イベント直近1h: {"heartbeat": 59, "no_signal": 64}

| 候補 | 1h決済 | 1h確定USD | 累積決済 | 累積確定USD | 含みUSD | 最大DD USD |
|---|---:|---:|---:|---:|---:|---:|
|mean_reversion-cautious|0|0.0000|50|-44.6263|0.0000|47.7347|
|mean_reversion-cautious-stress|0|0.0000|43|-44.7427|0.0000|46.8944|
|mean_reversion-moderate|0|0.0000|52|-50.7680|0.0000|53.8764|
|mean_reversion-moderate-stress|0|0.0000|54|-74.7465|0.0000|76.8982|
|trend-cautious|0|0.0000|34|-10.3941|-1.0912|33.1980|
|trend-cautious-stress|0|0.0000|36|-43.0472|0.0000|44.8551|
|trend-moderate|0|0.0000|34|-12.6714|-1.0912|35.4752|
|trend-moderate-stress|0|0.0000|36|-39.7750|0.0000|46.9629|

確定は決済取引の手数料・swap込み。含みは退出手数料・追加滑り前。古い/不正/欠損気配は未評価。
- trend-cautious: BTCUSD side=-1, quote=fresh, quote_ts=1790060530.810524
- trend-moderate: BTCUSD side=-1, quote=fresh, quote_ts=1790060530.810524

## 観測・判断の遅延

単位は秒。p95はnearest-rank。直近1hの間隔は終了時刻で集計し、開始が窓外でも含む。
| 指標 | 累積 件数 / 平均 / p95 / 最大 | 直近1h 件数 / 平均 / p95 / 最大 |
|---|---|---|
|観測間隔|10964 / 62.05 / 63.88 / 131.53|59 / 61.86 / 62.91 / 63.31|
|設定待機時間を超える分|10964 / 2.05 / 3.88 / 71.53|59 / 1.86 / 2.91 / 3.31|
|足確定→条件確認|1514 / 32.91 / 60.99 / 194.24|8 / 26.84 / 45.56 / 45.56|
|足確定→シグナル判断|267 / 33.94 / 61.66 / 194.24|0 / 未計測 / 未計測 / 未計測|
- total: 収集エラー 3件、エラーを挟む観測間隔 3件、150.0秒超の間隔 0件、鮮度期限超のシグナル観測 1件、不正な判断イベント 0件。
  エラー内訳: {"OHLC data is stale": 3}
- last_1h: 収集エラー 0件、エラーを挟む観測間隔 0件、150.0秒超の間隔 0件、鮮度期限超のシグナル観測 0件、不正な判断イベント 0件。
同じ銘柄・足は候補間で重複集計しない。初回起動時の古い足も含む。
判断時刻は取得完了を基準としたイベント時刻。実際の計算終了時刻ではない。
API通信時間・成功前の再試行回数は未記録。待機超過分は通信・処理・スケジュール・障害等を含み、通信遅延とは断定できない。
collection_errorは取得以外の処理例外も含む。進行中の停止は上記heartbeat経過秒で確認。
この診断だけでは遅延による損益影響や最適な取得間隔は判定できない。

警告: ['recorded_data_quality_errors', 'candidate_halted']
停止: [('mean_reversion-cautious', 'risk_budget_exhausted', False), ('mean_reversion-cautious-stress', 'risk_budget_exhausted', False), ('mean_reversion-moderate-stress', 'risk_budget_exhausted', False)]
改善レビュー要否: True。この集計はレビューを実行せず、完了時刻も更新しない。
前回レビュー: {"last_review_completed_at": 1790049645.593117, "review_file": "/Users/ermagent/Home/BreakOut/reports/reviews/20260922T040045Z.md", "decision": "no_change_collect_reentry_chains", "last_schedule_slot": "2026-09-22T13:00:00+09:00", "active_observation": "experiments/resume-20260914-v1", "next_hypothesis": "Measure profit-taking followed by same-direction BTC trend re-entry as one deduplicated chain, including fees and missed upside, across new forward regimes before considering a cooldown experiment."}

S&P500: 保存済み監視記録の参照のみ。この実行では価格/営業状態の再確認なし。
{"status": "stored_reference_not_rechecked", "file": "/Users/ermagent/Home/BreakOut/reports/monitoring/sp500/20260922T040045Z.json", "record_age_seconds": 10887.098221063614, "data": {"observed_at": 1790049645.243955, "observed_at_utc": "2026-09-22T04:00:45.243955Z", "instrument": "Breakout:S&P500", "cash_market_status": "closed_after_regular_session", "market_status_basis": {"timezone": "America/New_York", "local_observed_at": "2026-09-22T00:00:45.243955-04:00", "regular_session": "09:30-16:00", "weekday": "Tuesday", "holiday_check": "2026-09-22 is not listed as a NYSE holiday in the saved calendar check"}, "reference_instrument": "S&P 500 cash index (.INX:INDEXSP)", "reference_price": 7764.7, "reference_price_at": "2026-09-21T16:51:02-04:00", "reference_change": {"absolute": 114.2, "percent": 1.49, "meaning": "Google Finance displayed daily change for the S&P 500 cash-index reference"}, "breakout_bid": null, "breakout_ask": null, "price_status": "delayed_after_close_reference", "source_checks": [{"source": "https://www.google.com/finance/quote/.INX:INDEXSP", "status": "ok_via_browser", "observed_value": "7,764.70", "observed_change": "+114.20 (+1.49%)", "observed_timestamp": "2026-09-21 16:51:02 GMT-4"}, {"source": "https://www.nyse.com/markets/hours-calendars", "status": "calendar_reference", "note": "Saved public calendar and America/New_York time place this check after the regular session."}], "new_price_samples": 0, "new_live_samples": 0, "delay_or_missing": true, "sources": ["https://www.google.com/finance/quote/.INX:INDEXSP", "https://www.nyse.com/markets/hours-calendars"], "note": "The timestamped public reference remains the prior session close; no new price sample is counted. Breakout bid/ask is unconnected."}}

回収実績は docs/recovery-goal.md と実受取の証拠で別途確認。仮想利益を実受取に算入しない。
旧固定ゲートと期間可変の採用判断は別。戦略の有効性はこの集計だけでは判定しない。
