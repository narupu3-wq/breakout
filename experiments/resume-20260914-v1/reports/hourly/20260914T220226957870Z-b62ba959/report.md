# BreakOut 毎時集計

取得UTC: 2026-09-14T22:02:26.957870+00:00
状態: attention_required
実発注0。公開代理価格による仮想結果。候補は別口座で合算しない。

観測時間: 11.98 h / heartbeat経過秒: 27.455831050872803
直近1時間は取得時刻からの半開区間 (開始, 終了]。
イベント累積: {"daily_reset": 8, "decision": 168, "no_signal": 616, "heartbeat": 697, "intent": 30, "paper_fill": 30, "close": 26, "collection_error": 1}
イベント直近1h: {"close": 4, "heartbeat": 59, "no_signal": 64}

| 候補 | 1h決済 | 1h確定USD | 累積決済 | 累積確定USD | 含みUSD | 最大DD USD |
|---|---:|---:|---:|---:|---:|---:|
|mean_reversion-cautious|1|2.1539|5|-10.1250|0.0000|15.5436|
|mean_reversion-cautious-stress|1|1.6569|5|-10.7310|0.0000|14.7671|
|mean_reversion-moderate|1|4.7494|5|-7.7446|0.0000|15.9471|
|mean_reversion-moderate-stress|1|3.8060|5|-8.7808|0.0000|15.2610|
|trend-cautious|0|0.0000|1|-3.4225|-2.1358|7.7661|
|trend-cautious-stress|0|0.0000|2|-2.5843|-1.9776|6.2377|
|trend-moderate|0|0.0000|1|-3.4225|-2.1358|7.7661|
|trend-moderate-stress|0|0.0000|2|-2.5843|-1.9776|6.2377|

確定は決済取引の手数料・swap込み。含みは退出手数料・追加滑り前。古い/不正/欠損気配は未評価。
- trend-cautious: BTCUSD side=1, quote=fresh, quote_ts=1789423318.833128
- trend-cautious-stress: BTCUSD side=1, quote=fresh, quote_ts=1789423318.833128
- trend-moderate: BTCUSD side=1, quote=fresh, quote_ts=1789423318.833128
- trend-moderate-stress: BTCUSD side=1, quote=fresh, quote_ts=1789423318.833128

## 観測・判断の遅延

単位は秒。p95はnearest-rank。直近1hの間隔は終了時刻で集計し、開始が窓外でも含む。
| 指標 | 累積 件数 / 平均 / p95 / 最大 | 直近1h 件数 / 平均 / p95 / 最大 |
|---|---|---|
|観測間隔|696 / 61.96 / 63.40 / 131.53|59 / 61.50 / 61.84 / 61.95|
|設定待機時間を超える分|696 / 1.96 / 3.40 / 71.53|59 / 1.50 / 1.84 / 1.95|
|足確定→条件確認|98 / 36.74 / 62.26 / 194.24|8 / 39.08 / 58.14 / 58.14|
|足確定→シグナル判断|34 / 32.66 / 72.40 / 194.24|0 / 未計測 / 未計測 / 未計測|
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
改善レビュー要否: True。この集計はレビューを実行せず、完了時刻も更新しない。
前回レビュー: {"last_review_completed_at": 1789390998.765594, "review_file": "/Users/ermagent/Home/BreakOut/reports/reviews/20260914T130130Z.md", "decision": "no_change_single_selected_stop_case", "last_schedule_slot": "2026-09-14T22:00:00+09:00", "active_observation": "experiments/resume-20260914-v1", "next_hypothesis": "Paired old normal/stress stop crossing replay; verify current BTC/ETH exits; official SP500 Data link availability."}

S&P500: 保存済み監視記録の参照のみ。この実行では価格/営業状態の再確認なし。
{"status": "stored_reference_not_rechecked", "file": "/Users/ermagent/Home/BreakOut/reports/monitoring/sp500/20260914T130130Z.json", "record_age_seconds": 32348.192276000977, "data": {"observed_at": 1789390998.765594, "instrument": "Breakout:S&P500", "cash_market_status": "before_scheduled_regular_session", "reference_price": null, "reference_price_at": null, "breakout_bid": null, "breakout_ask": null, "status": "price_unavailable", "new_price_samples": 0, "new_live_samples": 0, "next_regular_open": "2026-09-14T13:30:00Z", "sources": ["https://www.nyse.com/trade/hours-calendars", "https://www.spglobal.com/spdji/en/indices/equity/sp-500/"], "note": "公式指数ページの抽出に時刻付き価格・履歴なし。新規価格0、通常営業開始前。", "price_source_checked_at": 1789390998.765594}}

回収実績は docs/recovery-goal.md と実受取の証拠で別途確認。仮想利益を実受取に算入しない。
旧固定ゲートと期間可変の採用判断は別。戦略の有効性はこの集計だけでは判定しない。
