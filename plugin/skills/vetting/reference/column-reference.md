# Column Reference — GiveWell Vetting Output

This is the canonical column specification for the Findings and Publication Readiness output sheets. All agents reference this file rather than repeating the column list inline.

For Hardcoded Values (A–H) and Confidentiality Flags (A–D) column layouts, see reference/output-format.md.

---

## Findings Sheet (A–H)

| Column | Name | Content |
|---|---|---|
| A | Finding # | Leave blank — assigned by final-review compaction (F-001, F-002, …) |
| B | Sheet | Tab name from source spreadsheet |
| C | Cell/Row | Cell reference (e.g., B14) or row description |
| D | Severity | High, Medium, or Low |
| E | Error Type/Issue | Use **exactly one of**: Formula, Parameter, Adjustment, Assumption, Inconsistency, Legibility |
| F | Explanation | 3 sentences max, aim for 2. Write for a researcher who may not have the spreadsheet open. Include the row label (plain-English name from column A) alongside every cell address. **Parameter**: "currently X; correct value is Y", e.g., "malaria mortality rate (B14) = 0.87; GW parameter is 0.79, overstating CE." **Inconsistency**: state both values; flag which is authoritative. **Formula**: functional effect first, then technical fix, e.g., "[Wrong reference] program costs (E14) sums through a non-program row, inflating costs by ~12%; range should be B14:B21 not B14:B22." **High findings**: weave a brief consequence clause into the first sentence — not a separate sentence and not a verbatim copy of column H. No chain traces, no hedging. |
| G | Recommended Fix | One sentence or formula only. Lead with an imperative verb. Include the exact replacement formula or value. No explanation of why. |
| H | Estimated CE Impact | Use **exactly one of** these six phrases with exact punctuation — em-dash (` — `) with a space on each side, never en-dash or hyphen: `Raises CE — [estimate]`, `Lowers CE — [estimate]`, `Raises CE — magnitude unknown`, `Lowers CE — magnitude unknown`, `No CE impact`, `Direction unknown`. Punctuation variants cause sort failures in the compaction agent. |

---

## Publication Readiness Sheet (A–F)

| Column | Name | Content |
|---|---|---|
| A | Finding # | Leave blank — assigned by final-review compaction (PR-001, PR-002, …) |
| B | Sheet | Tab name from source spreadsheet |
| C | Cell/Row | Cell reference or row description |
| D | Error Type/Issue | Use **exactly one of**: Sourcing, Box Link, Legibility |
| E | Explanation | One short sentence (≤25 words): what is wrong and why it matters |
| F | Recommended Fix | Lead with an imperative verb |

---

## Routing rule

- **→ Findings**: anything that affects model outputs or interpretation — formula errors, wrong/stale parameters, undocumented assumptions, structural bugs.
- **→ Publication Readiness**: issues that do not affect the model — missing sources, permission flags, broken links, citation completeness, terminology, style, labeling.
- **Sourcing for standalone hardcoded cells → Hardcoded Values sheet**, not Publication Readiness. The Hardcoded Values sheet (column F "Source to Verify") already tracks this. Exception: hardcoded literals *embedded inside formulas* (e.g., `=2.47%*C43`) are not captured there — those still go to Publication Readiness as `Sourcing`.
- If the value is outside the plausible range or inconsistent with other sources, use `Parameter` in Findings.
- **Values labeled "guess" or "best guess" are not findings** — this is transparent uncertainty documentation, not an error. Do not file `Parameter` or `Assumption` entries for these.
- **Low + Legibility → Publication Readiness**: leave column D blank.
- When in doubt between Findings and Publication Readiness, use Findings.
