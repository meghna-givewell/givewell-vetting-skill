# Final Review — Step 10c: Dashboard Agent

You are performing Step 10c of a GiveWell spreadsheet vet. This is the last of three sequential final-review steps. Compaction (10a) and validation (10b) are already complete and Finding IDs are assigned. You have been provided:
- Output spreadsheet ID (the spreadsheet containing Dashboard, Findings, Publication Readiness tabs)
- Session context scope declaration (which tabs were fully vetted, lite-passed, not checked)
- User email for MCP calls

**Do not read the source spreadsheet.** Your job is to write the Dashboard and present the Key Findings summary in chat.

---

## Step 1 — Read findings for summary

Read all non-divider rows from the Findings sheet (batched: A2:L200, A201:L400, continuing until empty). Collect: all High findings (for Key Findings summary), all findings with `✓` in column K (Needs input?), and the count of High/Medium/Low findings.

Read all rows from Publication Readiness (batched: A2:H200, continuing until empty). Collect the total count.

---

## Step 2 — Write Dashboard content

Use `modify_sheet_values` (USER_ENTERED) on the Dashboard tab.

**a. CE estimate direction (cell B22)**: Write a short phrase stating direction and estimated magnitude of misstatement. Review Estimated CE Impact (column J) for all High findings:
- If correcting them would raise CE → current estimate is understated
- If correcting them would lower CE → current estimate is overstated
- If both directions → write "Mixed"
- If no High findings → write "Not quantified (no High findings)"

Include a magnitude estimate drawn from column J values — e.g., `Likely overstated (~1.4x)` or `Likely understated (CE may rise from 8.7x to ~10x)`. If magnitude is unknown: `Likely overstated (magnitude unclear — see High findings)`.

**b. Findings by sheet table and Sheets not vetted (rows 24 onward)**:

Row 24: column headers — write `Sheet` in A24, `High` in B24, `Medium` in C24, `Low` in D24, `Total` in E24.

Rows 25 onward: one row per unique sheet name found in column B of the Findings sheet (excluding divider rows), in order of first appearance after sorting. Write sheet names as static text in column A. Write counts as `COUNTIFS` formulas that auto-update:
- For a sheet name in Dashboard cell A25: write `=COUNTIFS(Findings!B:B,A25,Findings!D:D,"High")` in B25, `=COUNTIFS(Findings!B:B,A25,Findings!D:D,"Medium")` in C25, `=COUNTIFS(Findings!B:B,A25,Findings!D:D,"Low")` in D25, `=SUM(B25:D25)` in E25.
- Repeat for each sheet name, incrementing row numbers.
- Include `Multiple` as a row if any findings use that sheet name.

After the last sheet row, write a totals row: `Total` in column A, `=SUM(B25:B{last})` in B, same pattern for C–D, `=SUM(E25:E{last})` in E.

After the Total row, skip one blank row, then write `Sheets not vetted:` in column A and a comma-separated list of tabs not checked at all in column B. Write `None` if all tabs were vetted or lite-passed. Pull from the session context scope declaration.

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
- Pull the Vet scope line from the session context scope declaration. If no scope restriction was declared: "Fully vetted: all tabs | Lite-pass: none | Not checked: none."
- List every High finding under "High findings," grouped by sheet. If no High findings, write "No High findings."
- List only items with `✓` in column K (Needs input?) from the Findings sheet under "Items requiring researcher input" — do not include pub-readiness items here. If none, omit this section.
- Keep each bullet to one sentence — the full detail is in the Findings sheet.
