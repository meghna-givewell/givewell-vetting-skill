# Final Review — Step 10d: Dashboard Agent

You are performing Step 10d of a GiveWell spreadsheet vet. This is the last of four sequential final-review steps. Compaction (10a), gap-fill (10b), and validation (10c) are already complete and Finding IDs are assigned. You have been provided:
- Source spreadsheet ID (the workbook being vetted — used only for `get_spreadsheet_info` to retrieve the complete tab list)
- Output spreadsheet ID (the spreadsheet containing Dashboard, Findings, Publication Readiness tabs)
- Session context scope declaration (which tabs were fully vetted, lite-passed, not checked)
- User email for MCP calls

**Permitted tools:** read_sheet_values (rv) — read Findings and Publication Readiness rows, and Dashboard metadata recovery cells; modify_sheet_values (wv) — write Dashboard content; get_spreadsheet_info (si) — retrieve source spreadsheet tab list (one call only); ToolSearch — load delete_sheet schema for cleanup. Do not call any other tool.

**Before starting:** read `reference/pitfalls.md` using the Read tool. This file contains calibration rules that affect coverage reporting and scope declarations.

**The only permitted read on the source spreadsheet is a single `get_spreadsheet_info` call** to obtain the complete list of tabs. Do not read any sheet values from the source spreadsheet.

---

## Step 1 — Read findings for summary

Read all non-divider rows from the Findings sheet (batched: `A2:J51`, `A52:J101`, `A102:J151`, continuing in 50-row increments until two consecutive batches return no non-empty rows). **The MCP tool returns at most 50 rows per call — larger ranges silently truncate.** Collect: all High findings (for Key Findings summary), all findings with `✓` in column I (Researcher judgment needed), and the count of High/Medium/Low findings. When counting, skip divider rows (column D is empty AND column B contains ───) and skip rows where column D = `AGENT_COMPLETE` — these are pipeline completion markers written by the final-review agents (compaction, gap-fill, validation), not findings. Do not include divider rows or AGENT_COMPLETE rows in any finding count or in the total count.

Also read the Hardcoded Values sheet column G (Verified? column) in the same batched manner to collect Wave 1.5 verification status counts: number of matched, contradicted, and could-not-verify values. If the column is entirely blank, note that Wave 1.5 source-citation-verify was skipped.

Read all rows from Publication Readiness (batched: `A2:H51`, `A52:H101`, continuing in 50-row increments until two consecutive batches return no non-empty rows). Collect the total count.

---

## Step 2 — Write Dashboard content

Use `modify_sheet_values` (USER_ENTERED) on the Dashboard tab.

**a. CE estimate direction (cell B22)**: Review Estimated CE Impact (column H) for all High findings and write one short phrase: `Likely overstated (~1.4x)`, `Likely understated (CE may rise from 8.7x to ~10x)`, `Mixed`, `Not quantified (no High findings)`, or `High findings present but none affect CE — see Findings sheet` (use the last phrase when High findings exist but all have "No CE impact" or blank column H). If magnitude is unknown: `Likely overstated (magnitude unclear — see High findings)`.

**Zero-findings gate**: If the Findings sheet has zero non-divider finding rows: write `Not quantified (no findings)` in B22; write only the headers in row 24 and a single Totals row in row 25 with static zeros (not SUM formulas, since the SUM range would be empty); write the Sheets not vetted block below row 26. Skip the per-sheet rows entirely. Then proceed to Step 3 with the zero-finding counts.

**b. Findings by sheet table and Sheets not vetted (rows 24 onward)**:

Row 24: column headers — write `Sheet` in A24, `High` in B24, `Medium` in C24, `Low` in D24, `Total` in E24.

Note: in the final Findings sheet (post-compaction), column B contains the source spreadsheet tab name (e.g., Main CEA, Inputs) — not the vetting agent name. The COUNTIFS formulas reference this column to group findings by source tab. Do not confuse the final Findings sheet column layout with the staging tab layout.

Rows 25 onward: one row per unique sheet name found in column B of the Findings sheet (excluding divider rows), sorted alphabetically by sheet name, with `Multiple` last if present. Write sheet names as static text in column A. Write counts as `COUNTIFS` formulas that auto-update:
- For a sheet name in Dashboard cell A25: write `=COUNTIFS(Findings!B:B,A25,Findings!D:D,"High")` in B25, `=COUNTIFS(Findings!B:B,A25,Findings!D:D,"Medium")` in C25, `=COUNTIFS(Findings!B:B,A25,Findings!D:D,"Low")` in D25, `=SUM(B25:D25)` in E25.
- Repeat for each sheet name, incrementing row numbers.
- Include `Multiple` as a row if any findings use that sheet name.

After the last sheet row, write a totals row: `Total` in column A, `=SUM(B25:B{last})` in B, same pattern for C–D, `=SUM(E25:E{last})` in E.

After the Total row, skip one blank row, then write `Sheets not vetted:` in column A. On each subsequent row, write one unvetted tab name in column A.

To compute the unvetted list accurately: call `get_spreadsheet_info` on the source spreadsheet to retrieve the complete list of all tabs. Compare that list against the vetted and lite-passed tabs from the session context scope declaration. Any tab not in either list is unvetted — write each on its own row in column A. If every tab in the workbook is covered by vetted or lite-passed, write `None`. Do not rely solely on the session context scope declaration — always verify against the actual workbook tab list.

After writing all Dashboard content with `modify_sheet_values`, make a single `format_sheet_range` call to bold the `Sheets not vetted:` cell. If `format_sheet_range` is not available, skip the bold — the label is readable without it.

If session context indicates a formula/heads-up only scope mode: add a `Partially vetted (heads-up only):` row below the Sheets not vetted list, listing any tabs where only heads-up agents ran. Do not list these tabs under Sheets not vetted — they were checked, just not at full depth.

The per-sheet table starts at row 25 per the reserved layout in output-setup.md. Do not write above row 24 under any circumstances — rows 1–23 contain static setup content written during output initialization. If the per-sheet table plus unvetted tabs list would extend past row 148, warn the researcher before writing.

**Scope declaration recovery** — if session context was compacted and the vetted/lite-passed tab lists are not available: read Dashboard cells B151:B153 of the output spreadsheet (written by the orchestrator before Wave 1). Cell B151 = comma-separated fully vetted tabs, cell B152 = comma-separated lite-pass tabs, cell B153 = vet scope ('full' or 'formula-only'). Do not read column A values — those are row labels, not data. Use B151–B153 as the scope declaration. If B151 is also blank or unreadable, announce: "Scope declaration unavailable — vet metadata at Dashboard B151:B153 is missing. Ask the researcher which tabs were fully vetted vs. lite-passed before finalizing the unvetted list." Then proceed with the tab list from `get_spreadsheet_info` and leave the vetted/lite-passed categorization blank.

---

## Cleanup — Delete staging tabs and Staging_backup

Perform this cleanup **before** writing the Key Findings summary to chat (Step 3), so the output spreadsheet is fully clean when the researcher opens it.

**Delete all stg-* staging tabs:**

1. Call ToolSearch with query `select:mcp__hardened-workspace__delete_sheet` to load the delete_sheet tool schema. If that exact name is not found, search ToolSearch with query `delete sheet tab spreadsheet` to find the correct tool name.
2. If found: retrieve the full list of stg-* tab names from Dashboard A99 onward (written during output setup) or from session context. For each stg-* tab name, call delete_sheet with the output spreadsheet ID and that tab name. Announce a single summary: `Deleted [N] staging tabs (stg-*). [N failed — researcher to delete manually: list]` (include failed deletions; do not silently omit them).
3. If delete_sheet is not found or not available: announce: `⚠️ Could not delete staging tabs — researcher should delete all tabs whose names begin with stg- manually before sharing the output spreadsheet.`

**Delete Staging_backup tab:**

1. Using the same delete_sheet tool (already loaded above): call it with the output spreadsheet ID and tab name `Staging_backup`. Announce: `✓ Staging_backup tab deleted — output spreadsheet is clean.`
2. If not found: announce: `⚠️ Could not delete Staging_backup tab — researcher should delete it manually before sharing the output spreadsheet (Dashboard → right-click Staging_backup → Delete).`

This step is required to prevent researchers from seeing raw pre-compaction data alongside the clean, sorted output.

---

## Step 3 — Write Key Findings summary in chat

Present the following in chat:

```
**Key Findings**

**Vet scope**: Fully vetted: [tab names] | Lite-pass: [tab names or "none"] | Not checked: [remaining tab names or "none"] | TA BOTEC: [checked / not detected / skipped]

[N] model findings: [H] High, [M] Medium, [L] Low — [X] require researcher input
[N] publication-readiness items (separate sheet)
[N] hardcoded values pre-verified: [M] matched, [K] contradicted, [P] could not verify. [Or: Wave 1.5 source-citation-verify: skipped — Verified? column is blank throughout.]

**High findings**
• [Sheet / Cell ref] — [one-sentence description and directional CE impact]
• ...

**Items requiring researcher input**
• [Sheet / Cell ref] — [the specific question the researcher must answer]
• ...
```

Rules:
- Use the tab list already retrieved in Step 2b — do not call `get_spreadsheet_info` again. Fully vetted = tabs in session context vetted list; Lite-pass = tabs in session context lite-pass list; Not checked = all remaining tabs in the workbook. Do not write "all tabs" — list the actual tab names (comma-separated) or write "none" only if the list is genuinely empty after comparing against the real workbook tab count.
- For the TA BOTEC field: derive from session context whether ce-chain-trace-ta reported findings, announced a clean exit, or was not run. If session context does not specify, omit this field rather than guessing.
- For the hardcoded values line: use the Verified? column counts collected in Step 1. If Wave 1.5 was skipped (all blank), use the skipped variant.
- If no High findings, omit the High findings section entirely (do not write the heading or "No High findings"). If no researcher input items, omit that section entirely. Only include sections that have content.
- If there are more than 10 High findings: group them by sheet name and write one bullet per sheet summarizing the count and dominant issue type (e.g., `Main CEA (4 findings): formula errors affecting CE chain`). List individual bullets only for findings with a known CE direction and quantified magnitude — these are the most actionable. For Direction unknown findings, group under a subheading `N High findings require researcher input (see Items requiring researcher input below).` For Direction unknown bullets, write: `[Sheet / Cell ref] — direction depends on researcher input (see Finding ID F-NNN).`
- If there are 10 or fewer High findings, list each individually grouped by sheet.
- List only items with `✓` in column I (Researcher judgment needed) from the Findings sheet under "Items requiring researcher input" — do not include pub-readiness items here. If none, omit this section.
- Keep each bullet to one sentence — the full detail is in the Findings sheet.

---

## Step 4 — Write AGENT_COMPLETE marker

Write the AGENT_COMPLETE marker to the Dashboard tab:
- Cell B200 = `final-review-dashboard`
- Cell D200 = `AGENT_COMPLETE`
- Cell F200 = `Dashboard content written. Key Findings written to chat. Staging_backup deleted (or researcher notified). Step 10d complete.`

This cell range (row 200) is safely below all other Dashboard content.
