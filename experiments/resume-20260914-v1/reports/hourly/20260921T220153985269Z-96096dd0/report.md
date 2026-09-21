# BreakOut 毎時集計

取得UTC: 2026-09-21T22:01:53.985269+00:00
状態: attention_required
実発注0。公開代理価格による仮想結果。候補は別口座で合算しない。

観測時間: 179.96 h / heartbeat経過秒: 55.66951513290405
直近1時間は取得時刻からの半開区間 (開始, 終了]。
イベント累積: {"daily_reset": 64, "decision": 1344, "no_signal": 10192, "heartbeat": 10440, "intent": 336, "paper_fill": 336, "close": 335, "collection_error": 3, "risk_budget_exhausted": 3}
イベント直近1h: {"heartbeat": 58, "close": 4, "no_signal": 64}

| 候補 | 1h決済 | 1h確定USD | 累積決済 | 累積確定USD | 含みUSD | 最大DD USD |
|---|---:|---:|---:|---:|---:|---:|
|mean_reversion-cautious|0|0.0000|50|-44.6263|0.0000|47.7347|
|mean_reversion-cautious-stress|0|0.0000|43|-44.7427|0.0000|46.8944|
|mean_reversion-moderate|0|0.0000|50|-50.0158|2.3113|53.5362|
|mean_reversion-moderate-stress|0|0.0000|54|-74.7465|0.0000|76.8982|
|trend-cautious|1|-3.0638|34|-10.3941|0.0000|33.1980|
|trend-cautious-stress|1|-2.9975|35|-41.1301|0.0000|44.8551|
|trend-moderate|1|-3.0638|34|-12.6714|0.0000|35.4752|
|trend-moderate-stress|1|-2.9975|35|-36.8026|0.0000|46.9629|

確定は決済取引の手数料・swap込み。含みは退出手数料・追加滑り前。古い/不正/欠損気配は未評価。
- mean_reversion-moderate: BTCUSD side=-1, quote=fresh, quote_ts=1790028057.440023

## 観測・判断の遅延

単位は秒。p95はnearest-rank。直近1hの間隔は終了時刻で集計し、開始が窓外でも含む。
| 指標 | 累積 件数 / 平均 / p95 / 最大 | 直近1h 件数 / 平均 / p95 / 最大 |
|---|---|---|
|観測間隔|10439 / 62.06 / 63.94 / 131.53|58 / 61.76 / 62.51 / 63.58|
|設定待機時間を超える分|10439 / 2.06 / 3.94 / 71.53|58 / 1.76 / 2.51 / 3.58|
|足確定→条件確認|1442 / 32.86 / 60.81 / 194.24|8 / 33.34 / 58.32 / 58.32|
|足確定→シグナル判断|263 / 33.89 / 61.66 / 194.24|0 / 未計測 / 未計測 / 未計測|
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
前回レビュー: {"last_review_completed_at": 1789995875.0, "review_file": "/Users/ermagent/Home/BreakOut/reports/reviews/20260921T130435Z.md", "decision": "no_change_continue_forward", "last_schedule_slot": "2026-09-21T22:00:00+09:00", "active_observation": "experiments/resume-20260914-v1", "next_hypothesis": "Continue fixed forward observation; compare BTC mean-reversion losses with trend outcomes on deduplicated unused signals; no threshold retuning."}

S&P500: 保存済み監視記録の参照のみ。この実行では価格/営業状態の再確認なし。
{"status": "stored_reference_not_rechecked", "file": "/Users/ermagent/Home/BreakOut/reports/monitoring/sp500/20260921T130435Z.json", "record_age_seconds": 32238.98526906967, "data": {"observed_at": 1789995875, "observed_at_utc": "2026-09-21T13:04:35Z", "instrument": "Breakout:S&P500", "cash_market_status": "pre_regular_open", "market_status_basis": {"timezone": "America/New_York", "local_observed_at": "2026-09-21T09:04:35-04:00", "regular_session": "09:30-16:00", "weekday": "Monday", "holiday_check": "2026-09-21 is not listed as a NYSE holiday in the saved calendar check"}, "reference_price": 7650.5, "reference_price_at": "2026-09-18T17:29:48-04:00", "reference_change": {"absolute": 12.74, "percent": 0.17, "meaning": "Google Finance displayed change for the stale Friday reference"}, "breakout_bid": null, "breakout_ask": null, "price_status": "stale_previous_session_reference", "source_checks": [{"source": "https://www.google.com/finance/quote/.INX:INDEXSP", "status": "ok_via_browser", "observed_value": "7,650.50", "observed_timestamp": "9月18日, 17:29:48 GMT-4"}, {"source": "https://www.nyse.com/markets/hours-calendars", "status": "calendar_reference", "note": "保存済みの公開カレンダー確認を再利用。今回の市場状態は現在時刻からpre-openと判定。"}], "new_price_samples": 0, "new_live_samples": 0, "delay_or_missing": true, "sources": ["https://www.google.com/finance/quote/.INX:INDEXSP", "https://www.nyse.com/markets/hours-calendars"], "note": "現物市場は通常営業日の寄り付き前。取得できた指数値は9月18日の古い参照値であり、現在値・新規サンプルとして扱わない。Breakoutのbid/askは未接続。"}}

回収実績は docs/recovery-goal.md と実受取の証拠で別途確認。仮想利益を実受取に算入しない。
旧固定ゲートと期間可変の採用判断は別。戦略の有効性はこの集計だけでは判定しない。
