# BreakOut 毎時集計

取得UTC: 2026-09-08T22:51:49.530178+00:00
状態: attention_required
実発注0。公開代理価格による仮想結果。候補は別口座で合算しない。

観測時間: 45.58 h / heartbeat経過秒: 59.49294424057007
直近1時間は取得時刻からの半開区間 (開始, 終了]。
イベント累積: {"daily_reset": 16, "no_signal": 2684, "heartbeat": 2656, "decision": 244, "intent": 72, "paper_fill": 72, "close": 72, "collection_error": 2}
イベント直近1h: {"heartbeat": 58, "no_signal": 64}

| 候補 | 1h決済 | 1h確定USD | 累積決済 | 累積確定USD | 含みUSD | 最大DD USD |
|---|---:|---:|---:|---:|---:|---:|
|mean_reversion-cautious|0|0.0000|12|5.4050|0.0000|7.3058|
|mean_reversion-cautious-stress|0|0.0000|12|-3.1197|0.0000|10.0661|
|mean_reversion-moderate|0|0.0000|12|5.4050|0.0000|7.3058|
|mean_reversion-moderate-stress|0|0.0000|12|-3.1197|0.0000|10.0661|
|trend-cautious|0|0.0000|6|-10.7187|0.0000|10.7187|
|trend-cautious-stress|0|0.0000|6|-12.0031|0.0000|12.0031|
|trend-moderate|0|0.0000|6|-10.7187|0.0000|10.7187|
|trend-moderate-stress|0|0.0000|6|-12.0031|0.0000|12.0031|

確定は決済取引の手数料・swap込み。含みは退出手数料・追加滑り前。古い/不正/欠損気配は未評価。

## 観測・判断の遅延

単位は秒。p95はnearest-rank。直近1hの間隔は終了時刻で集計し、開始が窓外でも含む。
| 指標 | 累積 件数 / 平均 / p95 / 最大 | 直近1h 件数 / 平均 / p95 / 最大 |
|---|---|---|
|観測間隔|2655 / 61.80 / 62.35 / 123.32|58 / 61.59 / 62.01 / 62.24|
|設定待機時間を超える分|2655 / 1.80 / 2.35 / 63.32|58 / 1.59 / 2.01 / 2.24|
|足確定→条件確認|366 / 33.92 / 61.59 / 78.87|8 / 36.75 / 55.44 / 55.44|
|足確定→シグナル判断|44 / 32.30 / 56.80 / 59.51|0 / 未計測 / 未計測 / 未計測|
- total: 収集エラー 2件、エラーを挟む観測間隔 2件、150.0秒超の間隔 0件、鮮度期限超のシグナル観測 0件、不正な判断イベント 0件。
  エラー内訳: {"OHLC data is stale": 2}
- last_1h: 収集エラー 0件、エラーを挟む観測間隔 0件、150.0秒超の間隔 0件、鮮度期限超のシグナル観測 0件、不正な判断イベント 0件。
同じ銘柄・足は候補間で重複集計しない。初回起動時の古い足も含む。
判断時刻は取得完了を基準としたイベント時刻。実際の計算終了時刻ではない。
API通信時間・成功前の再試行回数は未記録。待機超過分は通信・処理・スケジュール・障害等を含み、通信遅延とは断定できない。
collection_errorは取得以外の処理例外も含む。進行中の停止は上記heartbeat経過秒で確認。
この診断だけでは遅延による損益影響や最適な取得間隔は判定できない。

警告: ['recorded_data_quality_errors']
停止: []
改善レビュー要否: False。この集計はレビューを実行せず、完了時刻も更新しない。
前回レビュー: {"last_review_completed_at": 1788904389.788893, "review_file": "/Users/ermagent/Home/BreakOut/reports/reviews/20260908T215149Z.md", "decision": "no_change_cost_resilience_insufficient", "next_hypothesis": "Observe additional independent trades across symbols, directions and regimes; monitor costs and recurring WS gaps."}

S&P500: 保存済み監視記録の参照のみ。この実行では価格/営業状態の再確認なし。
{"status": "stored_reference_not_rechecked", "file": "/Users/ermagent/Home/BreakOut/reports/monitoring/sp500/20260908T215309787826Z.json", "record_age_seconds": 3519.7423520088196, "data": {"observed_at": 1788904389.787826, "instrument": "Breakout:S&P500", "cash_market_status": "outside_scheduled_regular_session_after_close", "reference_price": null, "reference_price_at": null, "change_percent": null, "breakout_bid": null, "breakout_ask": null, "status": "stored_reference_price_unavailable", "regular_session_open": "2026-09-08T13:30:00Z", "regular_session_close": "2026-09-08T20:00:00Z", "sources": ["https://www.nyse.com/trade/hours-calendars", "https://www.spglobal.com/spdji/en/indices/equity/sp-500/"], "source_verified_at": "2026-09-08T12:48:47.645157+00:00", "price_source_checked_at": "2026-09-08T18:52:05.771899+00:00", "note": "確認済みNYSE予定の通常終了後。今回外部再取得なし、Yahoo429は18:52 UTCの過去記録。指数終値・Breakout気配未取得、新規価格サンプル0。", "price_source": "https://finance.yahoo.com/quote/%5EGSPC/", "price_fetch_error": "HTTP 429 Too Many Requests", "next_regular_open": "2026-09-09T13:30:00Z"}}

回収実績は docs/recovery-goal.md と実受取の証拠で別途確認。仮想利益を実受取に算入しない。
旧固定ゲートと期間可変の採用判断は別。戦略の有効性はこの集計だけでは判定しない。
