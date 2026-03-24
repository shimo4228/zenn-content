# Claude Code Instructions for zenn-content

## Project Overview

This repository contains **Zenn articles and books** for AI agent development, Claude Code workflows, and LLM engineering experiments. All content follows the **"Build in Public"** principle, documenting real development sessions and design decisions.

## Git Push Reminder (CRITICAL)

記事の作成・編集・schedule.json の更新をコミットしたら、**必ずユーザーに push を促すこと**。未 push のコミットがあると、翌朝の自動公開スクリプト（`zenn_publish.py`）が `git pull --rebase` に失敗し、Zenn へのデプロイが止まる。

## Writing Guidelines

### Zenn Article Format

All articles MUST use Zenn frontmatter:

```markdown
---
title: "Article Title (50-60 characters)"
emoji: "📚"
type: "tech"  # or "idea"
topics: ["claude", "anki", "ai"]  # 1-5 tags
published: true  # or false for draft
---

# Article content starts here
```

### Content Standards

1. **Technical Depth**
   - Explain **"why"** decisions were made, not just **"what"** was implemented
   - Include real code examples from the repository
   - Discuss trade-offs and alternatives considered

2. **Code Examples**
   - All code snippets MUST be executable and tested
   - Include file paths for context (e.g., `src/pdf2anki/quality.py:322-329`)
   - Use syntax highlighting: ` ```python `, ` ```typescript `, ` ```bash `
   - Add comments for clarity

3. **Terminology Consistency**
   - Use consistent terms across articles:
     - "pdf2anki" (not "PDF2Anki" or "pdf-to-anki")
     - "Claude-Native" (design philosophy)
     - "CLI-First" (architecture principle)
     - "半自動 (Semi-automated)" (workflow approach)

4. **Tone and Style**
   - **Technical but approachable** - Assume readers are engineers
   - **Honest** - Discuss failures and challenges, not just successes
   - **Human insights** - AI-assisted writing, but human perspective
   - **No AI slop** - Avoid generic phrases like "powerful tool", "revolutionize", "seamless"

5. **Structure**
   - **Introduction** - Hook reader with a problem or insight
   - **Context** - Background and motivation
   - **Implementation** - Technical details with code examples
   - **Lessons Learned** - Reflections and takeaways
   - **Conclusion** - Summary and next steps

### Image Guidelines

- Store images in `images/` directory
- Use descriptive filenames: `tokenization-flow.png` not `image1.png`
- Embed with Zenn syntax: `![Alt text](/images/filename.png)`
- Sanitize screenshots: no file paths like `/Users/username/`, no API keys

## Editor Agent Usage

Before publishing, run the `editor` agent for rigorous review:

```bash
claude task --agent=editor --prompt="Review this Zenn article draft: articles/ARTICLE_NAME.md"
```

The editor agent will check:
- Technical accuracy
- Code snippet correctness
- Narrative flow and engagement
- Terminology consistency
- AI slop detection
- Audience appropriateness

## zenn-writer Skill

Use the `zenn-writer` skill for article-specific guidance:

```bash
claude skill zenn-writer
```

This skill provides:
- Zenn frontmatter templates
- Article structure patterns
- SEO best practices
- Code embedding formats
- Image embedding formats

## Testing Workflow

See `docs/RUNBOOK.md` for the full testing and publishing workflow.

## Publishing Checklist

Full procedure: `docs/RUNBOOK.md`

- [ ] Code snippets have no API keys
- [ ] Screenshots have no sensitive information (file paths, usernames)
- [ ] File paths are anonymized
- [ ] All code examples are tested and executable
- [ ] Editor agent review completed
- [ ] Lint passes (`npm run lint`)
- [ ] Preview looks good (`npm run preview`)
- [ ] English translation created in `articles-en/`
- [ ] `schedule.json` updated with both Japanese and English entries (including cross-post dates)
- [ ] Cross-post target scheduled: Dev.to (English)

---

**IMPORTANT**: This repository is PUBLIC. Never commit:
- Personal file paths (`/Users/username/`)
- API keys or credentials
- Sensitive screenshots
