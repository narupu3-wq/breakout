# 13時JST枠の解釈

現行run `paper-2c61155f42537ed8` は確認時に稼働中、heartbeat経過54.32秒。直近1時間の決済は0、未約定0、収集エラー0。BTC平均回帰中程度だけが02:00:44 UTCに新規ロング約定し、13時枠では未決済。fresh BTC気配で含み損益は +0.0439 USD（退出費用・追加滑り前、気配時刻は `report.json` の `quotes.BTCUSD.observed_at`）。

10時枠以降はdecision +12、intent/paper_fill +1、close +0。新規intentは候補重複を含む同一BTC平均回帰シグナルで、ETH判断は保有中のためblocked。前回確認したBTCトレンドの利確直後再エントリー連鎖は新しい決済がなく、追加証拠なし。累積8候補全て赤字、3候補が `risk_budget_exhausted`、最大DDは76.8982 USDで75 USD基準を超える。

独立WSはobserving・注文0、Jevは913判断（allow 76 / skip 837）、費用0.139479 USD、残予算0.860521 USD、既知PID 50159が稼働。Jevは別実験のため現行候補に合算しない。

段階は研究・無発注観測。実受取0 USD、Mac mini未回収100,000円。仮想損益を回収実績に算入しない。
