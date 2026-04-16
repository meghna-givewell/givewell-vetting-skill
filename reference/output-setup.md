# Output Spreadsheet Setup

Create the output spreadsheet using `create_spreadsheet` titled `Vetting Findings — <Workbook Name> — <Date>`. Share the link with the user immediately after creation so they can monitor progress.

## Tabs and Headers

Create six tabs with these header rows (row 1) before spawning agents:

**Dashboard** — leave blank at creation; content written by final-review agents.

**CE Baseline** — columns: `Geography/Scenario | Cost-Effectiveness`. Write the baseline CE table from Step 0, one row per geography/scenario.

**Findings** — columns A–L: `Finding # | Sheet | Cell/Row | Severity | Error Type/Issue | Current Formula/Value | Explanation | Recommended Fix | Changes CE? | Estimated CE Impact | Researcher judgment needed | Status`
- Column A (`Finding #`): left blank by agents — assigned by final-review-compaction
- Column F (`Current Formula/Value`): the formula or hardcoded value currently in the problematic cell; left blank for style/readability findings
- Column I (`Changes CE?`): mark ✓ if correcting the finding changes the bottom-line CE multiple; blank otherwise
- Column L (`Status`): left blank — researcher fills in (Open / Fixed / Won't Fix / Needs Discussion)

**Publication Readiness** — columns A–G: `Finding # | Sheet | Cell/Row | Error Type/Issue | Explanation | Recommended Fix | Status`
- Column A (`Finding #`): left blank by agents — assigned by final-review-compaction
- Column G (`Status`): left blank for researcher

**Hardcoded Values** — columns A–G: `Sheet | Cell | Category | Current Value | Description | Source to Verify | Verified?`
- Column A (`Sheet`): tab name only (e.g., `Main CEA`)
- Column B (`Cell`): cell reference only (e.g., `C14`)
- Column C (`Category`): one of `GiveWell Parameter`, `Study-Derived`, `Org-Reported`, `Structural`
- Column G (`Verified?`): left blank — researcher fills in (Yes / No / In Progress)

**Confidentiality Flags** — columns A–D: `Cell/Row | Content Found | Sensitivity Type | Recommended Action`

## Formatting Batch

Fire all formatting in a single parallel batch immediately after writing headers:

- `add_conditional_formatting`: Severity D3:D1000 on Findings — High → `#FFB3B3`, Medium → `#FFE5B3`, Low → `#B3D9B3`
- `add_conditional_formatting`: Changes CE? I3:I1000 on Findings — if value = `✓`, background → `#FFFF99`
- `add_conditional_formatting`: Researcher judgment needed K3:K1000 on Findings — if value = `✓`, background → `#FFFF99`
- `add_conditional_formatting`: Status L3:L1000 on Findings — `Fixed` → `#B3D9B3`, `Won't Fix` → `#E0E0E0`
- `add_conditional_formatting`: Section dividers A2:L1000 on Findings — CUSTOM_FORMULA `=ISNUMBER(SEARCH("───",$B2))`, background `#D9D9D9`
- `format_sheet_range`: header row 1 on Findings (A1:L1) — dark blue `#1F4E79`, white text, bold; freeze row 1 and columns A–C
- `format_sheet_range`: header row 1 on Publication Readiness (A1:G1) — dark blue `#1F4E79`, white text, bold; freeze row 1 and columns A–C
- `format_sheet_range`: header row 1 on Hardcoded Values (A1:G1) — dark blue `#1F4E79`, white text, bold
- `add_conditional_formatting`: Category C2:C1000 on Hardcoded Values — `GiveWell Parameter` → `#D9E1F2`, `Study-Derived` → `#E2EFDA`, `Org-Reported` → `#FFF2CC`, `Structural` → `#EDEDED`
- `add_conditional_formatting`: Dashboard B24:D24 — `High` → `#FFB3B3`, `Medium` → `#FFE5B3`, `Low` → `#B3D9B3`
- `format_sheet_range`: header row 1 on CE Baseline (A1:B1) — dark blue `#1F4E79`, white text, bold
- `format_sheet_range`: header row 1 on Confidentiality Flags (A1:D1) — dark blue `#1F4E79`, white text, bold
- `format_sheet_range`: column widths on Findings — A=80, B=120, C=120, D=100, E=140, F=200, G=220, H=400, I=100, J=150, K=100, L=120
- `format_sheet_range`: column widths on Publication Readiness — A=80, B=120, C=120, D=140, E=220, F=300, G=120
- `format_sheet_range`: text wrap on columns F, G, H, J of Findings; text wrap on columns E, F of Publication Readiness; row height rows 2:1000 on Publication Readiness → 60px
- `format_sheet_range`: row height rows 2:1000 on Findings → 80px; same on Publication Readiness
- Data validation (skip gracefully if unsupported): Severity D on Findings → dropdown `High,Medium,Low`; Error Type/Issue E on Findings → dropdown `Formula Error,Parameter Issue,Adjustment Issue,Assumption Issue,Structural Issue,Inconsistency`; Status L on Findings → dropdown `Open,Fixed,Won't Fix,Needs Discussion`; Error Type/Issue D on Publication Readiness → dropdown `Missing Source,Broken Link,Permission Issue,Readability,Terminology`; Status G on Publication Readiness → dropdown `Open,Fixed,Won't Fix,Needs Discussion`
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
- A10: `Total findings` | B10: `=COUNTA(Findings!D2:D1000)`
- A11: `Issues impacting bottom-line CE` | B11: `=COUNTIF(Findings!I:I,"✓")` *(column I = Changes CE? ✓)*
- A13: `PUBLICATION READINESS`
- A14: `Total items` | B14: `=COUNTA('Publication Readiness'!B2:B1000)`
- A15: `Missing Source` | B15: `=COUNTIF('Publication Readiness'!D:D,"Missing Source")`
- A16: `Readability` | B16: `=COUNTIF('Publication Readiness'!D:D,"Readability")+COUNTIF('Publication Readiness'!D:D,"Template Language")`
- A17: `Internal Reference` | B17: `=COUNTIF('Publication Readiness'!D:D,"Internal Reference")`
- A19: `CONFIDENTIALITY FLAGS`
- A20: `Total items` | B20: `=COUNTA('Confidentiality Flags'!A2:A1000)`
- A22: `CE estimate direction:` *(leave B22 blank — final-review-dashboard writes here)*
- *(rows 24 onward reserved — final-review-dashboard writes the findings-by-sheet table, then `Sheets not vetted:` two rows below the Total row)*

Then format the Dashboard: bold A1, A6, A13, A19, A22; column A width 260, column B width 80. Static background colors: A7 `#FFB3B3`, A8 `#FFE5B3`, A9 `#B3D9B3`.
