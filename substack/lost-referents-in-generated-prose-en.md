# Why Does AI Writing Feel Like It's Floating?

> Every sentence reads fine, yet the whole thing hangs in midair. On "common ground," and what an AI writer presumes you already have.

Reading text written by AI, I sometimes get a strange feeling. It feels as if it doesn't share its premises with a human being. Each sentence is correct and easy to read, yet the whole is hollow, floating in midair. In baseball terms, the strike zone is different. The ball never comes where I'm set to swing, and when I do swing, it feels like we're playing a different sport.

Take the research report I read every morning. I carry a handful of open questions about how AI agents should be designed. A pipeline I built collects papers related to those questions every day, and an LLM summarizes each day's batch in a few paragraphs of Japanese. One morning, the report said this (translated here):

> The problem the first study addressed was that instructions alone make it hard to catch behavioral drift.

> The problem the second study addressed was the risk that when the surrounding machinery (the harness) modifies itself, it ends up memorizing the practice tasks.

It reads smoothly. But I never figured out which papers it was talking about. I hadn't read the papers, so for me "the first study" pointed at nothing.

Where does this feeling come from? Over the past week or so, writing with AI, I ran into the same feeling again and again. Let me lay those scenes side by side.

## The mismatch ran in two directions

The first direction is explaining what the reader already knows. With Claude Code, I was writing a technical article for engineers. The draft explained skills as "some fifty short procedure documents (skills) built from the agent's own experience." I wrote back: "Readers know what a skill is. No need to explain."

The second direction is skipping what the reader needs. Another article's draft contained the line "At the end of the morning article, I wrote…". "The morning article" meant a different article I had published earlier that day. Claude Code and I were inside the same day's work, so between us it made sense. To a reader it doesn't. I wrote back: "Readers have no way of knowing that I'm writing this article on the afternoon of the same day, so unless you say exactly which article and which part, none of it makes sense." The report at the top runs in this direction too. The name of each paper, which a reader who hasn't read the papers needs most, was missing.

The awkward part is that both directions came from following the rules. The prompt given to the LLM that writes the report described the reader as someone who "hasn't read today's papers and doesn't know the field's jargon," and asked it to write "without jargon." The LLM did exactly that, and dropped the paper names along with the jargon. The drafts I tested before putting the pipeline into production also passed a check in which a separate LLM judges whether each summary is faithful to the original paper (LLM-as-a-judge).

The drafts of this essay were no different. Claude Code wrote them too, and I have it read a set of writing rules that define the reader for each outlet. For note, the Japanese platform where this essay first appeared, the rules said the reader was "a general reader who uses AI at work and in daily life." Reading that, Claude Code decided to avoid technical words: it renamed the prompt "the instruction text" and described GPT-5.6 Sol, which runs on a Codex subscription, as "another company's model that can run within a flat-rate plan." That is the first direction: treating words the reader knows as if they were unknown. Sentences that should have supplied a premise were missing all over the draft, too. That is the second direction. These are the words I used while reading it: "What's 'instruction text'?" "It keeps just missing the premise, so it floats." "It reads like a scene reconstructed from hearsay."

## Premises are built by checking

The feeling had a close relative in linguistics. The psycholinguists Herbert Clark and Susan Brennan called the knowledge, beliefs, and assumptions two people in a conversation share their "common ground" (1991). The two have to update this common ground moment by moment. Updating it while checking whether what was said has been understood is what they called grounding. You ask, "Do you have a car?" and hear back, "A car?" Only then do you learn the other person hasn't understood yet. The premises of a conversation are built from small checks like that.

For LLMs, Omar Shaikh and colleagues looked at this in a 2024 paper. Compared with humans, the text LLMs generate in dialogue contains fewer grounding acts, such as clarification questions and acknowledgments, and instead "appears to simply presume common ground." What they studied was dialogue, not articles or reports. Even so, the unease I had been feeling is very close to that word "presume."

Looking back at those scenes, it becomes clear what the AI writer actually had to work with. Not the reader in person. What it had was a written description of the reader: "hasn't read today's papers and doesn't know the field's jargon." "A general reader who uses AI at work and in daily life." And instead of the events themselves, records extracted from conversation logs and work history. From those descriptions and records, the AI infers what the reader knows and writes as if that were shared. When the inference is off, it explains what the reader knows and skips what the reader needs. It never lived through the scene, so the obvious premises that no record captured never make it into the text either. That, I suspect, is what I was calling "hearsay."

Back to the strike zone: the AI isn't looking at the catcher's mitt. It is reading a written description of the zone and throwing at that.

## What fixed the mismatch was a reader who stopped

So will writing more rules in advance fix it? In my experience, no. When I wrote the previous article, I had already added a rule to those writing rules: "Use existing terms without paraphrasing, and explain them at first use." The draft of this essay still said "instruction text." When I looked, the same rules already had, higher up, an older line saying "If you can say it in everyday words, don't use technical terms," which collided head-on with the rule I had added. Claude Code didn't break a rule when it wrote "instruction text." It followed the rule above.

What fixed the mismatch was a real reader stopping and saying where they stopped. The biggest fix was to this essay itself.

This essay was first written as a story about "paper names disappearing from AI writing." However many times Claude Code revised the draft, my reading stopped at the same place: "Honestly, I can't tell what this is trying to say overall. It's far too wordy." So I put into words what was actually bothering me: "What bothers me about AI writing is that it feels like it doesn't share its premises with a human being. It feels hollow somehow, like it's floating in midair." That one remark replaced the essay's question. The opening paragraph is a write-up of what I said then.

In Clark's terms, my reading, and that one remark made where I stopped, played the role of the grounding the writer lacked.

So what changes from here? Before reaching this conclusion, Claude Code proposed adding procedures, such as having it list the reader's premises before writing. I answered: "Isn't that just more surgery?" Adding a procedure is just adding one more written description of the reader.

So I decided that an essay's question is something I say in my own words, instead of letting AI infer it. The strongest parts of this essay are the opening paragraph about the unease and the remark that replaced the question. Neither is a sentence Claude Code wrote by inference. Both are places where words I said while reading went in as they were.

Whether it's a meeting summary or a research report, when AI writing feels like it's floating, I don't think the question to ask is whether it's well written. The question is what this text presumes I already have. And then: tell the writer where you stopped. Between me and this writer, that is the check that actually worked.

Whether an AI writer will ever be able to check on its own, to ask "Does this make sense to you?", I don't know yet.

---

## Sources

- The pipeline that writes the research report at the top (jev-research-pipeline, GitHub): https://github.com/shimo4228/jev-research-pipeline
- Clark, H. H., & Brennan, S. E. (1991). "Grounding in communication." In L. B. Resnick, J. M. Levine, & S. D. Teasley (Eds.), *Perspectives on Socially Shared Cognition* (pp. 127–149). American Psychological Association. https://web.stanford.edu/~clark/1990s/Clark,%20H.H.%20_%20Brennan,%20S.E.%20_Grounding%20in%20communication_%201991.pdf
- Shaikh, O., Gligorić, K., Khetan, A., Gerstgrasser, M., Yang, D., & Jurafsky, D. (2024). "Grounding Gaps in Language Model Generations." *Proceedings of NAACL 2024*. https://aclanthology.org/2024.naacl-long.348/

## Related links

- Original Japanese version (canonical, on note): https://note.com/shimo4228/n/n97d77b49b1c8
- Author's GitHub: https://github.com/shimo4228

---

**This essay is AI-mediated.** The text was generated by Claude Code. It is based on records of the author's daily-research pipeline and of drafts sent back during the author's writing (conversation logs, commits, prompt diffs), and on the deepening of the question through dialogue with the author. The English version was translated from the Japanese original by Claude Code. All observations, judgments, and claims, and responsibility for them, belong to the author, and the text was published after the author read it through. This disclosure follows the AI-assisted scholarship policy in the "Methodology" section of the author's research repository [attention-not-self](https://github.com/shimo4228/attention-not-self).
