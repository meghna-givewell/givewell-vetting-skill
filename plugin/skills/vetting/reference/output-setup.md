# Output Spreadsheet Setup

Create the output spreadsheet using `create_spreadsheet` titled `Vetting Findings — <Workbook Name> — <Date>`. Share the link with the user immediately after creation so they can monitor progress.

## Tabs and Headers

Create six tabs with these header rows (row 1) before spawning agents:

**Dashboard** — leave blank at creation; content written by final-review agents.

**CE Baseline** — columns: `Geography/Scenario | Cost-Effectiveness`. Write the baseline CE table from Step 0, one row per geography/scenario.

**Findings** — columns A–H: `Finding # | Sheet | Cell/Row | Severity | Error Type/Issue | Explanation | Recommended Fix | Estimated CE Impact`
- Column A (`Finding #`): left blank by agents — assigned by final-review-compaction

**Publication Readiness** — columns A–F: `Finding # | Sheet | Cell/Row | Error Type/Issue | Explanation | Recommended Fix`
- Column A (`Finding #`): left blank by agents — assigned by final-review-compaction

**Hardcoded Values** — columns A–H: `Sheet | Cell | Category | Current Value | Description | Source to Verify | Verified? | Auto-check evidence`
- Column A (`Sheet`): tab name only (e.g., `Main CEA`)
- Column B (`Cell`): cell reference only (e.g., `C14`)
- Column C (`Category`): one of `Study-Derived`, `Org-Reported`
- Column G (`Verified?`): pre-filled by source-citation-verify agent (Wave 1.5) with `Matched ✓` / `Contradicted ✗` / `Could not verify`; researcher confirms or overrides
- Column H (`Auto-check evidence`): verbatim sentence from source via Citations API, or reason verification was not possible; filled by source-citation-verify agent

**Confidentiality Flags** — columns A–D: `Cell/Row | Content Found | Sensitivity Type | Recommended Action`

## Pre-Expand Grid

Immediately after writing headers, before the formatting batch, write a single blank value to `Findings!A2000` and `'Publication Readiness'!A2000` using `modify_sheet_values`. This forces both sheets to allocate 2000 rows and prevents `modify_sheet_values` silent failures when agents write findings beyond the Google Sheets default 1000-row grid.

**Note**: Staging tab pre-expansion is handled separately — see the staging-tab setup instructions in SKILL.md (the Wave 0 / pre-spawn checklist). An implementation that follows only output-setup.md will skip the staging-tab pre-expansion step, which risks silent 1000-row truncation when Wave 1 agents write findings.

## Formatting Batch

Fire all formatting in a single parallel batch immediately after writing headers:

- `add_conditional_formatting`: Severity D2:D2000 on Findings — High → `#FFB3B3`, Medium → `#FFE5B3`, Low → `#B3D9B3`
- `add_conditional_formatting`: Section dividers A2:H2000 on Findings — CUSTOM_FORMULA `=ISNUMBER(SEARCH("───",$B2))`, background `#D9D9D9`
- `format_sheet_range`: header row 1 on Findings (A1:H1) — dark blue `#1F4E79`, white text, bold; freeze row 1 and columns A–C
- `format_sheet_range`: header row 1 on Publication Readiness (A1:F1) — dark blue `#1F4E79`, white text, bold; freeze row 1 and columns A–C
- `format_sheet_range`: header row 1 on Hardcoded Values (A1:H1) — dark blue `#1F4E79`, white text, bold
- `add_conditional_formatting`: Category C2:C1000 on Hardcoded Values — `Study-Derived` → `#E2EFDA`, `Org-Reported` → `#FFF2CC`
- `add_conditional_formatting`: Dashboard B24:D60 — `High` → `#FFB3B3`, `Medium` → `#FFE5B3`, `Low` → `#B3D9B3`
- `format_sheet_range`: header row 1 on CE Baseline (A1:B1) — dark blue `#1F4E79`, white text, bold
- `format_sheet_range`: header row 1 on Confidentiality Flags (A1:D1) — dark blue `#1F4E79`, white text, bold
- `format_sheet_range`: column widths on Findings — A=80, B=120, C=120, D=100, E=140, F=290, G=400, H=150
- `format_sheet_range`: column widths on Publication Readiness — A=80, B=120, C=120, D=140, E=220, F=300
- `format_sheet_range`: text wrap on columns F, G of Findings; text wrap on columns E, F of Publication Readiness
- `format_sheet_range`: row height rows 2:2000 on Findings → 80px; same on Publication Readiness
- Data validation (skip gracefully if unsupported): Severity D on Findings → dropdown `High,Medium,Low`; Error Type/Issue E on Findings → dropdown `Formula,Parameter,Adjustment,Assumption,Inconsistency,Legibility`; Error Type/Issue D on Publication Readiness → dropdown `Sourcing,Box Link,Legibility`
- Tab colors (skip gracefully if unsupported): Dashboard → `#595959`, CE Baseline → `#7F7F7F`, Findings → `#C00000`, Publication Readiness → `#E6B800`, Hardcoded Values → `#2F75B6`, Confidentiality Flags → `#7030A0`

## Dashboard Content

Write immediately after the formatting batch using `modify_sheet_values` (USER_ENTERED) on the Dashboard tab:

- A1: `VETTING DASHBOARD`
- A3: `Source spreadsheet:` | B3: `=HYPERLINK("<source_spreadsheet_url>","<Workbook Name>")`
- A4: `Grant page:` | B4: `=HYPERLINK("<grant_page_url>","<Grant Doc Title>")` — write only if a grant page was provided in Step 0.5; omit A4/B4 entirely otherwise
- A5: `Vet date:` | B5: today's date
- A6: `MODEL FINDINGS`
- A7: `High` | B7: `=COUNTIF(Findings!D:D,"High")`
- A8: `Medium` | B8: `=COUNTIF(Findings!D:D,"Medium")`
- A9: `Low` | B9: `=COUNTIF(Findings!D:D,"Low")`
- A10: `Total findings` | B10: `=B7+B8+B9`
- A11: `Issues impacting bottom-line CE` | B11: `=COUNTIF(Findings!H:H,"Raises CE*")+COUNTIF(Findings!H:H,"Lowers CE*")+COUNTIF(Findings!H:H,"Direction unknown")` *(column H = Estimated CE Impact; excludes "No CE impact" and blank)*
- A13: `PUBLICATION READINESS`
- A14: `Total items` | B14: `=COUNTA('Publication Readiness'!B2:B2000)`
- A15: `Sourcing` | B15: `=COUNTIF('Publication Readiness'!D:D,"Sourcing")`
- A16: `Legibility` | B16: `=COUNTIF('Publication Readiness'!D:D,"Legibility")`
- A17: `Box Link` | B17: `=COUNTIF('Publication Readiness'!D:D,"Box Link")`
- A19: `CONFIDENTIALITY FLAGS`
- A20: `Total items` | B20: `=COUNTA('Confidentiality Flags'!A2:A1000)`
- A22: `CE estimate direction:` *(leave B22 blank — final-review-dashboard writes here)*
- *(rows 24 onward reserved — final-review-dashboard writes the findings-by-sheet table, then `Sheets not vetted:` two rows below the Total row)*

Then format the Dashboard: bold A1, A6, A13, A19, A22; column A width 260, column B width 80. Static background colors: A7 `#FFB3B3`, A8 `#FFE5B3`, A9 `#B3D9B3`.

**Reserved — vet metadata block (rows 150–153)**: Do not write anything to these rows during output setup. They are written by the orchestrator after Step 2 (see SKILL.md "Write vet metadata") and read by the `/vetting-finalize` skill for Wave 3 recovery. Row 150 = header; B151 = fully vetted tabs; B152 = lite-pass tabs; B153 = vet scope.
