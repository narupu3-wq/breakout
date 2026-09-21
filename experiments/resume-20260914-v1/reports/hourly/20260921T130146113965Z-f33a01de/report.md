# BreakOut 毎時集計

取得UTC: 2026-09-21T13:01:46.113965+00:00
状態: attention_required
実発注0。公開代理価格による仮想結果。候補は別口座で合算しない。

観測時間: 170.97 h / heartbeat経過秒: 25.08783721923828
直近1時間は取得時刻からの半開区間 (開始, 終了]。
イベント累積: {"daily_reset": 64, "decision": 1284, "no_signal": 9676, "heartbeat": 9935, "intent": 321, "paper_fill": 321, "close": 317, "collection_error": 3, "risk_budget_exhausted": 1}
イベント直近1h: {"heartbeat": 54, "no_signal": 64, "close": 3}

| 候補 | 1h決済 | 1h確定USD | 累積決済 | 累積確定USD | 含みUSD | 最大DD USD |
|---|---:|---:|---:|---:|---:|---:|
|mean_reversion-cautious|1|-0.8504|49|-44.1743|0.0000|47.2827|
|mean_reversion-cautious-stress|0|0.0000|43|-44.7427|0.0000|46.8944|
|mean_reversion-moderate|1|-3.0441|49|-46.7313|0.0000|49.8397|
|mean_reversion-moderate-stress|1|-0.2802|54|-74.7465|0.0000|76.8982|
|trend-cautious|0|0.0000|30|-12.6442|0.5026|33.1980|
|trend-cautious-stress|0|0.0000|31|-40.4035|0.2700|44.8551|
|trend-moderate|0|0.0000|30|-14.9214|0.5026|35.4752|
|trend-moderate-stress|0|0.0000|31|-36.6844|0.3524|46.9629|

確定は決済取引の手数料・swap込み。含みは退出手数料・追加滑り前。古い/不正/欠損気配は未評価。
- trend-cautious: BTCUSD side=1, quote=fresh, quote_ts=1789995677.361067
- trend-cautious-stress: BTCUSD side=1, quote=fresh, quote_ts=1789995677.361067
- trend-moderate: BTCUSD side=1, quote=fresh, quote_ts=1789995677.361067
- trend-moderate-stress: BTCUSD side=1, quote=fresh, quote_ts=1789995677.361067

## 観測・判断の遅延

単位は秒。p95はnearest-rank。直近1hの間隔は終了時刻で集計し、開始が窓外でも含む。
| 指標 | 累積 件数 / 平均 / p95 / 最大 | 直近1h 件数 / 平均 / p95 / 最大 |
|---|---|---|
|観測間隔|9934 / 61.96 / 63.30 / 131.53|54 / 67.14 / 72.04 / 74.57|
|設定待機時間を超える分|9934 / 1.96 / 3.30 / 71.53|54 / 7.14 / 12.04 / 14.57|
|足確定→条件確認|1370 / 32.85 / 60.81 / 194.24|8 / 23.38 / 50.66 / 50.66|
|足確定→シグナル判断|251 / 33.71 / 61.66 / 194.24|0 / 未計測 / 未計測 / 未計測|
- total: 収集エラー 3件、エラーを挟む観測間隔 3件、150.0秒超の間隔 0件、鮮度期限超のシグナル観測 1件、不正な判断イベント 0件。
  エラー内訳: {"OHLC data is stale": 3}
- last_1h: 収集エラー 0件、エラーを挟む観測間隔 0件、150.0秒超の間隔 0件、鮮度期限超のシグナル観測 0件、不正な判断イベント 0件。
同じ銘柄・足は候補間で重複集計しない。初回起動時の古い足も含む。
判断時刻は取得完了を基準としたイベント時刻。実際の計算終了時刻ではない。
API通信時間・成功前の再試行回数は未記録。待機超過分は通信・処理・スケジュール・障害等を含み、通信遅延とは断定できない。
collection_errorは取得以外の処理例外も含む。進行中の停止は上記heartbeat経過秒で確認。
この診断だけでは遅延による損益影響や最適な取得間隔は判定できない。

警告: ['recorded_data_quality_errors', 'candidate_halted']
停止: [('mean_reversion-cautious-stress', 'risk_budget_exhausted', False)]
改善レビュー要否: False。この集計はレビューを実行せず、完了時刻も更新しない。
前回レビュー: {"last_review_completed_at": 1789985203.0, "review_file": "/Users/ermagent/Home/BreakOut/reports/reviews/20260921T100643Z.md", "decision": "no_change_continue_forward", "last_schedule_slot": "2026-09-21T19:00:00+09:00", "active_observation": "experiments/resume-20260914-v1", "next_hypothesis": "Continue fixed forward observation; verify BTC trend versus ETH sample and unresolved S&P500 price source; no threshold retuning."}

S&P500: 保存済み監視記録の参照のみ。この実行では価格/営業状態の再確認なし。
{"status": "stored_reference_not_rechecked", "file": "/Users/ermagent/Home/BreakOut/reports/monitoring/sp500/20260921T100643Z.json", "record_age_seconds": 10503.113965034485, "data": {"observed_at": 1789985203, "observed_at_utc": "2026-09-21T10:06:43Z", "instrument": "Breakout:S&P500", "cash_market_status": "pre_regular_open", "regular_session": {"timezone": "America/New_York", "open": "09:30", "close": "16:00", "local_observed_at": "2026-09-21T06:06:43-04:00", "weekday": "Monday"}, "holiday_check": {"status": "not_listed_as_holiday", "source": "https://www.nyse.com/markets/hours-calendars", "note": "NYSEの2026年休日表を確認。9月21日は休日欄にない。"}, "reference_price": null, "reference_price_at": null, "previous_close_change": null, "breakout_bid": null, "breakout_ask": null, "price_status": "unavailable", "source_checks": [{"source": "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?range=5d&interval=1m&includePrePost=false", "status": "rate_limited", "http_status": 429}, {"source": "https://stooq.com/q/l/?s=%5Espx&i=d", "status": "not_found", "http_status": 404}, {"source": "https://www.nyse.com/markets/hours-calendars", "status": "ok", "http_status": 200}], "new_price_samples": 0, "new_live_samples": 0, "delay_or_missing": true, "sources": ["https://www.nyse.com/markets/hours-calendars", "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?range=5d&interval=1m&includePrePost=false", "https://stooq.com/q/l/?s=%5Espx&i=d"], "note": "現物市場は通常営業日の寄り付き前。時刻付き指数値は取得不可で、Breakoutのbid/askも未接続。新規サンプルには数えない。"}}

回収実績は docs/recovery-goal.md と実受取の証拠で別途確認。仮想利益を実受取に算入しない。
旧固定ゲートと期間可変の採用判断は別。戦略の有効性はこの集計だけでは判定しない。
