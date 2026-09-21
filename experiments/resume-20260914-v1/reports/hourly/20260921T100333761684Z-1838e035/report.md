# BreakOut 毎時集計

取得UTC: 2026-09-21T10:03:33.761684+00:00
状態: attention_required
実発注0。公開代理価格による仮想結果。候補は別口座で合算しない。

観測時間: 168.00 h / heartbeat経過秒: 33.85261011123657
直近1時間は取得時刻からの半開区間 (開始, 終了]。
イベント累積: {"daily_reset": 64, "decision": 1276, "no_signal": 9492, "heartbeat": 9774, "intent": 321, "paper_fill": 321, "close": 314, "collection_error": 3, "risk_budget_exhausted": 1}
イベント直近1h: {"heartbeat": 57, "no_signal": 16, "decision": 48, "close": 7, "intent": 7, "paper_fill": 7}

| 候補 | 1h決済 | 1h確定USD | 累積決済 | 累積確定USD | 含みUSD | 最大DD USD |
|---|---:|---:|---:|---:|---:|---:|
|mean_reversion-cautious|1|-2.1356|48|-43.3239|-0.1964|47.0496|
|mean_reversion-cautious-stress|0|0.0000|43|-44.7427|0.0000|46.8944|
|mean_reversion-moderate|1|-3.3616|48|-43.6872|-0.7031|49.0055|
|mean_reversion-moderate-stress|1|-0.7158|53|-74.4663|-0.0662|76.8125|
|trend-cautious|1|3.8593|30|-12.6442|-0.9318|33.1980|
|trend-cautious-stress|1|1.5111|31|-40.4035|-0.7269|44.8551|
|trend-moderate|1|3.8593|30|-14.9214|-0.9318|35.4752|
|trend-moderate-stress|1|2.9384|31|-36.6844|-0.9488|46.9629|

確定は決済取引の手数料・swap込み。含みは退出手数料・追加滑り前。古い/不正/欠損気配は未評価。
- mean_reversion-cautious: BTCUSD side=-1, quote=fresh, quote_ts=1789984970.4621499
- mean_reversion-moderate: BTCUSD side=-1, quote=fresh, quote_ts=1789984970.4621499
- mean_reversion-moderate-stress: BTCUSD side=-1, quote=fresh, quote_ts=1789984970.4621499
- trend-cautious: BTCUSD side=1, quote=fresh, quote_ts=1789984970.4621499
- trend-cautious-stress: BTCUSD side=1, quote=fresh, quote_ts=1789984970.4621499
- trend-moderate: BTCUSD side=1, quote=fresh, quote_ts=1789984970.4621499
- trend-moderate-stress: BTCUSD side=1, quote=fresh, quote_ts=1789984970.4621499

## 観測・判断の遅延

単位は秒。p95はnearest-rank。直近1hの間隔は終了時刻で集計し、開始が窓外でも含む。
| 指標 | 累積 件数 / 平均 / p95 / 最大 | 直近1h 件数 / 平均 / p95 / 最大 |
|---|---|---|
|観測間隔|9773 / 61.88 / 62.99 / 131.53|57 / 63.34 / 68.71 / 75.45|
|設定待機時間を超える分|9773 / 1.88 / 2.99 / 71.53|57 / 3.34 / 8.71 / 15.45|
|足確定→条件確認|1346 / 32.87 / 60.99 / 194.24|8 / 30.93 / 49.06 / 49.06|
|足確定→シグナル判断|249 / 33.88 / 61.66 / 194.24|8 / 30.93 / 49.06 / 49.06|
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
改善レビュー要否: True。この集計はレビューを実行せず、完了時刻も更新しない。
前回レビュー: {"last_review_completed_at": 1789456295.270068, "review_file": "/Users/ermagent/Home/BreakOut/reports/reviews/20260915T070237Z.md", "decision": "comparison_complete_rejected_stress_dd", "last_schedule_slot": "2026-09-15T16:00:00+09:00", "active_observation": "experiments/resume-20260914-v1", "next_hypothesis": "Direction filter rejected for stress/DD; no threshold retuning. Review new forward evidence and unresolved SP500 source separately."}

S&P500: 保存済み監視記録の参照のみ。この実行では価格/営業状態の再確認なし。
{"status": "stored_reference_not_rechecked", "file": "/Users/ermagent/Home/BreakOut/reports/monitoring/sp500/20260915T070237Z.json", "record_age_seconds": 529213.0873689651, "data": {"observed_at": 1789455800.674315, "instrument": "Breakout:S&P500", "reference_price": null, "reference_price_at": null, "breakout_bid": null, "breakout_ask": null, "cash_market_status": "after_scheduled_regular_session", "next_regular_open": "2026-09-15T13:30:00Z", "new_price_samples": 0, "new_live_samples": 0, "status": "price_unavailable", "sources": ["https://www.spglobal.com/spdji/en/indices/equity/sp-500/#data", "https://www.nyse.com/trade/hours-calendars"], "note": "今回外部再確認なし。通常時間外は保存済み日程。価格0、登録不要履歴未解決。方向フィルター比較の実装・検証を優先。"}}

回収実績は docs/recovery-goal.md と実受取の証拠で別途確認。仮想利益を実受取に算入しない。
旧固定ゲートと期間可変の採用判断は別。戦略の有効性はこの集計だけでは判定しない。
