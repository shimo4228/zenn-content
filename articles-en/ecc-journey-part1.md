---
title: "A Beginner's First 10 Days of Real Development with ECC"
emoji: "🚀"
type: "tech"
topics: ["claude", "ai", "git", "beginners"]
published: true
---

## Introduction - What Is Everything Claude Code?

### Everything Claude Code (ECC)

**Everything Claude Code (ECC)** is a complete configuration collection for Claude Code. But calling it a "config collection" undersells what it actually is.

What ECC provides is an environment where you can experience the full PDCA cycle of software development.

```
Plan
├─ Research (problem understanding, tech investigation)
├─ Architect (system design)
└─ Plan (implementation planning)
    ↓
Do
├─ TDD (test-driven development)
└─ Implementation (Vibe Coding)
    ↓
Check
├─ Code review
├─ Test execution
└─ Security check
    ↓
Act
├─ Documentation update
└─ Next cycle
```

The creator of this repository, **Affaan Mustafa**, built [zenith.chat](https://zenith.chat) in just 8 hours using Claude Code at the **Anthropic x Forum Ventures hackathon** in September 2025, winning **$15,000 in API credits**.

ECC is composed of agents (15+), skills (30+), commands (30+), rules, and hooks. The key insight is that these components work together to create an end-to-end development flow.

### Development in the Vibe Coding Era

Before the AI era, coding (implementation) was where most of the time went. But in the Vibe Coding era (Claude Code, Cursor, etc.), implementation has become fast.

So what matters now?

The entire development flow. Previously, only a select few in management roles ever got to experience this full flow.

ECC makes it possible for anyone to experience this end-to-end development cycle, in as little as 10 days.

**References:**
- [GitHub - Everything Claude Code](https://github.com/affaan-m/everything-claude-code)
- [Everything Claude Code: The Repo That Won Anthropic Hackathon](https://medium.com/@joe.njenga/everything-claude-code-the-repo-that-won-anthropic-hackathon-33b040ba62f3)
- [The Claude Code setup that won a hackathon](https://blog.devgenius.io/the-claude-code-setup-that-won-a-hackathon-a75a161cd41c)

### Where I Started

I was a programming beginner who occasionally wrote a bit of Python as a hobby:

- Didn't know what git was
- Zero experience with real app development
- Never wrote tests, never wrote documentation
- Didn't even know version control existed as a concept

Then, in late January 2026, I heard about Everything Claude Code on a podcast and decided to try real development for the first time.

### What I Gained in 10 Days

What I gained during my first 10 days developing in the Everything Claude Code environment wasn't individual skills.

It was the experience of running the full PDCA development cycle, over and over again:

- How to understand a problem (research methodology)
- How to design a system (architectural thinking)
- How to plan implementation (planning techniques)
- How to ensure quality (TDD, code review)
- How to accumulate knowledge (documentation-driven development)

### The Peculiarity of Having "No Baseline"

Most developers migrate to Claude Code from traditional development environments. They notice things like "this is more efficient" or "development is faster now."

My case is different. The ECC environment is my "normal."

I have zero experience with traditional development environments or manual git operations. When I took my first step as a developer, I was already inside Everything Claude Code.

Because I have no baseline for comparison:
- No resistance to "planning is tedious"
- No bad habit of "tests can wait"
- No preconception that "documentation is a burden"
- Running the PDCA cycle feels natural

For me, the end-to-end flow of research -> architect -> plan -> implement -> review -> document is just how development works.

My learning approach in this environment was simple: ask questions relentlessly.

**"I can't feel the ECC effect, because I've never known any other framework."**

This is the paradoxical truth I realized after 10 days. And at the same time, it means I was fortunate to start developing in a solid learning environment.

## It All Started with a Spotify Podcast

### The Trigger (Late January 2026)

One day, I was listening to a podcast on Spotify. It was a conversation between **Obara Kazuhiro** (tech author and entrepreneur) and **Iketomo** (developer and content creator).

https://open.spotify.com/episode/6SzfYni0NBrlVTi0uADW7q

I listened carefully as Iketomo talked about Everything Claude Code (ECC).

"This might be something I can use."

After finishing the podcast, I decided to set up ECC immediately.

### Learning from YouTube

Next, I found Iketomo's YouTube video.

https://youtu.be/ElOLZ-L-Hk0

I watched this video carefully:

- Taking notes while watching
- Rewinding sections I didn't understand
- Learning the practical usage

What I learned from YouTube wasn't just conceptual understanding -- it covered concrete how-to's. This made the actual setup much smoother later.

### Gathering Information with NotebookLM

Next, I used NotebookLM to consolidate information about ECC:

- Content from Iketomo's podcast
- Content from the YouTube video
- The ECC developer's pages
- GitHub README and documentation
- Related ECC articles

By aggregating information in NotebookLM, I was able to identify best practices.

### The Pitfall of Manual Download

Since I wasn't comfortable with command-line tools (CLI), I manually downloaded a ZIP file from GitHub.

https://github.com/affaan-m/everything-claude-code

But here, I made a critical mistake.

**Misplacement**: I put all the files in `~/MyAI_Lab/.claude/`.

They should have gone in `~/.claude/` (directly under the user home directory).

```
Wrong placement:
MyAI_Lab/.claude/
├── rules/
├── skills/
├── agents/
├── README.md
├── LICENSE
└── .gitignore

Correct placement:
~/.claude/ (user level) ← rules/skills/agents go here
MyAI_Lab/.claude/ (workspace) ← only settings.local.json
<project>/.claude/ (project) ← only settings.local.json
```

This misplacement forced all projects to share the same configuration, making it impossible to set per-project configurations.

### 10 Days of Development

From January 31 to February 7, 2026, I continued developing with this incorrect placement.

Gradually, I started noticing: "I want different settings for different projects, but I can't do that."

### The Fix (February 7-8, 2026)

I re-read the official documentation and GitHub issues, and finally understood the true meaning of ECC's hierarchy (user > workspace > project).

The fix:

1. **Decision**: Committed to migrating from MyAI_Lab/.claude
2. **Move**: Moved rules/skills/agents to `~/.claude/`
3. **Delete**: Removed rules/skills/agents from MyAI_Lab/.claude/
4. **Clean up**: Left only `settings.local.json` in MyAI_Lab/.claude/
5. **Housekeeping**: Removed unnecessary GitHub-related files (README, LICENSE, etc.)

### Learning from Failure

This 10-day misplacement turned out to be a learning opportunity:

- **RTFM (Read The F***ing Manual)**: I should have read the official docs first
- **Understanding the hierarchy**: The roles of user/workspace/project levels
- **Learning by doing**: I noticed the problem through 10 days of development and fixed it

Because I had no baseline for comparison, I could try things without fear of failure. Without this experience, I would never have truly understood ECC's hierarchy.

## The Essence of ECC - The Development PDCA Cycle

### Previously Limited to a Select Few

Experiencing the full development flow used to be reserved for a select few in management roles:

- Juniors only handle "implementation"
- Mid-level developers handle "design and implementation"
- Seniors handle "planning through verification"
- Only managers experience "the full flow"

It typically took years -- sometimes a decade of career experience -- for a developer to experience this full flow.

### The Democratization ECC Brings

ECC makes it possible for anyone to run this complete development cycle, in a short period, repeatedly.

This PDCA cycle isn't limited to software development:

- Business: market research -> strategy -> execution -> measurement -> improvement
- Research: literature review -> hypothesis -> experiment -> verification -> paper writing
- Design: research -> concept -> prototype -> user testing -> improvement

Learning to develop with ECC is, in essence, learning how work itself gets done.

## Asking About Everything I Didn't Understand - The Heart of Learning

### At First, I Didn't Know Any of the Terms

"What is git?"
"What is a commit?"
"What is an ADR?"
"What is TDD?"
"What is coverage?"

This was my question list on day one of ECC.

Every time I encountered an unfamiliar term, I asked about it persistently.

Every time Claude Code suggested something, if there was a word I didn't know, I asked immediately. Got an answer, then asked a follow-up. Rinse and repeat.

### Kept Asking Until I Understood

I didn't blindly accept Claude Code's suggestions. I always had questions like:
- Why do it this way?
- Are there other approaches?
- What does this term mean?
- What's the reasoning behind this design?

I kept asking until I was satisfied.

### Multi-LLM Strategy (4 Levels)

When Claude Code alone wasn't enough, I used multiple LLMs strategically.

#### 1. Ask Claude Code

First, I'd ask Claude Code about terms and concepts that came up during development.

```
me: "What is git?"
Claude Code: "git is a version control system..."
```

However, Claude Code's answers can be terse. As a development-focused agent, its educational explanations were sometimes insufficient.

#### 2. Ask Gemini / Standard Claude

When Claude Code's answer felt insufficient, I'd ask Gemini or Claude (the standard chat version) the same question.

```
me: "Please explain what git is in a way a beginner can understand"
Gemini: "git is a tool that records the history of changes to your files. For example..."
```

This gave me more detailed explanations, clearer examples, and beginner-friendly descriptions.

#### 3. "Explain It Using Baki the Grappler"

When I still didn't get it, I got creative.

```
me: "Explain TDD (test-driven development) using an analogy from Baki the Grappler"
Claude: "TDD is like 'anticipating your opponent's technique' before 'developing your counter.'
Before Baki fights..."
```

Having things explained through manga and anime analogies deepened my understanding.

#### 4. Deep Research

When I wanted to investigate something thoroughly, I'd fire the same question at multiple LLMs in parallel.

- Claude Code: practical usage
- Gemini: detailed conceptual explanation
- ChatGPT: best practices
- NotebookLM: consolidating related articles and documentation

This 4-level approach let me understand even difficult concepts.

### Concrete Learning Moments

#### The Moment I Understood git

At first, I didn't even know what "commit" meant.

But when I executed `git commit` for the first time alongside Claude Code:

```bash
git add src/main.py
git commit -m "feat: Add initial implementation"
```

"Oh, so this is what 'recording a change' means." It clicked.

I experienced the concept of version control for the first time.

#### The Moment I Recognized the Value of ADRs

In one project, I had to make a decision about an algorithm choice.

Claude Code suggested: "Let's write an ADR."

```
me: "What's an ADR?"
Claude Code: "Architecture Decision Record. It documents important decisions."
me: "Why is it necessary?"
Claude Code: "Because in the future, you won't remember why you made that decision."
```

This explanation made me understand the value of documentation-driven development.

And so I wrote an ADR:

```markdown
# ADR-002: Algorithm Selection

## Status
Accepted

## Context
Migrating from Algorithm A to Algorithm B.
Reason: B has higher accuracy...
```

This ADR was later referenced in subsequent projects, leading to **knowledge reuse**.

#### The Moment a TDD Test Passed

In one project, I tried **writing tests first** for the first time.

```python
# Write the test first (RED)
def test_extract_text():
    result = extract_text("sample.txt")
    assert len(result) > 0

# Then write the implementation (GREEN)
def extract_text(file_path: str) -> str:
    # implementation...
```

I ran the test, and `PASSED` appeared.

"So this is TDD." It clicked.

Even after refactoring, if the tests pass, you can relax. I understood that this sense of safety is the value of TDD.

### Result: Massive Knowledge Gained

After repeating this "relentless questioning" learning process for 10 days, I had learned things like:

- **git workflow**: commits, branches, merges
- **TDD**: test-driven development
- **ADR**: Architecture Decision Records
- **Licensing**: differences between AGPL-3.0 and other licenses, and how to choose
- **E2E testing**: verification with Playwright
- **Type checking**: type safety

And this is just scratching the surface. In reality, I didn't know almost any development terminology 10 days prior.

By "asking relentlessly," I learned an enormous amount.

## Lessons from 10 Days - Internalizing the PDCA Cycle

Over 10 days working on multiple projects, I felt the PDCA cycle accelerating.

### First Full-Cycle Experience

In my first project, I experienced the end-to-end flow of Plan -> Do -> Check -> Act for the first time:

- **Plan**: tech investigation, architecture design, implementation planning
- **Do**: writing tests first with TDD, rapid implementation with Vibe Coding
- **Check**: code review, test execution, quality checks
- **Act**: recording decisions with ADRs, documentation maintenance

### The Cycle Speeds Up

Applying lessons from the previous project, the cycle ran faster in the next one:

- Reusing insights from before (architecture patterns, test strategies)
- Comprehensive test strategy including E2E tests
- Making security reviews habitual

### The Cycle Gets Refined

By the third project, I achieved a more refined cycle:

- **Solid planning discipline**: documenting detailed specs before implementation
- **Immutability principle**: using `frozen=True` to prevent unexpected mutations
- **Comprehensive documentation**: ADR, CONTRIBUTING.md, RUNBOOK.md, complete README

### Patterns That Emerged

The essence that became clear across projects:

1. **Planning matters** - "Don't jump straight into code" became second nature
2. **TDD has real value** - Write tests first, refactor with confidence
3. **Thorough reviews** - Using agents for quality and security checks
4. **Documentation-driven** - Accumulate learnings and feed them into the next cycle

The ECC environment proposed these as "the obvious way to do things," and I internalized their value by asking questions relentlessly.

## Acknowledgments

Without this Spotify podcast, I would never have discovered ECC:

https://open.spotify.com/episode/6SzfYni0NBrlVTi0uADW7q

I learned the concrete usage from Iketomo's YouTube video:

https://youtu.be/ElOLZ-L-Hk0

**Before**: A hobby programmer who didn't know what git was
**After**: Someone who has internalized the full PDCA development cycle

This 10-day transformation would not have happened without these two creators sharing their knowledge.

In this article, I've been honest about my failures too (the 10-day misplacement). So the next person doesn't make the same mistake.

## Conclusion

"Having no baseline" -- a singular starting point.

The reason I was able to turn that singularity into an advantage is that I asked questions relentlessly.

Every time I encountered an unfamiliar word, I asked. I kept digging until I understood. This repetition brought an enormous amount of learning in just 10 days.

A beginner who didn't even know what git was is now writing technical articles on Zenn.

What I learned wasn't "git" as an individual skill -- it was the full PDCA cycle of software development.

This isn't a miracle. It happened because of the Everything Claude Code learning environment and a relentless willingness to ask questions.

---

### Coming in Part 2

In the next part, I'll reveal the path to becoming an "ecosystem designer" that I reached during these 10 days.

- The metacognitive moment ("I can turn my development logs into content")
- Advanced multi-LLM deep research techniques
- Using ECC's Architect agent (from system design to creating custom Skills)
- The full ecosystem picture (input -> processing -> output -> feedback)

Stay tuned!

---

If you found this article helpful, please leave a like and bookmark it.

#EverythingClaudeCode #ECC #ClaudeCode #BuildInPublic
