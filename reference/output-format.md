# Output Format Reference

## Sheet routing rule

- **Findings** — model-integrity issues: formula errors, stale/wrong parameters, structural bugs, undocumented assumptions that affect CE or model interpretation.
- **Publication Readiness** — issues that don't affect the model: missing sources, permission flags, broken links, citation format, terminology, style, labeling, personal names in notes, internal-only references.
- **Missing Source for standalone hardcoded cells → Hardcoded Values sheet** (not Publication Readiness) — the Hardcoded Values sheet already tracks source completeness in column F. Exception: hardcoded literals embedded *inside* formulas still go to Publication Readiness. If the value is outside the plausible range or inconsistent with other sources, file it as `Parameter Issue` in Findings. **A value that is both potentially wrong and undocumented is always `Parameter Issue` in Findings — do not also file `Missing Source` in Publication Readiness for the same cell.**
- **Values labeled "guess" or "best guess" are not findings** — this is acceptable uncertainty documentation. Do not file Parameter Issue or Assumption Issue entries for these.
- When in doubt between Findings and Publication Readiness, use Findings.

---

## Findings Sheet — Sheet 1 (model integrity)

Columns (A–J): Finding # | Sheet | Cell/Row | Severity | Error Type / Issue | Explanation | Recommended Fix | Estimated CE Impact | Researcher judgment needed | Status

- **Finding #** (A): Sequential ID assigned by the final-review compaction step (e.g., `F-001`, `F-002` on the Findings sheet; `PR-001`, `PR-002` on Publication Readiness). Left blank by all analysis agents — do not write to this column.
- **Sheet** (B): The sheet name the finding applies to (e.g., `Main CEA`, `Leverage/Funging`, `Inputs`). Use `Multiple` if a finding spans more than one sheet.
- **Cell/Row** (C): Exact location (e.g., `B14`). For grouped findings, list all affected cells (e.g., `B14, B18, B22`).
- **Severity** (D): `High`, `Medium`, or `Low`. Color-coded — see Severity Rules below.
- **Error Type / Issue** (E): Use exactly one of the six standard categories below:
  - `Formula Error` — wrong cell reference, wrong range, broken logic, incorrect operator. When filing a Formula Error, include a bracketed sub-type at the start of the Explanation: `[Copy-paste]`, `[Wrong reference]`, `[Year range]`, `[Sign error]`, `[Wrong operator]`, or `[Off-by-one]`.
  - `Parameter Issue` — hardcoded value is stale/outdated, or conflicts with a GW cross-cutting standard (moral weight, benchmark, discount rate)
  - `Adjustment Issue` — an adjustment (IV, EV, leverage, funging, supplemental) is absent, has the wrong sign, wrong base, or is multiplicative vs. additive incorrectly
  - `Assumption Issue` — key assumption lacks a source, explanation, or is an unacknowledged edge case
  - `Structural Issue` — tab ordering, section ordering, missing required tab, inverted section structure
  - `Inconsistency` — values that should match across sheets or within the model don't
- **Explanation** (F): 1–2 sentences maximum. Lead with the specific problem — not background. Make a specific, falsifiable claim and include the actual value or formula fragment (e.g., "B14 = 0.87 but C22 = 0.79"). Plain language a non-expert can understand. Do not hedge what you can confirm. No chain traces, no reasoning.
- **Recommended Fix** (G): One sentence or formula only. Lead with an imperative verb (Change, Replace, Add, Delete). Include the exact replacement formula or value. No explanation of why — only the action.
- **Estimated CE Impact** (H): Always begin with one of these standard phrases, then append a magnitude note if known:
  - `Raises CE — [estimate, e.g. 17.4x → ~23.6x]`
  - `Lowers CE — [estimate, e.g. ~5% reduction]`
  - `Raises CE — magnitude unknown` or `Lowers CE — magnitude unknown` (direction clear, size unclear)
  - `No CE impact`
  - `Direction unknown` (use when even direction requires researcher input)

  **When to use `Direction unknown`**: Use this phrase whenever the researcher's judgment determines both *what the fix is* and *which direction it moves CE* — not just the magnitude. A finding marked `Researcher judgment needed ✓` where the researcher could legitimately revise the parameter in either direction (e.g., a placeholder that real-world evidence might revise up or down, an AMR assumption that a new study might increase or decrease) must use `Direction unknown`, not a directional phrase based on one assumed revision. Predicting a direction under one assumption and filing it as `Raises CE` or `Lowers CE` is only correct when the direction is unambiguous regardless of which reasonable fix the researcher chooses.
- **Researcher judgment needed** (I): Mark `✓` only when the researcher must make a **decision** — e.g., an intent question ("is this $0 intentional?") or a choice between two valid approaches. Do NOT mark for verification tasks ("check this against the source") or plausibility concerns ("this value seems off") — those are just Medium findings. Leave blank if the correct action is unambiguous, even if the researcher still has to perform it.
- **Status** (J): Left blank by Claude. The researcher fills this in: `Open` / `Fixed` / `Won't Fix` / `Needs Discussion`. Do not write to this column.

### Severity Rules
- **High**: Materially affects bottom-line CE — formula errors, structural omissions, adjustments calculated but not applied. Ask: does correcting this change the number a decision-maker sees? If yes, it's High.
- **Medium**: Affects interpretation, methodology, or parameter accuracy but does not directly change the calculated CE — stale parameters, missing sources, undocumented assumptions.
- **Low**: Cosmetic or labeling issues with no calculation impact.

### Grouping and Sorting
Sort by sheet (column B), then row number. Where the same issue applies to multiple cells, **group into a single finding** listing all affected cells (e.g., "B14, B18, B22"). Only create separate rows when the issue, explanation, or recommended fix differs meaningfully. Aim for ~15–25 grouped findings rather than 50+ individual entries.

**Newly-added geography column — missing source batch finding**: When a column represents a newly-added geography and multiple parameters in that column lack cell notes or source citations, file a single grouped Medium finding listing all affected cells rather than one finding per cell. Example wording: "CIV column (J) has N parameters with no source note — newly-added geographies commonly have documentation gaps across the board. Cells: [J16, J34, J92, J135, J146, ...]. Recommend adding a source note or cell note for each before publication." This prevents alert fatigue from 8+ identical Low/H findings that all have the same fix.

Write findings starting at row 2.

---

## Publication Readiness Sheet — Sheet 2 (pub-only issues)

6-column format (A–F) — streamlined for pub-readiness work. No Severity, Decision Relevance, Estimated CE Impact, or Current Formula/Value. Contains only issues that do not affect model outputs: permission flags, broken links, GBD/IHME citation completeness (text-only citations), personal names in notes, internal-only references, Box links, terminology (x cash → x benchmark), label/note style issues. Researchers working on model correctness can ignore this sheet entirely until the pre-publication checklist.

Columns (A–F): Finding # | Sheet | Cell/Row | Error Type / Issue | Explanation | Recommended Fix

- **Finding #** (A): Sequential ID assigned by final-review (e.g., `PR-001`, `PR-002`). Left blank by agents.
- **Sheet** (B): Sheet name the finding applies to.
- **Cell/Row** (C): Exact cell or row reference.
- **Error Type / Issue** (D): Use exactly one of the five standard categories below:
  - `Missing Source` — no citation for a value or claim
  - `Broken Link` — dead link, HTTP instead of HTTPS, or inaccessible URL
  - `Permission Issue` — file needs publish permission, or links to an internal-only GiveWell doc
  - `Readability` — unclear/stale labels, placeholder text, formatting that impedes comprehension
  - `Terminology` — wrong term (e.g., "x cash" instead of "x benchmark", outdated program names)
- **Explanation** (E): One short sentence (≤25 words) describing what is wrong in plain language. No chain trace, no internal doc IDs, no references to skill files or .md files. Write for a researcher, not for debugging output.
- **Recommended Fix** (F): Short imperative action — what to do, not why. E.g., "Add source note to B14" or "Change 'x cash' to 'x benchmark' in B6."

---

## Hardcoded Values Sheet — Sheet 3

Columns (A–G): Sheet | Cell | Category | Current Value | Description | Source to Verify | Verified?

- **Verified?** (G): Left blank by Claude. The researcher fills this in (Yes / No / In Progress) after checking each entry against its source.

---

## Confidentiality Flags Sheet — Sheet 5

Columns: Cell/Row | Content Found | Sensitivity Type | Recommended Action

- **Sensitivity Type**: `PII`, `Donor Info`, `Salary/Compensation`, `Unpublished Strategy`, `Contact Info`, `Other`
- **Recommended Action**: Specific instruction (e.g., "Remove name — replace with role title", "Delete row before publication")

Confidentiality Flags findings go on this sheet only — do not duplicate in the Findings sheet.
