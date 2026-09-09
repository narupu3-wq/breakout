# BreakOut 毎時集計

取得UTC: 2026-09-09T08:01:46.012057+00:00
状態: attention_required
実発注0。公開代理価格による仮想結果。候補は別口座で合算しない。

観測時間: 54.75 h / heartbeat経過秒: 19.635740041732788
直近1時間は取得時刻からの半開区間 (開始, 終了]。
イベント累積: {"daily_reset": 24, "no_signal": 3212, "heartbeat": 3192, "decision": 308, "intent": 84, "paper_fill": 84, "close": 80, "collection_error": 2}
イベント直近1h: {"heartbeat": 59, "no_signal": 56, "decision": 8}

| 候補 | 1h決済 | 1h確定USD | 累積決済 | 累積確定USD | 含みUSD | 最大DD USD |
|---|---:|---:|---:|---:|---:|---:|
|mean_reversion-cautious|0|0.0000|13|0.8856|-0.9284|7.6680|
|mean_reversion-cautious-stress|0|0.0000|13|-6.1237|-0.9674|11.0111|
|mean_reversion-moderate|0|0.0000|13|0.8856|-0.9284|7.6680|
|mean_reversion-moderate-stress|0|0.0000|13|-6.1237|-0.9674|11.0111|
|trend-cautious|0|0.0000|7|-13.8645|0.0000|13.8645|
|trend-cautious-stress|0|0.0000|7|-15.1440|0.0000|15.1440|
|trend-moderate|0|0.0000|7|-13.8645|0.0000|13.8645|
|trend-moderate-stress|0|0.0000|7|-15.1440|0.0000|15.1440|

確定は決済取引の手数料・swap込み。含みは退出手数料・追加滑り前。古い/不正/欠損気配は未評価。
- mean_reversion-cautious: BTCUSD side=-1, quote=fresh, quote_ts=1788940885.7000792
- mean_reversion-cautious-stress: BTCUSD side=-1, quote=fresh, quote_ts=1788940885.7000792
- mean_reversion-moderate: BTCUSD side=-1, quote=fresh, quote_ts=1788940885.7000792
- mean_reversion-moderate-stress: BTCUSD side=-1, quote=fresh, quote_ts=1788940885.7000792

## 観測・判断の遅延

単位は秒。p95はnearest-rank。直近1hの間隔は終了時刻で集計し、開始が窓外でも含む。
| 指標 | 累積 件数 / 平均 / p95 / 最大 | 直近1h 件数 / 平均 / p95 / 最大 |
|---|---|---|
|観測間隔|3191 / 61.77 / 62.30 / 123.32|59 / 61.65 / 62.09 / 62.13|
|設定待機時間を超える分|3191 / 1.77 / 2.30 / 63.32|59 / 1.65 / 2.09 / 2.13|
|足確定→条件確認|440 / 33.92 / 61.79 / 78.87|8 / 33.70 / 61.94 / 61.94|
|足確定→シグナル判断|57 / 31.47 / 59.51 / 63.37|2 / 24.02 / 36.56 / 36.56|
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
前回レビュー: {"last_review_completed_at": 1788937503.25008, "review_file": "/Users/ermagent/Home/BreakOut/reports/reviews/20260909T070239Z.md", "decision": "no_change_stop_overshoot_diagnosed", "next_hypothesis": "Replay saved WS during BTC stop crossing; ETH new regime evidence; one registration-free official SP500 history source. Alpha Vantage demo exhausted; no repeat."}

S&P500: 保存済み監視記録の参照のみ。この実行では価格/営業状態の再確認なし。
{"status": "stored_reference_not_rechecked", "file": "/Users/ermagent/Home/BreakOut/reports/monitoring/sp500/20260909T070503250080Z.json", "record_age_seconds": 3402.761976957321, "data": {"observed_at": 1788937503.25008, "instrument": "Breakout:S&P500", "reference_instrument": "S&P Dow Jones Indices S&P 500 price index via FRED SP500", "cash_market_status": "outside_scheduled_regular_session_after_close", "reference_price": 7673.52, "reference_price_at": "2026-09-08T20:00:00Z", "reference_price_at_basis": "FRED observation date with daily close definition and NYSE regular close; not a tick timestamp", "reference_observation_date": "2026-09-08", "previous_trading_date": "2026-09-04", "previous_close": 7718.6, "change_percent": -0.5840437385018049, "change_percent_basis": "calculated from two FRED closing observations", "breakout_bid": null, "breakout_ask": null, "status": "stored_daily_close_not_rechecked", "source_updated_at": "2026-09-09T00:02:00Z", "source_verified_at": "2026-09-09T00:54:36.177648+00:00", "price_source_checked_at": "2026-09-09T03:57:56.019733+00:00", "sources": ["https://fred.stlouisfed.org/series/SP500", "https://www.nyse.com/trade/hours-calendars"], "price_source": "https://fred.stlouisfed.org/series/SP500", "next_regular_open": "2026-09-09T13:30:00Z", "new_live_samples": 0, "note": "保存済み9月8日終値、価格再取得なし・新規0。Alpha Vantage SPY公開demoを確認しHTTP200だが無料キー要求メッセージのみ、価格なし。指数履歴/分足はpremium。新規口座・キー・課金なし。", "new_price_samples": 0, "usage_review_source": "https://fred.stlouisfed.org/legal/", "alternative_source_check": {"url": "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=SPY&apikey=demo", "http_status": 200, "outcome": "demo_requires_free_key_no_prices", "checked_at": 1788937503.25008, "documentation": "https://www.alphavantage.co/documentation/", "terms": "https://www.alphavantage.co/terms_of_service/"}}}

回収実績は docs/recovery-goal.md と実受取の証拠で別途確認。仮想利益を実受取に算入しない。
旧固定ゲートと期間可変の採用判断は別。戦略の有効性はこの集計だけでは判定しない。
