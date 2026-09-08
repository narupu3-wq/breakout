# BreakOut 毎時集計

取得UTC: 2026-09-08T10:46:16.877572+00:00
状態: attention_required
実発注0。公開代理価格による仮想結果。候補は別口座で合算しない。

観測時間: 33.49 h / heartbeat経過秒: 30.378109216690063
直近1時間は取得時刻からの半開区間 (開始, 終了]。
イベント累積: {"daily_reset": 16, "no_signal": 1956, "heartbeat": 1952, "decision": 204, "intent": 56, "paper_fill": 56, "close": 56, "collection_error": 2}
イベント直近1h: {"heartbeat": 58, "no_signal": 64, "close": 4}

| 候補 | 1h決済 | 1h確定USD | 累積決済 | 累積確定USD | 含みUSD | 最大DD USD |
|---|---:|---:|---:|---:|---:|---:|
|mean_reversion-cautious|1|2.2681|9|4.2311|0.0000|7.3058|
|mean_reversion-cautious-stress|1|1.0560|9|-2.5827|0.0000|8.8917|
|mean_reversion-moderate|1|2.2681|9|4.2311|0.0000|7.3058|
|mean_reversion-moderate-stress|1|1.0560|9|-2.5827|0.0000|8.8917|
|trend-cautious|0|0.0000|5|-7.2694|0.0000|10.2180|
|trend-cautious-stress|0|0.0000|5|-9.0357|0.0000|11.0121|
|trend-moderate|0|0.0000|5|-7.2694|0.0000|10.2180|
|trend-moderate-stress|0|0.0000|5|-9.0357|0.0000|11.0121|

確定は決済取引の手数料・swap込み。含みは退出手数料・追加滑り前。古い/不正/欠損気配は未評価。

## 観測・判断の遅延

単位は秒。p95はnearest-rank。直近1hの間隔は終了時刻で集計し、開始が窓外でも含む。
| 指標 | 累積 件数 / 平均 / p95 / 最大 | 直近1h 件数 / 平均 / p95 / 最大 |
|---|---|---|
|観測間隔|1951 / 61.80 / 62.29 / 123.32|58 / 61.61 / 61.93 / 61.98|
|設定待機時間を超える分|1951 / 1.80 / 2.29 / 63.32|58 / 1.61 / 1.93 / 1.98|
|足確定→条件確認|270 / 33.64 / 61.79 / 78.87|8 / 41.24 / 60.00 / 60.00|
|足確定→シグナル判断|36 / 31.98 / 59.51 / 59.51|0 / 未計測 / 未計測 / 未計測|
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
前回レビュー: {"last_review_completed_at": 1788860849.007501, "review_file": "/Users/ermagent/Home/BreakOut/reports/reviews/20260908T094616Z.md", "decision": "no_change_cost_and_sample_limits", "next_hypothesis": "Observe current MR BTC long exit and cost resilience across regimes; retain stop overshoot and WS gap evidence."}

S&P500: 保存済み監視記録の参照のみ。この実行では価格/営業状態の再確認なし。
{"status": "stored_reference_not_rechecked", "file": "/Users/ermagent/Home/BreakOut/reports/monitoring/sp500/20260908T094729007501Z.json", "record_age_seconds": 3527.8700711727142, "data": {"observed_at": 1788860849.007501, "instrument": "Breakout:S&P500", "cash_market_status": "outside_regular_session_before_2026-09-08_open", "reference_price": null, "reference_price_at": null, "change_percent": null, "breakout_bid": null, "breakout_ask": null, "status": "stored_calendar_price_unavailable", "next_regular_open": "2026-09-08T13:30:00Z", "sources": ["https://www.nyse.com/trade/hours-calendars"], "source_verified_at": "2026-09-08T04:46:04.253579+00:00", "note": "04:46 UTC確認済みNYSE通常時間を参照。NY現地9月8日05時台で現物指数通常時間外。今回外部再取得なし。指数値・Breakout直接気配未取得、新規価格サンプル0。"}}

回収実績は docs/recovery-goal.md と実受取の証拠で別途確認。仮想利益を実受取に算入しない。
旧固定ゲートと期間可変の採用判断は別。戦略の有効性はこの集計だけでは判定しない。
