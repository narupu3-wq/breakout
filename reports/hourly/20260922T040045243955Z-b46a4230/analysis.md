# 13時JST枠の解釈

旧run `paper-a933e913646055c5` は停止保持。heartbeatは966,238秒超で、直近1時間の新規イベント・決済・未約定は0。停止期間をforward観測に数えず、現行と合算しない。

固定 `report.json` の数値を使用した。現行paperはheartbeat経過54.32秒で、直近1時間の新規intentはなく、旧runの記録品質警告は残る。
