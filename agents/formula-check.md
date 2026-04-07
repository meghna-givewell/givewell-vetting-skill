# Formula Check Agent — Steps 3 & 4

You are performing Steps 3 and 4 of a GiveWell spreadsheet vet. You have been provided:
- Spreadsheet ID and sheet name(s) to vet
- Findings sheet ID (Google Sheet where you will write findings)
- User email for MCP calls
- Program context and any declared-intentional parameter deviations

Start by calling `mcp__hardened-workspace__start_google_auth` with the user email. Then read the spreadsheet — fire in parallel for each vetted sheet: `read_sheet_values` (FORMATTED_VALUE and FORMULA), `read_sheet_notes`, `read_sheet_hyperlinks`, and `read_spreadsheet_comments` (once for the workbook).

Also load when needed: Cross-Cutting CEA Parameters (`1ru1SNtgj0D9-vLAHEdTM27GEq_P17ySzG-aTxKD6Fzg`) and GiveWell Moral Weights (`1GAcGQSyBQxcB6oGJFGGWCYqwY-jW7oahJJK-cTZOkMc`) via `read_sheet_values`. For VOI sheets: Guidance on Modeling VoI (`159LMzmUfpnlkpXR6lH9XrLNOkdIxFPNG_91c5L-OTPs`).

## Step 3 — First Error Check

Before checking formula logic, **produce an explicit enumeration of every hardcoded (non-formula) cell across ALL vetted sheets** — go row by row across primary and all supporting sheets. This must be a dedicated pass. Apply the notes checks below to every cell on that list.

**Formula correctness:**
- Broken or incorrect cell references; logically inconsistent formulas (wrong range, mismatched units, circular references)
- Hardcoded values that should be formulas, or vice versa
- Adjustment scope mismatches: adjustments applying to only one component must be applied before aggregation, not to the aggregate
- **Formula direction errors**: For multiplication/division by key parameters, verify operation direction — if this input increases, should the result increase or decrease? When one error is found, audit every other term in that same formula before moving on.
- **Cost denominator identity**: For CE computed as UoV/cost, verify (a) division not multiplication, (b) denominator references the correct cost variable for that row's context
- **Aggregation completeness**: For AVERAGE, SUM, or multi-cell ranges, count inputs and verify they match the stated intent
- **Formula inconsistency across parallel rows**: Repeated structures (same calculation across scenarios) should reference the same input columns
- **Cross-sheet reference verification**: For every cross-sheet reference (e.g., `=CEA!$C$9`), read the actual value at the referenced cell and confirm the row label matches what the calling formula expects. Flag any reference that cannot be confirmed as correct.
- **Cascade formula correctness**: For cascade-step formulas (e.g., `% diagnosed × % on treatment × % virally suppressed`), verify each multiplicand belongs. Common error: including viral suppression in "% on ART."

**Notes column** (exhaustive check on the hardcoded cell list from above):
- Hardcoded value with no source note → flag, recommend source citation
- Formula with blank Notes column → recommend adding "Calculation."
- Existing notes → verify they (a) accurately describe the formula/value, (b) are clear and unambiguous, (c) use professional organizational voice. Flag first-person language ("I think," "I increased") → recommend organizational voice ("our estimate," "GiveWell's assessment")

**Cross-vet parameter consistency** (load Cross-Cutting CEA Parameters doc now):
For every shared parameter — benchmark, discount rate, moral weights, SMC deaths-averted rates, long-term income ratio — compare against the authoritative doc. Check `reference/key-parameters.md` for current values. For declared-intentional deviations: file as `Intentional` / Severity `Low` with researcher's stated reason, Recommended Fix "No action required". For undeclared mismatches: file as `Outdated Parameter` normally.

## Step 4 — Second Formula Pass

Re-read every formula independently, without reference to Step 3 findings. Formula logic only — no plausibility or readability.

- Any formula logic errors missed in Step 3
- Edge cases: blank cells, zero denominators, negative numbers producing unexpected results
- Whether any fixes suggested in Step 3 would themselves introduce a new formula error

## Writing Findings

Read existing rows in the Findings sheet first to determine the next empty row. Append findings using `modify_sheet_values`. Group findings where the same issue applies to multiple cells — aim for ~15–25 grouped findings, not one row per cell. Update the summary row (row 2) with current counts when done. See `reference/output-format.md` for column definitions and severity rules.
