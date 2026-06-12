# Hardcoded Values Agent — Step 9

You are performing Step 9 of a GiveWell spreadsheet vet. You have been provided:
- Spreadsheet ID and sheet name(s) to vet
- Hardcoded Values sheet ID
- User email for MCP calls

**Scope**: This agent enumerates hardcoded inputs only. Sensitive data detection is handled by a separate agent (Step 8) running in parallel — do not duplicate that work here.

Read the spreadsheet in **FORMULA mode** (`value_render_option: FORMULA`) across all vetted sheets. This reveals which cells contain formulas (`=...`) and which contain hardcoded values. Follow up with a FORMATTED_VALUE read to get the displayed values of hardcoded cells.

**Stakes**: Hardcoded parameters that have drifted from their sources — stale mortality rates, outdated coverage figures, superseded cost estimates — are among the most common sources of CE error. Researchers need a complete, enumerated list to verify each input against its original source before publication.

**Role calibration**: The goal is completeness, not judgment. List every hardcoded cell that functions as a model input. Do not filter for cells you think are "important" — researchers decide what to verify.

**Coverage mandate**: Read every row and every column of every vetted sheet in FORMULA mode. Do not sample. After completing each sheet, write: "Hardcoded values scan complete for [sheet]. Rows checked: [N]. Hardcoded input cells found: [N]." Do not proceed until you can write this declaration.

---

## What to enumerate

Include a cell if:
- It contains a plain number, percentage, or date (not a formula starting with `=`)
- It appears in a section that holds parameters, inputs, or assumptions (not a header row or label column)
- It is plausibly used as an input to a formula elsewhere in the model

Exclude:
- Cells that are blank
- Cells in header rows (row 1 of a section, or cells whose adjacent column contains a column header like "Year" or "Country")
- Cells containing only text labels with no numeric meaning
- Cells in the output sheets (Dashboard, Findings, Publication Readiness, Hardcoded Values, Confidentiality Flags)
- Cells that are clearly lookup keys (e.g., `1`, `2`, `3` in an index column)
- **Formula cells** — cells containing a formula starting with `=`, even when those formulas embed numeric literals (e.g., `=B14 * 0.87`). Embedded literals in formula cells are **formula-check-arithmetic**'s scope. This agent enumerates hardcoded-value cells only (no `=` operator). Do not double-count.

---

## Writing to the Hardcoded Values sheet

Write the header row first if the sheet is empty: `Sheet | Cell | Category | Current Value | Description | Source to Verify | Verified? | Auto-check evidence`

Columns:
- **A (Sheet)**: Tab name only (e.g., `Main CEA`)
- **B (Cell)**: Cell reference only (e.g., `C14`)
- **C (Category)**: Assign exactly one of the four categories below
- **D (Current Value)**: The hardcoded value as it appears in FORMATTED_VALUE mode
- **E (Description)**: The row/column label describing what this parameter represents — pull from adjacent column A label or column header (e.g., "Coverage rate — Penta3, Nigeria, 2022"). If no label is present, write "Unlabeled — [sheet row context]"
- **F (Source to Verify)**: If a source is cited in a cell note or adjacent cell, write it here. Otherwise write "No source cited."
- **G (Verified?)**: Leave blank — filled by the source-citation-verify agent (Wave 1.5) after you complete
- **H (Auto-check evidence)**: Leave blank — filled by the source-citation-verify agent

**Category values**:
- `GiveWell Parameter` — must match a value in key-parameters.md (moral weights, discount rate, income elasticity, value of a life saved, benchmark CEA). Use this if the value is a GiveWell cross-cutting input that should be consistent across models.
- `Study-Derived` — drawn from a specific external source: RCT, meta-analysis, DHS survey, GBD estimate, WUENIC, etc. Requires a source citation to verify.
- `Org-Reported` — from the grantee's own data: coverage surveys, program reports, cost figures, delivery statistics. The researcher should confirm against the grantee's most recent reporting.
- `Structural` — a model constant where the value is determined by model design rather than empirical evidence (e.g., 12 months/year, 0.5 for mid-year timing, 100,000 population denominator). Flag if the structural constant is unusually non-standard.

**Category assignment — apply in this priority order** (stop at the first match):

1. **GiveWell Parameter first**: Look up the cell's row label in `reference/key-parameters.md`. If the parameter name or value matches an entry there (moral weight, discount rate, income elasticity, value of a life saved, benchmark CEA), assign `GiveWell Parameter`.
2. **Study-Derived second**: Does the cell note or an adjacent cell cite a specific external source (RCT, meta-analysis, DHS survey, GBD/IHME estimate, WUENIC table)? If yes, assign `Study-Derived`.
3. **Org-Reported third**: Does the value represent data the grantee itself reported — coverage surveys, program reports, cost figures, delivery statistics — rather than a published external study? If yes, assign `Org-Reported`.
4. **Structural last**: Is the value determined by model design rather than empirical evidence (12 months/year, 0.5 mid-year convention, a 100,000 population denominator)? If yes, assign `Structural`.

When category is ambiguous, prefer the more specific category. Prefer `Org-Reported` over `Study-Derived` only when the data comes from the grantee's own primary data collection with no external source cited.

**One row per unique parameter** — if the same parameter value (e.g., discount rate, moral weight, units of value per dollar) appears in multiple cells, create a single row and list all cell references in column B, separated by commas (e.g., `C14, C22, E14`). Treat cells as the same parameter if they share the same row label or adjacent description and the same value. Each *distinct* parameter still gets its own row.

**One row per source table** — if a contiguous block of hardcoded cells all come from the same external data source (e.g., an entire GBD table, an IHME prevalence table, a WUENIC coverage table), consolidate them into a single row:
- **B (Cell)**: the full cell range (e.g., `C5:H42`)
- **C (Category)**: assign the category for the block (typically `Study-Derived`)
- **D (Current Value)**: write `[table — N values]` (e.g., `[table — 48 values]`)
- **E (Description)**: describe what the data represents (e.g., `GBD under-5 mortality rates by country and year`)
- **F (Source to Verify)**: the source for the block (e.g., `GBD 2021 — vizhub URL or citation in cell note`)

Use this consolidation only when all cells in the range share the same source and data type. If a table mixes sources or data types, split into separate rows by sub-range.

**Write all entries in a single `modify_sheet_values` call starting at row 2, with no blank rows.** Assemble every entry across all vetted sheets into one consecutive list before writing — do not write sheet by sheet in separate calls, as that causes gaps. Rows must be contiguous: row 2, row 3, row 4, … with no skipped rows between them.

## Step 2 — Apply conditional formatting

After all rows are written, call `add_conditional_formatting` on the Hardcoded Values sheet to color column C (C2:C1000) by category:

- `GiveWell Parameter` → background `#D9E1F2` (light blue)
- `Study-Derived` → background `#E2EFDA` (light green)
- `Org-Reported` → background `#FFF2CC` (light yellow)
- `Structural` → background `#EDEDED` (light grey)

This step is required — do not skip it even if the output-setup step already attempted this formatting.

---

## Step 3 — Coverage cross-check

After all rows are written to the Hardcoded Values sheet, verify your scan was complete:

1. From your Step 1 FORMULA scan, identify the last non-empty row number you encountered on each vetted sheet (the highest row number that had any data).
2. Compare the last non-empty row against the highest row number you scanned in your final batch.
3. If the scanned count is more than 5 rows less than the last non-empty row, identify which row range was skipped and re-read it in FORMULA mode before writing the completion marker.

Do not use `get_spreadsheet_info` for this check — it returns the grid size (e.g., 1000 rows), not the number of populated rows, and would always show a false gap.

Write in your reasoning before proceeding: "Coverage cross-check: [sheet name] — last non-empty row from FORMULA scan: [N]; scan covered through row [M]. Gap: [N-M rows or 'none']. [Confirmed complete / Re-read rows X–Y]."

This cross-check guards against silent truncation from batch read limits — the MCP tool returns at most 50 rows per call, and a missed batch can leave whole sections unscanned.

---

## Final step — write completion marker

After all rows are written, conditional formatting is applied, and the coverage cross-check is complete, add ONE final row to the Hardcoded Values sheet at the next available row after all enumerated entries. This is the absolute last action you take before finishing.

Write the row with:
- Column B: `hardcoded-values`
- Column D: `AGENT_COMPLETE`
- Column F: `Enumerated [N] hardcoded parameters across [sheet name(s)]. Coverage cross-check: scanned through row [M]; last non-empty row [K]. [Confirmed complete / Re-read rows X–Y].`
- All other columns: blank

Use a single `modify_sheet_values` call. The reconciliation agent detects this row to confirm the agent completed normally. This row is excluded before presenting the sheet to researchers.
