# Final Review — Step 10d: Dashboard Agent

## Guard — Verify prior stages are complete

Before reading any findings or writing any dashboard output, verify that all three prior final-review stages have completed successfully. Read Findings sheet rows around the known AGENT_COMPLETE marker range (or scan batched rows) and confirm that rows with column D = `AGENT_COMPLETE` exist for each of the following column B values:

- `final-review-compaction`
- `final-review-gap-fill`
- `final-review-validation`

If any of these three markers is missing: write a single row to the Findings sheet with column B = `final-review-dashboard`, column D = `ERROR`, and column F = `Dashboard halted — AGENT_COMPLETE marker missing for [name of missing stage(s)]. Re-run that stage before running the dashboard agent.` Then **STOP** — do not proceed with any dashboard work, cleanup, or Key Findings summary until all three prior stages have completed. Do not attempt to proceed on a partial audit trail.

---

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

Read all non-divider rows from the Findings sheet (batched: `A2:H51`, `A52:H101`, `A102:H151`, continuing in 50-row increments until two consecutive batches return no non-empty rows). **The MCP tool returns at most 50 rows per call — larger ranges silently truncate.** Collect: all High findings (for Key Findings summary), and the count of High/Medium/Low findings. When counting, skip divider rows (column D is empty AND column B contains ───) and skip rows where column D = `AGENT_COMPLETE` — these are pipeline completion markers written by the final-review agents (compaction, gap-fill, validation), not findings. Do not include divider rows or AGENT_COMPLETE rows in any finding count or in the total count.

Also read the Hardcoded Values sheet column G (Verified? column) in the same batched manner to collect Wave 1.5 verification status counts: number of matched, contradicted, and could-not-verify values. If the column is entirely blank, note that Wave 1.5 source-citation-verify was skipped.

Read all rows from Publication Readiness (batched: `A2:F51`, `A52:F101`, continuing in 50-row increments until two consecutive batches return no non-empty rows). Collect the total count.

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

**Tab-name comma handling**: When reading the list of unique sheet names from column B of the Findings sheet to populate the per-sheet table rows, treat each cell value in column B as a single tab name — even if the value contains a comma. Do not split on commas when extracting tab names from column B. (Commas in tab names are uncommon but possible.) When writing tab names as static text in Dashboard column A, write the full tab name including any commas. The COUNTIFS formula uses the full tab name as its criteria string and will match correctly as long as the Findings sheet column B also contains the full name.

After the last sheet row, write a totals row: `Total` in column A, `=SUM(B25:B{last})` in B, same pattern for C–D, `=SUM(E25:E{last})` in E. **{last} must be the row number of the last per-sheet data row — that is, the row immediately above the Totals row itself. The Totals row must not be included in the SUM range, or the formula will self-reference and produce a circular dependency error.**

After the Total row, skip one blank row, then write `Sheets not vetted:` in column A. On each subsequent row, write one unvetted tab name in column A.

To compute the unvetted list accurately: call `get_spreadsheet_info` on the source spreadsheet to retrieve the complete list of all tabs. Compare that list against the vetted and lite-passed tabs from the session context scope declaration. Any tab not in either list is unvetted — write each on its own row in column A. If every tab in the workbook is covered by vetted or lite-passed, write `None`. Do not rely solely on the session context scope declaration — always verify against the actual workbook tab list.

After writing all Dashboard content with `modify_sheet_values`, make a single `format_sheet_range` call to bold the `Sheets not vetted:` cell. If `format_sheet_range` is not available, skip the bold — the label is readable without it.

**Validation-completion guard (DASH-7 — secondary safety net only)**: The top-of-file guard already verified that the `final-review-validation` AGENT_COMPLETE marker is present; if that guard passed, this condition is satisfied and no re-check is needed. This block is retained only as a defense-in-depth fallback: if for any reason the top guard was bypassed or skipped, re-read the Findings sheet in batched increments and confirm a row exists where column B = `final-review-validation` AND column D = `AGENT_COMPLETE`. If this marker is absent when writing the dashboard, add the following warning in the Dashboard in the row immediately after the Total row (the first blank row following the per-sheet table — never in rows 1–23, which are reserved for static setup content): "⚠️ Validation not completed — some findings may not have been verified. Re-run final-review-validation (Step 10c) before sharing this output." Do not omit this warning if the marker is genuinely absent.

If session context indicates a formula/heads-up only scope mode: add a `Partially vetted (heads-up only):` row below the Sheets not vetted list, listing any tabs where only heads-up agents ran. Do not list these tabs under Sheets not vetted — they were checked, just not at full depth.

**Top High Findings block**: After the Sheets not vetted list, skip two blank rows, then write a `TOP HIGH FINDINGS` summary block to the Dashboard. This gives reviewers the most actionable items without opening the Findings sheet.

- Write `TOP HIGH FINDINGS` in column A (bold — include in the `format_sheet_range` bold call below or make a separate call if needed).
- For each High finding (up to 3; use the first 3 from the sorted Findings sheet): write one row with column A = Finding ID (e.g., F-001), column B = Sheet name, column C = Cell/Row, column D = one-sentence description (first ~80 chars of column F from the Findings sheet).
- If there are no High findings, write `No High findings` in column A of this block.

Place this block starting at the row immediately after the last "Sheets not vetted" or "Partially vetted" entry + 2 blank rows. **If the last dashboard row (the final unvetted-tabs or partially-vetted entry) is at row 93 or later, skip the block entirely** — rows 99–148 are reserved for the Staging Sheet Log and the block requires at minimum 5 rows of content plus 2 blank separator rows, so the block must start no later than row 94. When skipping, note: `TOP HIGH FINDINGS: skipped — unvetted tab list extends past row 93; Staging Sheet Log occupies rows 99–148`.

The per-sheet table starts at row 25 per the reserved layout in output-setup.md. Do not write above row 24 under any circumstances — rows 1–23 contain static setup content written during output initialization. If the per-sheet table plus unvetted tabs list would extend past row 148, warn the researcher before writing.

**Scope declaration recovery** — if session context was compacted and the vetted/lite-passed tab lists are not available: read Dashboard cells B151:B153 of the output spreadsheet (written by the orchestrator before Wave 1). Cell B151 = comma-separated fully vetted tabs, cell B152 = comma-separated lite-pass tabs, cell B153 = vet scope ('full' or 'formula-only'). Do not read column A values — those are row labels, not data. Use B151–B153 as the scope declaration. If B151 is also blank or unreadable, announce: "Scope declaration unavailable — vet metadata at Dashboard B151:B153 is missing. Ask the researcher which tabs were fully vetted vs. lite-passed before finalizing the unvetted list." Then proceed with the tab list from `get_spreadsheet_info` and leave the vetted/lite-passed categorization blank.

---

## Step 3 — Write Key Findings summary in chat

Present the following in chat:

```
**Key Findings**

**Vet scope**: Fully vetted: [tab names] | Lite-pass: [tab names or "none"] | Not checked: [remaining tab names or "none"] | TA BOTEC: [checked / not detected / skipped]

[N] model findings: [H] High, [M] Medium, [L] Low
[N] publication-readiness items (separate sheet)
[N] hardcoded values pre-verified: [M] matched, [K] contradicted, [P] could not verify. [Or: Wave 1.5 source-citation-verify: skipped — Verified? column is blank throughout.]

**High findings**
• [Sheet / Cell ref] — [one-sentence description and directional CE impact]
• ...
```

Rules:
- Use the tab list already retrieved in Step 2b — do not call `get_spreadsheet_info` again. Fully vetted = tabs in session context vetted list; Lite-pass = tabs in session context lite-pass list; Not checked = all remaining tabs in the workbook. Do not write "all tabs" — list the actual tab names (comma-separated) or write "none" only if the list is genuinely empty after comparing against the real workbook tab count.
- For the TA BOTEC field: derive from session context whether ce-chain-trace-ta reported findings, announced a clean exit, or was not run. If session context does not specify, omit this field rather than guessing.
- For the hardcoded values line: use the Verified? column counts collected in Step 1. If Wave 1.5 was skipped (all blank), use the skipped variant.
- If no High findings, omit the High findings section entirely (do not write the heading or "No High findings"). Only include sections that have content.
- If there are more than 10 High findings: group them by sheet name and write one bullet per sheet summarizing the count and dominant issue type (e.g., `Main CEA (4 findings): formula errors affecting CE chain`). List individual bullets only for findings with a known CE direction and quantified magnitude — these are the most actionable.
- If there are 10 or fewer High findings, list each individually grouped by sheet.
- Keep each bullet to one sentence — the full detail is in the Findings sheet.

---

## Cleanup — Delete staging tabs and Staging_backup

Perform this cleanup **after** writing the Key Findings summary to chat (Step 3) and **before** writing the AGENT_COMPLETE marker (Step 4). The Key Findings summary must be fully written first: if the summary reveals a finding count discrepancy, the audit trail (stg-* tabs and Staging_backup) is needed to re-run compaction before it is gone.

**Delete all stg-* staging tabs:**

1. Call ToolSearch with query `select:mcp__hardened-workspace__delete_sheet` to load the delete_sheet tool schema. If that exact name is not found, search ToolSearch with query `delete sheet tab spreadsheet` to find the correct tool name.
2. If found: retrieve the full list of stg-* tab names from Dashboard A99 onward (written during output setup) or from session context. For each stg-* tab name, call delete_sheet with the output spreadsheet ID and that tab name. Announce a single summary: `Deleted [N] staging tabs (stg-*). [N failed — researcher to delete manually: list]` (include failed deletions; do not silently omit them).
3. If delete_sheet is not found or not available: announce: `⚠️ Could not delete staging tabs — researcher should delete all tabs whose names begin with stg- manually before sharing the output spreadsheet.`

**Delete Staging_backup tab:**

1. Using the same delete_sheet tool (already loaded above): call it with the output spreadsheet ID and tab name `Staging_backup`. Announce: `✓ Staging_backup tab deleted — output spreadsheet is clean.`
2. If not found: announce: `⚠️ Could not delete Staging_backup tab — researcher should delete it manually before sharing the output spreadsheet (Dashboard → right-click Staging_backup → Delete).`

This step is required to prevent researchers from seeing raw pre-compaction data alongside the clean, sorted output.

---

## Step 4 — Write AGENT_COMPLETE marker

Write the AGENT_COMPLETE marker to the Dashboard tab:
- Cell B200 = `final-review-dashboard`
- Cell D200 = `AGENT_COMPLETE`
- Cell F200 = `Dashboard content written. Key Findings written to chat. Staging_backup deleted (or researcher notified). Step 10d complete.`

**Dynamic row placement**: Row 200 is the default placement and is safely below all expected dashboard content. However, if the per-sheet table plus unvetted tabs list extends close to row 200 (within 10 rows), compute the AGENT_COMPLETE row dynamically as the last data row in the Dashboard tab + 10. Use `read_sheet_values` on Dashboard column A in a large range (e.g., `A1:A250`) to find the last non-empty row, then write the AGENT_COMPLETE marker to that row + 10. This prevents the marker from being overwritten if the dashboard content grows. Note: the COUNTIFS formulas in Step 2b use explicit row ranges (e.g., `B25:B{last}`) scoped to the per-sheet data rows — they are not affected by where the AGENT_COMPLETE marker is placed, so moving the marker does not introduce circular references.
