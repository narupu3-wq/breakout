# 定時分析 2026-09-21 19:00 JST

現行 `paper-2c61155f42537ed8` はheartbeat約34秒、観測168.00時間（約7日）。直近1時間はBTCUSDの候補決済7件、候補合計の手数料込み確定損益は+5.9551 USD。候補間の仮想口座を合算しない。7候補でBTCUSD建玉を保有し、fresh quote（観測時刻1789984970.4621499）で含み損益を評価している。mean_reversion-cautious-stress は `risk_budget_exhausted`、その他のstress候補を含む現行成績は研究用の未確定証拠である。

固定版の停止run、旧データ、停止期間はforwardに加算しない。固定版と現行版は別成績として報告する。

S&P500の外部監視は `reports/monitoring/sp500/20260921T100643Z.json` に保存した。現物市場は寄り付き前、指数値・前日比は取得不可、Breakout bid/askは未接続で、新規価格サンプル0件。

回収段階は研究・無発注観測、実受取0 USD、Mac mini未回収100,000円。仮想利益は回収に算入しない。
