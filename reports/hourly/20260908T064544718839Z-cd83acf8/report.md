# BreakOut 毎時集計

取得UTC: 2026-09-08T06:45:44.718839+00:00
状態: attention_required
実発注0。公開代理価格による仮想結果。候補は別口座で合算しない。

観測時間: 29.49 h / heartbeat経過秒: 17.751991033554077
直近1時間は取得時刻からの半開区間 (開始, 終了]。
イベント累積: {"daily_reset": 16, "no_signal": 1708, "heartbeat": 1718, "decision": 196, "intent": 56, "paper_fill": 56, "close": 48, "collection_error": 2}
イベント直近1h: {"no_signal": 32, "decision": 48, "heartbeat": 59, "close": 4, "intent": 4, "paper_fill": 4}

| 候補 | 1h決済 | 1h確定USD | 累積決済 | 累積確定USD | 含みUSD | 最大DD USD |
|---|---:|---:|---:|---:|---:|---:|
|mean_reversion-cautious|1|-3.0704|8|1.9630|0.0703|7.3058|
|mean_reversion-cautious-stress|1|-2.9858|8|-3.6388|-0.1532|8.8917|
|mean_reversion-moderate|1|-3.0704|8|1.9630|0.0703|7.3058|
|mean_reversion-moderate-stress|1|-2.9858|8|-3.6388|-0.1532|8.8917|
|trend-cautious|0|0.0000|4|-8.6824|2.4144|10.2180|
|trend-cautious-stress|0|0.0000|4|-9.3880|1.7361|11.0121|
|trend-moderate|0|0.0000|4|-8.6824|2.4144|10.2180|
|trend-moderate-stress|0|0.0000|4|-9.3880|1.7361|11.0121|

確定は決済取引の手数料・swap込み。含みは退出手数料・追加滑り前。古い/不正/欠損気配は未評価。
- mean_reversion-cautious: BTCUSD side=1, quote=fresh, quote_ts=1788849926.290085
- mean_reversion-cautious-stress: BTCUSD side=1, quote=fresh, quote_ts=1788849926.290085
- mean_reversion-moderate: BTCUSD side=1, quote=fresh, quote_ts=1788849926.290085
- mean_reversion-moderate-stress: BTCUSD side=1, quote=fresh, quote_ts=1788849926.290085
- trend-cautious: BTCUSD side=-1, quote=fresh, quote_ts=1788849926.290085
- trend-cautious-stress: BTCUSD side=-1, quote=fresh, quote_ts=1788849926.290085
- trend-moderate: BTCUSD side=-1, quote=fresh, quote_ts=1788849926.290085
- trend-moderate-stress: BTCUSD side=-1, quote=fresh, quote_ts=1788849926.290085

## 観測・判断の遅延

単位は秒。p95はnearest-rank。直近1hの間隔は終了時刻で集計し、開始が窓外でも含む。
| 指標 | 累積 件数 / 平均 / p95 / 最大 | 直近1h 件数 / 平均 / p95 / 最大 |
|---|---|---|
|観測間隔|1717 / 61.82 / 62.29 / 123.32|59 / 61.62 / 61.98 / 62.74|
|設定待機時間を超える分|1717 / 1.82 / 2.29 / 63.32|59 / 1.62 / 1.98 / 2.74|
|足確定→条件確認|238 / 33.43 / 62.30 / 78.87|10 / 27.77 / 53.92 / 53.92|
|足確定→シグナル判断|35 / 31.44 / 59.51 / 59.51|8 / 24.86 / 53.92 / 53.92|
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
前回レビュー: {"last_review_completed_at": 1788846450.422892, "review_file": "/Users/ermagent/Home/BreakOut/reports/reviews/20260908T054547Z.md", "decision": "no_change_insufficient_cost_resilience", "next_hypothesis": "Observe current BTC opposite positions, cost resilience and stop overshoot across regimes; monitor independent WS rejection reasons and storage."}

S&P500: 保存済み監視記録の参照のみ。この実行では価格/営業状態の再確認なし。
{"status": "stored_reference_not_rechecked", "file": "/Users/ermagent/Home/BreakOut/reports/monitoring/sp500/20260908T054730422892Z.json", "record_age_seconds": 3494.2959468364716, "data": {"observed_at": 1788846450.422892, "instrument": "Breakout:S&P500", "cash_market_status": "outside_regular_session_before_2026-09-08_open", "reference_price": null, "reference_price_at": null, "change_percent": null, "breakout_bid": null, "breakout_ask": null, "status": "stored_calendar_price_unavailable", "next_regular_open": "2026-09-08T13:30:00Z", "sources": ["https://www.nyse.com/trade/hours-calendars"], "source_verified_at": "2026-09-08T04:46:04.253579+00:00", "note": "前回04:46 UTCに確認したNYSE通常時間を参照。現地9月8日01時台で通常時間外。今回は外部再取得なし。指数値・Breakout直接気配未取得、新規価格サンプル0。"}}

回収実績は docs/recovery-goal.md と実受取の証拠で別途確認。仮想利益を実受取に算入しない。
旧固定ゲートと期間可変の採用判断は別。戦略の有効性はこの集計だけでは判定しない。
