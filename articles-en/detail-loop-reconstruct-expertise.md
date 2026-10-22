---
title: "Using Claude Code to Rebuild Expertise I Don't Have, One Testable Rule at a Time"
emoji: "🔍"
type: "tech"
topics: ["claudecode", "agentskills", "typography", "a11y"]
published: false
description: "I built my personal site with Claude Code and spent half a day polishing Japanese typesetting and accessibility details, two fields outside my expertise. I split the details into one-rule units, took each unit's criterion from outside standards (JLReq, WCAG), and froze each fixed unit as a check that can go red. I think the hypothesis held to some extent. The round with zero new findings hasn't come yet."
tags: claudecode, agentskills, typography, a11y
---

In October 2026, I built a personal site with Claude Code (Opus 5.5). The skeleton came together quickly. After that, I spent half a day polishing details: pushing the corner bracket (「) at the start of a Japanese heading out past the text edge (hanging), characters that must not start a line (line-start kinsoku), a single word left alone on the last line of an English paragraph or heading, how far below the text the link underlines sit, and contrast in the dark color scheme. I value the idea that God is in the details, and when I asked Opus 5.5 to get the small things right too, it did. I also had reviewers acting as domain experts read the site, and their findings ran to several dozen.

But Japanese typesetting and accessibility are both outside my expertise. I don't know where to look, or what counts as good.

So I formed a hypothesis. Even outside your own field, if you split the details into elements and, for each one, research and set an evaluation criterion, then by going through the elements one at a time, you might be able to rebuild expertise at a high level.

When I asked the model to design a procedure around this hypothesis, the first thing it reported was what my site's check script (`eval/run.mjs`) contained. It held only checks that apply to any site: HTML validity, content overflowing the viewport, a lone word on the last line, and accessibility checks with axe. Neither kinsoku nor hanging was a check. Most of the details I had spent half a day fixing could break the next time I changed the CSS, and nobody would notice. This article is the record of testing that hypothesis on the site.

## What experts know: the elements and how to measure them

Experts know what a thing is made of. So they know what changes what, and how to evaluate it. If I, as a non-expert, could write those three things down, I should be able to look where an expert looks.

So I split the details into elements the size of one rule each, and called each element a unit. A unit records four things. The first three correspond to the expert's three, and I added the fourth.

- `what` — what the rule is
- `cause` — what you change to move it
- `eval` — how it shows up in the output
- `why` — what the rule does for the reader

Here is one unit from the site, main lines only. The rule: when a Japanese heading starts with a corner bracket, push the bracket outside the text edge and align the next character with the edge.

```yaml
- id: ja-quote-hang
  field: Japanese typesetting
  what: In a quoted section title the first letter after 「, not the mark, sits on the column edge, on every line of the title.
  why: The quoted phrase reads as a lemma aligned with its gloss; a mark that juts or a letter that sits in reads as an error.
  eval:
    judge: machine
    check: ja-quote-hang
    expect: first letter within 0.5px of the content edge, at 375 and 1280, in the author's font (Hiragino on macOS)
  cause: ".section-title:lang(ja):has(> q:first-child) { text-indent }, :lang(ja) { text-spacing-trim }"
  status: frozen
```

`expect` says the character after the corner bracket sits within 0.5px of the edge, measured at both 375px and 1280px wide, in Hiragino. `cause` is the place in the CSS that moves it.

I don't take evaluation criteria from my own head. I take them from standards documents outside it: [JLReq](https://www.w3.org/TR/jlreq/) (the W3C's requirements for Japanese text layout) for Japanese typesetting, and [WCAG](https://www.w3.org/TR/WCAG22/) for accessibility. The ones who read the site with those standards in hand are reviewers I spin up fresh for every review. There are four roles: Japanese typesetting, English typesetting, accessibility, and art direction. Each one measures the built pages in a real browser (Chrome). The reviewers don't see past findings or the list of units, because a reader who already has the answers repeats the same findings.

A finding from the Japanese-typesetting reviewer comes back in a form like this.

```text
3. fix — the Latin–Japanese space in running text is 0.33em (the Hiragino space); JLReq's default is a quarter em.
   Fix body:lang(ja){word-spacing:-0.08em} with display lines reset → 0.25em.
```

The finding: the space between Japanese and Latin text is 0.33em, and [JLReq's default is a quarter em](https://www.w3.org/TR/jlreq/#handling-of-western-text-in-japanese-text-using-proportional-western-fonts). I can't spot that difference by eye. But I can confirm that the standard lives in JLReq, and that the measured value deviates from it.

## Turning details into checks that can go red

Once a unit is fixed, I turn it into a check and freeze it. All the frozen checks run with one command: red if something broke, green if it holds. For now I run them on my Mac; they aren't in CI yet. One round is: pick which reviewer findings to take, fix them, and freeze. I repeat that. The stopping point I aim for is a round in which I take zero new findings.

Let me follow ja-quote-hang to show how one unit gets frozen. The first time I made units for the site and ran them, Opus 5.5 found the hanging-bracket misalignment as a new bug and fixed it. Looking at the screenshot after the fix, I replied, "Isn't this an old version of the site?" That run had been on a branch older than the published version. In the published version, the misalignment was already fixed. A unit means something only when it is measured against the published version.

When I reran on the published version, the unit went red, this time for a different reason. At both 375px and 1280px, the character after the corner bracket sat at +0.84px from the edge. The headings had 0.04em of letter spacing, and that spacing was also applied to the bracket pushed outside. Setting the letter spacing to 0 for the bracket alone brought the offset to +0.0px.

After a fix, I make sure the check actually works. I break the cause slightly on purpose, build, and run every check. For this unit, I change the one CSS line that pushes the corner bracket outside the text edge, like this.

```diff
- text-indent: -0.5em;
+ text-indent: -0.4em;
```

Only this unit went red; every other unit stayed green. That lets me say this check measures this rule.

If it stays green after the break, then either the break or the check is missing the rule. This did happen. One rule keeps a section heading that starts with a corner bracket on screen while the body scrolls, on wide screens. Deleting the first `sticky` declaration left it green, because another rule further down set the same declaration again. A unit for underline length also stayed green: when I broke the value, padding held the width in its place. In both cases the problem was in how I broke it, not in the check. I rewrote the first to break the later rule that was actually in effect, and the second to break the whole set of declarations behind the cause at once, confirmed that each went red, and then froze them.

## Running it, and where it fell short

I capped the review at three rounds per work session. In those three rounds, the round with zero new findings didn't come. In every round, I took seven or more new findings.

Fixes made in response to findings broke other details twice. A fix that kept English link text from breaking across lines used non-breaking spaces. In Charter, the English typeface, that space is drawn at exactly twice the width of a normal space, so the gaps between words doubled. A fix that kept a single word from being left alone on the last line of the English project descriptions also took effect on the Japanese description lines, and lines broke in the middle of words. Both times, the next round's reviewers found it, and it went onto the list of new findings I took. Since then, I limit each fix to the language and the page the finding named.

## The calls I handed over were overturned in Safari

Some judgments of taste remained that the reviewers couldn't make: how far down the underline sits, how much text fades as you scroll, the saturation of the green in the dark scheme, and so on. At first I tried to decide them one at a time, but partway through I handed them over: "Just go with your recommendation on all of them." Looking at the result, I thought, "Overall it feels higher quality, more professional."

After that, I opened my about page in Safari and wrote: "Isn't it only the Japanese about page where the line breaks are off? It breaks after （, it breaks after M1MAc上の　, and also the line widths being all over the place feels kind of weird." The two "after"s point to the spot right after an opening parenthesis, and the spot right after "M1 Mac上の" ("on an M1 Mac"). Here I overturned two of the calls I had handed over.

The first was setting the Japanese bio on the about page, like the headings, to not break between Japanese characters. In the bio, the only places a line could break became the spots decided in advance, such as after "上の" ("on"), and where a line still overflowed, the browser forced a break. In Safari, that forced break landed right after an opening parenthesis. The frozen checks ran only in Chrome, and in Chrome the opening parenthesis was pushed to the next line, so the check was green. I put the bio back to ordinary body text. The second was the call to leave Japanese body text unjustified, with ragged line ends. Read in Safari, the line widths looked uneven, so I made it justified when the screen is 30rem (480px) wide or more.

The two calls weren't overturned because they were made without asking me. They were overturned because they were made without looking at the page in the environment I read it in.

So I ran every frozen unit in Safari's engine (WebKit) as well. Of the 49 units that were green in Chrome, 7 went red.

- For 2 units, the difference was in measurement. Asked for the position of the first character on a line, WebKit also returns the position of the end of the previous line, and Safari's Tab key doesn't stop on links by default. I fixed the checks.
- For 2 units, the engines render differently. I widened the tolerance.
- 3 units were actually broken in Safari. I fixed the site.

With that, all 49 frozen units are green in Chrome. In WebKit, 48 are green: all but the one unit whose check needs the Chrome DevTools Protocol (CDP). The repository keeps 54 ways of breaking the 49 units. I recorded 56 units in all; the rest are 5 units I read by eye with no check, 1 unit that has no check yet, and 1 unit I stopped using.

## What I decided, and what I haven't

I think the hypothesis held to some extent. I split typesetting and accessibility, both outside my expertise, into units and measured them against outside standards. The site is simple, but it came out feeling well made.

From this experience, I decided three things.

First: if I hand things over, I let the model run all the way to the finished state without stopping it partway. Of the decisions it makes on my behalf, it shows me only the high-impact ones, and I judge from the finished result. But when the model decides, I have it measure in the environment I read in. I read in Safari, so it measures in WebKit too.

Second: I don't turn the overall impression into a check. Five units, such as how the page looks as a whole, the rhythm of the whitespace, and whether each section's lead says what the section contains, have no check; I kept them as things I read. Even if the model puts a score on the overall impression, that number doesn't tell you what to fix.

Third: I use this procedure not only for the site but for code and prose too. Partway through, I had turned the procedure I was running on the site into four Claude Code skills.

- detail-review — spins up reviewers and collects findings
- detail-units — splits findings into units
- unit-eval — freezes units into checks
- detail-loop — runs those in order

I reworked these four so they apply to code and prose as well. And I'm trying them on this article too. For prose, what detail-loop fixes is presentation: spelling, terminology, links, code, and figures. Changes to wording or claims come back to me as proposals, even when it has been handed the decisions. For this article, I handed over the accept-or-reject calls on those proposals as well. The hypothesis, and the assessment that it held to some extent, are my own decisions.

There are also things I haven't decided. I haven't yet reached a round with zero new findings. The checks protect only the details found so far. Details not yet found can only be found by review.

## Related links

- [The site's source and eval/ (GitHub)](https://github.com/shimo4228/shimo4228.github.io/tree/source/eval) — the unit list (units.yaml), the findings ledger (ledger.md; this article's three rounds are Rounds 4–6), and the break-and-check script (mutate.sh)
- [The detail-loop skill (GitHub)](https://github.com/shimo4228/claude-harness/tree/main/skills/detail-loop) — all four skills above are in skills/ in the same repository
- [The Markdown source of this article (GitHub)](https://github.com/shimo4228/zenn-content/blob/main/articles-en/detail-loop-reconstruct-expertise.md) — every article's Markdown and the index (docs/PUBLICATIONS.md) live in the same repository
- [The author's GitHub](https://github.com/shimo4228) — research repositories with DOIs

---

**How this was written:** Claude (Claude Code) wrote the prose, revised it through detail-loop's reviews and checks, and translated it into English. It worked from my session records, the site's units, findings ledger, and check records, and conversations with me. I decided the hypothesis (whether splitting details outside my expertise into elements can rebuild expertise) and the assessment that it held to some extent. I read the full Japanese original before publishing, and I am responsible for the content of both versions.
