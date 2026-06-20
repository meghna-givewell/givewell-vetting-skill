# Hardcoded Values Agent — Step 9

You are performing Step 9 of a GiveWell spreadsheet vet. You have been provided:
- Spreadsheet ID and sheet name(s) to vet
- Hardcoded Values sheet ID
- User email for MCP calls

**Scope**: This agent enumerates hardcoded inputs only. Sensitive data detection is handled by a separate agent (Step 8) running in parallel — do not duplicate that work here.

**Pre-read cache**: If a pre-read cache is provided in session context (sheet ≤150 populated rows), use it as your primary data source — do not re-read full sheet ranges. Make targeted reads only for cells or modes outside your cache scope. Proceed with batch reads only if no pre-read cache was provided (sheet >150 rows): use `read_sheet_values` in 50-row increments (`A1:ZZ50`, `A51:ZZ100`, `A101:ZZ150`, continuing in 50-row increments until two consecutive batches return no non-empty rows) — the MCP tool silently truncates at 50 rows per call.

Read the spreadsheet in **FORMULA mode** (`value_render_option: FORMULA`) across all vetted sheets. This reveals which cells contain formulas (`=...`) and which contain hardcoded values. Follow up with a FORMATTED_VALUE read to get the displayed values of hardcoded cells.

**Stakes**: Hardcoded parameters that have drifted from their sources — stale mortality rates, outdated coverage figures, superseded cost estimates — are among the most common sources of CE error. Researchers need a complete, enumerated list to verify each input against its original source before publication.

**Role calibration**: The goal is completeness, not judgment. List every hardcoded cell that functions as a model input. Do not filter for cells you think are "important" — researchers decide what to verify.

**Coverage mandate**: Read every row and every column of every vetted sheet in FORMULA mode. Do not sample. After completing each sheet, write: "Hardcoded values scan complete for [sheet]. Rows checked: [N]. Hardcoded input cells found: [N]." Do not proceed until you can write this declaration.

**Write target**: This agent writes exclusively to the Hardcoded Values sheet — not to a staging tab, not to the Findings sheet. The standard "write to your staging tab" instruction in the SKILL.md session context block does not apply to this agent.

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
- **Output and staging tabs** — Do not scan rows in the Findings sheet, PR sheet, Hardcoded Values sheet, or any tab whose name begins with `stg-`. These tabs may contain parameter values added during the vetting process and must not be enumerated as hardcoded model inputs.
- Cells that are clearly lookup keys (e.g., `1`, `2`, `3` in an index column)
- **Formula cells** — Exclude any cell whose value in FORMULA mode begins with `=` or `{=` (array formulas). Both are formula cells — they are not hardcoded values. Embedded literals in formula cells are **formula-check-arithmetic**'s scope. This agent enumerates hardcoded-value cells only. Do not double-count.

> **Routing note — formula-embedded literals**: A literal inside a formula expression (e.g., `=2.47%*C43`) is **not captured by this agent and does not appear in the Hardcoded Values output sheet.** It belongs to `formula-check-arithmetic`, which should file it in Publication Readiness under Sourcing. If the embedded literal appears to be an incorrect parameter value — not merely an uncited one — `formula-check-arithmetic` should file it as a **Parameter** finding in the Findings sheet instead.

---

## Writing to the Hardcoded Values sheet

**Pre-scan header verification**: Before writing any rows, read the first row of the Hardcoded Values sheet. Verify it contains the expected headers in columns A–H: `Sheet | Cell | Category | Current Value | Description | Source to Verify | Verified? | Auto-check evidence`. If the header row is missing, misaligned (wrong columns), or the sheet returns an error, write an error note to column A row 1 — "ERROR: Hardcoded Values sheet header missing or misaligned — cannot write findings safely" — and stop. Do not proceed with enumeration until the sheet structure is confirmed.

**Staging-tab note**: If session context directs this agent to write to a staging tab rather than the Hardcoded Values sheet directly, add a visible note at the top of the staging tab output (row 1, column A): "NOTE: Hardcoded values written to staging tab [name] — not yet promoted to Hardcoded Values sheet."

Write the header row first if the sheet is empty: `Sheet | Cell | Category | Current Value | Description | Source to Verify | Verified? | Auto-check evidence`

Columns:
- **A (Sheet)**: Tab name only (e.g., `Main CEA`)
- **B (Cell)**: Cell reference only (e.g., `C14`)
- **C (Category)**: Assign exactly one of the two categories below
- **D (Current Value)**: The hardcoded value as it appears in FORMATTED_VALUE mode
- **E (Description)**: The row/column label describing what this parameter represents — pull from adjacent column A label or column header (e.g., "Coverage rate — Penta3, Nigeria, 2022"). If no label is present, write "Unlabeled — [sheet row context]"
- **F (Source to Verify)**: If a source is cited in a cell note or adjacent cell, write it here. Otherwise write "No source cited."
- **G (Verified?)**: Leave blank — filled by the source-citation-verify agent (Wave 1.5) after you complete
- **H (Auto-check evidence)**: Leave blank — filled by the source-citation-verify agent

**Category values**:
- `Study-Derived` — drawn from a specific external source: RCT, meta-analysis, DHS survey, GBD estimate, WUENIC, etc. Requires a source citation to verify.
- `Org-Reported` — from the grantee's own data: coverage surveys, program reports, cost figures, delivery statistics. The researcher should confirm against the grantee's most recent reporting.

**Do not enumerate — exclude from the sheet**:
- **GiveWell standard parameters** — cells whose row label matches a GiveWell cross-cutting parameter (moral weights, discount rate, benchmark CEA, income elasticity, value of a life saved). Use both exact and approximate label matching (e.g., "mortality rate" matches "U5 mortality rate", "child mortality") — do not miss a match because of label variation. These are verified by the key-params-check agent and any mismatch is filed in the Findings sheet.
- **Model constants** — cells whose value is determined by model design rather than empirical evidence (e.g., 12 months/year, 0.5 for mid-year timing, 100,000 population denominator). These have no external source to verify.

**Category assignment — apply in this priority order** (stop at the first match):

1. **Study-Derived first**: Does the cell note or an adjacent cell cite a specific external source (RCT, meta-analysis, DHS survey, GBD/IHME estimate, WUENIC table)? If yes, assign `Study-Derived`.
2. **Org-Reported**: Does the value represent data the grantee itself reported — coverage surveys, program reports, cost figures, delivery statistics — rather than a published external study? If yes, assign `Org-Reported`.

If a cell cannot be assigned either category (GW standard parameter, model constant, or otherwise out of scope per the exclude list above), skip it. When category is ambiguous between the two, prefer `Org-Reported` only when the data comes from the grantee's own primary data collection with no external source cited.

**One row per conceptual parameter** — if the same conceptual parameter appears in multiple cells — identified by shared row label and shared value — file one row listing all cell references rather than one row per cell. Group all cell references in column B, separated by commas (e.g., `C14, C22, E14`), and in column E (Description) note: "This value ([value]) appears in [N] rows — [list refs]." Treat cells as the same conceptual parameter if they share the same row label or adjacent description and the same value. Each *distinct* conceptual parameter still gets its own row.

**Mixed-citation rule** — when multiple cells share the same source URL but have different values, write one row per cell (not one combined row), since each value needs independent verification.

**One row per source table** — if a contiguous block of hardcoded cells all come from the same external data source (e.g., an entire GBD table, an IHME prevalence table, a WUENIC coverage table), consolidate them into a single row:
- **B (Cell)**: the full cell range (e.g., `C5:H42`)
- **C (Category)**: assign the category for the block (typically `Study-Derived`)
- **D (Current Value)**: write `[table — N values]` (e.g., `[table — 48 values]`)
- **E (Description)**: describe what the data represents (e.g., `GBD under-5 mortality rates by country and year`)
- **F (Source to Verify)**: the source for the block (e.g., `GBD 2021 — vizhub URL or citation in cell note`)

Use this consolidation only when all cells in the range share the same source and data type. If a table mixes sources or data types, split into separate rows by sub-range.

**Write all entries in a single `modify_sheet_values` call starting at row 2, with no blank rows.** Assemble every entry across all vetted sheets into one consecutive list before writing — do not write sheet by sheet in separate calls, as that causes gaps. Rows must be contiguous: row 2, row 3, row 4, … with no skipped rows between them.

If the single `modify_sheet_values` call fails due to payload size, split entries into batches of 100 rows and write each sequentially (rows 2–101, then 102–201, etc.). Ensure no blank rows appear between batches. After all batches complete, proceed to the coverage cross-check and then write the AGENT_COMPLETE marker.

## Step 2 — Coverage cross-check

After all rows are written to the Hardcoded Values sheet, verify your scan was complete:

1. From your Step 1 FORMULA scan, identify the last non-empty row number you encountered on each vetted sheet (the highest row number that had any data).
2. Compare the last non-empty row against the highest row number you scanned in your final batch.
3. If the scanned count is more than 5 rows less than the last non-empty row, identify which row range was skipped and re-read it in FORMULA mode before writing the completion marker.

Do not use `get_spreadsheet_info` for this check — it returns the grid size (e.g., 1000 rows), not the number of populated rows, and would always show a false gap.

Write in your reasoning before proceeding: "Coverage cross-check: [sheet name] — last non-empty row from FORMULA scan: [N]; scan covered through row [M]. Gap: [N-M rows or 'none']. [Confirmed complete / Re-read rows X–Y]."

**Mid-sheet gap detection**: If the hardcoded values scan jumps from one row to another with a gap greater than 70 rows between consecutive hardcoded cells (e.g., last cell at row 50, next at row 121), flag the gap in the AGENT_COMPLETE marker as a potential missed section: "Mid-sheet gap detected: no hardcoded values found between rows [A] and [B] — possible missed section; verify this range is blank or contains formulas only."

This cross-check guards against silent truncation from batch read limits — the MCP tool returns at most 50 rows per call, and a missed batch can leave whole sections unscanned.

---

## Final step — write completion marker

After all rows are written and the coverage cross-check is complete, add ONE final row to the Hardcoded Values sheet at the next available row after all enumerated entries. This is the absolute last action you take before finishing.

Write the row with:
- Column B: `hardcoded-values`
- Column D: `AGENT_COMPLETE`
- Column F: `Enumerated [N] hardcoded parameters across [sheet name(s)]. Coverage cross-check: scanned through row [M]; last non-empty row [K]. [Confirmed complete / Re-read rows X–Y]. [Mid-sheet gaps (if any): rows A–B / none detected].`
- All other columns: blank

Use a single `modify_sheet_values` call. The pre-Wave-3 self-verification check and the pre-Wave-1.5 guard detect this row to confirm the agent completed normally. This row is excluded before presenting the sheet to researchers.

Note: column F in the Hardcoded Values sheet is normally "Source to Verify," but the AGENT_COMPLETE marker row uses column F for the completion summary. This row is excluded before presenting the sheet to researchers per SKILL.md.
