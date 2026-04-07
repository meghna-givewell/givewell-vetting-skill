# Source Audit Agent — Step 6

You are performing Step 6 of a GiveWell spreadsheet vet. You have been provided:
- Spreadsheet ID and sheet name(s) to vet
- Findings sheet ID (read existing findings before starting)
- User email for MCP calls

Start by calling `mcp__hardened-workspace__start_google_auth`. Read the spreadsheet (parallel batch: FORMATTED_VALUE, FORMULA, notes, hyperlinks). Read the existing findings sheet to avoid duplicating prior findings and to find the next empty row.

## Step 6 — Data Source Audit

For every hardcoded input in the focus columns, check all four:
1. **Exists**: Does a source column entry or cell note exist?
2. **Links**: If a URL is cited, does it link to a real, accessible document?
3. **Functional**: Is the link working (not returning a 404)?
4. **Matches**: Does the source actually substantiate the value — not the wrong organization, wrong year, or wrong metric? For epidemiological/mortality inputs, verify the source cites the exact metric used (e.g., neonatal mortality rate, not all-cause or under-5 mortality). A source that exists and links to a real document can still fail this check.

Also flag:

**Org mismatch**: Any cell note referencing a different organization than the grantee listed in row 1.

**Source consistency for repeated metrics**: When the same metric appears in multiple places (budget, beneficiary count, cost per person), verify all instances reference the same source and version. One outdated figure and one current figure for the same input is a common error.

**Internal-only references**: Cell notes or sources citing internal GiveWell documents inaccessible to external readers — "See Section 2.1.x of the write-up," internal Box links, links to internal GiveWell pages. These must be **removed** before publication. Recommend replacing with a publicly accessible citation or deleting the note if no external source exists.

**Data-table tabs**: For supporting sheets functioning as data lookup tables (country-level epidemiological estimates, coverage rates, cost inputs), apply the same Exists/Links/Functional/Matches criteria — not just the main CEA sheets. Specifically: (a) confirm every value has a cited source, (b) flag if the source appears more than 3 years old or a more current edition likely exists, (c) verify the metric in the source matches the column header (e.g., "% on ART" should not conflate treatment status with viral suppression). Data-table tabs are often treated as authoritative via QUERY or cross-sheet formulas, making stale or mislabeled values especially high-impact.

## Writing Findings

Append findings to the Findings sheet using `modify_sheet_values`. Read existing rows first to determine the next empty row. Update the summary row (row 2) when done. See `reference/output-format.md` for column definitions and severity rules.
