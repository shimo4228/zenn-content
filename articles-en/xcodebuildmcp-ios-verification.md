---
title: "I Gave Claude Code a Simulator and It Started Tapping and Taking Screenshots on Its Own"
emoji: "📱"
type: "tech"
topics: ["claudecode", "ios", "xcode", "mcp"]
published: false
---

Claude Code tapping an app in the simulator, taking screenshots to verify results, and checking for bugs on its own. Not science fiction. I installed an MCP server called XcodeBuildMCP, and that's exactly what happened.

This article documents the practice of adding a new feature to an existing iOS app and having Claude Code handle the entire pipeline: **build → test → launch app → UI interaction → screenshot verification**.

> **Note:** The app featured in this article is referred to as "BakiQuiz" (a martial arts trivia app based on the Baki manga series) for convenience. The actual development domain is different. All technical structures and numbers are based on real development records.

## What Is XcodeBuildMCP?

[XcodeBuildMCP](https://github.com/getsentry/XcodeBuildMCP) is an MCP server that wraps CLI tools like `xcodebuild` and returns JSON-structured responses. Originally a personal project by Cameron Cooke, it was **acquired by Sentry** and is now developed under the getsentry organization. It has over 4,000 GitHub stars.

What stands out is that it provides **59 tools**. Compared to the 20 tools in Apple's native MCP released with Xcode 26.3, that's roughly 3x the coverage.

Its most significant feature: **Xcode process is not required**. It directly invokes `xcodebuild` commands, running headlessly. Building, testing, and simulator operations all complete without opening Xcode.

### Setup

```bash
# Add as an MCP server to Claude Code
claude mcp add XcodeBuildMCP -- npx -y xcodebuildmcp@latest mcp
```

Or write it directly in `~/.claude.json`:

```json
{
  "mcpServers": {
    "XcodeBuildMCP": {
      "command": "npx",
      "args": ["-y", "xcodebuildmcp@latest", "mcp"],
      "env": { "SENTRY_DISABLED": "true" }
    }
  }
}
```

To enable UI automation, place a config file in the project root:

```yaml
# .xcodebuildmcp/config.yaml
schemaVersion: 1
enabledWorkflows:
  - simulator
  - ui-automation
sessionDefaults:
  scheme: "BakiQuiz"
  projectPath: "BakiQuiz.xcodeproj"
  simulatorName: "iPhone 16 Pro"
```

With `sessionDefaults`, you don't need to pass the scheme or project path with every tool call. Three steps and you're done.

## Apple Native MCP vs XcodeBuildMCP

With Xcode 26.3, Apple's official MCP server became available. How does it differ from XcodeBuildMCP? Here's a comparison from actually using both:

| Area | Apple MCP (20 tools) | XcodeBuildMCP (59 tools) |
|------|---------------------|--------------------------|
| Xcode dependency | **Required** (via XPC) | **Not required** (standalone) |
| Build & test | Supported | Supported |
| Simulator management | Not supported | **Supported** |
| LLDB integration | Not supported | **Supported** |
| UI automation (tap/swipe) | Not supported | **Supported** |
| Log capture | Not supported | **Supported** |
| Documentation search | **Supported** (semantic) | Not supported |
| Swift snippet execution | **Supported** | Not supported |
| SwiftUI Preview | **Supported** | Not supported |
| Physical device deploy | Not supported | **Supported** |

They are **complementary**. Apple MCP excels at IDE integration (documentation search, SwiftUI Preview), while XcodeBuildMCP excels at headless operations (simulator, UI automation, debugging).

When using Claude Code, Apple MCP can be connected with:

```bash
claude mcp add --transport stdio xcode -s user -- xcrun mcpbridge
```

Installing both and choosing based on the use case felt like the best practice at this point.

## Practice: Automated Verification of Cram Mode

Here's the main event. I had Claude Code implement "cram mode" — a feature that prioritizes questions you're about to forget — in the BakiQuiz app, then had it verify the implementation entirely on its own. I didn't write a single line of code.

### Phase 1: Session Setup

First, set the project information. XcodeBuildMCP's `session_set_defaults` eliminates the need to pass project path and scheme with every subsequent tool call.

```text
session_set_defaults(
  projectPath: "BakiQuiz.xcodeproj",
  scheme: "BakiQuiz",
  simulatorId: "2438BB91-...",
  bundleId: "dev.shimo4228.baki-quiz"
)
```

### Phase 2: Build + Test

```text
build_sim → ✅ Build succeeded
test_sim  → ✅ 608 tests (605 passed, 3 skipped, 0 failed)
```

Build and tests passed on the first try. The 418 lines of test code (15 test cases across 3 suites) added for cram mode all passed. Nothing different from regular CI so far.

### Phase 3: App Launch + Screenshots

This is where XcodeBuildMCP's true value emerges.

```text
build_run_sim → App launched
screenshot   → Main screen captured
```

Claude Code captured a screenshot and **read the screen contents itself** to verify. It confirmed that the "Cram" segment was displayed, that the StatCard showed 93 questions, and that the description text was correct — all through image recognition of the screenshot.

### Phase 4: UI Automation

This was the most impactful phase. The moment Claude Code started operating the app from the other side of the terminal, I felt "this isn't CI — this is something else entirely."

```text
snapshot_ui                → Get accessibility IDs and coordinates of all UI elements
tap(label: "追い込み")      → Switch segment
screenshot                 → Verify cram mode display
tap(label: "学習開始")      → Start session
screenshot                 → Verify question screen (1/93)
tap(id: "quiz_choice_D")   → Tap answer choice
screenshot                 → Verify correct answer + explanation display
tap(label: "次の問題へ")    → Navigate to next question
screenshot                 → Verify transition to 2/93
tap(id: "quiz_end_button") → End session
screenshot                 → Verify return to start screen, review count updated
```

Claude Code executed this entire flow autonomously. It took a screenshot at each step and **judged for itself** whether the screen matched expectations. It was performing the same work a human would do manually operating the simulator and visually checking.

What surprised me was that Claude Code identified the interaction targets by itself from the `snapshot_ui` results. This tool returns a list of all UI elements on screen with their accessibility IDs, labels, and coordinates. Claude Code found the "追い込み" label and `quiz_choice_D` ID among them, assembling the next tap target on its own.

`tap` can specify either `label` (display text) or `id` (accessibility ID). I initially tried `label`, but noticed that switching to `id` was more stable. Labels can change with localization, but IDs don't.

## Zero Fixes Needed on Physical Device

Cram mode is an "additional feature implementation" that requires consistency with the existing codebase. After passing the automated verification with XcodeBuildMCP, I deployed to a physical device and tested manually. The result: **not a single fix was needed.**

To understand how significant this is, compare it with the previous workflow.

Until now, post-implementation verification on this project meant I had to operate the physical iPhone myself to check. Screen transition bugs, layout breaks, tap responsiveness — finding these issues required building in Xcode, transferring to the device, and checking with my own eyes and fingers. This manual verification consumed significant cognitive resources and time. Finding a problem meant verbalizing it to Claude Code, having it fix the issue, then checking on the device again. It wasn't unusual for this loop to cycle 2-3 times.

XcodeBuildMCP **automated the bulk of this loop.** Because Claude Code operates and verifies the screen itself, most issues are caught before reaching the physical device. "Zero fixes" this time wasn't a coincidence — it was the structural outcome.

### How It Differs from Previous E2E Testing

To be clear, E2E testing existed before XcodeBuildMCP. Claude Code would write XCUITest-based test code and run it via `xcodebuild test`.

| Aspect | Previous Self-Built E2E (XCUITest) | XcodeBuildMCP |
|--------|-------------------------------------|---------------|
| Test scenarios | **Static** (follows pre-written code) | **Dynamic** (AI judges by looking at screen) |
| Unexpected issue detection | Misses issues not in test code | Can notice anomalies via screenshots |
| Maintenance cost | Requires test code updates on UI changes | Adapts if accessibility IDs exist |
| Verification depth | Pass/fail via assert | Visual confirmation via image recognition |
| Execution speed | Fast (automated) | Somewhat slower (MCP call overhead) |

XCUITest verifies "does it work as the written scenario says?" XcodeBuildMCP lets AI judge "does the screen look as expected?" The former is strong at regression testing; the latter at exploratory testing.

In practice, using both was the right answer. Run XCUITest for fast regression on known scenarios, and XcodeBuildMCP for exploratory verification of new features. For cram mode, the 15 XCUITest cases guaranteed basic behavior, while XcodeBuildMCP's UI operations verified the overall user experience.

## Cram Mode Technical Details

A word about the design of "cram mode" itself — the verification target. Claude Code wrote 540 lines of implementation and 418 lines of tests.

### Architecture (MVVM + FSRS)

```text
StudyMode.cram
  → SessionManager.selectCramQuestions()
    → FSRSAlgorithm.cramPriority() calculates R value
    → Sort by R ascending (most forgotten first)
  → QuizViewModel.cramCount → UI display
```

The FSRS (Free Spaced Repetition Scheduler) v5.0 Retrievability formula calculates the "forgettability" of each question:

```text
R = (1 + t/(9*S))^(-1)

t = days since last review
S = Stability (memory stability)
R = 0.0–1.0 (lower = more forgotten)
```

Questions with `R < 0.9` are extracted as cram targets. This time, 93 questions were identified.

<details>
<summary>cramPriority() and selectCramQuestions() implementation</summary>

**cramPriority()**: Unlearned questions get `R = 0.0` (highest priority), while learned questions use the FSRS formula.

```swift
public static func cramPriority(
    record: ProgressRecord,
    referenceDate: Date = Date()
) -> Double {
    guard let lastReviewed = record.lastReviewed else { return 0.0 }
    let elapsed = Calendar.current.dateComponents(
        [.day], from: lastReviewed, to: referenceDate
    )
    let t = max(0, Double(elapsed.day ?? 0))
    let stability = record.stability ?? max(1, Double(record.intervalDays))
    return retrievability(elapsedDays: t, stability: stability)
}
```

**selectCramQuestions()**: Sorts only learned questions by R ascending. Not "vaguely oldest first" but backed by FSRS mathematics.

```swift
allQuestions
    .filter { progressMap[$0.questionId]?.lastReviewed != nil }
    .sorted { r1 < r2 }  // R ascending (most forgotten first)
```

</details>

### Files Changed

| File | Lines Added | Content |
|------|-------------|---------|
| StudyMode.swift | +15 | `case cram` + displayName + validation |
| FSRSAlgorithm.swift | +24 | `cramPriority()` method |
| SessionManager.swift | +30 | `selectCramQuestions()` + `cramCount()` |
| QuizViewModel.swift | +3 | `cramCount` property |
| QuizStartComponents.swift | +50 | UI (Picker, StatCard, description) |
| CramModeTests.swift | +418 | 15 test cases (3 suites) |
| **Total** | **+540** | — |

Tests account for 77% of the total. Written TDD-style, tests far outweigh the implementation.

## Tips

### Design Accessibility IDs First

XcodeBuildMCP's UI operations depend on accessibility IDs. While `snapshot_ui` can retrieve them, elements without IDs must be tapped by label or coordinates, which is unstable.

In SwiftUI, it's as simple as `.accessibilityIdentifier("quiz_choice_A")`. Designing IDs alongside UI implementation dramatically stabilizes automated verification with XcodeBuildMCP. As a side benefit, VoiceOver and other accessibility support is also covered.

### Leverage snapshot_ui

`snapshot_ui` returns all UI elements on screen as structured data. Claude Code uses this to recognize that "the accessibility ID for the cram segment is `study_mode_picker`" and assembles the appropriate operations.

When writing UI tests manually, you can also use `snapshot_ui` to understand the screen structure first, then identify the IDs.

### Auto-Fix Loop on Build Errors

When `build_sim` fails, Claude Code reads the error message, fixes the code, and rebuilds. This loop pairs well with XcodeBuildMCP's headless operation. The cycle of opening Xcode, checking errors, and manually fixing became completely unnecessary.

## Conclusion

In this entire practice, I didn't write a single line of code. I gave the instruction "build cram mode." I watched as Claude Code operated the completed feature on the simulator and verified it.

What I realized from introducing XcodeBuildMCP is that **Claude Code's autonomy extended from "build passes" to "UI works correctly."** Traditional AI coding had "write code and pass the build" as its goal. The 59 tools — especially `tap`, `screenshot`, and `snapshot_ui` — now enable AI to actually operate the app, look at the screen, and verify correct behavior.

Apple MCP (IDE integration) and XcodeBuildMCP (headless automation) are complementary. With both installed, the AI agent's coverage in iOS development is remarkably broad. The experience of "verifying an iOS app without opening Xcode" is something you can't go back from.

## References

- [Apple Newsroom: Xcode 26.3 agentic coding](https://www.apple.com/newsroom/2026/02/xcode-26-point-3-unlocks-the-power-of-agentic-coding/)
- [Apple Developer: Giving external tools access to Xcode](https://developer.apple.com/documentation/xcode/giving-agentic-coding-tools-access-to-xcode)
- [Sentry Blog: Sentry acquires XcodeBuildMCP](https://blog.sentry.io/sentry-acquires-xcodebuildmcp/)
- [GitHub: getsentry/XcodeBuildMCP](https://github.com/getsentry/XcodeBuildMCP)
- [Blake Crosley: Two MCP Servers Turned Claude Code Into an iOS Build System](https://blakecrosley.com/blog/xcode-mcp-claude-code)
