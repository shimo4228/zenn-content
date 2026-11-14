# Where Does the Human Do the Eval?

> Trying to answer a question from a lecture, I couldn't say what I meant by my own Eval. It turned out to be how I judge the final artifact, and from there the question kept drifting toward who takes on the explaining.

If someone tells you a score is 7, the score itself doesn't tell you what that 7 means. Whether 7 is high or low, and 7 compared to what, is decided by a yardstick that sits outside the score. For a secondhand item's appraisal, that yardstick is the price the item actually sold for. Held up against the selling price, an appraisal stops being just a number.

This came up in a lecture on judgment and measurement that I've been studying lately. In my notes for that session, I left myself a question: "For my own eval, what is the external yardstick that plays the role of price?"

When I tried to answer it, I got stuck. Before I could get to the external yardstick, I couldn't say what the thing I call my Eval actually refers to.

## Scores don't give reasons

In the LLM field right now, "Eval" usually means a benchmark or a score. You have a model solve tasks, grade the answers it gives, and compare accuracy. What gets graded is mostly the result. Why the result came out that way is, in most cases, not asked.

I find this crude. The idea that all that matters is getting the result looks to me like machine-learning evaluation simply stretched further. But when a person evaluates something and hands that evaluation to someone else, the question "why did it come out this way?" is, in most cases, asked as much as the result itself. LLM Evals don't reach that far.

## What I was deciding on was the final artifact

When I have Claude Code build an Eval for me, it's almost always in an area I don't know well. I can't write down what counts as good myself, so I leave even the grading method to Claude. Still, whether to use what comes out of it, the final artifact, is something I decide at the end.

The code I have Claude write is mostly my own AI agents. Looking back at what actually decides it for me: with code, I run the agent and see whether it behaves the way I intended. I don't look at whether the code is well written. With an article, I read it and see whether it fits my own sense of it.

On the article side, there's a clear example. In August I wrote an essay on note, a Japanese blogging platform, "After I Ran Out of Things to Ask AI, One Desire Remained." At the time, I was running a system I had built with Claude to judge drafts. It said the draft was good enough to publish. It had also passed review by the agents that handle reviewing. Even so, I read it through, rebuilt the first half, and took the thinking further.

I still think that essay is the best-written thing I've made. I feel my own thinking runs all the way through to the conclusion, and that it became something only I could have written. The standard for whether my thinking ran through it was at work inside me as I read.

For code, I watch the behavior; for an article, I read and decide by feel. What I'm looking at differs. With an article, the article itself is the final artifact, but with code, the final artifact isn't the code but the behavior the code produces. If I answer the question in my notes, what played the role of the external yardstick was my own sense for articles and the agent's behavior for code. While I was looking for the yardstick, I first came to see what my own Eval was: how I judge the final artifact.

Even when I left the building of the Eval to Claude, judging the final artifact stayed in my hands. Where is it that a human has to do the Eval? In my case, this was the first answer.

## Who was asking for the explanation?

I'm dissatisfied that LLM Evals don't give enough explanation of why a result came out the way it did (see footnote). Yet my own Eval looks only at the final artifact. I wasn't asking about the process that led there, or why it came out that way. The very person demanding explanations was deciding on results alone.

Evaluations that are expected to come with explanations do exist. Take land valuation for tax purposes: there are ways to check the basis on which an assessed value was calculated, and if you aren't convinced, there's a procedure for filing an objection. The side that produces and issues the valuation has to be able to answer why the value is what it is. That level of explanation is what I feel is missing from LLM Evals.

So was my dissatisfaction misplaced? The dissatisfaction itself hasn't changed. But the two things I was comparing were in different positions to begin with.

If I map this onto me and Claude, the person who issues an assessed value in land valuation is in Claude's position. The side that produces and issues the evaluation is the one asked for reasons. When I decide whether to use what Claude produced, I'm on the receiving side. For its own use, the receiving side can decide by looking at the final artifact.

But this distinction doesn't split cleanly. Someone who receives an assessed value can also ask why it is what it is. The ways to check the basis exist, presumably, so that the receiving side can check. The same thing happens with code. If I hand an agent I built to someone else, I, who was supposedly on the receiving side, now stand on the side that produces and issues it. When someone asks why I can say it's fine, the one who answers isn't Claude but me. In the end, the one who explains is a human.

Thinking it through this way, the question of where a human has to do the Eval gets pulled toward a different question: who takes on the explaining?

## A candidate answer, and why I can't commit to it

There is one thing that looks like an answer. A human has to do the Eval wherever they end up on the side that explains. If you're only using something yourself, looking at the final artifact is enough; if you're handing it to someone, then before you hand it over, you check it to the point where you can explain it.

It seems to hold together. But I can't commit to this answer. If I do, the question of the Eval gets replaced outright by a question of responsibility. Once it's settled who takes on the explaining, where to do the Eval is settled too. Thinking about the Eval then becomes almost the same as deciding how to divide up responsibility, and whatever remains as a question about the Eval itself drops out of sight.

I suspect that the question of where to do the Eval and the question of who takes on the explaining can't be pulled apart. If they can't, what remains as a question about the Eval? That is what I still don't understand.

## Maybe "Eval" is too narrow

One reason I don't understand it may lie in how far the word "Eval" reaches.

In the LLM field right now, the word "Eval" is pulled strongly toward benchmarks and scores. When I wrote "[Can You Tell an Eval from a Review?](https://dev.to/shimo4228/can-you-tell-an-eval-from-a-review-1b3)" earlier, I lined up the sources and got as far as confirming that having a score is not what separates an Eval from what isn't one. Even so, the center of gravity keeps sliding back toward scores before I notice. That pull may have been at work in how I framed the question, too: where does a human have to do the Eval?

But evaluation doesn't only happen where scores are given. The things this essay has looked at, reading an article and rebuilding its first half or running an agent to check how it behaves, are evaluation too. We are evaluating something almost all the time. LLMs, too, are evaluating constantly.

If I take Eval that broadly, the shape of the question of where a human has to do the Eval may itself change. How it would change, I can't say yet.

What I've decided for now is to put the starting point at how I judge the final artifact. And the question of where to do the Eval and the question of who takes on the explaining probably can't be pulled apart. I can say that much. Whether to commit to saying that a human does the Eval wherever they end up on the side that explains, and how broadly to take the word "Eval": those two I haven't decided yet.

## Footnote

(Footnote) When I wrote "not enough explanation," I didn't mean there's no explanation at all. With LLM Evals, too, you can add how the scores were given, or the reasons for a judgment, after the fact. What bothers me is that I can't tell whether the judgment was reached through a process that could stand up to explanation. In land valuation for tax purposes, the valuation procedure is fixed in advance, and the assessed value comes out by following it. There, you could say, the explanation isn't something assembled after the judgment but something placed before it. Does the explanation come after the judgment or before it? How to think about that difference looks like a big question in its own right, so in this essay I've left it open.

## Sources

- "[Can You Tell an Eval from a Review?](https://dev.to/shimo4228/can-you-tell-an-eval-from-a-review-1b3)" (DEV; Japanese original on Zenn: https://zenn.dev/shimo4228/articles/claude-code-eval-concepts)
- "[After I Ran Out of Things to Ask AI, One Desire Remained](https://shimo4228.substack.com/p/after-i-ran-out-of-things-to-ask)" (Substack; Japanese original on note: https://note.com/sakamaki4228/n/n2375bfc4d521)

---

**How this was written:** Claude (Claude Code) wrote the prose, and also translated it from the Japanese original into this English version. The material was my notes from a lecture I've been studying lately and an interview Claude did with me for this essay, one question at a time. I handed over my answers as material, and Claude put the text together. I decided which question to put at the center and what to leave undecided. Claude checked the background of the August essay against the records from that time. I read the full text before publishing, and I am responsible for its content.
