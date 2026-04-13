# Output Format Reference

## Sheet routing rule

- **Findings** — model-integrity issues: anything with Decision Relevance `D` or `H` (formula errors, stale/wrong parameters, structural bugs, undocumented assumptions that affect CE or model interpretation).
- **Publication Readiness** — issues that don't affect the model: Decision Relevance `O` findings (style, labeling, terminology), plus Low/H findings whose sole issue is citation format, link permissions, Box/Drive publish status, personal names in notes, or internal-only references.
- When in doubt, use Findings. It is better to over-include in Findings than to hide a real issue in Publication Readiness.

---

## Findings Sheet — Sheet 1 (model integrity)

Columns (A–J): Cell/Row | Severity | Decision Relevance | Sheet | Error Type / Issue | Explanation | Recommended Fix | Estimated CE Impact | Status | Needs input?

- **Cell/Row** (A): Exact location (e.g., `Main CEA!B14`). For grouped findings, list all affected cells (e.g., `B14, B18, B22`).
- **Severity** (B): `High`, `Medium`, or `Low`. Color-coded — see Severity Rules below.
- **Decision Relevance** (C): `D` if correcting the finding would change the bottom-line CE multiple; `H` if it affects interpretation, credibility, or reader understanding but not the calculated CE; `O` if it is a documentation, style, or labeling issue with no interpretation impact. Rule of thumb: High severity → usually D; Low severity → usually O; Medium → classify by content (stale parameter that changes CE = D; missing source for key assumption = H; first-person note = O).
- **Sheet** (D): The sheet name the finding applies to (e.g., `Main CEA`, `Leverage/Funging`, `Inputs`). Use `Multiple` if a finding spans more than one sheet.
- **Error Type / Issue** (E): `Formula Error`, `Missing Source`, `Readability`, `Confidential Info`, `Adjustment Scope`, `Edge Case`, `Outdated Parameter`, `Template Language`, `Internal Reference`, `Intentional`
- **Explanation** (F): Why this is an error or concern.
- **Recommended Fix** (G): Specific corrective action.
- **Estimated CE Impact** (H): For High findings, quantify directional effect on bottom-line CE (e.g., "raises weighted CE from 8.7x to ~10.2x"). For Medium/Low with negligible or unknown impact: "None / not quantified".
- **Status** (I): Researcher fills in: `Resolved`, `Won't Fix`, `Disagree`, or `In Progress`. Leave blank when creating the finding. Use dropdown validation if the MCP supports `setDataValidation`; otherwise leave as free text.
- **Needs input?** (J): Mark `✓` if the finding cannot be resolved without researcher input — e.g., an intent question ("is this $0 intentional?") or a verification that requires the researcher to check a source. Leave blank if the fix is unambiguous.

### Severity Rules
- **High**: Materially affects bottom-line CE — formula errors, structural omissions, adjustments calculated but not applied. Ask: does correcting this change the number a decision-maker sees? If yes, it's High.
- **Medium**: Affects interpretation, methodology, or parameter accuracy but does not directly change the calculated CE — stale parameters, missing sources, undocumented assumptions.
- **Low**: Cosmetic or labeling issues with no calculation impact.

### Grouping and Sorting
Sort by sheet (column D), then row number. Where the same issue applies to multiple cells, **group into a single finding** listing all affected cells (e.g., "B14, B18, B22"). Only create separate rows when the issue, explanation, or recommended fix differs meaningfully. Aim for ~15–25 grouped findings rather than 50+ individual entries.

**Newly-added geography column — missing source batch finding**: When a column represents a newly-added geography and multiple parameters in that column lack cell notes or source citations, file a single grouped Medium finding listing all affected cells rather than one finding per cell. Example wording: "CIV column (J) has N parameters with no source note — newly-added geographies commonly have documentation gaps across the board. Cells: [J16, J34, J92, J135, J146, ...]. Recommend adding a source note or cell note for each before publication." This prevents alert fatigue from 8+ identical Low/H findings that all have the same fix.

### Summary Row
Row 2 (immediately below header, before findings): total findings, High count, Medium count, Low count, D count, H count, O count, count of rows with `✓` in Needs input?. Light gray background. Write findings starting at row 3.

---

---

## Publication Readiness Sheet — Sheet 2 (pub-only issues)

Same 10-column format as the Findings sheet (A–J). Contains only issues that do not affect model outputs: permission flags, broken links, GBD/IHME citation completeness (text-only citations), personal names in notes, internal-only references, Box links, terminology (x cash → x benchmark), label/note style issues. Summary row (row 2) counts total / High / Medium / Low. Researchers working on model correctness can ignore this sheet entirely until the pre-publication checklist.

---

## Hardcoded Values Sheet — Sheet 3

Columns: Cell/Row | Current Value | Description | Source to Verify | Validation Priority

**Validation Priority**:
- **High**: (a) feeds 3+ downstream calculations or referenced by multiple sheets; (b) no dated source, labeled "guess," or from a data-table tab with unverifiable provenance; (c) drives a benefit stream >15% of total CE. Two or more criteria → High.
- **Medium**: drives one benefit stream with a reasonable but older/indirect source, or is a structural assumption with some documentation.
- **Low**: supplementary rows, well-sourced parameters, values not materially affecting bottom-line CE.

Add a brief note at the top of the sheet listing High-priority inputs for triage.

---

## Sensitivity Sheet — Sheet 4

Columns: Cell/Row | Content Found | Sensitivity Type | Recommended Action

- **Sensitivity Type**: `PII`, `Donor Info`, `Salary/Compensation`, `Unpublished Strategy`, `Contact Info`, `Other`
- **Recommended Action**: Specific instruction (e.g., "Remove name — replace with role title", "Delete row before publication")

Sensitivity findings go on this sheet only — do not duplicate in the Findings sheet.
