# Output Format Reference

## Sheet routing rule

- **Findings** — model-integrity issues: formula errors, stale/wrong parameters, structural bugs, undocumented assumptions that affect CE or model interpretation.
- **Publication Readiness** — issues that don't affect the model: missing sources, permission flags, broken links, citation format, terminology, style, labeling, personal names in notes, internal-only references.
- **Sourcing for standalone hardcoded cells → Hardcoded Values sheet** (not Publication Readiness) — the Hardcoded Values sheet already tracks source completeness in column F. Exception: hardcoded literals embedded *inside* formulas still go to Publication Readiness as `Sourcing`. If the value is outside the plausible range or inconsistent with other sources, file it as `Parameter` in Findings. **A value that is both potentially wrong and undocumented is always `Parameter` in Findings — do not also file `Sourcing` in Publication Readiness for the same cell.**
- **Values labeled "guess" or "best guess" are not findings** — this is acceptable uncertainty documentation. Do not file `Parameter` or `Assumption` entries for these.
- When in doubt between Findings and Publication Readiness, use Findings.

---

## Findings Sheet — Sheet 1 (model integrity)

Columns (A–J): Finding # | Sheet | Cell/Row | Severity | Error Type / Issue | Explanation | Recommended Fix | Estimated CE Impact | Researcher judgment needed | Status

- **Finding #** (A): Sequential ID assigned by the final-review compaction step (e.g., `F-001`, `F-002` on the Findings sheet; `PR-001`, `PR-002` on Publication Readiness). Left blank by all analysis agents — do not write to this column.
- **Sheet** (B): The sheet name the finding applies to (e.g., `Main CEA`, `Leverage/Funging`, `Inputs`). Use `Multiple` if a finding spans more than one sheet.
- **Cell/Row** (C): Exact location (e.g., `B14`). For grouped findings, list all affected cells (e.g., `B14, B18, B22`).
- **Severity** (D): `High`, `Medium`, or `Low`. Color-coded — see Severity Rules below.
- **Error Type / Issue** (E): Use exactly one of the six standard categories below:
  - `Formula` — wrong cell reference, wrong range, broken logic, incorrect operator. When filing a Formula, include a bracketed sub-type at the start of the Explanation: `[Copy-paste]`, `[Wrong reference]`, `[Year range]`, `[Sign error]`, `[Wrong operator]`, or `[Off-by-one]`.
  - `Parameter` — hardcoded value is stale/outdated, or conflicts with a GW cross-cutting standard (moral weight, benchmark, discount rate)
  - `Adjustment` — an adjustment (IV, EV, leverage, funging, supplemental) is absent, has the wrong sign, wrong base, or is multiplicative vs. additive incorrectly
  - `Assumption` — key assumption lacks a source, explanation, or is an unacknowledged edge case; also covers structural model issues (missing required tab, inverted section structure that affects CE interpretation)
  - `Inconsistency` — values that should match across sheets or within the model don't
  - `Legibility` — tab ordering, section ordering, unclear or stale labels, terminology errors (e.g., "x cash" instead of "x benchmark"), placeholder text

  **`Adjustment` vs. `Inconsistency` — decision tree** (these are frequently confused):
  - Use `Adjustment` when the finding concerns an *operation* that should (or should not) exist: an adjustment that is missing, double-counted, applied to the wrong base, has the wrong sign, or is additive vs. multiplicative incorrectly. The issue is with the treatment of the adjustment itself.
  - Use `Inconsistency` when the finding concerns two *values that should match* but don't, with no formula or adjustment operation as the root cause: the same parameter appears in two cells with different values, a cross-sheet reference pulls a value that doesn't match its stated source, or a figure cited in a note doesn't match the cell value.
  - If an adjustment produces a value that is inconsistent across tabs → `Adjustment` (root cause is the adjustment treatment).
  - If the same parameter value is hardcoded differently in two places with no formula involved → `Inconsistency`.
  - If a formula references a wrong cell causing a mismatch → `Formula` (root cause is the formula error, not the inconsistency).

- **Explanation** (F): 1–2 sentences maximum. Lead with the specific problem — not background. Make a specific, falsifiable claim and include the actual value or formula fragment (e.g., "B14 = 0.87 but C22 = 0.79"). Plain language a non-expert can understand. Do not hedge what you can confirm. No chain traces, no reasoning.
- **Recommended Fix** (G): One sentence or formula only. Lead with an imperative verb (Change, Replace, Add, Delete). Include the exact replacement formula or value. No explanation of why — only the action.
- **Estimated CE Impact** (H): Always begin with one of these standard phrases, then append a magnitude note if known:
  - `Raises CE — [estimate, e.g. 17.4x → ~23.6x]`
  - `Lowers CE — [estimate, e.g. ~5% reduction]`
  - `Raises CE — magnitude unknown` or `Lowers CE — magnitude unknown` (direction clear, size unclear)
  - `No CE impact`
  - `Direction unknown` (use when even direction requires researcher input)

  **Exact punctuation required**: all phrases use an em-dash (` — `) with one space on each side. Do not use en-dash (`–`) or hyphen (`-`). The compaction agent sorts column H lexicographically — any punctuation variation produces an inconsistent sort order and breaks grouping.

  **When to use `Direction unknown` — decision tree** (apply in order, stop at first match):
  1. Does the researcher's answer determine both *what the fix is* AND *which direction it moves CE*? → `Direction unknown`
  2. Could a reasonable researcher apply fixes that raise CE in one scenario and lower it in another (e.g., a placeholder where real-world evidence might revise up or down)? → `Direction unknown`
  3. Is the finding marked `Researcher judgment needed ✓` and could the researcher's answer change the direction of CE impact? → `Direction unknown`
  4. Is the direction clear but the magnitude unknown? → `Raises CE — magnitude unknown` or `Lowers CE — magnitude unknown`
  5. Are both direction and magnitude clear? → `Raises CE — [estimate]` or `Lowers CE — [estimate]`

  **Do not use `Direction unknown`** when the direction is evident from the evidence but you simply cannot compute the magnitude — use `Raises CE — magnitude unknown` or `Lowers CE — magnitude unknown` instead.

  **Column H completeness by Error Type**:
  - `Formula`, `Parameter`, `Adjustment` findings at Medium or High severity: column H must **never be blank**. Use `Direction unknown` if the direction depends on researcher input; use `Raises CE — magnitude unknown` or `Lowers CE — magnitude unknown` if the direction is clear.
  - `Assumption` findings at Medium severity: blank is acceptable only when the assumption has no clear directional CE effect. When the assumption does affect CE, use `Direction unknown` or a directional phrase.
  - `Inconsistency`, `Legibility` findings at Medium severity: blank is acceptable.

  **`No CE impact` must be written explicitly — never leave blank when the determination is zero**: When you have assessed a finding's CE impact and determined it is zero, write `No CE impact` in column H — do not leave column H blank. Blank means "CE impact not yet assessed"; `No CE impact` means "assessed and confirmed as zero." A blank column H on a Formula, Parameter, or Adjustment finding will be treated as an unassessed impact during validation and routing. This applies at all severity levels — write `No CE impact` explicitly even for Low findings when CE impact is confirmed zero.
- **Researcher judgment needed** (I): Mark `✓` only when the researcher must make a **decision** and BOTH of the following hold: (1) the researcher's answer changes what you recommend — either the severity OR the fix itself, not just how you word the explanation; AND (2) the researcher's answer cannot be determined from spreadsheet content, external sources, or GiveWell guidance without entering the researcher's specific analytical intent. If the spreadsheet can answer the question (e.g., a cell note already states the intent, or the value can be verified against a GW reference document), do not mark `✓`. **Do NOT mark `✓` for**:
  - Verification tasks: "check this against the source," "confirm the GBD vintage," "verify this value" — these are Medium findings; the researcher performs the action, but no judgment call is required
  - Documentation tasks: "add a cell note," "update the label," "add a source citation" — the action is unambiguous regardless of researcher intent
  - Deterministic fixes: any finding where the correct action is a specific formula change or specific value substitution — the fix is clear regardless of intent
  - Plausibility concerns: "this value seems off" without a specific correction — downgrade to Low or reframe as a question in column F

  Leave blank if the correct action is unambiguous, even if the researcher still has to perform it.
- **Status** (J): Left blank by Claude. The researcher fills this in: `Open` / `Fixed` / `Won't Fix` / `Needs Discussion`. Do not write to this column.

### Severity Rules

Every finding has a **Nature** and a **Materiality**. Determine both, then read severity from the matrix.

**Nature**
- **Defect** — objectively wrong: there is a correct answer and the sheet has it wrong. Includes formula errors (wrong reference, wrong logic, sign error, broken range), confirmed value mismatches against a cited source, GW standard parameter violations with no documented rationale, logical impossibilities.
- **Gap** — something required is absent: a source citation on a key input, a required adjustment, a link that should exist.
- **Judgment** — a defensible modeling choice you would question, not an error: a parameter at the optimistic end of a plausible range, a discount rate choice, a structural modeling decision.

**Materiality** (effect on bottom-line CE)
- **Decision-changing** — would flip whether the program clears the funding bar.
- **Material** — moves bottom-line CE by ≥5% but does not flip the decision.
- **Immaterial** — moves bottom-line CE by <5%.
- **Zero** — does not touch the bottom line: orphaned cell, label, documentation gap on a value that is itself correct.

**Severity matrix**

|  | Decision-changing | Material (≥5%) | Immaterial (<5%) | Zero |
|---|---|---|---|---|
| **Defect** (incl. formula errors) | High | High | Medium | Medium |
| **Gap** | High | High | Medium | Low |
| **Judgment** | High | Medium | Low | — |

**Bright-line rules** — apply these before reading the matrix; they override it:
1. **Defect floor**: A confirmed objective error is never below Medium, even with zero CE impact. An orphaned formula error, a confirmed value mismatch in a non-CE tab — both remain Medium. Errors may become material if inputs change; they also undermine confidence in adjacent calculations.
2. **Unknown materiality rounds up**: If CE impact cannot be estimated, treat materiality as one tier higher. A Defect or Gap with unknown materiality → High. A Judgment with unknown materiality → Medium. Write `Raises/Lowers CE — magnitude unknown` or `Direction unknown` in column H accordingly.
3. **Decision-changing always wins**: Any finding that could flip whether the program clears the bar is High regardless of category.
4. **GW standard parameters always High**: Any deviation from a benchmark, moral weight, or discount rate in `key-parameters.md` with no documented cell note rationale is always High — these parameters are cross-cutting and a miscalibration in one CEA propagates to others.

**Nature disambiguation when ambiguous**:
- Defect vs. Gap: default to Defect — treat as objectively wrong until the researcher confirms the absence was intentional.
- Gap vs. Judgment: if the researcher could have intended the current state, use Gap — it asks the researcher to confirm rather than asserting error.

**Rounding note**: Small rounding differences (≤2% relative deviation from the source value AND <5% CE impact) are a Judgment + Immaterial → **Low**, not a Defect. Classify as a Defect only when the deviation materially misrepresents the source value.

**Discount rate omission exception**: Omitting the discount rate from the CE chain is filed as Low/H per `key-parameters.md` calibration — discount rates are present in virtually all models and their chain omission is almost always intentional (applied at the UoV level). See `key-parameters.md` for per-parameter severity overrides.

### Grouping and Sorting
Sort by sheet (column B), then row number. Where the same issue applies to multiple cells, **group into a single finding** listing all affected cells (e.g., "B14, B18, B22"). Only create separate rows when the issue, explanation, or recommended fix differs meaningfully. Aim for ~15–25 grouped findings rather than 50+ individual entries.

**Mandatory same-root-cause grouping**: Before writing any set of findings, identify groups of candidate findings that share (a) the same root cause AND (b) the same recommended fix. Any group of N ≥ 2 MUST be written as a single finding that lists all affected cells in column C. Lead the Explanation with the pattern description, not the individual cell: "B14, B22, B36: all reference the 'All ages' GBD row instead of the 5–14 age band — same copy-paste error across three geographies." A single finding citing 10 cells is preferable to 10 separate findings. Do not write individual per-cell findings when a pattern finding covers the same ground — the researcher needs to understand the pattern and fix it once, not process N identical recommended fixes.

**Exceptions — keep findings separate when**:
- The recommended fix differs meaningfully between cells (e.g., one cell should reference row 14, another should reference row 22)
- Cells are on different sheets and the Explanation would need to describe two distinct contexts to be intelligible
- Severity differs between cells (e.g., one cell has a documented note rationale that triggers a downgrade; another does not — they cannot share a finding at a single severity)

**Newly-added geography column — missing source batch finding**: When a column represents a newly-added geography and multiple parameters in that column lack cell notes or source citations, file a single grouped Medium finding listing all affected cells rather than one finding per cell. Example wording: "CIV column (J) has N parameters with no source note — newly-added geographies commonly have documentation gaps across the board. Cells: [J16, J34, J92, J135, J146, ...]. Recommend adding a source note or cell note for each before publication." This prevents alert fatigue from 8+ identical Low/H findings that all have the same fix.

Write findings starting at row 2.

---

## Publication Readiness Sheet — Sheet 2 (pub-only issues)

6-column format (A–F) — streamlined for pub-readiness work. No Severity, Decision Relevance, Estimated CE Impact, or Current Formula/Value. Contains only issues that do not affect model outputs: permission flags, broken links, GBD/IHME citation completeness (text-only citations), personal names in notes, internal-only references, Box links, terminology (x cash → x benchmark), label/note style issues. Researchers working on model correctness can ignore this sheet entirely until the pre-publication checklist.

Columns (A–F): Finding # | Sheet | Cell/Row | Error Type / Issue | Explanation | Recommended Fix

- **Finding #** (A): Sequential ID assigned by final-review (e.g., `PR-001`, `PR-002`). Left blank by agents.
- **Sheet** (B): Sheet name the finding applies to.
- **Cell/Row** (C): Exact cell or row reference.
- **Error Type / Issue** (D): Use exactly one of the three standard categories below:
  - `Sourcing` — missing citation, broken link, dead URL, HTTP instead of HTTPS, inaccessible document, or file needing publish permission
  - `Box Link` — Box.com URL present in a cell note or citation field (not appropriate for published spreadsheets; remove or replace with a public link)
  - `Legibility` — unclear/stale labels, placeholder text, terminology errors (e.g., "x cash" instead of "x benchmark"), formatting that impedes comprehension
- **Explanation** (E): One short sentence (≤25 words) describing what is wrong in plain language. No chain trace, no internal doc IDs, no references to skill files or .md files. Write for a researcher, not for debugging output.
- **Recommended Fix** (F): Short imperative action — what to do, not why. E.g., "Add source note to B14" or "Change 'x cash' to 'x benchmark' in B6."

---

## Hardcoded Values Sheet — Sheet 3

Columns (A–H): Sheet | Cell | Category | Current Value | Description | Source to Verify | Verified? | Auto-check evidence

- **Verified?** (G): Pre-filled by the source-citation-verify agent with one of: `Matched ✓` / `Contradicted ✗` / `Could not verify`. Researcher confirms or overrides (Yes / No / In Progress) after reviewing the auto-check evidence.
- **Auto-check evidence** (H): The verbatim sentence extracted from the source document via the Anthropic Citations API, or the reason verification was not possible (e.g., "source not accessible", "PDF not text-extractable"). Left blank by hardcoded-values agent; filled by source-citation-verify agent.

---

## Confidentiality Flags Sheet — Sheet 4

Columns: Cell/Row | Content Found | Sensitivity Type | Recommended Action

- **Sensitivity Type**: `PII`, `Donor Info`, `Salary/Compensation`, `Unpublished Strategy`, `Contact Info`, `Other`
- **Recommended Action**: Specific instruction (e.g., "Remove name — replace with role title", "Delete row before publication")

Confidentiality Flags findings go on this sheet only — do not duplicate in the Findings sheet.
