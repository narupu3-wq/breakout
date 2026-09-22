# BreakOut 毎時集計

取得UTC: 2026-09-22T04:00:45.593117+00:00
状態: attention_required
実発注0。公開代理価格による仮想結果。候補は別口座で合算しない。

観測時間: 185.94 h / heartbeat経過秒: 54.32405686378479
直近1時間は取得時刻からの半開区間 (開始, 終了]。
イベント累積: {"daily_reset": 72, "decision": 1356, "no_signal": 10548, "heartbeat": 10788, "intent": 337, "paper_fill": 337, "close": 336, "collection_error": 3, "risk_budget_exhausted": 3}
イベント直近1h: {"no_signal": 56, "decision": 8, "heartbeat": 58}

| 候補 | 1h決済 | 1h確定USD | 累積決済 | 累積確定USD | 含みUSD | 最大DD USD |
|---|---:|---:|---:|---:|---:|---:|
|mean_reversion-cautious|0|0.0000|50|-44.6263|0.0000|47.7347|
|mean_reversion-cautious-stress|0|0.0000|43|-44.7427|0.0000|46.8944|
|mean_reversion-moderate|0|0.0000|51|-47.7147|0.0439|53.5362|
|mean_reversion-moderate-stress|0|0.0000|54|-74.7465|0.0000|76.8982|
|trend-cautious|0|0.0000|34|-10.3941|0.0000|33.1980|
|trend-cautious-stress|0|0.0000|35|-41.1301|0.0000|44.8551|
|trend-moderate|0|0.0000|34|-12.6714|0.0000|35.4752|
|trend-moderate-stress|0|0.0000|35|-36.8026|0.0000|46.9629|

確定は決済取引の手数料・swap込み。含みは退出手数料・追加滑り前。古い/不正/欠損気配は未評価。
- mean_reversion-moderate: BTCUSD side=1, quote=fresh, quote_ts=1790049590.44187

## 観測・判断の遅延

単位は秒。p95はnearest-rank。直近1hの間隔は終了時刻で集計し、開始が窓外でも含む。
| 指標 | 累積 件数 / 平均 / p95 / 最大 | 直近1h 件数 / 平均 / p95 / 最大 |
|---|---|---|
|観測間隔|10787 / 62.06 / 63.91 / 131.53|58 / 62.06 / 63.55 / 68.46|
|設定待機時間を超える分|10787 / 2.06 / 3.91 / 71.53|58 / 2.06 / 3.55 / 8.46|
|足確定→条件確認|1488 / 32.94 / 60.99 / 194.24|8 / 37.83 / 56.17 / 56.17|
|足確定→シグナル判断|266 / 33.95 / 61.66 / 194.24|2 / 36.22 / 54.68 / 54.68|
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
改善レビュー要否: False。この集計はレビューを実行せず、完了時刻も更新しない。
前回レビュー: {"last_review_completed_at": 1790038939.396702, "review_file": "/Users/ermagent/Home/BreakOut/reports/reviews/20260922T010219Z.md", "decision": "no_change_collect_reentry_chains", "last_schedule_slot": "2026-09-22T10:00:00+09:00", "active_observation": "experiments/resume-20260914-v1", "next_hypothesis": "Measure profit-taking followed by same-direction BTC trend re-entry as one deduplicated chain, including fees and missed upside, across new forward regimes before considering a cooldown experiment."}

S&P500: 保存済み監視記録の参照のみ。この実行では価格/営業状態の再確認なし。
{"status": "stored_reference_not_rechecked", "file": "/Users/ermagent/Home/BreakOut/reports/monitoring/sp500/20260922T010219Z.json", "record_age_seconds": 10706.19641494751, "data": {"observed_at": 1790038939.396702, "observed_at_utc": "2026-09-22T01:02:19.396702Z", "instrument": "Breakout:S&P500", "cash_market_status": "closed_after_regular_session", "market_status_basis": {"timezone": "America/New_York", "local_observed_at": "2026-09-21T21:02:19.396702-04:00", "regular_session": "09:30-16:00", "weekday": "Monday", "holiday_check": "2026-09-21 is not listed as a NYSE holiday in the saved calendar check"}, "reference_instrument": "S&P 500 cash index (.INX:INDEXSP)", "reference_price": 7764.7, "reference_price_at": "2026-09-21T16:51:02-04:00", "reference_change": {"absolute": 114.2, "percent": 1.49, "meaning": "Last internally consistent timestamped Google Finance display retained from the 07:00 JST check"}, "breakout_bid": null, "breakout_ask": null, "price_status": "unchanged_stale_reference", "source_checks": [{"source": "https://www.google.com/finance/quote/.INX:INDEXSP", "status": "page_loaded_value_unchanged_timestamp_inconsistent", "observed_value": "7,764.70", "observed_change": "+114.20 (+1.49%)", "displayed_timestamp": "12月31日 20:00:00 UTC-4", "note": "The displayed date is inconsistent with the 2026-09-22 check and cannot establish a new timestamped sample. The last internally consistent timestamp remains 2026-09-21 16:51:02 EDT."}, {"source": "https://www.nyse.com/markets/hours-calendars", "status": "saved_calendar_reference", "note": "Saved public calendar and America/New_York time place this check after the regular session."}], "new_price_samples": 0, "new_live_samples": 0, "delay_or_missing": true, "sources": ["https://www.google.com/finance/quote/.INX:INDEXSP", "https://www.nyse.com/markets/hours-calendars"], "note": "No new valid timestamped price. The unchanged stale external index reference is not Breakout bid/ask and is not counted as a new sample."}}

回収実績は docs/recovery-goal.md と実受取の証拠で別途確認。仮想利益を実受取に算入しない。
旧固定ゲートと期間可変の採用判断は別。戦略の有効性はこの集計だけでは判定しない。
