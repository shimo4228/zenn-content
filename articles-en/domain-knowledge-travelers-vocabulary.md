---
title: "People Inside the Business Don't Call It a 'Domain'"
emoji: "🗺️"
type: "idea"
topics: ["discuss", "ddd", "aiagents", "career"]
published: true
description: "\"What engineers will have left is domain knowledge.\" The phrase only works if someone is standing outside the business, looking in. I go back to Eric Evans's DDD to show that domain, model, and ubiquitous language were built as translation tools between two banks, then argue that once the business side can ask an agent in its own words, the translator's seat on the bridge is the first to go, and naming rights go back with it. With one fictional salesperson, one healthcare operations lead, and one honest line I still cannot draw."
tags: discuss, ddd, aiagents, career
---

"What engineers will have left is domain knowledge." I saw that line over and over this summer.

In June 2026, Anthropic analyzed about 400,000 Claude Code sessions and reported that "the ability to steer Claude toward success comes more from command of a domain than from the ability to write code"[^1]. A little earlier, an essay titled "Domain Expertise Has Always Been the Real Moat" was read widely[^2], and the better agents get at implementation, the louder this claim becomes.

I nodded along, and something else kept snagging. Not the conclusion. The phrase itself: "domain knowledge." It only works if someone is standing outside the business, looking in. My claim in this article is that once agents do the implementation, that premise is already gone.

Here is the order. First, how the phrase is being used right now. Then its origin in DDD, from the primary sources, to confirm that it was built for translation. Then I set the view of the person who translates (the translator) against the view of the people being translated (the people inside the business), and spell out what it means to keep using the word.

## What "domain knowledge" is for, right now

Line up this year's discourse and the same phrase, "domain knowledge," is doing two different jobs. One is about tooling. The other is about careers.

**The tooling job.** In February 2026, Matt Pocock's skills repository brought DDD vocabulary into agent context management. The README of that repository, which has collected 260k stars, quotes Evans and says:

> At the start of a project, devs and the people they're building the software for (the domain experts) are usually speaking different languages. I felt the same tension with my agents.[^3]

The fix is a shared-language document called CONTEXT.md: a glossary so the agent can decode the business's jargon. "Domain knowledge" here is a tool for telling the agent about the business. The agent took the developer's chair, so DDD's translation apparatus got rebuilt for agents.

**The career job.** In the same February, Boris Cherny, the creator of Claude Code, said that "today coding is practically solved" and that "we're going to start to see the title of software engineer go away"[^4]. Engineer redundancy was placed on the table as a premise. The late-May essay "Domain Expertise Has Always Been the Real Moat" answered it, drew more than 500 comments on Hacker News[^2], and told engineers: "Pick an industry, an instrument, a regulatory regime, a physical process, and learn it the way you once learned a programming language or framework."

Anthropic's June analysis gave that usage numbers. "Every one of the ten largest occupations in our dataset lands within seven points of software engineers in terms of their success," and the fastest-growing non-software groups were management, sales, and legal[^1]. The analysis itself does not claim that occupations are interchangeable, but it became the dataset the redundancy side cites.

By September it had settled into career-advice vocabulary. "The best engineers will not be the best coders anymore, and even they will not write any code. They will be domain experts, define architecture and direct agents and judge their outcomes"[^5]; in Japan, "business understanding for engineers"[^6].

Put the two side by side and this is what you see. A word that was a tool for telling agents about the business is now being used to secure a place for engineers. And the prescription "learn it" assumes the reader is an engineer and the business is something to go and learn.

That raises a question. Whose side is the phrase "domain knowledge" seen from? To find out, go back to where it came from.

## Where "domain knowledge" came from

"Domain," in the sense used here, is not an everyday word. It is software-engineering vocabulary. The word has been in use since domain analysis in the 1980s and carries into Michael Jackson's Problem Frames (2001)[^7], but what fixed "domain," "model," and "ubiquitous language" as one widely adopted vocabulary system was Eric Evans's *Domain-Driven Design* (2003; DDD from here on).

Every core concept in DDD is a translation tool. To confirm that, I need only the six this argument uses.

**Domain.** Evans defines it as "a sphere of knowledge, influence, or activity. The subject area to which the user applies a program is the domain of the software"[^8]. For an airline booking system, the domain is reservations; for accounting software, it is accounting.

**Domain expert.** Someone who knows that sphere deeply. A developer can double as one, but DDD builds its tools on the typical assumption that it is a different person. The starting point is getting the knowledge in these people's heads into a form software can use.

**Domain model.** Not a full copy of the business but "a selectively simplified and consciously structured form of knowledge"[^9]. Evans compares it to filmmaking. Even a documentary does not show unedited reality.

**Knowledge crunching.** The process in which developers and domain experts talk repeatedly, find the thin relevant stream inside a mass of information, and refine the model. Evans writes: "Knowledge crunching is not a solitary activity. A team of developers and domain experts collaborate, typically led by developers"[^10].

**Ubiquitous language.** The language built around the domain model, which the whole team keeps using in conversation, in code, and in diagrams. Evans is explicit about the harm of translation: "On a project without a common language, developers have to translate for domain experts. ... Translation is always inaccurate and hides disconnects in understanding"[^11].

**Bounded context.** DDD acknowledges that the same word, "customer," means different things in sales and in accounting, and this is the device that draws a line around where a model applies. The definition is "a description of a boundary ... within which a particular model is defined and applicable"[^12]. This one comes back in the second half of the article.

Line up the six and what DDD is for becomes clear. Developers do not know the business; business people do not know software. Domain, model, and ubiquitous language are the vocabulary for bridging that gap.

So DDD's vocabulary system was assembled from the start to handle a translation problem. Translation is needed because different people stand on the two banks. If only one bank has people on it, you do not need a bridge.

From here on I will call the person standing on this bridge the translator: a developer who takes in the business from outside and restates it in the language of code.

## "Domain" is a word from outside the business

The viewpoint from which "learn domain knowledge" or "catch up on domain knowledge" makes sense is outside the business. For the people inside, it is their job, not knowledge brought in from elsewhere.

Only travelers talk about "the locals." People who live there do not call themselves the locals. "Catching up" carries a built-in premise: I came from somewhere else, and I have somewhere else to go back to. That is why "can you find it interesting?" becomes a question. Nobody asks whether you are interested in the town you live in.

The good intentions behind "pick an industry and learn it" sit inside the same frame. Praising the people who go and learn leaves intact the position where not learning is still allowed. Writing specs without knowing what the business does should be the abnormal case. Because it is the norm, the people who do know get praised as exceptions.

## Questions only come from inside the business

The difference between learning from outside and being inside shows up sharply the moment you use an agent. An example.

A salesperson always calls the warehouse before sending a quote, to check the stock. The inventory system shows the number, but she calls anyway. She knows from experience that receipt processing sometimes slips to the next day, so the numbers cannot be trusted for the first few days of the month. It is written in no procedure manual. She is fictional, but most likely every workplace has similar habits.

The question she gives an agent is: "Where do the stock counts go wrong at the start of the month?" Cross-check the inbound and outbound records exported from the inventory system against the processing timestamps, and there is a likely answer by morning. Once the cause is known, she asks the same agent: "Give me a list of items pending receipt every morning." The list arrives the next morning, and the call to the warehouse becomes a glance at the list. Explaining requirements to the IT department, having inventory language translated into development language, waiting for a release: none of those steps exist anywhere.

Someone who learned inventory management from outside does not have that first question. Learning gets you as far as "the inventory system has the number," because nobody ever put the reason for the phone call into words. An outsider can pick up questions by comparing manuals or observing the floor, but only the ones insiders have already articulated. The friction that has not yet become words exists only where the person running the business is.

What the agent shortened is the time between asking a question and having a mechanism run. Without a question, there is nothing to shorten.

This is where "pick an industry you can be interested in" does not reach. Interest or not, someone who is not running the business generates almost no friction worth throwing at an agent. Before it is a question of interest, it is a question of position.

One more thing. What "learn it" recommends is acquiring knowledge, and agents have made acquiring knowledge fast for everyone. What got fast for everyone is not a differentiator. The differentiator is what you throw at the agent, and that comes from the friction of the person running the business. "Learn it" recommends the half that stopped being a differentiator.

## The translator's seat disappears

Someone in accounting asks an agent, in her own words, "make this reconciliation easier." That is enough. Next to her stands the person whose job was to elicit the spec and translate it into the language of code, not knowing what to do.

This is the scene where the person DDD called the domain expert asks directly, without going through a developer. There is an article that describes the same scene from the business side: a healthcare operations lead with 15 years of experience building her own work tools with an agent. The author writes:

> She's not replacing the engineer. Instead, she's removing herself as a bottleneck.[^13]

The cases already exist. In trade compliance, where a tariff-classification error is a direct loss, a two-person team built an agent that reproduced an expert's five-step judgment procedure as-is and took first place on a global benchmark[^14]. A lawyer won Anthropic's hackathon[^15]. Asking directly, in the words of the person who touches the business's friction every day, is much faster and loses much less meaning than routing the request through one more person in between.

Here comes the objection: "Translation didn't disappear. It moved to the agent." Correct. The work of untangling ambiguity and the work of making exceptions explicit do not go away. Someone still has to say that sales's "customer" and accounting's "customer" differ.

What changes is where the person doing that work stands. The untangling is done by someone inside the business, and the result stays in the business's language. The step where an outsider restates it in the vocabulary of their own model is no longer needed at all.

Turn "domain knowledge matters" inside out and it reads like this. Only people inside the business who can use agents remain. The translator's seat is gone.

### The translator is squeezed from both sides

The order in which the translator's seat disappears comes in two forms, depending on the shape of the workplace.

In the workplaces where DDD works, in-house organizations where the business side sits in the same room as developers every day, the business side is already sitting next to the system. They are within reach of using agents themselves, so the need to go through a translator disappears first. The translator becomes unnecessary first in the very workplaces where translation was working best.

In outsourced development projects and at systems integrators (SIers), where DDD does not work, translation was one-way from the developer from the start, and ubiquitous language survived as vocabulary only. When agents enter, the business side loses its reason to go through developers.

In either workplace, what disappears first is the translator's seat.

## Naming rights come back too

When the translator disappears, one more thing returns to the business side along with it: the right to decide what words mean. This section checks which side holds that right today.

**The business side already has its words.** In any business with a long history, the business side already has a glossary. Accounting has definitions for its chart of accounts; fixed assets has a list of depreciation categories. When a developer says "let's build a shared language," from the business side the words already exist, and the only side missing them is the developer's.

**DDD pins those words to one meaning.** DDD does not throw away the business's glossary, but it does not use it as-is either. Evans lists documents used in the business as material for knowledge crunching, and also writes: "A UBIQUITOUS LANGUAGE based on the domain model assumes there is just one model in play"[^16]. Because the domain model is a "selectively simplified" form of knowledge, developers pick the words the model needs out of the glossary and pin each to one meaning.

What drops out is the layer the glossary does not record. Sales and accounting use "customer" in different senses; the person in charge remembers "for this client alone, the invoice goes to a different recipient" as part of the word itself. The business's words live together with this operation. A word pinned into a model cannot carry that layer. Because it cannot, the developer asks the business side to "speak in the model's vocabulary from now on." Shared in name; the one who decided what the words mean was the developer.

**Equality in principle, and how it collapses.** In Evans's stated principle the two sides are equal. "Domain experts object to terms or structures that are awkward or inadequate to convey domain understanding, while developers watch for ambiguity or inconsistency that will trip up design"[^17], he writes, which assumes the business side has a veto.

But equality in principle is itself a view from the system's side. The business comes first and the system attaches to it later, so the seat where words get their meaning belongs to the business side alone. The moment that is put on a negotiating table, the order of precedence is gone.

In practice it collapses further. To object, the business side needs a venue where it reworks the model with developers every day. In contract work and short requirements phases, the business side meets developers for the first few sessions, and then developers take the words away and pin them. The business side's chance to say "that's not the word" does not come until acceptance testing, when the thing is already built. Even if they say it there, changes after requirements definition come back as change requests with cost and schedule attached, so the business side gives way.

It is the traveler again, the translator from earlier: the traveler arrives, proposes "let's agree on a common language, for both our sakes," and the language chosen is the traveler's.

**DDD itself knew this.** Bounded context is the device that separates sales's "customer" and accounting's "customer" into different models and keeps both alive. Even so, in practice the meaning converges to one, because the developer is also the one drawing the boundary. Evans only wrote "typically led by developers." Leading and naming rights are different things, but in practice they tend to coincide. That is my read.

**Hard to see from the developer's side.** It is hard to see from the developer's side because, to the developer, it looks like respect. It is done in good faith: "we'll learn the business's words properly," "we'll listen to the experts." So when the business side says "you're talking down to us," nothing rings a bell, and the complaint does not land.

**Agents return the naming rights.** If the business side can ask an agent in its own words, the right to decide what words mean returns to the business side. It is not that the agent-facing glossary becomes unnecessary. The person writing it changes, and the exceptions stop falling outside it.

## What remains

So far I have written that only people inside the business remain. There is work left on the engineering side too.

Someone builds the environment the agent runs in. Someone decides permissions, logging, and what happens on failure; someone designs data consistency at scale and processing that spans several business functions. Those are still needed. Who approves what, and which state counts as correct, involve business judgment, but the business side makes that judgment, not the translator.

Coordination across several business functions remains as work close to translation. But that is translation between one function and another. What this article says disappears is only the translation between the business and the code.

Put simply, the work that remains is not translating between business and code. It is laying the pipes. The business side turns the tap; the engineers who remain run the plumbing.

Earlier, I [described the value structure of an AI harness as an hourglass](https://zenn.dev/shimo4228/articles/ai-agent-accountability-wall). The top (deciding what to build) and the bottom (data, infrastructure, physical constraints) hold their value, and the implementation layer in the middle trends toward zero. Back then I placed "domain knowledge" in the top layer. This article takes that apart. What remains on top is the business itself; "domain knowledge" as something engineers bring in from outside goes out with the middle layer.

And of what remains, the far larger side, in both headcount and value, is the business side. People who run the actual work on the floor and can use agents are people who can now resolve their own friction themselves. They have no need to teach anyone anything.

What makes this claim hard is not that there is less work. It is that the very reason engineers were thought necessary has passed into the business side's hands.

Where "plumbing" ends and "translation" begins, I cannot yet draw the line. I know the line moves with the complexity of the business. Beyond that, I do not know yet.

## This is not a blame story

The argument so far may look like a judgment of individuals. It is the outcome of a division of labor, not a fault of individual engineers.

What needed the phrase "domain knowledge" was the division of labor of an era when implementation was scarce. Inside that division, the translator was necessary, and the vocabulary was rational. DDD was written in 2003 because the gap was real. What changed is not the people but the terrain. This is less "you are wrong" and more "the terrain you grew up on moved."

If I add one prescription, it is not "learn it" but "go inside." Stand where problems on the floor happen in front of you, and questions arise on their own. "Run one business process yourself" is a shorter path to having questions for an agent than "pick an industry and learn it."

But the person at the end of that path is "someone inside the business," not "an engineer who knows the domain well."

## Closing

Every time I heard "domain knowledge matters," something snagged. Put into words, it is this: what matters is the business, and how to take it in as knowledge is no longer the subject.

As long as you frame the world in terms of "learning domain knowledge," you keep placing yourself on the scarcity side. Keeping that vocabulary makes it hard to notice that you are standing on the side that disappears.

The next time you say "learn domain knowledge," check once which bank that view is from. If you are standing on the bridge, decide early which bank to step down to. The first seat to go is the one on the bridge.

[^1]: Anthropic, "Agentic coding and persistent returns to expertise" (2026-06-16). Analysis of about 400,000 sessions from about 235,000 users, October 2025 to April 2026. "the ability to steer Claude toward success comes more from command of a domain than from the ability to write code." / "every one of the ten largest occupations in our dataset lands within seven points of software engineers in terms of their success." / "The fastest-growing non-software occupation groups in our sample are management, sales, and legal occupations." https://www.anthropic.com/research/claude-code-expertise
[^2]: Aaron Brethorst, "Domain Expertise Has Always Been the Real Moat" (2026-05-30). "The binding constraint has moved from *can you build it* to *can you tell whether it's right*." / "Pick an industry, an instrument, a regulatory regime, a physical process, and learn it the way you once learned a programming language or framework." https://www.brethorsting.com/blog/2026/05/domain-expertise-has-always-been-the-real-moat/ . Hacker News thread (884 points / 549 comments): https://news.ycombinator.com/item?id=48340411
[^3]: mattpocock/skills README (repository created 2026-02-03; 260k stars as of 2026-09-12), section "#2: The Agent Is Way Too Verbose". "At the start of a project, devs and the people they're building the software for (the domain experts) are usually speaking different languages. I felt the same tension with my agents. Agents are usually dropped into a project and asked to figure out the jargon as they go. ... The Fix for this is a shared language. It's a document that helps agents decode the jargon used in the project." https://github.com/mattpocock/skills
[^4]: Boris Cherny (creator of Claude Code), speaking on a Y Combinator podcast. Quoted in The San Francisco Standard, "AI writes code now. What's left for software engineers?" (2026-02-19). "Today coding is practically solved." / "We're going to start to see the title of software engineer go away. It's just going to be 'builder' or 'product manager.'" https://sfstandard.com/2026/02/19/ai-writes-code-now-s-left-software-engineers/
[^5]: Milan Milanović, "What is the future of software engineering?" (Tech World With Milan, 2026-09-03). "What we will see in the next few years is that the best engineers will not be the best coders anymore, and even they will not write any code. They will be domain experts, define architecture and direct agents and judge their outcomes." https://newsletter.techworld-with-milan.com/p/what-is-the-future-of-software-engineering-d52
[^6]: 地家伶人 (Persol Career; the slides give no romanized name), "Specialization and Boundary Spanning" (専門性と越境), slides for Enterprise IT Conference 2026 (2026-09-10), slide 9. In Japanese; my translation: "Technical judgment for PdMs, development know-how for IT consultants, business understanding for engineers. Toward a relationship where we think through the next move together, inside the same organization." https://speakerdeck.com/techtekt/specialization-and-boundary-spanning
[^7]: Michael Jackson, *Problem Frames: Analysing and Structuring Software Development Problems* (Addison-Wesley, 2001). The domain analysis lineage goes back to Neighbors (1984) and Prieto-Díaz (1987).
[^8]: Eric Evans, *Domain-Driven Design Reference: Definitions and Pattern Summaries* (Domain Language, 2015), Definitions. "A sphere of knowledge, influence, or activity. The subject area to which the user applies a program is the domain of the software." Published under CC BY 4.0: https://www.domainlanguage.com/ddd/reference/
[^9]: Eric Evans, *Domain-Driven Design: Tackling Complexity in the Heart of Software* (Addison-Wesley, 2003), opening of Part I (the introduction before Chapter 1). "A model is a selectively simplified and consciously structured form of knowledge."
[^10]: Ibid., Chapter 1, "Crunching Knowledge". "Knowledge crunching is not a solitary activity. A team of developers and domain experts collaborate, typically led by developers."
[^11]: Ibid., Chapter 2, "Communication and the Use of Language". "On a project without a common language, developers have to translate for domain experts. ... Translation is always inaccurate and hides disconnects in understanding."
[^12]: Evans (2015), Definitions. "A description of a boundary (typically a subsystem, or the work of a particular team) within which a particular model is defined and applicable."
[^13]: Marliis Schneider, "The Biggest Winners of the AI Revolution Aren't Engineers" (Built In, 2026-07-08). "She's not replacing the engineer. Instead, she's removing herself as a bottleneck." https://builtin.com/articles/ai-rewards-domain-knowledge
[^14]: Gahee Seo, "The 1% problem: How domain expertise + Claude let a 2-person team hit #1 on a global classification benchmark", Code w/ Claude: Extended | Tokyo (hosted by Anthropic, 2026-06-11). Via the Findy Tech Blog attendance report (2026-06-12, in Japanese): https://tech.findy.co.jp/entry/2026/06/12/180000
[^15]: The winner of Anthropic's "Built with Opus 4.6" hackathon (February 2026) was a lawyer in California. Anthropic's announcement: https://claude.com/blog/meet-the-winners-of-our-built-with-opus-4-6-claude-code-hackathon . GIGAZINE (2026-04-25) covered it with comments from Dexter Hadley: https://gigazine.net/gsc_news/en/20260425-anthropic-hackathon/
[^16]: Ibid., Chapter 2. "A UBIQUITOUS LANGUAGE based on the domain model assumes there is just one model in play." The passage that lists business documents as material is in Chapter 1: "It comes in the form of documents written for the project or used in the business, and lots and lots of talk."
[^17]: Ibid., Chapter 2. "Domain experts object to terms or structures that are awkward or inadequate to convey domain understanding, while developers watch for ambiguity or inconsistency that will trip up design."

## Sources and references

- Anthropic, "Agentic coding and persistent returns to expertise", 2026-06-16. https://www.anthropic.com/research/claude-code-expertise
- Aaron Brethorst, "Domain Expertise Has Always Been the Real Moat", 2026-05-30. https://www.brethorsting.com/blog/2026/05/domain-expertise-has-always-been-the-real-moat/
- The San Francisco Standard, "AI writes code now. What's left for software engineers?", 2026-02-19 (Boris Cherny's remarks). https://sfstandard.com/2026/02/19/ai-writes-code-now-s-left-software-engineers/
- Matt Pocock, mattpocock/skills (README section "The Agent Is Way Too Verbose", `/domain-modeling`, `/grill-with-docs`). https://github.com/mattpocock/skills
- Milan Milanović, "What is the future of software engineering?", 2026-09-03. https://newsletter.techworld-with-milan.com/p/what-is-the-future-of-software-engineering-d52
- 地家伶人, "Specialization and Boundary Spanning" (専門性と越境), Enterprise IT Conference 2026, 2026-09-10. In Japanese. https://speakerdeck.com/techtekt/specialization-and-boundary-spanning
- Marliis Schneider, "The Biggest Winners of the AI Revolution Aren't Engineers", Built In, 2026-07-08. https://builtin.com/articles/ai-rewards-domain-knowledge
- Findy Tech Blog, "Code w/ Claude Extended | Tokyo" attendance report, 2026-06-12. In Japanese. https://tech.findy.co.jp/entry/2026/06/12/180000
- Anthropic, "Meet the winners of our Built with Opus 4.6 Claude Code hackathon". https://claude.com/blog/meet-the-winners-of-our-built-with-opus-4-6-claude-code-hackathon
- GIGAZINE (English edition), on the winner of Anthropic's "Built with Opus 4.6" hackathon, 2026-04-25. https://gigazine.net/gsc_news/en/20260425-anthropic-hackathon/
- Eric Evans, *Domain-Driven Design: Tackling Complexity in the Heart of Software*, Addison-Wesley, 2003 (Japanese edition: Shoeisha, 2011, supervising translator 今関剛)
- Eric Evans, *Domain-Driven Design Reference: Definitions and Pattern Summaries*, Domain Language, 2015. CC BY 4.0. https://www.domainlanguage.com/ddd/reference/
- Vaughn Vernon, *Implementing Domain-Driven Design*, Addison-Wesley, 2013 (Japanese edition: Shoeisha, 2015, translated by 髙木正弘). The better route if you want to relearn the strategic concepts in the order practice uses them
- Michael Jackson, *Problem Frames: Analysing and Structuring Software Development Problems*, Addison-Wesley, 2001. One example of how "domain" was used before DDD

## Related links

- [A Sign on a Climbable Wall: Why AI Agents Need Accountability, Not Just Guardrails](https://zenn.dev/shimo4228/articles/ai-agent-accountability-wall) — first appearance of the hourglass model mentioned in the body
- [The Markdown source of this article (GitHub)](https://github.com/shimo4228/zenn-content/blob/main/articles/domain-knowledge-travelers-vocabulary.md) — the Markdown for every article, plus the index (docs/PUBLICATIONS.md), lives in the same repository
- [My GitHub](https://github.com/shimo4228) — my research repositories, with DOIs
