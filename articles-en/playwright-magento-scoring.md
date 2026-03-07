---
title: "click() Betrayed Me 3 Times — Playwright × Magento Battle-Tested Patterns"
emoji: "🎭"
type: "tech"
topics: ["playwright", "python", "magento", "automation"]
published: false
---

## Introduction

I tried to automate a Magento-based e-commerce site with Playwright. Magento is Adobe's open-source e-commerce platform, widely used by online stores worldwide. Setting delivery times, searching products, fetching data — the tasks were straightforward. `click()`, read text, navigate to the next page.

By the third time `click()` betrayed me, I realized: "This is nothing like what the tutorials describe."

This article covers five pitfalls I encountered on a Magento/KnockoutJS site while using Playwright. KnockoutJS is the JavaScript framework powering Magento's frontend — it enables dynamic UIs, but produces tricky behavior from an automation perspective. The second half documents how I applied time-decay scoring to purchase data to auto-generate a "frequently bought items" list.

:::message
Selectors and module names in code examples have been generalized. Since Magento templates differ between sites, you'll need to inspect the actual DOM for your target site.
:::

## Five Traps of Magento/KnockoutJS

### Trap 1: Elements Outside the Viewport Can't Be Clicked

The viewport is the currently visible area of the browser window. Playwright, by default, can only click elements that are visible within this area.

I tried to click a radio button inside a Magento modal (a dialog that pops up over the page).

```python
# NG: Normal click — "Element is outside of the viewport"
radio.click()

# NG: force=True — Same error inside Magento modals
radio.click(force=True)

# NG: scroll_into_view_if_needed — Doesn't reach the modal's scroll container
radio.scroll_into_view_if_needed()
radio.click(force=True)
```

Three attempts, three failures.

The root cause lies in Magento's modal structure. Magento uses its own scroll container (`.modal-popup.modal-slide._inner-scroll`) that is separate from Playwright's viewport-based scrolling. `scroll_into_view_if_needed()` works for the page-level scroll, but can't reach inside the modal's internal scroll container.

The fix: click via JavaScript directly.

```python
# OK: Direct JavaScript click — bypasses viewport constraints entirely
radio.evaluate("el => el.click()")
```

`evaluate()` fires DOM events directly, regardless of whether the element is within the viewport. For Magento modal interactions, I adopted this as the standard pattern. The confirm button had the same viewport issue, so I unified all modal operations under `evaluate("el => el.click()")`.

### Trap 2: text= Selectors Match Hidden Elements

```python
# NG: query_selector matches hidden elements too
trigger = page.query_selector("text=配送日時を選択")
trigger.click()  # TimeoutError: element is not visible
```

The element was found. But it couldn't be clicked.

The cause was KnockoutJS's template structure. Magento renders the same text in multiple locations — desktop menu, mobile menu, sidebar, etc. `query_selector` returns the first DOM-order match, which may not be the one currently visible.

```python
# OK: Locator API targets only visible elements
locator = page.locator("text=配送日時を選択").locator("visible=true")
if locator.count() > 0:
    locator.first.click()
```

The Locator API's `visible=true` filter narrows results to currently displayed elements. On KnockoutJS sites, prefer Locator API over `query_selector`.

### Trap 3: Two Different Card Structures on the Same Site

I wrote a selector for product cards. It worked in the sidebar (mini cart). Zero matches on the search results page.

Investigation revealed that the sidebar and main content use different card structures. Magento applies different templates depending on page context, so a single selector can't cover the entire site.

```python
# Manage selectors per page type
SELECTORS = {
    "sidebar": {
        "product_card": ".sidebar .product-item",
        "product_name": ".product-item-name a",
    },
    "main": {
        "product_card": ".products-grid .product-item",
        "product_name": ".product-item-link",
    },
}

def get_selector(page_type: str, element: str) -> str:
    return SELECTORS[page_type][element]
```

Centralizing selectors in a per-page-type dictionary keeps modification points confined to a single file when the DOM changes.

### Trap 4: Filtering Mixed Rows in a Modal with Regex

Opening the delivery time modal revealed a table with over a dozen rows. But not all rows share the same structure.

```text
Row 0: "Store Name"           → Store selection row (unwanted)
Row 5: "3/7 14:00-16:00 ○"   → Time slot row (wanted)
Row 8: "\n     \n     "      → Empty row (unwanted)
```

Store rows, time slot rows, and empty rows are all mixed together. Row indices aren't fixed, so content-based filtering is the only option.

```python
import re

def is_time_slot_row(row_text: str) -> bool:
    """Extract only rows containing a time pattern like 14:00-16:00"""
    return bool(re.search(r"\d{1,2}:\d{2}-\d{1,2}:\d{2}", row_text))
```

Detecting the `HH:MM-HH:MM` time pattern via regex proved more robust than DOM selectors for modals with unstable structure.

### Trap 5: Status Detection via Japanese Symbols (○△✕)

Delivery slot availability was expressed not through CSS classes, but through Japanese symbols embedded in text.

```python
def parse_slot_availability(row_text: str) -> dict | None:
    time_match = re.search(r"(\d{1,2}:\d{2}-\d{1,2}:\d{2})", row_text)
    if not time_match:
        return None

    # ○ = available, △ = limited, ✕ = full
    available = "○" in row_text or "△" in row_text

    return {
        "time_range": time_match.group(1),
        "available": available,
    }
```

I expected something like `class="available"`, but the actual implementation relied on full-width symbols embedded in text. This is a common pattern on Japanese e-commerce sites, especially those running Magento with Japanese themes.

## Time-Decay Scoring for Purchase Data

Having navigated all five traps, I successfully extracted purchase data from the EC site via Playwright. With the product list exported to CSV or JSON, the next question was: "How do I actually use this data?"

The goal was simple: auto-generate a list of frequently bought items.

Raw purchase counts alone can't distinguish between an item bought 10 times six months ago and one bought 3 times last week. That's where **time decay** comes in.

### Input Data

```json
[
  {
    "name": "Milk 1L",
    "purchased_at": ["2026-01-15", "2026-02-01", "2026-02-15", "2026-03-01"]
  },
  {
    "name": "Bread (6 slices)",
    "purchased_at": ["2025-12-01", "2025-12-15", "2026-01-01"]
  }
]
```

Each product has an array of purchase dates. The goal is to score "how actively this item has been purchased recently."

### Algorithm: count × decay^weeks

```python
import math
from datetime import date


def compute_recency_score(
    entry: dict,
    reference_date: date | None = None,
    decay_rate: float = 0.8,
) -> float:
    """score = purchase_count × decay_rate ^ weeks_since_last_purchase"""
    ref = reference_date or date.today()
    purchased_at = entry.get("purchased_at", [])

    if not purchased_at:
        return 0.0

    purchase_count = len(purchased_at)
    last_date = date.fromisoformat(max(purchased_at)[:10])
    weeks_since = max(0, (ref - last_date).days / 7)

    return purchase_count * math.pow(decay_rate, weeks_since)
```

The score has two components:

- **purchase_count** — Higher count means higher score (staple item indicator)
- **decay_rate ^ weeks** — Score decreases as time passes since last purchase (freshness)

For example, scoring "Milk 1L" with reference date `2026-03-07`:

- Purchase count: 4
- Weeks since last purchase: ~0.86
- Score: `4 × 0.8^0.86 ≈ 3.33`

Meanwhile, "Bread (6 slices)":

- Purchase count: 3
- Weeks since last purchase: ~9.3
- Score: `3 × 0.8^9.3 ≈ 0.38`

Bread's purchase count (3) is close to milk's (4), but with the last purchase over 2 months ago, it decays significantly. The result matches intuition.

### Choosing decay_rate

Think of `decay_rate` in terms of **half-life** — it becomes much more intuitive.

| decay_rate | Half-life (time for score to halve) |
|------------|-------------------------------------|
| 0.9 | ~6.6 weeks (1.5 months) |
| 0.8 | ~3.1 weeks (3 weeks) |
| 0.7 | ~1.9 weeks (under 2 weeks) |

Half-life formula: `ln(0.5) / ln(decay_rate)`

For a weekly grocery shopping cadence, `0.8` (half-life ≈ 3 weeks) worked well. If you haven't bought something in 3 weeks, "maybe it's not a staple anymore" feels right. `0.9` decays too slowly — seasonal items linger forever. `0.7` is too aggressive — missing one shopping trip tanks the score.

### Incremental Update Pattern

Reprocessing all entries every time new purchase data arrives is wasteful. Use known IDs to manage deltas.

```python
import json
from pathlib import Path


def update_incrementally(
    new_entries: list[dict],
    meta_path: Path,
) -> list[dict]:
    """Skip known IDs and return only unseen entries.

    PRECONDITION: new_entries must be in reverse chronological order (newest first).
    Since processing stops at the first known ID, entries not in this order
    require changing break to continue.
    """
    if meta_path.exists():
        known_ids = set(json.loads(meta_path.read_text()))
    else:
        known_ids = set()

    unseen = []
    for entry in new_entries:
        entry_id = entry["id"]
        if entry_id in known_ids:
            # In reverse chronological order, hitting a known ID means the rest are known too
            break
        unseen.append(entry)

    # Persist new IDs
    known_ids.update(e["id"] for e in unseen)
    meta_path.write_text(json.dumps(sorted(known_ids)))

    return unseen
```

This assumes data arrives in reverse chronological order (newest first), which is the default sort for most e-commerce order histories. First run processes everything; subsequent runs handle only new entries.

## Takeaways

### Five Lessons from Magento × Playwright

1. **When `click()` fails, use `evaluate("el => el.click()")`** — Instantly solves Magento modal viewport issues
2. **Prefer Locator API over `query_selector`** — KnockoutJS renders the same text in multiple locations
3. **Manage selectors per page type** — Magento switches templates based on context
4. **Fight unstable structures with text patterns** — Regex can be more stable than DOM selectors
5. **Be prepared to parse locale-specific symbols from text** — Don't assume CSS classes exist for state indicators

### Applying Time-Decay Scoring Beyond E-Commerce

`count × decay^weeks` is a general-purpose pattern for any scenario where you need to rank by "frequency × recency":

- **Access logs** — Surface recently viewed documents
- **Favorites** — Automatically sink unused items
- **Search queries** — Prioritize recent queries in suggestions

Varying `decay_rate` by category enables domain-specific tuning: `0.7` (2-week half-life) for perishables, `0.9` (1.5-month half-life) for household staples, and so on.
