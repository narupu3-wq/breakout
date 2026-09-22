# 10時JST枠の解釈

旧run `paper-a933e913646055c5` は停止保持。heartbeatは955,532秒超で、直近1時間の新規イベント・決済・未約定は0。累積候補は全て `data_gap_requires_new_version` であり、現在の成績と混ぜない。

数値は同フォルダーの固定 `report.json` に基づく。旧runの停止期間をforward観測として数えず、リセットや再開は行っていない。
