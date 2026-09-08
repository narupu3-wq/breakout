# BreakOut 毎時集計

取得UTC: 2026-09-08T14:49:50.136966+00:00
状態: attention_required
実発注0。公開代理価格による仮想結果。候補は別口座で合算しない。

観測時間: 37.55 h / heartbeat経過秒: 41.73211097717285
直近1時間は取得時刻からの半開区間 (開始, 終了]。
イベント累積: {"daily_reset": 16, "no_signal": 2184, "heartbeat": 2188, "decision": 232, "intent": 68, "paper_fill": 68, "close": 68, "collection_error": 2}
イベント直近1h: {"heartbeat": 58, "no_signal": 56, "decision": 8, "close": 8}

| 候補 | 1h決済 | 1h確定USD | 累積決済 | 累積確定USD | 含みUSD | 最大DD USD |
|---|---:|---:|---:|---:|---:|---:|
|mean_reversion-cautious|1|3.0350|11|4.2205|0.0000|7.3058|
|mean_reversion-cautious-stress|1|2.1439|11|-3.6679|0.0000|10.0661|
|mean_reversion-moderate|1|3.0350|11|4.2205|0.0000|7.3058|
|mean_reversion-moderate-stress|1|2.1439|11|-3.6679|0.0000|10.0661|
|trend-cautious|1|-3.4493|6|-10.7187|0.0000|10.7187|
|trend-cautious-stress|1|-2.9675|6|-12.0031|0.0000|12.0031|
|trend-moderate|1|-3.4493|6|-10.7187|0.0000|10.7187|
|trend-moderate-stress|1|-2.9675|6|-12.0031|0.0000|12.0031|

確定は決済取引の手数料・swap込み。含みは退出手数料・追加滑り前。古い/不正/欠損気配は未評価。

## 観測・判断の遅延

単位は秒。p95はnearest-rank。直近1hの間隔は終了時刻で集計し、開始が窓外でも含む。
| 指標 | 累積 件数 / 平均 / p95 / 最大 | 直近1h 件数 / 平均 / p95 / 最大 |
|---|---|---|
|観測間隔|2187 / 61.81 / 62.37 / 123.32|58 / 62.14 / 62.95 / 63.04|
|設定待機時間を超える分|2187 / 1.81 / 2.37 / 63.32|58 / 2.14 / 2.95 / 3.04|
|足確定→条件確認|302 / 33.87 / 62.00 / 78.87|8 / 43.62 / 62.88 / 62.88|
|足確定→シグナル判断|41 / 32.23 / 56.80 / 59.51|2 / 23.67 / 23.67 / 23.67|
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
前回レビュー: {"last_review_completed_at": 1788871727.645157, "review_file": "/Users/ermagent/Home/BreakOut/reports/reviews/20260908T124716Z.md", "decision": "no_change_small_sample_and_costs", "next_hypothesis": "Observe new MR BTC long exit and cost resilience; collect further rapid-move events before assessing usefulness."}

S&P500: 保存済み監視記録の参照のみ。この実行では価格/営業状態の再確認なし。
{"status": "stored_reference_not_rechecked", "file": "/Users/ermagent/Home/BreakOut/reports/monitoring/sp500/20260908T134933382271Z.json", "record_age_seconds": 3616.7546949386597, "data": {"observed_at": 1788875373.382271, "instrument": "Breakout:S&P500", "cash_market_status": "within_scheduled_regular_session", "reference_price": null, "reference_price_at": null, "change_percent": null, "breakout_bid": null, "breakout_ask": null, "status": "price_unavailable_from_public_page", "regular_session_open": "2026-09-08T13:30:00Z", "regular_session_close": "2026-09-08T20:00:00Z", "sources": ["https://www.nyse.com/trade/hours-calendars", "https://www.spglobal.com/spdji/en/indices/equity/sp-500/"], "source_verified_at": "2026-09-08T12:48:47.645157+00:00", "price_source_checked_at": "2026-09-08T13:49:33.382271+00:00", "note": "確認済みNYSEカレンダーでは通常時間内。S&P公式ページを今回取得したが時刻付き指数価格は抽出できず欠損。Breakout気配未接続、新規価格サンプル0。指数価格の実更新で営業を確認したわけではない。"}}

回収実績は docs/recovery-goal.md と実受取の証拠で別途確認。仮想利益を実受取に算入しない。
旧固定ゲートと期間可変の採用判断は別。戦略の有効性はこの集計だけでは判定しない。
