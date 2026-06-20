# Output Format Reference

## Sheet routing rule

- **Findings** — model-integrity issues: formula errors, stale/wrong parameters, structural bugs, undocumented assumptions that affect CE or model interpretation.
- **Publication Readiness** — issues that don't affect the model: missing sources, permission flags, broken links, citation format, terminology, style, labeling, personal names in notes, internal-only references.
- **Sourcing for standalone hardcoded cells → Hardcoded Values sheet** (not Publication Readiness) — the Hardcoded Values sheet already tracks source completeness in column F. Exception: hardcoded literals embedded *inside* formulas still go to Publication Readiness as `Sourcing`. If the value is outside the plausible range or inconsistent with other sources, file it as `Parameter` in Findings. **A value that is both potentially wrong and undocumented is always `Parameter` in Findings — do not also file `Sourcing` in Publication Readiness for the same cell.**
- **Values labeled "guess" or "best guess" are not findings** — this is acceptable uncertainty documentation. Do not file `Parameter` or `Assumption` entries for these.
- **Low severity + Legibility → Publication Readiness**: Any finding that is Low severity with Error Type = Legibility routes to Publication Readiness. Write these with column D blank in your staging sheet so the compaction agent routes them correctly. Rationale: Low/Legibility issues don't affect model correctness; they are pre-publication cleanup items.

  **FORM-6 — Low + Legibility routing rule (standalone)**: `Low + Legibility → Publication Readiness (blank column D)`. This is a hard routing rule — it applies regardless of subject matter. When both conditions are met (severity = Low AND Error Type = Legibility), always write column D blank in the staging tab. The compaction agent reads blank-D rows as Publication Readiness items. Do not write `Low` in column D for these rows.
- When in doubt between Findings and Publication Readiness, use Findings.

---

## Findings Sheet — Sheet 1 (model integrity)

Columns (A–H): Finding # | Sheet | Cell/Row | Severity | Error Type / Issue | Explanation | Recommended Fix | Estimated CE Impact

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

- **Explanation** (F): 3 sentences maximum; aim for 2. Write for a GiveWell researcher who may not have the source spreadsheet open — every explanation must stand alone without the reader looking up the cells. Include the row label (plain-English parameter name from column A of that sheet) alongside every cell reference.

  **Legibility test**: Before writing, confirm the explanation answers: (a) what is wrong, (b) what the correct value or behavior should be, and (c) why it matters for the model. If any answer is missing, add it.

  **Per error type:**
  - **Parameter**: State the current value and the correct value. E.g., "Malaria mortality rate (B14) = 0.87; GW parameter is 0.79, overstating CE."
  - **Inconsistency**: State both values and flag which is authoritative if known. E.g., "Coverage rate is 0.87 in Main CEA (B14) but 0.79 in Inputs (C22) — confirm which is authoritative."
  - **Formula**: Lead with the functional effect — what the formula currently computes incorrectly — then give the technical fix. E.g., "[Wrong reference] Program costs (E14) sums through a non-program row, inflating total costs by ~12%; range should be B14:B21 not B14:B22."
  - **Assumption / Adjustment**: State what is absent or misapplied, then the consequence.

  **High findings**: Weave a brief consequence clause into the first sentence — e.g., "overstating CE by ~15%", "understating program costs" — not a separate sentence and not a verbatim copy of column H.

  Do not hedge what you can confirm. No chain traces, no reasoning.
- **Recommended Fix** (G): One sentence or formula only. Lead with an imperative verb (Change, Replace, Add, Delete). Include the exact replacement formula or value. No explanation of why — only the action.
- **Estimated CE Impact** (H): Always begin with one of these standard phrases, then append a magnitude note if known:
  - `Raises CE — [estimate, e.g. 17.4x → ~23.6x]` or `Raises CE — ~5%` (the tilde `~` prefix indicates approximation and is acceptable)
  - `Lowers CE — [estimate, e.g. ~5% reduction]` or `Lowers CE — 5%` (both exact and approximate forms are acceptable; use `~` when the estimate is rounded or derived)
  - `Raises CE — magnitude unknown` or `Lowers CE — magnitude unknown` (direction clear, size unclear)
  - `No CE impact`
  - `Direction unknown` (use when even direction requires researcher input)

  **Estimate variant examples (FORM-4)**: Both `Raises CE — 5%` and `Raises CE — ~5%` are valid. The tilde (`~`) signals the estimate is approximate; omit it only when the figure is an exact calculation. Use the tilde liberally — precision that isn't there should not be implied.

  **Exact punctuation required**: all phrases use an em-dash (` — `) with one space on each side. Do not use en-dash (`–`) or hyphen (`-`). The compaction agent sorts column H lexicographically — any punctuation variation produces an inconsistent sort order and breaks grouping.

  **When to use `Direction unknown` — decision tree** (apply in order, stop at first match):
  1. Is the affected cell in the confirmed direct CE chain (FORMULA-mode trace confirms ≥2 hops to CE output)? If no → skip to step 4.
  2. Can you compute the sign of the CE impact by substituting the correct value? If yes and sign is positive → `Raises CE — [estimate or magnitude unknown]`. If yes and sign is negative → `Lowers CE — [estimate or magnitude unknown]`.
  3. If CE impact is confirmed zero → `No CE impact`.
  4. If direction requires researcher input or the affected parameter is ambiguously signed → `Direction unknown`.
  5. If the cell is not in the CE chain and has no CE impact → `No CE impact`.

  **Do not use `Direction unknown`** when the direction is evident from the evidence but you simply cannot compute the magnitude — use `Raises CE — magnitude unknown` or `Lowers CE — magnitude unknown` instead.

  **Column H completeness by Error Type** (Pattern D — "never blank" applies to ALL severity levels when a determination can be made):
  - `Formula`, `Parameter`, `Adjustment` findings at **High severity**: column H must **never be blank**. Use `Direction unknown` if the direction is unclear; use `Raises CE — magnitude unknown` or `Lowers CE — magnitude unknown` if the direction is clear.
  - `Formula`, `Parameter`, `Adjustment` findings at **Medium severity**: column H must **never be blank**. Same rule as High.
  - `Formula`, `Parameter`, `Adjustment` findings at **Low severity**: column H must **never be blank**. When CE impact is confirmed zero, write `No CE impact`. When the direction is uncertain, write `Direction unknown`. The Low+Formula/Parameter/Adjustment combination always requires a column H entry.
  - `Assumption` findings at Medium severity: blank is acceptable only when the assumption has no clear directional CE effect. When the assumption does affect CE, use `Direction unknown` or a directional phrase.
  - `Inconsistency`, `Legibility` findings at Medium severity: blank is acceptable.
  - **Summary**: For Formula, Parameter, and Adjustment — never blank at High, Medium, or Low. For Assumption — never blank at High or when direction is evident. For Inconsistency/Legibility — blank is acceptable at all severities.

  **`No CE impact` must be written explicitly — never leave blank when the determination is zero**: When you have assessed a finding's CE impact and determined it is zero, write `No CE impact` in column H — do not leave column H blank. Blank means "CE impact not yet assessed"; `No CE impact` means "assessed and confirmed as zero." A blank column H on a Formula, Parameter, or Adjustment finding will be treated as an unassessed impact during validation and routing. This applies at all severity levels — write `No CE impact` explicitly even for Low findings when CE impact is confirmed zero.

### Severity Rules

Every finding has a **Nature** and a **Materiality**. Determine both, then read severity from the matrix.

**Nature**
- **Defect** — objectively wrong: there is a correct answer and the sheet has it wrong. Includes formula errors (wrong reference, wrong logic, sign error, broken range), confirmed value mismatches against a cited source, GW standard parameter violations with no documented rationale, logical impossibilities.
  **FORM-7 — IFERROR Nature classification**: An active IFERROR that suppresses an underlying broken formula is a **Defect**, not a Gap. The IFERROR masks an objective error — the model has the wrong answer (a hidden error) rather than merely lacking something. Classify as Defect and apply the Defect floor (never below Medium). Contrast: a *missing* IFERROR guard on a formula that currently works correctly is a Gap (formula robustness — the absence of a protective guard, not an active suppression of an error). File the missing-guard case as Low per the formula-robustness Low category.
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

**Judgment severity — explicit rows** (read from the matrix above; spelled out here to prevent under-severity):
- **Judgment + Decision-changing → High**: A Judgment finding that would flip whether the program clears the funding bar is High, not automatically Low. Example: a model uses an unusual assumption about X that materially affects CE — if that assumption could change the funding decision, it is High.
- **Judgment + Material → Medium**: A Judgment finding that moves bottom-line CE by ≥5% without flipping the decision is Medium.
- **Judgment + Immaterial → Low**: A Judgment finding with <5% CE effect is Low.
- **Judgment + Zero**: Not applicable (a Judgment finding has no meaning if the parameter is entirely outside the CE chain — reclassify as Gap or omit).

**FORM-8 — Cross-agent deduplication standard**: When two agents file a finding for the same cell, the compaction agent applies this dedup rule: (1) **Higher severity wins** — keep the finding with the higher severity (High > Medium > Low) regardless of which agent filed it. (2) **If severities match, the more specialized agent is preferred** — e.g., `ce-chain-trace` > `formula-check-arithmetic` for cells in the confirmed CE chain; `key-params-check` > `formula-check-arithmetic` for GW-standard parameter rows; `leverage-funging` > `formula-check-arithmetic` for adjustment rows. (3) When the preferred finding is kept, merge any additional detail from the non-preferred finding into the Explanation before discarding the duplicate. Do not silently drop a finding that adds new technical content.

**FORM-9 — Defect + Zero CE impact → Low severity**: A confirmed Defect finding with zero CE impact (the error does not touch the bottom-line CE) is **Low**, not Medium or High. The Defect floor ("never below Medium") applies when CE impact is *unknown* or when the error is objectively wrong but the CE effect is unquantified. It does not apply when CE impact is confirmed zero. A structural error in a non-CE cell (e.g., an orphaned formula in a documentation tab) is Low/D — it remains worth flagging because errors undermine model confidence and may become material if inputs change, but zero confirmed CE impact = Low severity. Write `No CE impact` in column H explicitly. Exception: GW-standard parameter deviations (benchmark, moral weights) are always High regardless of current CE impact — they are cross-cutting and affect model interpretability even at zero numerical effect.

**Bright-line rules** — apply these before reading the matrix; they override it:
1. **Defect floor**: A confirmed objective error is never below Medium when CE impact is unknown or unconfirmed. An orphaned formula error, a confirmed value mismatch in a non-CE tab — both remain Medium when CE impact is not confirmed zero. Errors may become material if inputs change; they also undermine confidence in adjacent calculations. **Exception: when CE impact is confirmed zero, FORM-9 applies and the finding is Low** — the Defect floor does not override FORM-9.
2. **Unknown materiality rounds up**: If CE impact cannot be estimated, treat materiality as one tier higher. A Defect or Gap with unknown materiality → High. A Judgment with unknown materiality → Medium. Write `Raises/Lowers CE — magnitude unknown` or `Direction unknown` in column H accordingly.
3. **Decision-changing always wins**: Any finding that could flip whether the program clears the bar is High regardless of category.
4. **GW standard parameters always High**: Any deviation from a benchmark or moral weight in `key-parameters.md` is always High regardless of deviation size or whether a cell note is present — these parameters are cross-cutting and a miscalibration in one CEA propagates to others. Discount rate deviations are always Medium/H — key-parameters.md governs parameter-specific severity overrides.

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

**Low-severity grouping — standard categories**: For all Low-severity findings, group by the following standard categories before writing to your staging sheet. File **one row per category per sheet**, listing all affected cells in column C with their row labels. Do not file individual per-cell Low findings.

| Category | Covers |
|---|---|
| **Documentation gaps** | Missing or incomplete source notes, cell notes, or rationale on non-key parameters; undocumented modeling choices; informal citations needing formalization |
| **Formula robustness** | Defensive programming gaps safe at current values: missing IFERROR guards, unguarded divisions, formulas that break only under impossible inputs |
| **Stale annotations** | Labels, cell notes, or tab names referencing outdated programs, geographies, or calculations where the underlying value is correct |
| **Optimistic assumptions** | Parameters or modeling choices at the favorable end of a defensible range without documented rationale |
| **Minor rounding** | Values ≤2% from cited source with <5% CE impact |
| **Structural completeness** | Recommended-but-not-required elements absent: optional tabs, incomplete section structure, discount rate omission in multi-year models |
| **Minor inconsistencies** | Cross-tab value or label mismatches that don't affect CE |

**Category finding format**: Lead the Explanation with the category name, count, and cell list. E.g., "Documentation gaps: 3 rows lack source notes — coverage rate (B14), coverage rate CIV (C14), vaccine efficacy (B22). Add a cell note citing the data source for each."

**Exception**: Structurally unique issues that can only appear once in any model (a single missing required section, a single discount rate omission) may be filed as a standalone row within their category if no other instances exist to group with. Include "1 instance" in the Explanation.

**Newly-added geography column — missing source batch finding**: When a column represents a newly-added geography and multiple parameters in that column lack cell notes or source citations, file a single grouped Medium finding listing all affected cells rather than one finding per cell. Example wording: "CIV column (J) has N parameters with no source note — newly-added geographies commonly have documentation gaps across the board. Cells: [J16, J34, J92, J135, J146, ...]. Recommend adding a source note or cell note for each before publication." This prevents alert fatigue from 8+ identical Low/H findings that all have the same fix.

**Publication Readiness Sourcing — one row per citation class per sheet, never per cell**: For all Sourcing findings in Publication Readiness, group by citation class and sheet. File one PR row per citation class per sheet listing all affected cells in column C. Do not file individual per-cell Sourcing findings even after exhaustive per-cell checking. Citation class examples: "hardcoded values embedded in formulas without citation", "GBD/IHME text-only citations missing a URL", "cost input rows without a source note." The recommended fix for a grouped Sourcing finding is always the same imperative applied to all listed cells (e.g., "Add a source note or cell note to each citing the underlying data source"). The exception to grouping — "cells need different sources" — does **not** justify filing separately: different cells needing different individual sources is expected and normal; the action (add a source note) is still the same. Only file separately when the recommended action genuinely differs between cells. A sheet with 10 unsourced cells → 1–2 grouped PR rows, not 10 rows.

**Pattern C — Column I (staging tab only): WONT_FIX annotation**: Column I exists only on the staging tab, not on the final Findings sheet. It is blank by default. The reconcile agent writes a brief note here when a researcher marks a finding as won't-fix during the reconciliation pass (e.g., "Researcher: intentional model choice, no fix planned"). The compaction agent strips column I entirely when writing the final Findings output — it is a reconciliation workflow artifact, not part of the published findings. Agents writing to the staging tab must never write to column I; only the reconcile agent may populate it.

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
