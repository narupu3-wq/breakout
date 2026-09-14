# BreakOut 毎時集計

取得UTC: 2026-09-14T13:01:30.523401+00:00
状態: observing
実発注0。公開代理価格による仮想結果。候補は別口座で合算しない。

観測時間: 2.96 h / heartbeat経過秒: 28.266231060028076
直近1時間は取得時刻からの半開区間 (開始, 終了]。
イベント累積: {"daily_reset": 8, "decision": 24, "no_signal": 184, "heartbeat": 174, "intent": 8, "paper_fill": 8}
イベント直近1h: {"heartbeat": 58, "no_signal": 56, "decision": 8, "intent": 4, "paper_fill": 4}

| 候補 | 1h決済 | 1h確定USD | 累積決済 | 累積確定USD | 含みUSD | 最大DD USD |
|---|---:|---:|---:|---:|---:|---:|
|mean_reversion-cautious|0|0.0000|0|0.0000|2.0199|2.3544|
|mean_reversion-cautious-stress|0|0.0000|0|0.0000|1.4432|1.9234|
|mean_reversion-moderate|0|0.0000|0|0.0000|2.0199|2.3544|
|mean_reversion-moderate-stress|0|0.0000|0|0.0000|1.4432|1.9234|
|trend-cautious|0|0.0000|0|0.0000|-0.2546|0.0000|
|trend-cautious-stress|0|0.0000|0|0.0000|-0.3939|0.0000|
|trend-moderate|0|0.0000|0|0.0000|-0.2546|0.0000|
|trend-moderate-stress|0|0.0000|0|0.0000|-0.3939|0.0000|

確定は決済取引の手数料・swap込み。含みは退出手数料・追加滑り前。古い/不正/欠損気配は未評価。
- mean_reversion-cautious: BTCUSD side=-1, quote=fresh, quote_ts=1789390861.554297
- mean_reversion-cautious-stress: BTCUSD side=-1, quote=fresh, quote_ts=1789390861.554297
- mean_reversion-moderate: BTCUSD side=-1, quote=fresh, quote_ts=1789390861.554297
- mean_reversion-moderate-stress: BTCUSD side=-1, quote=fresh, quote_ts=1789390861.554297
- trend-cautious: ETHUSD side=-1, quote=fresh, quote_ts=1789390862.25717
- trend-cautious-stress: ETHUSD side=-1, quote=fresh, quote_ts=1789390862.25717
- trend-moderate: ETHUSD side=-1, quote=fresh, quote_ts=1789390862.25717
- trend-moderate-stress: ETHUSD side=-1, quote=fresh, quote_ts=1789390862.25717

## 観測・判断の遅延

単位は秒。p95はnearest-rank。直近1hの間隔は終了時刻で集計し、開始が窓外でも含む。
| 指標 | 累積 件数 / 平均 / p95 / 最大 | 直近1h 件数 / 平均 / p95 / 最大 |
|---|---|---|
|観測間隔|173 / 61.66 / 62.30 / 63.76|58 / 61.69 / 62.16 / 62.52|
|設定待機時間を超える分|173 / 1.66 / 2.30 / 3.76|58 / 1.69 / 2.16 / 2.52|
|足確定→条件確認|26 / 50.20 / 194.24 / 194.24|8 / 39.77 / 62.26 / 62.26|
|足確定→シグナル判断|4 / 78.20 / 194.24 / 194.24|1 / 62.26 / 62.26 / 62.26|
- total: 収集エラー 0件、エラーを挟む観測間隔 0件、150.0秒超の間隔 0件、鮮度期限超のシグナル観測 1件、不正な判断イベント 0件。
- last_1h: 収集エラー 0件、エラーを挟む観測間隔 0件、150.0秒超の間隔 0件、鮮度期限超のシグナル観測 0件、不正な判断イベント 0件。
同じ銘柄・足は候補間で重複集計しない。初回起動時の古い足も含む。
判断時刻は取得完了を基準としたイベント時刻。実際の計算終了時刻ではない。
API通信時間・成功前の再試行回数は未記録。待機超過分は通信・処理・スケジュール・障害等を含み、通信遅延とは断定できない。
collection_errorは取得以外の処理例外も含む。進行中の停止は上記heartbeat経過秒で確認。
この診断だけでは遅延による損益影響や最適な取得間隔は判定できない。

警告: []
停止: []
改善レビュー要否: False。この集計はレビューを実行せず、完了時刻も更新しない。
前回レビュー: {"last_review_completed_at": 1789380264.446985, "review_file": "/Users/ermagent/Home/BreakOut/reports/reviews/20260914T100217Z.md", "decision": "new_isolated_observation_same_strategy", "last_schedule_slot": "2026-09-14T19:00:00+09:00", "active_observation": "experiments/resume-20260914-v1", "next_hypothesis": "Verify fresh run and quote rejection recurrence; bounded saved BTC stop-crossing WS replay; ETH and SP500 evidence gaps remain."}

S&P500: 保存済み監視記録の参照のみ。この実行では価格/営業状態の再確認なし。
{"status": "stored_reference_not_rechecked", "file": "/Users/ermagent/Home/BreakOut/reports/monitoring/sp500/20260914T100217Z.json", "record_age_seconds": 10626.076416015625, "data": {"observed_at": 1789380264.446985, "instrument": "Breakout:S&P500", "cash_market_status": "before_scheduled_regular_session", "reference_price": null, "reference_price_at": null, "breakout_bid": null, "breakout_ask": null, "status": "price_unavailable", "new_price_samples": 0, "new_live_samples": 0, "next_regular_open": "2026-09-14T13:30:00Z", "sources": ["https://www.nyse.com/trade/hours-calendars"], "note": "日程確認。今回価格取得なし、過去終値を現在値として使用しない。履歴取得調査は復旧優先で未実施。"}}

回収実績は docs/recovery-goal.md と実受取の証拠で別途確認。仮想利益を実受取に算入しない。
旧固定ゲートと期間可変の採用判断は別。戦略の有効性はこの集計だけでは判定しない。
