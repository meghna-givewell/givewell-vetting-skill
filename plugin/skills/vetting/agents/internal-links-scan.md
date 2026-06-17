# Internal Links Scan Agent — Wave 2

You are performing an internal links scan as part of a GiveWell spreadsheet vet. Your job is to scan every cell, cell note, and hyperlink across all vetted sheets for Box links and internal Google Drive/Docs/Sheets/Presentation links that may require publish-permission verification before the spreadsheet is made public.

**Write to your staging sheet only** — the compaction agent routes findings to Publication Readiness based on Error Type. Do not write to the Findings sheet or directly to the Publication Readiness sheet.

**Do not invoke any skills or load additional context files other than `reference/pitfalls.md`, which you must read before starting using the Read tool.**

---

## What to flag

Flag every URL matching one of these patterns:

| Category | URL pattern | Error Type |
|---|---|---|
| Box link | Any URL containing `box.com` (e.g. `givewell.app.box.com`, `app.box.com`, `givewell.box.com`) | `Box Link` |
| Internal Google Doc | `docs.google.com/document/d/` | `Sourcing` |
| Internal Google Sheet | `docs.google.com/spreadsheets/d/` | `Sourcing` |
| Internal Google Presentation | `docs.google.com/presentation/d/` | `Sourcing` |
| Internal Google Drive file | `drive.google.com/file/d/` | `Sourcing` |

**Do NOT flag:**
- The source spreadsheet itself or the output spreadsheet — their IDs are in session context; exclude any Google Sheets URL whose ID matches either
- URLs where the hyperlink display text, cell note text, or nearby description contains "(public)" (case-insensitive) — these are intentionally published
- Well-known public external sources: journal URLs (pubmed.ncbi.nlm.nih.gov, bmj.com, thelancet.com, doi.org, etc.), WHO, UNICEF, IHME/GBD, DHS Statcompiler, givewell.org, statcompiler.com, github.com, worldbank.org — these are not internal documents
- givewell.org links — these are already public

---

## Step 1 — Read all vetted sheets

For each vetted sheet, fire all of the following in a **single parallel batch** — do not read sheets sequentially:

- `read_sheet_hyperlinks` — finds all embedded hyperlink URLs across all cells
- `read_sheet_notes` — finds all cell notes; scan each note for URLs matching the above patterns
- `read_sheet_values` (FORMATTED_VALUE) — scan all cell values for plain-text URLs matching the above patterns (e.g. a URL typed directly into a cell rather than attached as a hyperlink)

Use the full sheet range (e.g. `'Main CEA'!A1:Z1000`). If any sheet has more than 1000 populated rows, extend the range accordingly.

Also call `read_spreadsheet_comments` once for the whole workbook and scan comment text for URLs matching the above patterns.

---

## Step 2 — Extract and record flagged URLs

For each URL found, record:
- **Sheet name**
- **Cell reference** (e.g. `B14`)
- **Where found**: `hyperlink`, `cell note`, `cell value`, or `comment`
- **Full URL**
- **Display text or note context** (the label or surrounding text, if any)

**Grouping rule**: When the same URL appears in multiple cells (e.g. the same Box link in a shared-formula column C, D, and E), group them into a single entry listing all cell references (e.g. `C14, D14, E14`). Do not write one finding row per cell for the same URL.

**Overlap with sources agent**: The sources agent scans the Notes column (column F) for Box and Google Drive URLs. Some findings here may duplicate sources-agent findings. This is expected — the compaction agent deduplicates. Do not skip scanning the Notes column here; your coverage extends to every cell, not just column F.

---

## Step 3 — Mandatory declaration table

After completing the full scan for all sheets, write the following declaration table to chat **before** writing any findings to your staging sheet. Fill in every line. If a category has no instances, write "none."

```
Internal links scan complete.
pitfalls.md read and applied [___]
Sheet(s) scanned: [list all sheet names]
Source spreadsheet ID excluded: [ID from session context]
Output spreadsheet ID excluded: [ID from session context]

Box links found: [N] (cells: [list])
Internal Google Docs found: [N] (cells: [list])
Internal Google Sheets found: [N] (cells: [list, excluding source/output IDs])
Internal Presentations found: [N] (cells: [list])
Internal Drive files found: [N] (cells: [list])
Comment-thread URLs found: [N]
Total flagged entries: [N]
```

---

## Step 4 — Write findings to staging sheet

Write all findings to your staging sheet starting at row 2. Use the standard 9-column layout (columns A–I), leaving column D (Severity) and column H (Estimated CE Impact) blank — all findings from this agent are Publication Readiness items.

Column reference: **A** Finding # (leave blank) | **B** Sheet | **C** Cell/Row | **D** Severity (leave blank) | **E** Error Type/Issue (`Box Link` or `Sourcing`) | **F** Explanation (3 sentences max, aim for 2; state what was found and why it needs review in plain language) | **G** Recommended Fix (one sentence: "Verify this [document / Box file] is publicly accessible before publishing. If it cannot be made public, replace with an external citation or remove the link.") | **H** Estimated CE Impact (leave blank) | **I** Status (leave blank — reconcile agent writes WONT_FIX here; compaction strips column I when writing to the final Findings sheet)

**Explanation wording**:
- For Box links: `Box link at [ref] ([cell note context if available]) requires publish-permission verification before publication.`
- For Google Sheets: `Internal Google Sheet at [ref] (title: "[title if retrievable, else document ID]") requires publish-permission or replacement with a public link before publication.`
- For Google Docs / Presentations / Drive files: `Internal Google [Doc/Presentation/Drive file] at [ref] requires publish-permission verification before publication.`

**Batch by URL**: Write one finding row per unique URL (listing all cells in column C). Do not write one row per cell when the same URL appears in multiple cells.

---

## Final step — write completion marker

After all findings are written, write ONE final row to your staging sheet immediately after your last finding (or at row 2 if no findings were written). This is the absolute last action you take.

Write the row with:
- Column B: `internal-links-scan`
- Column D: `AGENT_COMPLETE`
- Column F: `COVERAGE_ROWS: all rows, all vetted sheets | Staging sheet: [name from session context]. Filed [K] findings in rows 2–[K+1]. Box: [N] | Google Sheets: [N] | Google Docs: [N] | Presentations: [N] | Drive files: [N] | zero-findings reason: [brief statement if K=0, e.g., "no Box or internal Google Drive links found in any vetted sheet"]`
- All other columns: blank

Use a single `modify_sheet_values` call.
