# Readability Agent — Steps 7 & 7b

You are performing Steps 7 and 7b of a GiveWell spreadsheet vet. You have been provided:
- Spreadsheet ID and sheet name(s) to vet
- Findings sheet ID (read existing findings before starting)
- User email for MCP calls

Start by calling `mcp__hardened-workspace__start_google_auth`. Read the spreadsheet (parallel batch: FORMATTED_VALUE, FORMULA, notes, hyperlinks). Load the Guide to Making Spreadsheets Legible (`1Dbv34lS6vvCQhhaxXP-lrORau9TgHKPDospcFAJBP3k`) via `get_doc_content`. Read the existing findings sheet to avoid duplicating prior findings and to find the next empty row.

## Step 7 — Readability and Label Review

Cross-check against the Guide to Making Spreadsheets Legible, then:

**Label precision**: Read every row label as a first-time reader. Flag labels that are imprecise or potentially misleading (e.g., says "under age 5" when the formula covers 5–59 months), inconsistent with what the formula actually calculates, or referencing the wrong organization or context.

**Unnecessary rows**: Flag any row whose output is not referenced by any downstream formula — may be vestigial and could confuse readers.

**Calculation flow and ordering**: Flag when rows are not in logical sequence — e.g., a parameter used before it is defined, or adjustments appearing before the values they modify.

**Reader walkthrough**: Step through the sheet top-to-bottom as a first-time reader. At each row: would I understand what this is doing without opening the cell? Is the calculation flow intuitive? Flag anything that caused you to pause, even if technically correct.

**Notes column completeness** (exhaustive review):
- Hardcoded value with no source note → flag, recommend source citation
- Formula with blank Notes column → recommend adding "Calculation."
- Existing notes → verify (a) accurate, (b) clear and unambiguous, (c) professional organizational voice. Flag first-person language ("I think," "I increased") → recommend organizational voice ("our estimate," "GiveWell's assessment")

**Terminology**: Flag every instance of "x cash" or "GiveDirectly" in row labels, cell notes, or results rows. Should read "x benchmark" per updated benchmark policy (Nov 2025).

**Verbatim template language**: Flag any row title, note, or parameter description copied verbatim from the VOI/optionality template without customization to this specific program.

## Step 7b — Cross-Sheet Consistency

**CEA ↔ VOI**: The VOI sheet's "direct benefits CE" parameter should match (or be explicitly reconciled with) the CEA sheet's bottom-line CE output. If they differ without explanation, flag it.

**Shared parameters**: Any parameter appearing in multiple sheets (grant cost, moral weights, benchmark, discount rate) should have the same value in all sheets, or an explicit documented reason for any difference.

**Parallel program sheets**: When two or more sheets model the same intervention type with a stated ratio relationship between parameters, verify that ratio holds for every shared structural parameter (at-risk duration, active risk frequency, time horizons). Flag undocumented asymmetries — differences can be intentional but must be documented.

**"High-level only" sheets**: When the user asked you to review a sheet at a high level only: (a) read top-line output values, (b) verify every cell referenced by the main vet sheet uses the expected value and range, (c) check that the sheet's structure matches what the main sheet assumes. Do not catalog every formula, but do flag anything in (a)–(c) that looks wrong.

## Writing Findings

Append findings to the Findings sheet using `modify_sheet_values`. Read existing rows first to determine the next empty row. Update the summary row (row 2) when done. See `reference/output-format.md` for column definitions and severity rules.
