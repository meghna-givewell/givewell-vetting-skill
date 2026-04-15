# Evaluation Guide — Comparing Claude's Vet Against a Human Vet

Use this when scoring Claude's performance against a human vet of the same workbook.

---

## Step 1 — Access the Human Vet Record

**Read threaded comments, not just cell notes.** Human vetters leave their findings as threaded comments in the post-vet spreadsheet copy. Use `read_spreadsheet_comments` on that copy — do not use `read_sheet_notes`. A post-vet copy with no cell notes may still have 20+ findings in threaded comments. Never assume cell notes are the canonical record.

Confirm you have the correct post-vet copy: it should contain resolved threads from a human reviewer with replies from the researcher. If you only see sparse cell notes and no threads, ask the user for the correct link before scoring.

---

## Step 2 — Score Each Human Finding

For each finding in the human vet:

- **Caught (✓)**: Claude identified the same cell/issue and correctly characterized it.
- **Partial (~)**: Claude flagged the right area but missed specifics, or identified a symptom but not the root cause. Counts **fully** toward recall — same weight as ✓. The partial sub-columns in the tracker are diagnostic, not a recall penalty.
- **Missed (✗)**: Claude did not flag it.

---

## Step 3 — Score Claude-Only Findings

For each Claude finding not present in the human vet:

- **V — Valid catch**: A real issue the human missed. Confirm with researcher or Brendan if unsure.
- **F — False positive**: Not actually an issue.
- **U — Uncertain**: Requires researcher input to classify. Excluded from both numerator and denominator of the precision calculation.

---

## Finding Types

- **D — Decision-relevant**: Correcting it would change the bottom-line CE estimate by ≥5%, OR it is a clear factual error (wrong external parameter, broken reference, confirmed formula bug) whose CE impact is plausibly material. Default to H when CE impact is uncertain.
- **H — Heads-up**: Valid issues with structure, reasoning, or documentation — questionable assumptions, undocumented deviations, plausibility concerns, findings whose CE impact requires researcher confirmation.
- **O — Other**: Legibility, sourcing, notes, label text, readability — valid but no impact on calculations or analytical framing.

**D vs. H rule**: CE impact drives the tier, not finding type. A formula error with trivial CE impact is H. A modeling choice that moves CE by 10% is D. The ≥5% threshold is primary, not a tiebreaker.

---

## Formulas

- **D-recall** = D findings caught (✓ or ~) ÷ total D findings in human vet
- **H-recall** = H findings caught (✓ or ~) ÷ total H findings in human vet
- **O-recall** = O findings caught ÷ total O findings in human vet
- **Precision** = (total Claude findings − F − U) ÷ (total Claude findings − U)

**Precision threshold**: Only apply the 70% target when (total Claude findings − U) ≥ 8. Below that, report raw V/F/U counts in Notes and mark Precision as "n/a (small sample)."

---

## Thresholds (targets for RLT case)

| Metric | Target |
|--------|--------|
| D-recall | ≥ 90% |
| H-recall | ≥ 80% |
| Precision | ≥ 70% *(when non-U findings ≥ 8)* |

---

## Tracker

**Spreadsheet ID:** `10oaatfSyw_eHhNRN-sIfo6I1z4Yn6iDwOcw5KYvHfmU`

Write a new row to the **Log** sheet using `modify_sheet_values`. **All values must be strings** — pass `"5"` not `5`; integer values cause validation errors.

| Col | Field | Notes |
|-----|-------|-------|
| A | # | Row number |
| B | Workbook name | |
| C | Spreadsheet type | VOI / top-charity CEA / newer-intervention CEA / other |
| D | Findings sheet link | URL to Claude's Findings Sheet |
| E | D findings (human) | Count |
| F | D caught by Claude | Count (includes partials) |
| G | D partials | Count of ~ findings |
| H | D-recall % | Write as formula: `=IF(E19="","",IF(E19=0,"N/A",F19/E19))` |
| I | H findings (human) | |
| J | H caught by Claude | |
| K | H partials | |
| L | H-recall % | Formula |
| M | O findings (human) | |
| N | O caught by Claude | |
| O | O-recall % | Formula |
| P | Claude-only findings | Total count of Claude findings not in human vet |
| Q | False positives | Count of F findings |
| R | Uncertain findings | Count of U findings |
| S | Precision % | Formula: `=(P19-Q19-R19)/(P19-R19)` or "n/a (small sample)" |
| T | Valid catches (V) | Count of Claude-only V findings |
| U | Researcher-to-confirm | Claude findings flagged Needs input? ✓ |
| V | Notes | Vet scope, key misses, valid catches summary |

Write recall/precision columns as `value_input_option: USER_ENTERED` so formulas auto-calculate.

Also write each individual human finding to the **Human Findings** sheet (columns: Vet # | Workbook | Type | Description | Cell/Location | Status).

---

## Scope alignment note

Human vets and Claude vets often cover different tabs. Before scoring, note which tabs each vet covered and flag any findings that were outside Claude's declared scope — these are missed by design, not by error, and should be distinguished in the Notes column from genuine misses within scope.
