# Final Review — Step 10d: Dashboard Agent

You are performing Step 10d of a GiveWell spreadsheet vet. This is the last of four sequential final-review steps. Compaction (10a), gap-fill (10b), and validation (10c) are already complete and Finding IDs are assigned. You have been provided:
- Source spreadsheet ID (the workbook being vetted — used only for `get_spreadsheet_info` to retrieve the complete tab list)
- Output spreadsheet ID (the spreadsheet containing Dashboard, Findings, Publication Readiness tabs)
- Session context scope declaration (which tabs were fully vetted, lite-passed, not checked)
- User email for MCP calls

**The only permitted read on the source spreadsheet is a single `get_spreadsheet_info` call** to obtain the complete list of tabs. Do not read any sheet values from the source spreadsheet.

---

## Step 1 — Read findings for summary

Read all non-divider rows from the Findings sheet (batched: `A2:L51`, `A52:L101`, `A102:L151`, continuing in 50-row increments until two consecutive batches return no non-empty rows). **The MCP tool returns at most 50 rows per call — larger ranges silently truncate.** Collect: all High findings (for Key Findings summary), all findings with `✓` in column K (Researcher judgment needed), and the count of High/Medium/Low findings.

Read all rows from Publication Readiness (batched: `A2:H51`, `A52:H101`, continuing in 50-row increments until two consecutive batches return no non-empty rows). Collect the total count.

---

## Step 2 — Write Dashboard content

Use `modify_sheet_values` (USER_ENTERED) on the Dashboard tab.

**a. CE estimate direction (cell B22)**: Review Estimated CE Impact (column I) for all High findings and write one short phrase: `Likely overstated (~1.4x)`, `Likely understated (CE may rise from 8.7x to ~10x)`, `Mixed`, or `Not quantified (no High findings)`. If magnitude is unknown: `Likely overstated (magnitude unclear — see High findings)`.

**b. Findings by sheet table and Sheets not vetted (rows 24 onward)**:

Row 24: column headers — write `Sheet` in A24, `High` in B24, `Medium` in C24, `Low` in D24, `Total` in E24.

Rows 25 onward: one row per unique sheet name found in column B of the Findings sheet (excluding divider rows), in order of first appearance after sorting. Write sheet names as static text in column A. Write counts as `COUNTIFS` formulas that auto-update:
- For a sheet name in Dashboard cell A25: write `=COUNTIFS(Findings!B:B,A25,Findings!D:D,"High")` in B25, `=COUNTIFS(Findings!B:B,A25,Findings!D:D,"Medium")` in C25, `=COUNTIFS(Findings!B:B,A25,Findings!D:D,"Low")` in D25, `=SUM(B25:D25)` in E25.
- Repeat for each sheet name, incrementing row numbers.
- Include `Multiple` as a row if any findings use that sheet name.

After the last sheet row, write a totals row: `Total` in column A, `=SUM(B25:B{last})` in B, same pattern for C–D, `=SUM(E25:E{last})` in E.

After the Total row, skip one blank row, then write `Sheets not vetted:` in column A (bold). On each subsequent row, write one unvetted tab name in column A.

To compute the unvetted list accurately: call `get_spreadsheet_info` on the source spreadsheet to retrieve the complete list of all tabs. Compare that list against the vetted and lite-passed tabs from the session context scope declaration. Any tab not in either list is unvetted — write each on its own row in column A. If every tab in the workbook is covered by vetted or lite-passed, write `None`. Do not rely solely on the session context scope declaration — always verify against the actual workbook tab list.

---

## Step 3 — Write Key Findings summary in chat

Present the following in chat:

```
**Key Findings**

**Vet scope**: Fully vetted: [tab names] | Lite-pass: [tab names or "none"] | Not checked: [remaining tab names or "none"]

[N] model findings: [H] High, [M] Medium, [L] Low — [X] require researcher input
[N] publication-readiness items (separate sheet)

**High findings**
• [Sheet / Cell ref] — [one-sentence description and directional CE impact]
• ...

**Items requiring researcher input**
• [Sheet / Cell ref] — [the specific question the researcher must answer]
• ...
```

Rules:
- Build the Vet scope line using the `get_spreadsheet_info` result from Step 2b: Fully vetted = tabs in session context vetted list; Lite-pass = tabs in session context lite-pass list; Not checked = all remaining tabs in the workbook. Do not write "all tabs" — list the actual tab names (comma-separated) or write "none" only if the list is genuinely empty after comparing against the real workbook tab count.
- List every High finding under "High findings," grouped by sheet. If no High findings, write "No High findings."
- List only items with `✓` in column K (Researcher judgment needed) from the Findings sheet under "Items requiring researcher input" — do not include pub-readiness items here. If none, omit this section.
- Keep each bullet to one sentence — the full detail is in the Findings sheet.
