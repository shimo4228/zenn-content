---
title: "How to Fix prh Regex Errors After Upgrading to Node.js 20"
emoji: "⚠️"
type: "tech"
topics: ["nodejs", "textlint", "regex", "troubleshooting"]
published: true
---

## Symptoms

The day after upgrading Node.js from 18 to 20, CI's textlint suddenly started crashing. I hadn't changed a single line of code.

If you have textlint + prh configured for terminology consistency checking and you include hyphen-containing patterns in `prh.yml`, you'll get this error:

```text
SyntaxError: Invalid regular expression: /Claude\-Native/v: Invalid escape
```

If everything worked fine on Node.js 18 but suddenly crashes on Node.js 20 or later, this is the pattern you're hitting.

## Root Cause

Node.js 20 ships with V8 engine v11.3+, which supports **Unicode Sets mode (`v` flag)** for regular expressions. prh internally compiles regular expressions with the `v` flag, so `\-` (backslash + hyphen) is no longer recognized as a valid literal hyphen escape and triggers a syntax error.

Under the previous `u` flag, `\-` was tolerated. The `v` flag enforces stricter syntax validation.

## Reproducing the Issue with prh.yml

```yaml
# NG: Crashes on Node.js 20+
- expected: Claude-Native
  pattern: /Claude\-Native/
```

## Solutions

### Option 1: Use patterns (Avoid Regex Entirely)

```yaml
# OK: Use string matching
- expected: Claude-Native
  patterns:
    - Claude based
    - claude native
```

`patterns` takes literal strings (which are internally converted to regex, so manual escapes like `\-` are unnecessary). Hyphen-containing strings like `Claude-Native` can be written as-is.

### Option 2: Use Character Classes for Safe Hyphen Handling

```yaml
# OK: Place hyphen at the start of a character class (valid under v flag)
- expected: Claude-Native
  pattern: /Claude[-]Native/
```

When using a hyphen inside a character class `[...]`, place it at the start or end.

```yaml
# NG
pattern: /[a\-z]/

# OK: Hyphen at the start
pattern: /[-az]/

# OK: Hyphen at the end
pattern: /[az-]/
```

### Option 3: Don't Write Hyphen-Containing Patterns in prh at All

This is the approach I adopted. Only write patterns without hyphens in `prh.yml`, and handle hyphenated terminology consistency through other means (e.g., a review checklist).

```yaml
# prh.yml — Policy: no hyphen-containing patterns
- expected: GitHub
  patterns:
    - Github

- expected: TypeScript
  patterns:
    - Typescript
```

## Verification

```bash
node -v   # Confirm v20 or later
npx textlint articles/test.md   # Confirm no crash
```

## Migration Checklist

When upgrading to Node.js 20, review your prh.yml with these steps:

1. Search for `pattern` entries containing `\-` in `prh.yml`
2. Rewrite matching rules to use `patterns` (literal strings) or use the character class workaround `[-]`
3. Run `npx textlint articles/any-article.md` and confirm it doesn't crash
4. Confirm `node -v` shows v20 or later

**Key takeaway**: `pattern` (regex) crashes with hyphens. `patterns` (literal strings) is safe.
