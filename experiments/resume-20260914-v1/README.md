# 独立観測再開 2026-09-14 v1

事前登録：2026-09-14 19時定時レビュー。旧runはデータ欠損停止のまま保持。同一戦略・費用・損失限度・ゲートを別DBで再観測する運用版であり、収益改善仮説ではない。ソース4ファイルは基準版と同一。設定はversionのみ変更。

開始以降のみ新しいforward。旧データ、停止期間、今回取得する過去足をforwardの成績に加算しない。短縮合格は行わず100決済等を維持し、旧60日表示と可変期間判断は別。通常/倍費用の全8候補と品質・最大DDを報告。旧版と新規版を合算しない。利益・品質が十分でない限り昇格なし。

起動：`python3 experiments/resume-20260914-v1/service.py start`
状態：`python3 experiments/resume-20260914-v1/service.py status`
集計：`python3 experiments/resume-20260914-v1/research.py report`
定時JSON：`python3 hourly_report.py --db experiments/resume-20260914-v1/data/research.sqlite3 --out experiments/resume-20260914-v1/reports/hourly`

ROOT、既定config、DB、凍結run、ログ、レポートはすべて本フォルダー内。旧writerは停止確認済み。AI・実注文0。OS自動起動やスリープ変更なし。
