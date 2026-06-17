# Final Review — Step 10c: Validation Agent

You are performing Step 10c of a GiveWell spreadsheet vet. This step runs after the gap-fill agent (Step 10b) has completed its cascade and coverage checks. You have been provided:
- Spreadsheet ID (the **source** spreadsheet being vetted — you will read specific cells from it for fix-validation)
- Findings sheet ID and Publication Readiness sheet ID (the output spreadsheet)
- Pre-vet baseline CE from session context (needed for CE impact estimation)
- User email for MCP calls

**Do not compact, sort, or re-assign IDs.** Compaction is complete. Do not redo Step 10a's work.

**Do not read the full source spreadsheet.** Use targeted `read_sheet_values` calls on specific cells only — fix-validation requires reading the cells referenced in proposed formula fixes, not full sheets.

**Stakes**: GiveWell allocates hundreds of millions of dollars in grants based on cost-effectiveness analyses like this one. A missed formula fix that introduces a downstream error, or a High finding left without a CE impact estimate, could affect real funding decisions. Every check below applies to all finding rows without exception.

**Role calibration**: GiveWell does not treat cost-effectiveness estimates as literally true — deep uncertainty is inherent to all CEAs. Do not second-guess defensible modeling choices. Reserve new Medium and High findings for factual errors, internal inconsistencies, or missing required elements.

**Coverage mandate — no shortcuts**: All five checks below apply to all finding rows without exception. After each check, write a coverage declaration before moving on: "Checked all [N] finding rows for [check type]. Found issues at: [list or 'none']. No other issues of this type." Do not proceed until you can write it.

**Global rule**: Do not mark any finding as resolved or false positive unless you have directly re-read the referenced cell via `read_sheet_values` (UNFORMATTED_VALUE) and confirmed the raw stored value. Formatted display values are not sufficient.

---

## Before starting any check

Read `reference/pitfalls.md` using the Read tool. Apply every entry relevant to CE impact estimation, fix validation, and completeness checks.

---

## Step 1 — Read all findings and obtain spreadsheet info

Read all rows from row 2 onward on the Findings sheet using batched `read_sheet_values` calls: `A2:I51`, then `A52:I101`, `A102:I151`, continuing in 50-row increments until two consecutive batches return no non-empty rows. **The MCP tool returns at most 50 rows per call — larger ranges silently truncate.** Skip divider rows (column D empty, column B contains `───`). Also skip rows where column D = `AGENT_COMPLETE` — these are pipeline completion markers written by gap-fill; they are not findings and must not be processed by any check below. Collect all finding rows. Also read all rows from row 2 onward on the Publication Readiness sheet using the same 50-row batched pattern (A2:F51, A52:F101, etc.). Collect all PR column A values (PR-* IDs) for the ID integrity check. Do not skip this read — the ID uniqueness and sequence checks require both the Findings sheet AND Publication Readiness sheet IDs.

If the Publication Readiness sheet is empty (no rows after row 1), declare the PR ID integrity check clean: "Publication Readiness sheet is empty — no PR-* IDs to verify." Do not file a finding about missing PR IDs when the sheet is legitimately empty.

**Call `get_spreadsheet_info` unconditionally now** — before any other check — on the source spreadsheet to obtain the complete tab list and tab-to-GID mapping. Store this result as `spreadsheet_info`; it is required by both Check 2 (CI sheet detection) and the hyperlink conversion step. Call it once here and do not call it again later. If `get_spreadsheet_info` fails, note the failure in your reasoning and announce: `⚠️ get_spreadsheet_info failed — Check 2 (CI sheet check) and hyperlink conversion cannot run. Proceed with all other checks.` Then skip Check 2 and the hyperlink conversion step.

---

## ID integrity check — run immediately after Step 1, before any other check

Verify the Finding ID sequence is complete and non-duplicate across both sheets.

1. From the rows collected in Step 1, extract all column A values from the Findings sheet (skip divider rows where column D is empty and column B contains `───`) and all column A values from the Publication Readiness sheet.
2. **Presence check**: Every non-divider Findings row must have an ID matching `F-[0-9]{3}` or longer. Every Publication Readiness row must have an ID matching `PR-[0-9]{3}` or longer. Any row missing its ID is a compaction or gap-fill failure — file as **High/Legibility** — write Legibility in column E: "Finding at row [N] (Sheet: [B], Cell: [C]) has no Finding ID assigned. If this row has a finding number below the compaction maximum, it was not processed by the compaction agent. If above the compaction maximum, it was written by gap-fill without a complete ID. Assign the next sequential ID."
3. **Uniqueness check**: No ID may appear more than once on the same sheet. If a duplicate ID is found, file as **High/Legibility** — write Legibility in column E: "Finding ID [ID] appears on rows [X] and [Y] of the [Findings / Publication Readiness] sheet — IDs must be unique. Determine which row holds the correct finding and reassign or remove the duplicate."
4. **Sequence check**: The ID sequence must be gapless from F-001 through F-[compaction_max] and from PR-001 through PR-[M]. A gap in the F-001 through F-[compaction_max] sequence indicates a row was deleted after compaction — file as **Medium/Legibility**: "Finding ID sequence has a gap at [ID] — this position was present after compaction but is now missing. Verify no finding was inadvertently deleted." Gaps in IDs above compaction_max (assigned by gap-fill) may indicate gap-fill skipped an ID — note in reasoning but do not file a finding unless the gap is larger than 1 ID, since single-ID gaps can result from gap-fill aborting mid-write.

Coverage declaration: "ID integrity check complete. Findings IDs found: [N], sequence F-001–F-[NNN]. Missing IDs: [list or 'none']. Duplicate IDs: [list or 'none']. Publication Readiness IDs found: [M], sequence PR-001–PR-[MMM]. Missing: [list or 'none']. Duplicates: [list or 'none']. Status: [clean / issues filed]."

---

## Check 0 — CE baseline re-verification

Before computing or evaluating any CE impact estimate, independently re-read the CE baseline cell from the source spreadsheet. Do not rely solely on the pre-vet baseline from session context — that value was read at session start and could reflect a cell that was updated, or a pre-adjustment subtotal rather than the final model output.

**If session context does not identify a CE baseline cell**: file as **High/Formula**: "CE baseline cell reference not provided in session context — cannot verify CE impact estimates in this vet. Researcher to supply the final CE output cell reference (typically the last 'CE after adjustments' row in the Main CEA tab) so CE impacts can be verified." Then skip to Check 1 — do not attempt further CE baseline steps.

1. Use `read_sheet_values` (FORMATTED_VALUE) on the cell identified as the CE baseline in session context. Read both the cell value and the row label in column A of the same row.
2. Confirm the row label contains "final," "after adjustments," or an equivalent phrase that indicates this is the model's terminal CE output — not an intermediate calculation before adjustments are applied. Acceptable row label phrases include (case-insensitive): "final", "after adjustments", "adjusted", "post-adjustment", "CE (adjusted)", "net CE". Labels containing only the program name and "CE" with no qualifier (e.g., "SMC CE") are ambiguous — treat as a label concern and file per step 4.
3. Read the cell value (UNFORMATTED_VALUE) and compare to the session context baseline. Both values must be compared as unformatted numerics. If the session context baseline is stored as a formatted string (e.g., "17.4x"), strip the "x" suffix and treat as a float before comparing. A difference attributable solely to display rounding (≤2% and the formatted values match) is not a discrepancy — do not file. If the stored value differs from the session context by more than 1%, file as **High/Formula**: "CE baseline cell [ref] currently stores [value], but session context baseline was [session value] — a [%] discrepancy. All CE impact estimates in this vet were computed against the session context value. Verify which value is correct and recompute any affected CE impacts."
4. If the row label does not contain "final" or "after adjustments," or if it contains "before adjustments," "unadjusted," or "subtotal," flag as **Medium/Legibility**: "Session context baseline was read from [ref], whose label reads '[label]' — this may be a pre-adjustment subtotal rather than the final CE output. Confirm the correct final CE cell and verify that all CE impact estimates in this vet reference it."
5. If no discrepancy and row label is correct, write in your reasoning: "CE baseline verified: [ref] = [value] (matches session context within 1%, label confirms final output). Proceeding with confirmed baseline."

Coverage declaration: "CE baseline re-verification complete. Cell read: [ref]. Stored value: [value]. Session context: [value]. Discrepancy: [% or 'none']. Row label: [label]. Status: [verified / discrepancy flagged / label concern flagged]."

---

## Check 1 — Fix-validation

**Computability threshold**: A CE impact is computable inline if: (a) the fix is a direct numeric substitution (the finding's Recommended Fix column states the exact replacement value), AND (b) the formula chain from the fixed cell to CE output uses no intermediate cells flagged 'Guess' or 'TBD.' If either condition fails, write 'Magnitude unknown — replacement value not specified' in column H. Do not assume a replacement value that isn't stated in the finding.

For each **High or Medium** finding in the Findings sheet whose Recommended Fix (column G) includes a specific formula change:

1. Use `read_sheet_values` (FORMULA mode) on the cell being fixed to confirm the current formula matches what the finding describes. If it does not match, note the discrepancy in the finding's Explanation — do not mark the finding resolved.
2. Identify cells that reference the changed cell by reading the row range around the fixed cell — read ±10 rows in FORMULA mode and scan for any formula containing the fixed cell reference (e.g., if fixing B14, search for formulas containing B14, $B$14, or B:B). For cross-sheet consumers, check if the fixed cell is referenced in the primary CEA tab if the fix is on a supporting sheet. Do not read whole sheets.
3. Verify the proposed fix would produce a correct result in each downstream consumer.
4. **Blank-range check**: For any proposed fix whose Recommended Fix formula involves multiplication or division across a cell range (e.g., `=A1*B1`, `=SUM(C4:C18)/D4`, `=PRODUCT(...)`), use `read_sheet_values` (UNFORMATTED_VALUE) on all cells in the range. If any cell in the range is blank, append to the finding's Explanation: "Note: [cell ref] in the proposed fix range is currently blank — populate it before applying this fix or the result will silently be zero." Do not mark the finding resolved.
5. **Flag as a new High finding** any proposed fix that would introduce a new formula error — name the breaking cell and why.

Coverage declaration: "Fix-validation complete. Checked [N] High/Medium findings with formula fixes. New issues flagged: [list or 'none']. No other fix-validation issues."

---

## Check 2 — Confidence intervals sheet

Use the `spreadsheet_info` result obtained in Step 1 to check whether a "Confidence intervals" or "Uncertainty" sheet exists:
- If present: verify it is populated (not blank) via a targeted `read_sheet_values` call. If blank, file as Medium/Assumption — write Assumption in column E, route to Findings.
- If absent: write directly to the Publication Readiness sheet with column D = Legibility, column E = "Confidence intervals or Uncertainty sheet not found — uncertainty ranges are a required component of published top-charity CEAs."
- **Do not apply this check** to BOTECs, VOI models, or exploratory analyses that do not target a published CEA.

**To determine whether this check applies**: check session context for a model type declaration (e.g., "program type: BOTEC" or "optionality model"). If not in session context, read the workbook title from the `spreadsheet_info` result obtained in Step 1 — titles containing "BOTEC", "optionality", "VoI", or "exploratory" indicate this check does not apply. If model type is ambiguous, apply the check and note in the Explanation: "Apply only if this is a published top-charity CEA, not a BOTEC or exploratory analysis."

If a prior agent already flagged this, verify the finding exists — do not duplicate.

**CI sheet cell-reference verification** (applies only when the CI sheet is present and populated): The CI sheet must draw its central CE estimate from the same terminal output cell as the pre-vet baseline — not from an intermediate pre-adjustment row.

1. Read the CI sheet's CE output row using `read_sheet_values` (FORMULA mode). Look for a row labeled "central estimate," "best estimate," "CE," or equivalent. If no row matching these labels is found after reading the CI sheet in FORMULA mode, file as **Medium/Legibility**: "CI sheet does not contain a clearly labeled central estimate row (looked for: central estimate, best estimate, CE). Cannot verify whether the CI sheet references the correct CE baseline cell. Researcher to confirm the CI sheet structure." Then skip the remaining steps of this sub-check.
2. Confirm the formula in that row references the same cell you verified as the CE baseline in Check 0. If it references a different cell, read the row label of that different cell on the main CEA sheet to determine whether it is a pre-adjustment subtotal.
3. If the CI sheet's central CE row references a pre-adjustment cell (row label contains "before adjustments," "unadjusted," "subtotal," or similar), file as **Medium/Formula**: "CI sheet's central estimate at [CI cell ref] references [main CEA cell], which is labeled '[label]' — a pre-adjustment value. The CI sheet should reference the final post-adjustment CE cell [baseline cell ref] so that confidence intervals reflect the fully adjusted model output."
4. If the CI sheet references the correct final cell, write in your reasoning: "CI sheet cross-reference verified: [CI cell ref] → [main CEA cell ref] (confirmed final output)."


Coverage declaration: "Confidence intervals check complete. Sheet present: [yes/no]. Status: [populated / blank / absent]. CI cell-reference: [verified / pre-adjustment ref flagged / not applicable]."

---

## Check 3 — Stale placeholder and draft language

Using targeted `read_sheet_values` calls on column A and column B of each vetted sheet (do not read full sheets), scan for:
- Cells containing any of these terms (exact match, case-insensitive): `TBD`, `TODO`, `DRAFT`, `Placeholder`, `Update this`, `to be confirmed`, `fill in`, `[fill in]`, `provisional`, `preliminary`, `working estimate`, `confirm before`, `update before`, `ASK`, `FIXME`, `TEMP`
- Column headers with generic names like `Column X`, `Country A`, `Year N`
- Cell notes containing internal-only markers (use `read_sheet_notes` on each vetted sheet to scan for notes beginning with `Note to self`, `INTERNAL`, or `ASK [name]`)
- Workbook title (from the `spreadsheet_info` result obtained in Step 1) containing `draft`, `v1`, `wip`, or `copy of`
- Any date visible in the workbook header, key tab, or title row that is more than 18 months before today — flag as Low/H if it appears to be a last-updated date rather than a data vintage date

Do not limit to header rows — scan all populated rows.

To distinguish last-updated from data vintage: a last-updated date typically appears in workbook metadata rows (e.g., a row labeled "Last updated:", "Version:", or "As of:"). A data vintage date typically appears in a row label describing a data source (e.g., "GBD 2021", "DHS 2020 data"). If the date context is ambiguous (e.g., a standalone year in a header row), treat as a last-updated date and apply the 18-month rule.

Write each unflagged instance directly to the Publication Readiness sheet with Error Type: Legibility (column D of the PR sheet) — not to the Findings sheet. If a prior agent already flagged it, verify the finding exists in Publication Readiness before filing a duplicate.

Coverage declaration: "Placeholder scan complete. Header rows and column A checked for all [N] vetted sheets. Instances found: [list or 'none']. No other instances."

---

## Check 4 — CE impact completeness

**Pre-condition check**: Before running Pass A or Pass B, verify that Check 0 successfully located and confirmed the CE baseline cell. If Check 0 filed a missing-baseline finding (the CE baseline cell was not found, was blank, or contained a non-numeric value), skip both Pass A and Pass B entirely — CE impact cannot be computed without a valid baseline. Write in your reasoning: "Pass A and Pass B skipped — CE baseline cell not confirmed in Check 0."

**Pass A — fill blanks**: For every **High** finding and every **Medium** finding whose Error Type is `Formula`, `Parameter`, or `Adjustment` — where Estimated CE Impact (column H) is blank — compute the directional impact using the pre-vet baseline CE from session context. Write using the standard format: `Raises CE — 8.7x → ~10.2x` or `Lowers CE — magnitude unknown` etc. Always lead with the standard phrase from output-format.md. Use `Direction unknown` if the researcher's answer would determine the direction. Update the finding in place using `modify_sheet_values`.

If Check 0 found a >1% discrepancy between the live cell value and the session context baseline and filed a High finding, use the live cell value (from Check 0 step 3) as the baseline for CE impact estimation, not the session context value — the live value is more likely to be correct.

Rationale: Medium Formula, Parameter, and Adjustment findings can affect CE even if their impact is below the High threshold. Researchers need the CE direction to triage them against High findings. For Medium `Assumption` findings where CE impact is confirmed zero, write `No CE impact` — do not leave blank. For Medium `Legibility` and `Inconsistency` findings: per output-format.md, blank column H is acceptable — write `No CE impact` only when you have positively confirmed the CE impact is zero; do not fill it automatically.

**Pass B — quantify High "magnitude unknown" and flag unresolved directions**: For every **High** finding where column H contains "magnitude unknown" (i.e., already filled but not quantified):

1. Read the cell(s) referenced in column C of that finding using `read_sheet_values` (UNFORMATTED_VALUE) on the source spreadsheet.
2. Read the CE baseline cell (verified in Check 0) in UNFORMATTED_VALUE mode.
3. Before computing, confirm that the finding's Recommended Fix (column G) contains a specific numeric replacement value. If column G says "Researcher to determine" or similar, skip computation and proceed to step 4 — retain magnitude unknown with reason: "(replacement value not specified in fix — researcher must supply)". Otherwise, attempt to compute: what is the CE multiple if this finding is resolved as recommended? If the referenced cell directly multiplies into the CE chain (e.g., a moral weight, a benchmark value, an adjustment factor), the impact is computable — calculate and replace "magnitude unknown" with the numerical estimate, e.g., `Lowers CE — 9.3x → ~9.0x`.
4. If computation is genuinely not possible without assumptions the researcher must supply (e.g., the fix requires knowing a correct parameter value that doesn't exist in the model), retain "magnitude unknown" but append a brief reason in parentheses: `Lowers CE — magnitude unknown (requires researcher to supply replacement value for [parameter])`.
5. If the cell is not in the CE chain (e.g., a labeling issue or structural issue that doesn't affect computation), change to `No CE impact` if that is accurate.

The goal is that no High finding exits validation with a bare "magnitude unknown" — every High finding should either have a numerical estimate or a specific stated reason why one cannot be computed.

Do not modify any other columns of existing findings.

Coverage declaration: "CE impact completeness check done. Pass A — High findings: [N total, M filled, K already had content]. Medium Formula/Parameter/Adjustment findings: [N total, M filled, K already had content]. Pass B — High 'magnitude unknown' findings reviewed: [N], quantified: [M], retained with reason: [K], changed to No CE impact: [J]."

---

## Writing new findings

If this pass surfaces genuinely new findings not already covered, add them to the appropriate sheet before completing.

Before writing any new finding, confirm: (1) exact cell reference(s), (2) specific issue, (3) precise fix required.

Assign the next sequential Finding ID continuing from the highest existing Finding ID in the Findings sheet (which includes IDs assigned by both compaction and gap-fill — read the last F-NNN row to determine the current maximum before assigning any new IDs).

**Findings sheet** (A–H): A=Finding # | B=Sheet | C=Cell/Row | D=Severity | E=Error Type/Issue (write the exact label only — no additional text, description, dashes, or punctuation after it; choose one of: Formula | Parameter | Adjustment | Assumption | Legibility | Inconsistency) | F=Explanation | G=Recommended Fix | H=Estimated CE Impact (use exactly one of: Raises CE — [estimate], Lowers CE — [estimate], Raises CE — magnitude unknown, Lowers CE — magnitude unknown, No CE impact, Direction unknown)

**Publication Readiness** (A–F): A=Finding # | B=Sheet | C=Cell/Row | D=Error Type/Issue (write the exact label only — no additional text, description, dashes, or punctuation after it; choose one of: Sourcing | Box Link | Legibility) | E=Explanation | F=Recommended Fix

---

## Final step — Hyperlink conversion (run last, after all checks and new findings are written)

Convert every cell reference in column C of both the Findings sheet and Publication Readiness sheet into a clickable `=HYPERLINK(...)` formula that opens the referenced cell directly in the source spreadsheet.

**Run hyperlink conversion after**: (1) all five checks are complete, (2) all new findings have been written, and (3) all in-place updates to column F and column H are complete. Do NOT run hyperlink conversion after writing the AGENT_COMPLETE marker — the AGENT_COMPLETE row does not need a hyperlink.

1. **Get the GID mapping**: From the `spreadsheet_info` result obtained in Step 1, extract the tab name → numeric GID mapping for every tab in the source spreadsheet (`sheetId` field in the sheets list). (Do not call `get_spreadsheet_info` again — it was called once in Step 1.)

2. **Read all column C values**: Read Findings sheet columns A:C in batches until empty. Separately read Publication Readiness sheet columns A:C. Collect every non-divider, non-blank row with its sheet row number and current column C text.

3. **Parse each column C value** to extract a sheet name and cell reference:
   - **`SheetName!CellRef`** (e.g., `Main CEA!B47`) → sheet name = `Main CEA`, cell ref = `B47`
   - **`CellRef` only** (e.g., `B47`, no `!`) → sheet name = primary vetted sheet from session context, cell ref = `B47`
   - **Comma-separated cell list** (e.g., `B14, B18, B22`) → extract the first cell ref before the first comma. If the first cell includes a sheet qualifier (e.g., `Main CEA!B14`), use that sheet name and cell reference — do not fall back to the primary vetted sheet. Only fall back to the primary vetted sheet when the first cell has no sheet prefix. Keep the full comma-separated text as the display text. This covers grouped findings where multiple cells are listed in one row.
   - **`Row N` or `rows N–M`** (e.g., `Row 47`) → sheet name = value from column B of this finding row, cell ref = `A47` (first cell of that row)
   - **Range** (e.g., `B47:C51`) → link to the first cell of the range (`B47`); keep the full range as the display text
   - **`Multiple`** as the sheet name → skip; leave column C as plain text (no single target cell to link to)
   - **Blank column C** → skip

4. **Look up the GID** for the resolved sheet name in the mapping from step 1. If the sheet name is not found (e.g., a misspelling by an earlier agent), leave the cell as plain text — do not error or skip the entire batch.

5. **Construct the HYPERLINK formula**:

   ```
   =HYPERLINK("https://docs.google.com/spreadsheets/d/{source_spreadsheet_id}/edit#gid={gid}&range={cell_ref}","{original_column_C_text}")
   ```

   Example: column C = `Main CEA!B47`, source ID = `1aBcDeFgH...`, Main CEA GID = `987654321`:
   ```
   =HYPERLINK("https://docs.google.com/spreadsheets/d/1aBcDeFgH.../edit#gid=987654321&range=B47","Main CEA!B47")
   ```

   The cell ref in the URL is the A1 notation **without** the sheet name prefix — just `B47`, not `Main CEA!B47`.

6. **Write all hyperlinks** in a single `modify_sheet_values` call per sheet, targeting only column C, using `value_input_option: USER_ENTERED` so Google Sheets evaluates the formula. Do not overwrite any other columns. Exclude divider rows and the AGENT_COMPLETE marker row from the hyperlink write. Only write HYPERLINK formulas to rows where column C is non-blank and the row is a valid finding row (column A contains an F-* or PR-* ID, or column A is blank and column B contains a sheet name, not a divider marker).

Coverage declaration: "Hyperlink conversion complete. Findings rows converted: [N]. Publication Readiness rows converted: [N]. Skipped (Multiple/blank): [N]. GID lookup failures (left as plain text): [N]."

---

## Final step — Write AGENT_COMPLETE marker

After hyperlink conversion is complete, write a completion row to the Findings sheet: column B = `final-review-validation`, column D = `AGENT_COMPLETE`, column F = `COVERAGE_ROWS: Findings sheet rows 2–[last_row] | Staging sheet: Findings. CE baseline: [verified/not found]. ID integrity: [clean/issues filed]. [K] new findings filed.`
