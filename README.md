# zenn-content

Zenn articles and books for the **pdf2anki ecosystem**.

## 📚 Content Strategy

This repository follows the **"Build in Public"** principle, documenting the development journey of pdf2anki through:

- **Technical articles** - Design decisions, implementation insights, TDD workflows
- **SpecStory narratives** - Real development sessions transformed into engaging content
- **Code deep-dives** - Architecture patterns, Claude-Native development, CLI-first design

## 🛠️ Tech Stack

- **Zenn CLI** - Article management and preview
- **textlint** - Japanese technical writing linter
- **SpecStory** - Development session recorder
- **Claude Code** - Editor agent for rigorous content review

## 📝 Writing Workflow

1. **Record** - Capture development sessions with SpecStory
2. **Draft** - Write articles in `articles/` using Zenn format
3. **Review** - Run `editor` agent for technical accuracy and clarity
4. **Lint** - `npm run lint` for style consistency
5. **Publish** - Push to GitHub, sync with Zenn

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Preview articles locally
npm run preview

# Create new article
npm run new:article

# Run linter
npm run lint
```

## 📖 Content Guidelines

### Technical Depth
- Focus on **"why"** over **"what"**
- Include real code examples from pdf2anki
- Explain trade-offs and alternatives

### Audience
- Software engineers interested in AI tooling
- Claude Code users learning best practices
- Anki power users seeking automation

### Tone
- **半自動 (Semi-automated)** - Human insights, AI-assisted writing
- Technical but approachable
- Honest about challenges and failures

## 🔍 Quality Standards

- **No AI slop** - Every article reviewed by `editor` agent for generic phrases
- **Code accuracy** - All snippets are tested and executable
- **Terminology consistency** - Maintained across all articles
- **SpecStory integration** - Development narratives based on real sessions

## 📂 Directory Structure

```
zenn-content/
├── articles/        # Zenn articles (Markdown)
├── books/           # Zenn books (multi-chapter)
├── scripts/         # Helper scripts (SpecStory processing, etc.)
├── images/          # Article images and screenshots
├── .claude/
│   ├── agents/      # Editor agent definition
│   └── skills/      # zenn-writer skill
├── .github/
│   └── workflows/   # CI/CD (lint, validation)
└── package.json     # Zenn CLI + textlint
```

## 🔗 Related Repositories

- [Anki-QA](https://github.com/shimomoto_tatsuya/Anki-QA) - The pdf2anki CLI tool
- [MyAI_Lab](https://github.com/shimomoto_tatsuya/MyAI_Lab) - Development workspace

## 📜 License

Articles are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Code snippets within articles inherit their source repository's license (AGPL-3.0 for pdf2anki).

---

**Maintained by**: shimomoto_tatsuya
**Built with**: Claude Code + SpecStory + Zenn
**Philosophy**: Build in Public, Share Learning
