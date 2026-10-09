# Editorial brief: skill-description-pointer

証拠台帳: `drafts/article-context_skill-description-pointer_2026-10-09.md`（非公開。付属 `drafts/skill-description-pointer-evidence/`）
内部調査: [research/2026-10-09-skill-listing-budget.md](research/2026-10-09-skill-listing-budget.md)（Claude Code 2.1.295 の listing の実装）

```markdown
Reader: Zenn の読者（検索・feed から来た engineer が、数秒で用途を理解し、再現または判断できる）。著者の「誰に向けて」の原文は未取得 — brief 確認で聞く
Channel: Zenn（articles/<slug>.md）。Dev.to 版は内容 GO 後に判断
Author's words: 「スキルのDescriptionはどうあるべきか？」「といのまま読者に渡していいよ」。起点の発話「なんか私のスキルのDescription長すぎない？」（台帳 2026-10-08）、判断の発話「そうだな、彼の設計指針には同意だ。この方向でスキル設計することをハーネスに反映した上で、descriptionを整理しようか」（同）
Personas:
- primary: Claude Code で自作の skill を 10〜50 本持ち、description を docs の書き方どおりに「何をするか + いつ使うか」で書いてきた engineer。`/skill-doctor` はまだ開いたことがない。比べる相手は Anthropic の skills docs。5 分で要点を掴みたい
- inflow: Zenn の claudecode トピックの feed から来た人。plugin の skill を数本入れているが、自作は 1〜2 本。流し読み 60 秒で、自分に関係があるかだけを決める
- practitioner: 自前の harness（CLAUDE.md・rules・skills・hooks）を半年以上運用し、日本語のハーネス記事（減築・棚卸しの実測記事）を読み比べてきた人。mattpocock/skills の名前は知っている。設定を削った記事は数字の前後と、削って何が分からなくなったかで読む
Central thesis: skill の description は、毎ターン model に送られる listing に常駐し、予算を超えると使われていない skill から名前だけになる — その層を、著者は「invocation を先に決め、model に呼ばせる skill だけを常駐ポインタとして短く書き、幅を lint で数える」と決めたが、それで発火がどう変わるかは測っていない。skill の description はどうあるべきか、を読者に問いのまま渡す
Entry bridge: 自分の skill の description を見て「長すぎない？」と思った人の場面。54 本の合計は 28,131 字で、`/skill-doctor` で見ると、~/.claude/skills に置いた skill のうち description が 459〜1,048 字ある 4 本（うち mono-color は外部の skill の symlink）が、20 token 未満の行（= 名前だけ）で毎ターン送られていた
Figure plan: hero なし（比喩を置かない）/ 「予算があり、超えると名前だけ」節 → 流れ → 図あり（budget）/ 「先に、モデルに呼ばせるか」節 → 対比 → 図あり（invocation）/ 「削っても戻る」「lint」「決めなかったこと」→ 表と散文で足りる・形が言えない → 図なし
Causal spine:
1. 観察 — 「長すぎない？」から測る: 54 本・合計 28,131 字・中央値 435.5 字・800 字超 10 本（C1）。`/skill-doctor` で、listing の 1 行が 20 token 未満の skill が 29 本、そのうち自前で description の長い 4 本は名前だけで載っていた（C10、凡例と内部調査）
2. 緊張 — 名前だけの skill は model から呼ばれにくく、呼ばれないので使用スコアが 0 のまま、名前だけに留まる（機序からの読み。発火の実測ではない）。しかも削っても戻る: 8/30 から 5 本減ったのに字数は増えていた（C4）
3. 機序 — listing の予算は context window × 1 token あたり 3 字 × 1%（Opus 5.5 の 1M では 30,000。1M が止められていれば 6,000）。超えると、bundled 以外を使用スコア（使用回数 × 7 日の半減）順に並べ、残り予算に丸ごと収まる description だけを付け、残りは名前だけ。途中で切らず、入らなければ飛ばして次へ進む。幅は全角 2（内部調査）
4. 著者の判断 — 決めたこと: Pocock の invocation 二分に同意（C20、Author's words）。model に呼ばせない skill は `disable-model-invocation` で listing から出す（2 本移動、C12）。呼ばせる skill は常駐ポインタ: 1 分岐 1 トリガー、手順を書かない、日本語は括弧で 1 回、衝突する対だけ肯定形の振り分け（C13 の実物）。幅を lint で数える（1 本 400・合計 12,000、C14）。結果: 合計 10,378 字、20 token 未満の自前 0 本（C2・C11）。決めなかったこと: 発火率は測っていない（C16）。前回は文言の手直しで自発発火が 27% → 8% に下がっている（C17、分母は記録に無い）。400 と 12,000 は較正していない（C15）。締めは問いのまま
Selected evidence:
- C1・C10（凡例つき）: 観察の実物。自前 4 本の名前だけの行を 1 件見せる
- 内部調査 §5: 名前だけになる規則（使用スコア順・丸ごと・飛ばして次へ）。コード片は短い逐語 1 つまで
- 内部調査 §1・§2: 予算の式と 30,000（条件つき）
- C4: 削っても戻る
- C20: invocation の二分という外部の設計指針（mattpocock/skills b0618bc）
- C13: measurement-discipline の前後（1,046 → 291 字）を、ポインタの書き方の 1 例として全文で
- C14・C15: lint の 400 / 12,000 と、較正していないこと
- C2・C11: 後の数字（10,378 字、自前の名前だけ 0）
- C16・C17: 決めなかったこと
Out of scope:
- C21（Pocock 38 本の中央値、⚠ 未検証）・C23〜C25（⚠ 未検証の外部主張）・C28（公開 repo への反映、⚠）
- C22（#68086 の英語トリガー 0 回発火）— 日本語話者に効く論点だが、n=1 の自己申告で、「直った」部分は未検証
- docs の既定値が fetch ごとに食い違った件、ADR と再計測の 3 字差、2.1.286 / 2.1.295 の版差
- RFC-0018 の「誰も監査しない常駐の指示層」— 命題の言い換えに近いが、著者の言葉ではないので本文の語にしない
- 「20 token 未満 29 本」の内訳のうち、自前 4 本以外（plugin・claude.ai 同期）が名前だけか、短い description かの切り分け
```

## brief 確認で著者に聞くこと

- Reader の「誰に向けて書くか」の原文
- Personas の 3 人
- 数字の訂正: 依頼の「/skill-doctor の名前だけ 29 → 6 本」は、生出力の凡例では「listing の 1 行が 20 token 未満」の本数で、名前だけと確定できるのは自前の description の長い 4 本（→ 0 本）だけ。本文はこの言い方にする
