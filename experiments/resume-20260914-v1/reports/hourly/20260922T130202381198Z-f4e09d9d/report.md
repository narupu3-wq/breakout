# BreakOut 毎時集計

取得UTC: 2026-09-22T13:02:02.381198+00:00
状態: attention_required
実発注0。公開代理価格による仮想結果。候補は別口座で合算しない。

観測時間: 194.97 h / heartbeat経過秒: 46.815197229385376
直近1時間は取得時刻からの半開区間 (開始, 終了]。
イベント累積: {"daily_reset": 72, "decision": 1384, "no_signal": 11112, "heartbeat": 11314, "intent": 343, "paper_fill": 343, "close": 342, "collection_error": 3, "risk_budget_exhausted": 3}
イベント直近1h: {"heartbeat": 58, "no_signal": 60, "close": 1, "decision": 4, "intent": 1, "paper_fill": 1}

| 候補 | 1h決済 | 1h確定USD | 累積決済 | 累積確定USD | 含みUSD | 最大DD USD |
|---|---:|---:|---:|---:|---:|---:|
|mean_reversion-cautious|0|0.0000|50|-44.6263|0.0000|47.7347|
|mean_reversion-cautious-stress|0|0.0000|43|-44.7427|0.0000|46.8944|
|mean_reversion-moderate|1|-0.4795|53|-51.2475|-0.2459|55.5158|
|mean_reversion-moderate-stress|0|0.0000|54|-74.7465|0.0000|76.8982|
|trend-cautious|0|0.0000|35|-13.6271|0.0000|33.1980|
|trend-cautious-stress|0|0.0000|36|-43.0472|0.0000|44.8551|
|trend-moderate|0|0.0000|35|-15.9043|0.0000|35.4752|
|trend-moderate-stress|0|0.0000|36|-39.7750|0.0000|46.9629|

確定は決済取引の手数料・swap込み。含みは退出手数料・追加滑り前。古い/不正/欠損気配は未評価。
- mean_reversion-moderate: ETHUSD side=-1, quote=fresh, quote_ts=1790082075.566001

## 観測・判断の遅延

単位は秒。p95はnearest-rank。直近1hの間隔は終了時刻で集計し、開始が窓外でも含む。
| 指標 | 累積 件数 / 平均 / p95 / 最大 | 直近1h 件数 / 平均 / p95 / 最大 |
|---|---|---|
|観測間隔|11313 / 62.04 / 63.83 / 131.53|58 / 61.83 / 62.48 / 62.76|
|設定待機時間を超える分|11313 / 2.04 / 3.83 / 71.53|58 / 1.83 / 2.48 / 2.76|
|足確定→条件確認|1562 / 32.94 / 61.01 / 194.24|8 / 33.06 / 53.27 / 53.27|
|足確定→シグナル判断|273 / 33.86 / 61.66 / 194.24|1 / 13.82 / 13.82 / 13.82|
- total: 収集エラー 3件、エラーを挟む観測間隔 3件、150.0秒超の間隔 0件、鮮度期限超のシグナル観測 1件、不正な判断イベント 0件。
  エラー内訳: {"OHLC data is stale": 3}
- last_1h: 収集エラー 0件、エラーを挟む観測間隔 0件、150.0秒超の間隔 0件、鮮度期限超のシグナル観測 0件、不正な判断イベント 0件。
同じ銘柄・足は候補間で重複集計しない。初回起動時の古い足も含む。
判断時刻は取得完了を基準としたイベント時刻。実際の計算終了時刻ではない。
API通信時間・成功前の再試行回数は未記録。待機超過分は通信・処理・スケジュール・障害等を含み、通信遅延とは断定できない。
collection_errorは取得以外の処理例外も含む。進行中の停止は上記heartbeat経過秒で確認。
この診断だけでは遅延による損益影響や最適な取得間隔は判定できない。

警告: ['recorded_data_quality_errors', 'candidate_halted']
停止: [('mean_reversion-cautious', 'risk_budget_exhausted', False), ('mean_reversion-cautious-stress', 'risk_budget_exhausted', False), ('mean_reversion-moderate-stress', 'risk_budget_exhausted', False)]
改善レビュー要否: False。この集計はレビューを実行せず、完了時刻も更新しない。
前回レビュー: {"last_review_completed_at": 1790071774.7660558, "review_file": "/Users/ermagent/Home/BreakOut/reports/reviews/20260922T100201Z.md", "decision": "no_change_collect_reentry_chains", "last_schedule_slot": "2026-09-22T19:00:00+09:00", "active_observation": "experiments/resume-20260914-v1", "next_hypothesis": "Measure profit-taking followed by same-direction BTC trend re-entry as one deduplicated chain, including fees and missed upside, across new forward regimes before considering a cooldown experiment."}

S&P500: 保存済み監視記録の参照のみ。この実行では価格/営業状態の再確認なし。
{"status": "stored_reference_not_rechecked", "file": "/Users/ermagent/Home/BreakOut/reports/monitoring/sp500/20260922T100201Z.json", "record_age_seconds": 10347.615624189377, "data": {"observed_at": 1790071774.765574, "source": "https://www.google.com/finance/quote/.INX:INDEXSP", "reference_instrument": "S&P 500 cash index", "cash_market_status": "closed_before_regular_session", "market_status_basis": "America/New_York 06時台、通常09:30-16:00。既存NYSEカレンダー参照。", "reference_price": 7764.7, "reference_price_at": "2026-09-21T16:51:02-04:00", "reference_change": {"absolute": 114.2, "percent": 1.49}, "new_price_samples": 0, "delay_or_missing": true, "breakout_bid": null, "breakout_ask": null, "source_status": "ok_via_browser"}}

回収実績は docs/recovery-goal.md と実受取の証拠で別途確認。仮想利益を実受取に算入しない。
旧固定ゲートと期間可変の採用判断は別。戦略の有効性はこの集計だけでは判定しない。
