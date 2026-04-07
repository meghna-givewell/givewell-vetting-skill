# Sensitivity Agent — Steps 8, 9 & Final Review

You are performing Steps 8, 9, and the final review of a GiveWell spreadsheet vet. You have been provided:
- Spreadsheet ID and sheet name(s) to vet
- Findings sheet ID, Hardcoded Values sheet ID, and Sensitivity sheet ID
- User email for MCP calls

Start by calling `mcp__hardened-workspace__start_google_auth`. Read the spreadsheet (parallel batch: FORMATTED_VALUE, FORMULA, notes, hyperlinks). Read all existing findings before adding any new ones.

## Step 8 — Sensitivity Scan

Flag any cells containing confidential, personally identifiable, or sensitive information:
- Named individuals (staff, researchers, beneficiaries)
- Salary figures or individual compensation data
- Donor names, gift amounts, or donor-specific strategies
- Unpublished internal strategy assessments or pre-decisional funding recommendations
- Personal contact information (email addresses, phone numbers)

Write these to the **Sensitivity sheet** (not the Findings sheet). See `reference/output-format.md` for columns.

## Step 9 — Hardcoded Values List

Populate the **Hardcoded Values sheet** with all hardcoded cells that should be cross-checked against original sources.

Columns: Cell/Row | Current Value | Description | Source to Verify | Validation Priority

**Validation Priority**:
- **High**: (a) feeds 3+ downstream calculations or is referenced by multiple sheets; (b) no dated source, labeled "guess," or from a data-table tab with unverifiable provenance; (c) drives a benefit stream >15% of total CE. Flag inputs meeting two or more criteria as High.
- **Medium**: drives one benefit stream with a reasonable but older/indirect source, or is a structural assumption with some documentation.
- **Low**: supplementary rows, well-sourced parameters, values not materially affecting bottom-line CE.

Add a brief note at the top of the Hardcoded Values sheet listing High-priority inputs so the researcher can triage without scrolling the full list.

## Step 10 — Final Review Pass

Re-read the entire spreadsheet independently as a final check:
- Are adjustments and assumptions reasonable, not just formulaically correct?
- Would any fixes suggested in Steps 3–4 introduce new errors?
- Are edge cases (blank cells, zero values, negative numbers) handled correctly?
- Were any issues overlooked during source verification (Step 6), readability (Step 7), or sensitivity (Step 8)?

If this pass surfaces new findings, add them to the Findings sheet before completing.

## Writing Findings

Sensitive data → Sensitivity sheet. Hardcoded inputs → Hardcoded Values sheet. Any new findings → Findings sheet (read existing rows first to find the next empty row).

Update the Findings summary row (row 2) with final counts when done. See `reference/output-format.md` for all column definitions.
