# jev-filter-v1: Jev見送りフィルター比較（無発注）

既存の8候補戦略は変更しない。新規エントリー直前にJev（TypeSafe）へ
「allow / skip」を1問だけ問い、skipなら見送るフィルターを独立DBで比較する。

- 予算: API費用は総額1 USD・請求は入力トークンのみ（$0.042/MTok公表値）。
  台帳 `data/ledger.sqlite3` に実績を記録し、残額が1リクエスト予約額（0.01 USD）を
  下回ったら呼び出し前で停止する。
- 期限: 30日。それ以降の新規判断はしない。
- 判断は確定足ごとに1回。同じ `candle_key` の再呼び出しは拒否する。
- API失敗・応答不正のときは取引を見送り、例外を記録する。自動リトライしない。
- 実発注なし。既存の観測DB・常駐プロセスには書き込まない。

## 使い方

```sh
# 保存済み応答の判定（API通信なし）
echo '{"answers":{"entry":{"type":"choice","choice":"allow","probabilities":{"allow":0.8,"skip":0.2}}}}' \
  | python3 experiments/jev-filter-v1/compare.py

# テスト（モックのみ、外部通信なし）
python3 -m unittest discover -s experiments/jev-filter-v1/tests -v
```

実APIの呼び出しは `jev.evaluate(..., dry_run=False)` で、
キーチェーン（ログイン・アカウント `jev`・項目 `TYPESAFE_AI_API_KEY`）からキーを取得する。
キーはファイル・ログに出力しない。

## 制約

- Kraken代理価格のまま。Breakout約定の証明にはならない。
- 判定しなかった足は基準版と同じ挙動を保つ。後から判断を付け直さない。
- 収益性の結論は30日分のforward蓄積後に行う。単発の疎通・短期的な損益では判定しない。
