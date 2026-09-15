# BreakOut 毎時集計

取得UTC: 2026-09-15T04:02:08.256418+00:00
状態: attention_required
実発注0。公開代理価格による仮想結果。候補は別口座で合算しない。

観測時間: 17.96 h / heartbeat経過秒: 61.42312216758728
直近1時間は取得時刻からの半開区間 (開始, 終了]。
イベント累積: {"daily_reset": 16, "decision": 200, "no_signal": 968, "heartbeat": 1047, "intent": 38, "paper_fill": 38, "close": 38, "collection_error": 1}
イベント直近1h: {"heartbeat": 58, "close": 4, "no_signal": 64}

| 候補 | 1h決済 | 1h確定USD | 累積決済 | 累積確定USD | 含みUSD | 最大DD USD |
|---|---:|---:|---:|---:|---:|---:|
|mean_reversion-cautious|1|-3.0707|7|-15.6174|0.0000|18.7258|
|mean_reversion-cautious-stress|1|-3.0212|7|-16.0014|0.0000|18.1531|
|mean_reversion-moderate|1|-3.0707|7|-13.7958|0.0000|16.9042|
|mean_reversion-moderate-stress|1|-3.0212|7|-14.9632|0.0000|17.1149|
|trend-cautious|0|0.0000|2|-6.6602|0.0000|8.6158|
|trend-cautious-stress|0|0.0000|3|-5.6426|0.0000|6.9512|
|trend-moderate|0|0.0000|2|-6.6602|0.0000|8.6158|
|trend-moderate-stress|0|0.0000|3|-5.6426|0.0000|6.9512|

確定は決済取引の手数料・swap込み。含みは退出手数料・追加滑り前。古い/不正/欠損気配は未評価。

## 観測・判断の遅延

単位は秒。p95はnearest-rank。直近1hの間隔は終了時刻で集計し、開始が窓外でも含む。
| 指標 | 累積 件数 / 平均 / p95 / 最大 | 直近1h 件数 / 平均 / p95 / 最大 |
|---|---|---|
|観測間隔|1046 / 61.83 / 62.85 / 131.53|58 / 61.64 / 62.52 / 63.13|
|設定待機時間を超える分|1046 / 1.83 / 2.85 / 71.53|58 / 1.64 / 2.52 / 3.13|
|足確定→条件確認|146 / 34.72 / 60.01 / 194.24|8 / 30.49 / 54.31 / 54.31|
|足確定→シグナル判断|42 / 32.68 / 62.26 / 194.24|0 / 未計測 / 未計測 / 未計測|
- total: 収集エラー 1件、エラーを挟む観測間隔 1件、150.0秒超の間隔 0件、鮮度期限超のシグナル観測 1件、不正な判断イベント 0件。
  エラー内訳: {"OHLC data is stale": 1}
- last_1h: 収集エラー 0件、エラーを挟む観測間隔 0件、150.0秒超の間隔 0件、鮮度期限超のシグナル観測 0件、不正な判断イベント 0件。
同じ銘柄・足は候補間で重複集計しない。初回起動時の古い足も含む。
判断時刻は取得完了を基準としたイベント時刻。実際の計算終了時刻ではない。
API通信時間・成功前の再試行回数は未記録。待機超過分は通信・処理・スケジュール・障害等を含み、通信遅延とは断定できない。
collection_errorは取得以外の処理例外も含む。進行中の停止は上記heartbeat経過秒で確認。
この診断だけでは遅延による損益影響や最適な取得間隔は判定できない。

警告: ['recorded_data_quality_errors']
停止: []
改善レビュー要否: False。この集計はレビューを実行せず、完了時刻も更新しない。
前回レビュー: {"last_review_completed_at": 1789434141.579799, "review_file": "/Users/ermagent/Home/BreakOut/reports/reviews/20260915T010047Z.md", "decision": "no_change_regime_diagnostic_only", "last_schedule_slot": "2026-09-15T10:00:00+09:00", "active_observation": "experiments/resume-20260914-v1", "next_hypothesis": "Predefine one persistent-uptrend condition and design cost/stop-inclusive historical comparison; no retrospective holdout claim."}

S&P500: 保存済み監視記録の参照のみ。この実行では価格/営業状態の再確認なし。
{"status": "stored_reference_not_rechecked", "file": "/Users/ermagent/Home/BreakOut/reports/monitoring/sp500/20260915T010047Z.json", "record_age_seconds": 10786.676619052887, "data": {"observed_at": 1789434141.579799, "instrument": "Breakout:S&P500", "reference_price": null, "reference_price_at": null, "breakout_bid": null, "breakout_ask": null, "cash_market_status": "after_scheduled_regular_session", "next_regular_open": "2026-09-15T13:30:00Z", "new_price_samples": 0, "new_live_samples": 0, "status": "price_unavailable", "sources": ["https://www.spglobal.com/spdji/en/indices/equity/sp-500/#data", "https://www.nyse.com/trade/hours-calendars"], "note": "今回外部再確認なし。価格未取得、通常時間外は保存済み日程に基づく。新規価格0。"}}

回収実績は docs/recovery-goal.md と実受取の証拠で別途確認。仮想利益を実受取に算入しない。
旧固定ゲートと期間可変の採用判断は別。戦略の有効性はこの集計だけでは判定しない。
