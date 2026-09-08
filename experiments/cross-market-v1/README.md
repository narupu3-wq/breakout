# XYZ100・S&P500とBTC・ETHの比較観測

2026-09-08承認。売買追加の判断材料を集める独立観測。実注文・仮想売買・AI呼び出し0。
Python 3.9以上、標準ライブラリのみ。既存のBTC/ETH研究DB・WebSocket観測を変更しない。

## 記録

約60秒ごとに4銘柄を並列取得。
- XYZ100: Hyperliquid `xyz:XYZ100` L2最良bid/ask。
- S&P500: Hyperliquid `xyz:SP500` L2最良bid/ask。
- BTC/ETH: Kraken現物USDの公開Ticker bid/ask。

Hyperliquidのmetaで両指数が掲載されていることを起動時に確認し、原メタデータを保存。
Hyperliquid価格はBreakoutが参照する外部市場の代理気配。Breakoutとの完全一致は未検証。
KrakenにはTickerのソース時刻がなく、受信時刻で代用する。異なる市場・建値通貨基準の差も含む比較。
4銘柄の時刻差5秒超、指数ソース時刻が15秒超古い、未来5秒超、不正気配、取得エラーは無効記録。
原レスポンス・取得日時・欠損・原因は独立SQLiteに追記。失敗は補間しない。HTTPタイムアウト10秒、次周期に再試行。

## 比較指標（1時間ごと自動集計）

米国現物通常時間と時間外を分ける。2026年の祝日・短縮営業はNY​​SE公表日程、夏時間はAmerica/New_York。
2027年以降はcalendar_unknownとして分離。臨時休場を自動確認する仕組みはない。
- 同一観測周期の変化率相関と同時下落件数。連続する正常観測の間隔45〜90秒のみ。
- BTC/ETH両方の絶対変化が5bps未満の時、指数が10bps以上動いた件数。探索用の固定定義。
- 重ならない15分区間の観測値幅と、仮定コストの比率。12観測以上、観測幅11分以上、90秒超の穴なし。
- 仮定コスト: 往復手数料8bps＋往復滑り10bps＋平均代理スプレッド。swapを含まない。

値幅は後から分かる最大最小の幅で、実現可能な利益ではない。瞬間の高安も取りこぼす。
相関は30組未満・ゼロ分散ならnull。30組は表示開始条件であり、採用・利益・分散の証明ではない。
短い好成績だけで採用しない。通常時間の複数営業日、下落局面、コスト負担を確認し、
XYZ100とS&P500が重複するなら両方採用を前提にしない。仮想売買開始には別の戦略事前登録が必要。

## 操作

```sh
python3 experiments/cross-market-v1/monitor.py start
python3 experiments/cross-market-v1/monitor.py status
python3 experiments/cross-market-v1/monitor.py report
python3 experiments/cross-market-v1/monitor.py stop
python3 -m unittest discover -s experiments/cross-market-v1 -p test_monitor.py -v
```

起動時・毎時に `reports/<UTC-一意ID>.json` を保存。必要時にもreportで集計可能。
集計は最新runのみ。各起動のsource/config/hashをdata/runsへ凍結。過去版を合算しない。
flockで多重writerを拒否。Mac再起動・スリープからの自動復帰設定は追加しない。
既存の毎時AI報告からは上記status/reportを参照可能。追加のAI自動化は作成しない。
データはGit対象外。原記録を削除する自動保持期限はこの観測には設けていない。

## 出典（2026-09-08確認）

- https://intercom.help/breakoutprop/en/articles/16003959-why-do-non-crypto-asset-prices-differ-from-other-platforms
- https://intercom.help/breakoutprop/en/articles/16003943-what-are-the-trading-hours-for-non-crypto-assets
- https://www.breakoutprop.com/symbols/
- https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint
- https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals
- https://www.nyse.com/trade/hours-calendars
