# Publication procedures

`writing-ecosystem` の出典編入と公開前の開示で、必要な phase にだけ読む手順。

## 引用の検証水準（citation tier）

引用に要求される検証の深さは、**引用が何を主張するか**と**ジャンル**で決まる。

| 引用のレベル | 例 | 必要な検証 |
|---|---|---|
| **帰属**（著者 X は Y と主張している） | 「Froese は AI ジレンマを定式化した」 | 抄録で可 — 抄録は著者自身が書き査読を通った公式の主張要約 |
| **中身・ニュアンス**（議論の詳細・特定ページ） | 「p.165 で〜と述べる」 | 該当箇所の通読 |
| **評価・反駁**（当否の判定・批判・拡張） | 「この議論は誤っている」 | 全文精読 |

- **エッセイ / 記事**（人間向け）: 帰属レベルに収まる引用なら抄録ベースで可。当否判定をしないことを本文で明示するとなお良い
- **学術 paper**: 本表を適用しない。`paper-ecosystem`（`~/MyAI_Lab/paper-lab` 常駐）の Source Fidelity Rules（一次ソース直接照合）が正本で、常に厳格側
- **検証の格を隠さない**: 抄録引用は全文精読と同じ見た目になる（citation laundering）。抄録には本文より強く言う「スピン」の実証報告もある。本文で開示する先例: 「出典の格は中程度（三次文献）であり、一次学術文献での裏取りは未了」型の一文

## AI 開示

AI が本文を書いた稿は、全媒体で記事の最末尾に開示の段落を 1 つ置く。関連リンク節があればその後に `---` を
引いて置く（`zenn_evidence.py` はこの区切りで関連リンク節を閉じる）。見出し語は JA `**この記事の書き方**`、
EN `**How this was written:**` に固定する — reviewer は両方の語で、`zenn_evidence.py` は Zenn 稿の JA の語で探す。

枠はその記事の具体で埋める。毎回同じ文を貼ると読み飛ばされ、何をしたかの情報が消える:

1. 誰が本文を書いたか（ツール名）
2. 素材 — 承認済み brief と証拠台帳から取る
3. 著者が決めたこと — 中心の主張、何を採り何を捨てたか
4. 著者が確かめたこと — 再計測、一次資料との照合など。確かめていない検証は書かない。書けない枠は文ごと削る
5. 責任の一文

リンクは置かない。来歴の根拠は本文と関連リンクが持つ。主語は著者の一人称（私 / I）。

```markdown
---

**この記事の書き方**: 本文は Claude（Claude Code）が書きました。素材は〈私のセッション記録と計測結果〉と、私との対話です。〈中心の主張と、どの結果を採るか〉は私が決め、〈数値は手元で再計測し、引用は一次資料と照らし合わせ〉ました。公開前に私が全文を読み、内容の責任は私が負います。
```

```markdown
---

**How this was written:** Claude (Claude Code) wrote the prose. It worked from 〈my session records and measurements〉 and from conversations with me. I decided 〈the central claim and which results to keep〉, and I 〈re-ran the measurements and checked each quote against its source〉. I read the full text before publishing, and I am responsible for its content.
```

EN 稿は JA 稿の開示を訳し、EN 稿で新たに AI がしたこと（翻訳）を (1) に足す。
