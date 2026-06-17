# Column Reference — GiveWell Vetting Output

> **Pattern B — Canonical source notice**: This file (`column-reference.md`) is the **canonical source** for column E/D vocabulary, routing rules, and the Direction-unknown decision tree. All agent files should reference this file rather than maintaining inline copies of these definitions. If a definition here conflicts with a copy in another file, this file governs. Update this file first, then update cross-references.

This is the canonical column specification for the Findings and Publication Readiness output sheets. All agents reference this file rather than repeating the column list inline.

**Quick-reference severity summary (KEY-9)**: Common parameters and their severity implications.

| Parameter | Standard value | Severity if missing | Severity if wrong |
|---|---|---|---|
| Benchmark (UoV per $) | 0.00333 | High/D | High/D |
| Moral weights (all age bands) | See key-parameters.md table | High/D | High/D |
| Avert under-5 death | 116 UoV | High/D | High/D |
| Avert over-5 death | 73 UoV | High/D | High/D |
| Long-term income ratio | 0.3064 | High/D | High/D |
| Discount rate (general) | 4% | Low/H | Medium/H |
| Income effects malaria | 0.58088% | Medium/H | Medium/H |
| Years to benefits | 10 | Medium/H | Medium/H |
| Treatment costs averted | +20% (top 4 charities) | Medium/H | Medium/H |
| TA p(failure) | 30% (scale-up) | Low/H | Medium/H |

For full parameter list with Min/Max ranges, see `reference/key-parameters.md`. For sheet setup instructions, see `reference/output-setup.md`. **CROSS-6**: Whenever this file references output-format.md for column definitions, also consult output-setup.md for the corresponding sheet setup and formatting instructions — the two files are complementary, not alternatives.

For Hardcoded Values (A–H) and Confidentiality Flags (A–D) column layouts, see reference/output-format.md.

---

## Findings Sheet (A–H)

| Column | Name | Content |
|---|---|---|
| A | Finding # | Leave blank — assigned by final-review compaction. **COL-3**: Findings sheet IDs use the prefix **F-** (e.g., `F-001`, `F-002`). Publication Readiness IDs use the prefix **PR-** (e.g., `PR-001`, `PR-002`). These prefixes are mandatory — the compaction agent assigns them sequentially. Never use a numeric-only ID or a different prefix. |
| B | Sheet | Tab name from source spreadsheet |
| C | Cell/Row | Cell reference (e.g., B14) or row description |
| D | Severity | High, Medium, or Low |
| E | Error Type/Issue | Use **exactly one of**: Formula, Parameter, Adjustment, Assumption, Inconsistency, Legibility. **Formula findings**: begin the Explanation (column F) with a bracketed sub-type — `[Copy-paste]`, `[Wrong reference]`, `[Year range]`, `[Sign error]`, `[Wrong operator]`, `[Off-by-one]`. **This sub-type list is the canonical source; any copies in other files (output-format.md, SKILL.md) are cross-references and must be updated to match this file.** **COL-1 — routing constraint**: `Sourcing` and `Box Link` are valid Error Types for Publication Readiness (column D of that sheet) **only** — they are valid exclusively for PR-routed rows (Findings column D blank). For Findings-routed rows (column D = High / Medium / Low), use one of the six Findings Error Types above. Never write `Sourcing` or `Box Link` in column E of the Findings sheet. |
| F | Explanation | 3 sentences max, aim for 2. Write for a researcher who may not have the spreadsheet open. Include the row label (plain-English name from column A) alongside every cell address. **Parameter**: "currently X; correct value is Y", e.g., "malaria mortality rate (B14) = 0.87; GW parameter is 0.79, overstating CE." **Inconsistency**: state both values; flag which is authoritative. **Formula**: functional effect first, then technical fix, e.g., "[Wrong reference] program costs (E14) sums through a non-program row, inflating costs by ~12%; range should be B14:B21 not B14:B22." **High findings**: weave a brief consequence clause into the first sentence — not a separate sentence and not a verbatim copy of column H. No chain traces, no hedging. |
| G | Recommended Fix | One sentence or formula only. Lead with an imperative verb. Include the exact replacement formula or value. No explanation of why. |
| H | Estimated CE Impact | Use **exactly one of** these six phrases with exact punctuation — em-dash (` — `) with a space on each side, never en-dash or hyphen: `Raises CE — [estimate]`, `Lowers CE — [estimate]`, `Raises CE — magnitude unknown`, `Lowers CE — magnitude unknown`, `No CE impact`, `Direction unknown`. Punctuation variants cause sort failures in the compaction agent. **Direction unknown decision tree (5 steps)**: (1) Is the affected cell in the confirmed direct CE chain (FORMULA-mode trace confirms ≥2 hops to CE output)? If no → skip to step 4. (2) Can you compute the sign of the CE impact by substituting the correct value? If yes and sign is positive → `Raises CE — [estimate or magnitude unknown]`. If yes and sign is negative → `Lowers CE — [estimate or magnitude unknown]`. (3) If CE impact is confirmed zero → `No CE impact`. (4) If direction requires researcher input or the affected parameter is ambiguously signed → `Direction unknown`. (5) If the cell is not in the CE chain and has no CE impact → `No CE impact`. Full decision tree in `reference/output-format.md`. |

---

## Publication Readiness Sheet (A–F)

| Column | Name | Content |
|---|---|---|
| A | Finding # | Leave blank — assigned by final-review compaction (PR-001, PR-002, …). See COL-3 note in the Findings sheet table above for prefix rules. |
| B | Sheet | Tab name from source spreadsheet |
| C | Cell/Row | Cell reference or row description |
| D | Error Type/Issue | Use **exactly one of**: Sourcing, Box Link, Legibility |
| E | Explanation | One short sentence (≤25 words): what is wrong and why it matters |
| F | Recommended Fix | Lead with an imperative verb |

---

## Routing rule

- **→ Findings**: anything that affects model outputs or interpretation — formula errors, wrong/stale parameters, undocumented assumptions, structural bugs.
- **→ Publication Readiness**: issues that do not affect the model — missing sources, permission flags, broken links, citation completeness, terminology, style, labeling.
- **Sourcing for standalone hardcoded cells → Hardcoded Values sheet**, not Publication Readiness. The Hardcoded Values sheet (column F "Source to Verify") already tracks this. **Tie-break rule**: a standalone hardcoded cell (a cell containing only a literal number, with no formula) routes to the Hardcoded Values sheet. A hardcoded literal *embedded inside a formula* (e.g., `=2.47%*C43`) is not captured by the Hardcoded Values sheet — route those to Publication Readiness as `Sourcing` instead.
- If the value is outside the plausible range or inconsistent with other sources, use `Parameter` in Findings.
- **Values labeled "guess" or "best guess" are not findings** — this is transparent uncertainty documentation, not an error. Do not file `Parameter` or `Assumption` entries for these.
- **Low + Legibility → Publication Readiness**: leave column D blank.
- When in doubt between Findings and Publication Readiness, use Findings.
