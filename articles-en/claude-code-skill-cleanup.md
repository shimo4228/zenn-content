---
title: "How to Audit and Clean Up Overflowing Learned Skills in Claude Code"
emoji: "🗃️"
type: "tech"
topics: ["claudecode", "ai", "devenv", "productivity"]
published: true
---

## The Problem

When you use Claude Code's `/learn` command or the continuous-learning skill, skills accumulate in `~/.claude/skills/learned/`. Over 15 days of development, mine grew from 16 to 48 files.

This growth eats into the **Character Budget** — the character limit allocated for displaying the skill list. Only about 2% of the context window (roughly 16,000 characters) is available for skill discovery. Once you exceed that limit, skills get silently truncated, and the ones you actually need become invisible.

## Criteria for the Audit

Classify each skill by asking three questions:

1. **Is this skill used in only one project?** → Move it to that project's `.claude/skills/`
2. **Is it used across multiple projects?** → Keep it as a global skill in `~/.claude/skills/`
3. **Can it be re-derived with a one-liner?** → Delete it (re-generate with `/learn` when needed)

## Step-by-Step Procedure

### 1. Assess the Current State

```bash
# List global learned skills
ls ~/.claude/skills/learned/

# List project-specific skills
ls .claude/skills/
```

### 2. Move Project-Specific Skills

Swift/iOS patterns belong only in the iOS project. Zenn writing skills belong only in the zenn-content project.

```bash
# Move to the iOS project
mv ~/.claude/skills/learned/swift-di-pattern.md \
   ~/MyProject-iOS/.claude/skills/learned/

# Move to the Zenn project
mv ~/.claude/skills/learned/zenn-textlint-workaround.md \
   ~/zenn-content/.claude/skills/learned/
```

### 3. Disable Unused Skills

If Everything Claude Code (ECC) templates include skills you don't use — like Django or Spring Boot — add the following to the top of the SKILL.md file:

```yaml
---
disable-model-invocation: true
---
```

Add this to the YAML frontmatter of the SKILL.md. The reason to disable rather than delete is to keep the option open for future use. Once disabled, the skill stops consuming the Character Budget during discovery.

### 4. Delete or Archive Retired Skills

Delete skills that can be re-derived with a one-liner. If you want a safety net, move them to a separate directory.

```bash
# Archive
mkdir -p ~/.claude/skills-archive
mv ~/.claude/skills/learned/pbpaste-trick.md \
   ~/.claude/skills-archive/pbpaste-trick.md
```

## When to Trigger an Audit

If you don't decide "when" in advance, you'll notice the problem too late.

**Audit when any single layer exceeds 10 skills.** That's my threshold. When `~/.claude/skills/learned/` crosses 10, I sort them into global vs. project-specific. When a project's `.claude/skills/` crosses 10, I consider consolidation or retirement.

## Example Structure After Cleanup

```text
~/.claude/skills/
├── learned/              ← Cross-project shared (7 skills)
│   ├── ai-era-architecture-principles/
│   ├── python-immutable-accumulator/
│   └── ...
└── search-first/         ← Manually created skill

zenn-content/.claude/skills/
├── zenn-writer/          ← Zenn-specific
├── seo-optimizer/        ← Zenn-specific
└── learned/              ← Zenn-specific learned skills

pdf2anki/.claude/skills/
└── learned/              ← Python CLI-specific learned skills
```

## Takeaways

- Skills keep growing. Auditing is not a one-time task — it's recurring
- Trigger an audit when any layer exceeds 10 skills
- Project-specific skills don't belong in the global directory
- Use `disable-model-invocation: true` to disable skills you don't need
- Don't be afraid to delete. You can always re-generate with `/learn`
