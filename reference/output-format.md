# Output Format Reference

## Findings Sheet — Sheet 1

Columns: Cell/Row | Error Type / Issue | Explanation | Recommended Fix | Severity | Estimated CE Impact | Researcher to confirm? | Status

- **Cell/Row**: Exact location (e.g., `Sheet1!B14`)
- **Error Type**: `Formula Error`, `Missing Source`, `Readability`, `Confidential Info`, `Adjustment Scope`, `Edge Case`, `Outdated Parameter`, `Template Language`, `Internal Reference`, `Intentional`
- **Explanation**: Why this is an error or concern
- **Recommended Fix**: Specific corrective action
- **Severity**: `High`, `Medium`, or `Low`
- **Estimated CE Impact**: For High findings, quantify directional effect on bottom-line CE (e.g., "raises weighted CE from 8.7x to ~10.2x"). For Medium/Low with negligible or unknown impact: "None / not quantified"
- **Researcher to confirm?**: Mark `✓` if the finding cannot be resolved without researcher input. Leave blank if the fix is unambiguous.
- **Status**: Leave blank. Researcher fills in: `Resolved`, `Won't Fix`, or `Disagree`.

### Severity Rules
- **High**: Materially affects bottom-line CE — formula errors, structural omissions, adjustments calculated but not applied. Ask: does correcting this change the number a decision-maker sees? If yes, it's High.
- **Medium**: Affects interpretation, methodology, or parameter accuracy but does not directly change the calculated CE — stale parameters, missing sources, undocumented assumptions.
- **Low**: Cosmetic or labeling issues with no calculation impact.

### Grouping and Sorting
Sort by sheet, then row number. Where the same issue applies to multiple cells, **group into a single finding** listing all affected cells (e.g., "B14, B18, B22"). Only create separate rows when the issue, explanation, or recommended fix differs meaningfully. Aim for ~15–25 grouped findings rather than 50+ individual entries.

### Summary Row
Row 2 (immediately below header, before findings): total findings, High count, Medium count, Low count, count of rows marked "Researcher to confirm". Light gray background. Write findings starting at row 3.

---

## Hardcoded Values Sheet — Sheet 2

Columns: Cell/Row | Current Value | Description | Source to Verify | Validation Priority

**Validation Priority**:
- **High**: (a) feeds 3+ downstream calculations or referenced by multiple sheets; (b) no dated source, labeled "guess," or from a data-table tab with unverifiable provenance; (c) drives a benefit stream >15% of total CE. Two or more criteria → High.
- **Medium**: drives one benefit stream with a reasonable but older/indirect source, or is a structural assumption with some documentation.
- **Low**: supplementary rows, well-sourced parameters, values not materially affecting bottom-line CE.

Add a brief note at the top of the sheet listing High-priority inputs for triage.

---

## Sensitivity Sheet — Sheet 3

Columns: Cell/Row | Content Found | Sensitivity Type | Recommended Action

- **Sensitivity Type**: `PII`, `Donor Info`, `Salary/Compensation`, `Unpublished Strategy`, `Contact Info`, `Other`
- **Recommended Action**: Specific instruction (e.g., "Remove name — replace with role title", "Delete row before publication")

Sensitivity findings go on this sheet only — do not duplicate in the Findings sheet.
