---
title: "Everything Claude Code (ECC) Complete Cheatsheet"
emoji: "📚"
type: "tech"
topics: ["claude", "ai", "devtools", "cheatsheet"]
published: true
---

## Introduction

**Everything Claude Code (ECC)** is a comprehensive configuration collection for Claude Code. It consists of 13 agents, 30+ skills, 30+ commands, rules, and hooks that enable an end-to-end PDCA development cycle.

This cheatsheet serves as a quick reference for every ECC feature.

:::message
Official ECC repository: [everything-claude-code](https://github.com/affaan-m/everything-claude-code)
:::

---

## Slash Commands (`/command`)

### Development Workflow

| Command | Description |
|---------|-------------|
| `/plan` | Gather requirements, assess risks, and create an implementation plan. Waits for user confirmation before touching code |
| `/tdd` | Enforce TDD workflow: write tests first, implement, verify 80%+ coverage |
| `/build-fix` | Incrementally fix TypeScript / build errors |
| `/code-review` | Security and quality review of uncommitted changes |
| `/refactor-clean` | Detect and safely remove dead code (with test verification) |
| `/test-coverage` | Analyze test coverage and generate missing tests |
| `/verify` | Comprehensive verification of the entire codebase |
| `/checkpoint` | Create and verify checkpoints during workflows |

### E2E Testing

| Command | Description |
|---------|-------------|
| `/e2e` | Generate and run E2E tests with Playwright |

### Multi-Model Collaboration

| Command | Description |
|---------|-------------|
| `/multi-plan` | Collaborative planning with dual models |
| `/multi-execute` | Collaborative execution based on a plan |
| `/multi-workflow` | Collaborative development with intelligent routing |
| `/multi-frontend` | Frontend-focused development workflow |
| `/multi-backend` | Backend-focused development workflow |
| `/orchestrate` | Sequential agent workflow for complex tasks |

### Go

| Command | Description |
|---------|-------------|
| `/go-test` | Go TDD workflow (table-driven tests) |
| `/go-build` | Fix Go build errors, vet warnings, and linter issues |
| `/go-review` | Review Go code for idiomatic patterns and safety |

### Python

| Command | Description |
|---------|-------------|
| `/python-review` | Python review for PEP 8, type hints, and security |

### Documentation

| Command | Description |
|---------|-------------|
| `/update-docs` | Sync and update documentation from source |
| `/update-codemaps` | Analyze codebase and update architecture documents |

### Learning System

| Command | Description |
|---------|-------------|
| `/learn` | Extract and save reusable patterns from sessions |
| `/evolve` | Evolve related instincts into skills, commands, or agents |
| `/instinct-status` | List all learned instincts with confidence levels |
| `/instinct-export` | Export instincts for sharing |
| `/instinct-import` | Import instincts |
| `/skill-create` | Extract coding patterns from git history and generate SKILL.md |

### Other

| Command | Description |
|---------|-------------|
| `/eval` | Evaluation-Driven Development (EDD) workflow management |
| `/sessions` | Manage session history (list, load, alias) |
| `/pm2` | Analyze project and generate PM2 service commands |
| `/setup-pm` | Configure package manager (npm/pnpm/yarn/bun) |

---

## Agents (Auto-triggered)

Agents are automatically invoked by Claude Code when the right context arises.

### Planning & Architecture

| Agent | Trigger |
|-------|---------|
| **planner** | Complex feature requests, refactoring |
| **architect** | System design, architectural decisions |

### Code Quality

| Agent | Trigger |
|-------|---------|
| **code-reviewer** | After code changes |
| **python-reviewer** | After Python code changes |
| **go-reviewer** | After Go code changes |
| **security-reviewer** | Changes involving auth, APIs, or sensitive data |
| **database-reviewer** | SQL, schema, or DB performance related changes |

### Testing

| Agent | Trigger |
|-------|---------|
| **tdd-guide** | Enforces TDD during new features and bug fixes |
| **e2e-runner** | E2E test generation and execution |

### Fix & Cleanup

| Agent | Trigger |
|-------|---------|
| **build-error-resolver** | Build or type errors |
| **go-build-resolver** | Go build errors |
| **refactor-cleaner** | Dead code detection and removal |

### Documentation

| Agent | Trigger |
|-------|---------|
| **doc-updater** | Documentation updates, CODEMAP generation |

---

## Skills (Reference Knowledge)

Skills are the knowledge base that agents and commands draw from.

### General

| Skill | Content |
|-------|---------|
| coding-standards | TypeScript/JS/React/Node.js coding conventions |
| security-review | Security checklist and patterns |
| tdd-workflow | TDD workflow (80%+ coverage) |
| frontend-patterns | React/Next.js, state management, performance |
| backend-patterns | API design, DB optimization, server-side |
| eval-harness | Evaluation-Driven Development (EDD) framework |
| strategic-compact | Optimal timing for context compaction |

### Python

| Skill | Content |
|-------|---------|
| python-patterns | PEP 8, type hints, decorators, concurrency |
| python-testing | pytest, TDD, fixtures, mocking, coverage |

### Go

| Skill | Content |
|-------|---------|
| golang-patterns | Idiomatic Go, concurrency patterns |
| golang-testing | Table-driven tests, benchmarks, fuzzing |

### Django

| Skill | Content |
|-------|---------|
| django-patterns | DRF, ORM, caching, signals, middleware |
| django-security | Auth, CSRF, SQLi, XSS prevention |
| django-tdd | pytest-django, factory_boy, mocking |

### Spring Boot

| Skill | Content |
|-------|---------|
| springboot-patterns | REST API, layered architecture, async processing |
| springboot-security | Spring Security, auth, rate limiting |
| springboot-tdd | JUnit 5, Mockito, Testcontainers |
| jpa-patterns | Entity design, query optimization, transactions |

### Database

| Skill | Content |
|-------|---------|
| postgres-patterns | Query optimization, schema design, indexing |
| clickhouse-io | Analytics workloads, data engineering |

### Learning

| Skill | Content |
|-------|---------|
| continuous-learning | Automatic pattern extraction from sessions |
| continuous-learning-v2 | Instinct-based learning system |
| configure-ecc | ECC interactive installer |

---

## Rules (Always Active)

Placed in `~/.claude/rules/`, these are enforced at all times.

```
rules/
├── common/           # Language-agnostic
│   ├── coding-style  # Immutability, file organization, error handling
│   ├── git-workflow   # Commit messages, PRs, feat/fix/refactor
│   ├── testing        # 80%+ coverage, TDD required
│   ├── performance    # Model selection, context management
│   ├── patterns       # Repository pattern, API response format
│   ├── hooks          # PreToolUse/PostToolUse/Stop
│   ├── agents         # Agent list and trigger conditions
│   └── security       # Secret management, OWASP Top 10
├── python/           # Python-specific
│   ├── coding-style  # PEP 8, black/isort/ruff
│   ├── testing       # pytest, coverage
│   ├── patterns      # Protocol, dataclass
│   ├── hooks         # Auto-run black/mypy
│   └── security      # bandit, dotenv
└── typescript/       # TypeScript-specific
    ├── coding-style  # Zod, async/await
    ├── testing       # Playwright E2E
    ├── patterns      # Custom hooks, Repository
    ├── hooks         # Auto-run Prettier/tsc
    └── security      # Environment variables, security-reviewer
```

---

## Configuration

| File | Scope | Purpose |
|------|-------|---------|
| `~/.claude/settings.json` | Global | Permissions shared across all projects |
| `<project>/.claude/settings.json` | Project (shared) | Team-shared settings |
| `<project>/.claude/settings.local.json` | Project (local) | Personal permissions (gitignored) |
| `<project>/CLAUDE.md` | Project | Project-specific instructions |

---

## Quick Reference

Standard flow for new feature development:

```bash
# 1. Plan
/plan

# 2. Implement with TDD
/tdd

# 3. Code review
/code-review

# 4. Final verification
/verify
```

When the build breaks:

```bash
/build-fix     # TypeScript
/go-build      # Go
```

Refactoring:

```bash
/refactor-clean  # Remove dead code
/test-coverage   # Check coverage
```

Learning and improvement:

```bash
/learn           # Extract patterns
/instinct-status # Check learning status
/evolve          # Evolve into skills
```

---

## Summary

ECC is a comprehensive framework that dramatically improves development efficiency with Claude Code. Keep this cheatsheet handy for quick reference whenever you need it.

The key takeaways:
- **Development flow**: `/plan` → `/tdd` → `/code-review` → `/verify`
- **Auto-triggered agents**: Automatically ensure quality at the right moments
- **Rules**: Always active, enforcing coding standards and best practices

Give ECC a try and experience the AI-native development workflow.

:::message
For more details, check out the [official ECC repository](https://github.com/affaan-m/everything-claude-code).
:::
