# Claude Code Instructions for zenn-content

## Project Overview

This repository contains **Zenn articles and books** for the pdf2anki ecosystem. All content follows the **"Build in Public"** principle, documenting real development sessions and design decisions.

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
   - Include real code examples from pdf2anki repository
   - Discuss trade-offs and alternatives considered
   - Reference SpecStory sessions when applicable

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

### SpecStory Integration

When writing articles based on SpecStory sessions:

1. **Extract narrative** - Transform development log into engaging story
2. **Anonymize** - Remove personal file paths and credentials
3. **Add context** - Explain decisions that may not be obvious from logs
4. **Include code** - Show actual implementation, not just logs

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

1. **Preview locally**
   ```bash
   npm run preview
   ```

2. **Run linter**
   ```bash
   npm run lint
   ```

3. **Validate frontmatter**
   ```bash
   npx zenn list:articles
   ```

4. **Review with editor agent**
   ```bash
   claude task --agent=editor --prompt="Review articles/NEW_ARTICLE.md"
   ```

5. **Human review** - Add personal insights and final polish

## Publishing Checklist

Before publishing (see `docs/security-checklist.md` in Anki-QA):

- [ ] Code snippets have no API keys
- [ ] Screenshots have no sensitive information (file paths, usernames)
- [ ] SpecStory logs are sanitized
- [ ] File paths are anonymized
- [ ] All code examples are tested and executable
- [ ] Editor agent review completed
- [ ] Lint passes (`npm run lint`)
- [ ] Preview looks good (`npm run preview`)

## Related Documentation

- [Anki-QA CLAUDE.md](../Anki-QA/CLAUDE.md) - pdf2anki development guidelines
- [Security Checklist](../Anki-QA/docs/security-checklist.md) - Pre-publication security checks
- [Architecture Docs](../docs/architecture/) - pdf2anki ecosystem design decisions

---

**IMPORTANT**: This repository is PUBLIC. Never commit:
- Personal file paths (`/Users/username/`)
- API keys or credentials
- Sensitive screenshots
- Unsanitized SpecStory logs
