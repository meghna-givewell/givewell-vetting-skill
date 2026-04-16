# Column Reference — GiveWell Vetting Output

This is the canonical column specification for the two output sheets. All agents reference this file rather than repeating the column list inline.

---

## Findings Sheet (A–L)

| Column | Name | Content |
|---|---|---|
| A | Finding # | Leave blank — assigned by final-review compaction (F-001, F-002, …) |
| B | Sheet | Tab name from source spreadsheet |
| C | Cell/Row | Cell reference (e.g., B14) or row description |
| D | Severity | High, Medium, or Low |
| E | Error Type/Issue | Use **exactly one of**: Formula Error, Parameter Issue, Adjustment Issue, Assumption Issue, Structural Issue, Inconsistency |
| F | Current Formula/Value | The formula or hardcoded value from the problematic cell as currently written (e.g., `=SUM(D4:D18)` or `0.73`). Write the most representative cell if the finding covers multiple cells. Leave blank for documentation-only findings where cell content is not the core issue. |
| G | Explanation | 1–2 sentences: what is wrong and why it matters. For formula errors, include the current or expected value. No chain traces. |
| H | Recommended Fix | Lead with an imperative verb. For formula fixes, include the complete replacement formula so the researcher can copy-paste directly. |
| I | Changes CE? | Mark ✓ if correcting this finding would change the bottom-line CE multiple. Leave blank if the finding affects interpretation or documentation only, without moving the calculated number. |
| J | Estimated CE Impact | Use **exactly one of**: Raises CE — [estimate], Lowers CE — [estimate], Raises CE — magnitude unknown, Lowers CE — magnitude unknown, No CE impact, Direction unknown |
| K | Researcher judgment needed | Mark ✓ only when the researcher must make a **decision** — e.g., an intent question or a choice between two valid approaches. Do NOT mark for verification tasks or plausibility concerns. Leave blank if the correct action is unambiguous. |
| L | Status | Leave blank — filled in by the researcher after review |

---

## Publication Readiness Sheet (A–G)

| Column | Name | Content |
|---|---|---|
| A | Finding # | Leave blank — assigned by final-review compaction (PR-001, PR-002, …) |
| B | Sheet | Tab name from source spreadsheet |
| C | Cell/Row | Cell reference or row description |
| D | Error Type/Issue | Use **exactly one of**: Missing Source, Broken Link, Permission Issue, Readability, Terminology |
| E | Explanation | 1–2 sentences: what is wrong and why it matters |
| F | Recommended Fix | Lead with an imperative verb |
| G | Status | Leave blank — filled in by the researcher after review |

---

## Routing rule

- **→ Findings**: anything that affects model outputs or interpretation — formula errors, wrong/stale parameters, undocumented assumptions, structural bugs.
- **→ Publication Readiness**: issues that do not affect the model — missing sources, permission flags, broken links, citation completeness, terminology, style, labeling.
- **Missing Source for standalone hardcoded cells → Hardcoded Values sheet**, not Publication Readiness. The Hardcoded Values sheet (column F "Source to Verify") already tracks this. Exception: hardcoded literals *embedded inside formulas* (e.g., `=2.47%*C43`) are not captured there — those still go to Publication Readiness as "Missing Source."
- If the value is outside the plausible range or inconsistent with other sources, use `Parameter Issue` in Findings.
- **Values labeled "guess" or "best guess" are not findings** — this is transparent uncertainty documentation, not an error. Do not file Parameter Issue or Assumption Issue entries for these.
- When in doubt between Findings and Publication Readiness, use Findings.
