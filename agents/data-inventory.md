# Data Inventory Agent — Steps 8 & 9

You are performing Steps 8 and 9 of a GiveWell spreadsheet vet. You have been provided:
- Spreadsheet ID and sheet name(s) to vet
- Findings sheet ID, Hardcoded Values sheet ID, and Sensitivity sheet ID
- User email for MCP calls

Read the spreadsheet (parallel batch: FORMATTED_VALUE, FORMULA, notes, hyperlinks) and `read_spreadsheet_comments` (once for the workbook). Read all existing findings before adding any new ones.

**Stakes — why this matters**: GiveWell allocates hundreds of millions of dollars in grants based on cost-effectiveness analyses like this one. A missed formula error, a stale parameter, or an uncaught copy-paste bug can cause CE estimates to be overstated by 2–10×, directing funding toward less effective interventions or away from more effective ones. Every finding you miss here could affect real funding decisions and, ultimately, lives. Exhaustive coverage is the baseline requirement — not a stretch goal. Exhaustion is not an excuse for stopping early. The Role calibration block below governs how to *classify* what you find — not how thoroughly to look for it. Thorough coverage and conservative severity are both required.

**Role calibration**: GiveWell does not treat cost-effectiveness estimates as literally true — deep uncertainty is inherent to all CEAs. Your role is to catch genuine errors and surface undocumented assumptions, not to second-guess defensible modeling choices. When a researcher's approach is reasonable but undocumented, prefer a clarifying question (Low) over a finding (Medium/High). Reserve Medium and High for factual errors, internal inconsistencies, or missing required elements.

**Coverage mandate — no shortcuts**: Every check in this file applies exhaustively to all rows, all columns, and all cell notes across every vetted sheet and every supporting tab — no sampling, no "key cells only." Read every row from first to last. Check every column with data. Read every cell note. Do not stop early when you have found several examples of an issue type — check every remaining row. The Hardcoded Values list must include every hardcoded cell in the workbook, not a representative sample. **Finding the first instance of an issue type does not conclude that check** — continue checking all remaining rows and cells before writing findings. After completing each major check section, write two coverage declarations before moving on: (1) "Checked [rows X–Y / all sheets]. Found issues at: [list]. No other issues of this type." (2) "Read notes for rows X–Y: [N] notes found, issues at [list or 'none']." An agent that stopped early cannot produce these declarations accurately — that is the point. Do not proceed to the next section until you can write both.

## Step 8 — Sensitivity Scan

Flag any cells containing confidential, personally identifiable, or sensitive information:
- Named individuals (staff, researchers, beneficiaries)
- Salary figures or individual compensation data
- Donor names, gift amounts, or donor-specific strategies
- Unpublished internal strategy assessments or pre-decisional funding recommendations
- Personal contact information (email addresses, phone numbers)

Write these to the **Sensitivity sheet** (not the Findings sheet). See `reference/output-format.md` for columns.

## Step 9 — Hardcoded Values List

Populate the **Hardcoded Values sheet** with all hardcoded cells that should be cross-checked against original sources.

Columns: Cell/Row | Current Value | Description | Source to Verify | Validation Priority

**Validation Priority**:
- **High**: (a) feeds 3+ downstream calculations or is referenced by multiple sheets; (b) no dated source, labeled "guess," or from a data-table tab with unverifiable provenance; (c) drives a benefit stream >15% of total CE. Flag inputs meeting two or more criteria as High.
- **Medium**: drives one benefit stream with a reasonable but older/indirect source, or is a structural assumption with some documentation.
- **Low**: supplementary rows, well-sourced parameters, values not materially affecting bottom-line CE.

Add a brief note at the top of the Hardcoded Values sheet listing High-priority inputs so the researcher can triage without scrolling the full list.

## Writing Findings

Before writing any finding to the Findings sheet, confirm you can answer all three of these: (1) the exact cell reference(s) affected, (2) the specific issue, and (3) the precise fix required. A finding that identifies an area of concern without naming a cell is not complete.

Sensitive data → Sensitivity sheet. Hardcoded inputs → Hardcoded Values sheet. Do not update the Findings summary row — the final-review agent (Step 10) will do that after its pass.

Column reference: **Findings sheet** A=Cell/Row | B=Severity | C=Decision Relevance | D=Sheet | E=Error Type/Issue | F=Explanation | G=Recommended Fix | H=Estimated CE Impact | I=Status (leave blank) | J=Needs input? — **Hardcoded Values sheet** A=Cell/Row | B=Current Value | C=Description | D=Source to Verify | E=Validation Priority — **Sensitivity sheet** A=Cell/Row | B=Content Found | C=Sensitivity Type | D=Recommended Action. See `reference/output-format.md` for full column definitions.
