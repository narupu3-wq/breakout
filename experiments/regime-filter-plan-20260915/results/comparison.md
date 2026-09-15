# BTC方向フィルター比較結果

status: ``complete``

期間: 1788732000 <= ts < 1789380000（720本、15分足）

| candidate | arm | net realized | max DD | closed | halt |
|---|---|---:|---:|---:|---|
| trend-cautious | baseline | -35.625832 | 38.003893 | 29 |  |
| trend-cautious | btc_mean_reversion_filter | -35.625832 | 38.003893 | 29 |  |
| trend-cautious-stress | baseline | -44.632025 | 44.632025 | 21 | risk_budget_exhausted |
| trend-cautious-stress | btc_mean_reversion_filter | -44.632025 | 44.632025 | 21 | risk_budget_exhausted |
| mean_reversion-cautious | baseline | -44.544074 | 44.569201 | 45 | risk_budget_exhausted |
| mean_reversion-cautious | btc_mean_reversion_filter | -27.732658 | 41.853448 | 39 |  |
| mean_reversion-cautious-stress | baseline | -44.656280 | 44.656280 | 32 | risk_budget_exhausted |
| mean_reversion-cautious-stress | btc_mean_reversion_filter | -44.521010 | 48.256913 | 38 | risk_budget_exhausted |
| trend-moderate | baseline | -35.625832 | 38.003893 | 29 |  |
| trend-moderate | btc_mean_reversion_filter | -35.625832 | 38.003893 | 29 |  |
| trend-moderate-stress | baseline | -74.728541 | 74.728541 | 31 | risk_budget_exhausted |
| trend-moderate-stress | btc_mean_reversion_filter | -74.728541 | 74.728541 | 31 | risk_budget_exhausted |
| mean_reversion-moderate | baseline | -74.121481 | 74.575966 | 58 |  |
| mean_reversion-moderate | btc_mean_reversion_filter | -28.711048 | 46.812932 | 39 |  |
| mean_reversion-moderate-stress | baseline | -74.618293 | 74.618293 | 46 | risk_budget_exhausted |
| mean_reversion-moderate-stress | btc_mean_reversion_filter | -74.575516 | 78.311419 | 50 | risk_budget_exhausted |
