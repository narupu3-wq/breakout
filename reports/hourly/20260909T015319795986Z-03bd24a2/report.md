# BreakOut 毎時集計

取得UTC: 2026-09-09T01:53:19.795986+00:00
状態: attention_required
実発注0。公開代理価格による仮想結果。候補は別口座で合算しない。

観測時間: 48.60 h / heartbeat経過秒: 45.95828294754028
直近1時間は取得時刻からの半開区間 (開始, 終了]。
イベント累積: {"daily_reset": 24, "no_signal": 2864, "heartbeat": 2833, "decision": 256, "intent": 76, "paper_fill": 76, "close": 72, "collection_error": 2}
イベント直近1h: {"heartbeat": 58, "no_signal": 52, "decision": 12, "intent": 4, "paper_fill": 4}

| 候補 | 1h決済 | 1h確定USD | 累積決済 | 累積確定USD | 含みUSD | 最大DD USD |
|---|---:|---:|---:|---:|---:|---:|
|mean_reversion-cautious|0|0.0000|12|5.4050|-0.8751|7.3058|
|mean_reversion-cautious-stress|0|0.0000|12|-3.1197|-0.9303|10.0661|
|mean_reversion-moderate|0|0.0000|12|5.4050|-0.8751|7.3058|
|mean_reversion-moderate-stress|0|0.0000|12|-3.1197|-0.9303|10.0661|
|trend-cautious|0|0.0000|6|-10.7187|0.0000|10.7187|
|trend-cautious-stress|0|0.0000|6|-12.0031|0.0000|12.0031|
|trend-moderate|0|0.0000|6|-10.7187|0.0000|10.7187|
|trend-moderate-stress|0|0.0000|6|-12.0031|0.0000|12.0031|

確定は決済取引の手数料・swap込み。含みは退出手数料・追加滑り前。古い/不正/欠損気配は未評価。
- mean_reversion-cautious: BTCUSD side=-1, quote=fresh, quote_ts=1788918752.9433558
- mean_reversion-cautious-stress: BTCUSD side=-1, quote=fresh, quote_ts=1788918752.9433558
- mean_reversion-moderate: BTCUSD side=-1, quote=fresh, quote_ts=1788918752.9433558
- mean_reversion-moderate-stress: BTCUSD side=-1, quote=fresh, quote_ts=1788918752.9433558

## 観測・判断の遅延

単位は秒。p95はnearest-rank。直近1hの間隔は終了時刻で集計し、開始が窓外でも含む。
| 指標 | 累積 件数 / 平均 / p95 / 最大 | 直近1h 件数 / 平均 / p95 / 最大 |
|---|---|---|
|観測間隔|2832 / 61.78 / 62.34 / 123.32|58 / 61.63 / 61.98 / 64.01|
|設定待機時間を超える分|2832 / 1.79 / 2.34 / 63.32|58 / 1.64 / 1.98 / 4.01|
|足確定→条件確認|390 / 33.88 / 61.79 / 78.87|8 / 31.51 / 57.76 / 57.76|
|足確定→シグナル判断|47 / 32.18 / 57.76 / 59.51|3 / 30.38 / 57.76 / 57.76|
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
前回レビュー: {"last_review_completed_at": 1788915276.257656, "review_file": "/Users/ermagent/Home/BreakOut/reports/reviews/20260909T005221Z.md", "decision": "no_change_insufficient_forward_evidence", "next_hypothesis": "BTC/ETH additional independent cost resilience evidence; S&P500 daily history suitability and intraday data gap. Do not count repeated FRED closes as fresh samples."}

S&P500: 保存済み監視記録の参照のみ。この実行では価格/営業状態の再確認なし。
{"status": "stored_reference_not_rechecked", "file": "/Users/ermagent/Home/BreakOut/reports/monitoring/sp500/20260909T005436177648Z.json", "record_age_seconds": 3523.618337869644, "data": {"observed_at": 1788915276.177648, "instrument": "Breakout:S&P500", "reference_instrument": "S&P Dow Jones Indices S&P 500 price index via FRED SP500", "cash_market_status": "outside_scheduled_regular_session_after_close", "reference_price": 7673.52, "reference_price_at": "2026-09-08T20:00:00Z", "reference_price_at_basis": "FRED observation date with daily close definition and NYSE regular close; not a tick timestamp", "reference_observation_date": "2026-09-08", "previous_trading_date": "2026-09-04", "previous_close": 7718.6, "change_percent": -0.5840437385018049, "change_percent_basis": "calculated from two FRED closing observations", "breakout_bid": null, "breakout_ask": null, "status": "daily_close_reference_not_live", "source_updated_at": "2026-09-09T00:02:00Z", "source_verified_at": "2026-09-09T00:54:36.177648+00:00", "price_source_checked_at": "2026-09-09T00:54:36.177648+00:00", "sources": ["https://fred.stlouisfed.org/series/SP500", "https://www.nyse.com/trade/hours-calendars"], "price_source": "https://fred.stlouisfed.org/series/SP500", "next_regular_open": "2026-09-09T13:30:00Z", "new_live_samples": 0, "note": "Initial verification of this dated close; closed-market observation is not a new intraday/forward sample. No automated history collector or Breakout quotes. Future repeats of this close must not count as new samples."}}

回収実績は docs/recovery-goal.md と実受取の証拠で別途確認。仮想利益を実受取に算入しない。
旧固定ゲートと期間可変の採用判断は別。戦略の有効性はこの集計だけでは判定しない。
