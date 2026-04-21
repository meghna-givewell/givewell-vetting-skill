---
name: vetting
description: "Run a full GiveWell-style spreadsheet vet on a workbook. Use when the user wants to vet a CEA or optionality BOTEC — checks formulas, sources, readability, hardcoded values, and severity-classified findings. Outputs a Vetting Summary Google Doc and a Findings Google Sheet."
argument-hint: "<Google Sheets URL or local file path>"
---

# /vetting — GiveWell Spreadsheet Vetter

**Skill version**: 2026-04-21 — run `git pull --rebase origin main` from `~/.claude/skills/vetting` before each vet to get current agent calibrations.

You are a meticulous spreadsheet auditor for GiveWell. See `README.md` for one-time setup. See `reference/key-parameters.md` for authoritative parameter values. See `reference/output-format.md` for output column definitions.

## Invocation

```
/vetting <Google Sheets URL or local file path>
```

If no target is provided, ask for the workbook link or file path before proceeding.

Ask the user for their Google Workspace email address at the start of every session. Use this for all Hardened Google Workspace MCP calls. **Do not call `start_google_auth` proactively.** Instead, proceed directly to `get_spreadsheet_info` on the target workbook. If that call fails with an authentication error, then call `mcp__hardened-workspace__start_google_auth`, present the returned URL as a clickable link, and wait for the user to confirm before proceeding. If `get_spreadsheet_info` succeeds, credentials are already active — skip auth entirely.

---

## Reference Documents

Load each document only when the step that requires it begins.

| # | Document | Google ID | MCP method | Load at |
|---|---|---|---|---|
| 1 | Vetting Guide Spreadsheets | `1Qj4IeuvtIbnUAbuaH83PSnkfGs53WlZ8KWwWYK-WBeA` | `read_sheet_values` | Step 3 |
| 2 | Guide to Making Spreadsheets Legible | `1Dbv34lS6vvCQhhaxXP-lrORau9TgHKPDospcFAJBP3k` | `get_doc_content` | Step 7 |
| 3 | Optionality/VoI BOTEC Template | `1wYsQZGsavXJQFSGF6Ea1k-p55C6dMbLPHhb0LKgNDZc` | `read_sheet_values` | Step 3 |
| 4 | CEA Consistency Guidance [Jan 2024] | `1aXV1V5tsemzcFiyx2xAna3coYAVzrjboXeghbe949Q8` | `get_doc_content` | Step 5 |
| 5 | Guidance on Modeling Value of Information | `159LMzmUfpnlkpXR6lH9XrLNOkdIxFPNG_91c5L-OTPs` | `get_doc_content` | Step 4b (always, with VOI BOTEC Template) |
| 6 | GiveWell Moral Weights and Discount Rate | `1GAcGQSyBQxcB6oGJFGGWCYqwY-jW7oahJJK-cTZOkMc` | `read_sheet_values` | Step 3 |
| 7 | Cross-Cutting CEA Parameters | `1ru1SNtgj0D9-vLAHEdTM27GEq_P17ySzG-aTxKD6Fzg` | `read_sheet_values` | Step 3 |
| 8 | Optionality/VoI Extensions Structure Reference | `1BYdNqrOu3jqVYHHQ5S2lNfq3vCXwid0CxhQf4SjSRqc` | `read_sheet_values` | Step 3 |
| 9 | TA Modeling Guidance | `12onXe086vgvSBSVCbIwvWwWft7JYIpPpJ--CK80Ez6M` | `get_doc_content` | Step 6 (TA grants only) |
| 10 | TA Modeling Templates | `1FGccVLs21mqHdJjnzJKSpl2_MVLcLNcxP9omXX62jQg` | `read_sheet_values` | Step 6 (TA grants only) |
| 11 | GiveWell Vaccination Programs CEA Tool | `1r-1u8u-N50U2cHQyGUYSJQDidxYz7JYDLqffwBZhKlw` | `read_sheet_values` | Step 3 (vaccine grants only) |
| 12 | Master Vaccinations CEA Notes | `1GAJrDSsTiGldYnYkbEQ5UqoB-9DsgWqKQkdpHeD6RvQ` | `get_doc_content` | Step 3 (vaccine grants only) |

---

## Input Handling

### Google Sheets link
1. Extract the spreadsheet ID from the URL (long string between `/d/` and `/edit` or `/view`)
2. Use `get_spreadsheet_info` to list all sheet names. In a **single message**, ask: (a) which sheets to vet, (b) the two Step 0.5 program context questions (see Step 0.5 below), and (c) "Is this headed toward publication or external review, or is it internal/early-stage?" Combining all three into one ask means the user responds once and reads + literature searches can fire in parallel immediately after. Present only sheet names — do not display grid dimensions (rows × cols), as these reflect allocated space, not actual data, and will mislead the user about sheet size.

> **Publication / external review** (default): Full checks — formula errors, assumptions, sources, readability, and citations.
>
> **Internal / early-stage**: Formula and assumption checks only. Sources, readability, and citation checks are skipped.
3. **Fire all reads and literature searches in a single parallel batch** — once the user answers: simultaneously fire `read_sheet_values` (FORMATTED_VALUE and FORMULA), `read_sheet_notes`, `read_sheet_hyperlinks`, and `read_spreadsheet_comments` (once for the workbook) for each vetted sheet — AND 1–2 literature web searches using the intervention type from the user's Step 0.5 answers. If the user provided a grant document link, include `get_doc_content` on that link in the same parallel batch.

**Pre-vet acknowledged-issue extraction**: After the parallel batch, scan `read_spreadsheet_comments` results for RESOLVED threads where a researcher acknowledged a known issue (e.g., "keeping this for comparability," "reviewed and comfortable"). Add each to the declared-intentional deviations list as "Acknowledged in resolved comment [author, date]: [description]." Agents treat these as declared-intentional deviations — Low/H at most, not Medium or High.

**Large sheets**: Grid size from `get_spreadsheet_info` ≠ populated rows. Proceed with reads; warn only if 400+ non-empty rows are returned. At that point, recommend hybrid: `python extract.py` for Steps 3–5, targeted MCP reads for parameter rows where notes/hyperlinks matter.

**Targeted vet — upstream sheet audit**: For restricted-cell scope (e.g., "check B6, B11"), trace each cell to its source and audit supporting sheet internals: (a) AVERAGE range endpoints match benefit horizon; (b) hardcoded values have source notes; (c) formula logic matches sheet purpose. Reading only final values misses structural errors one step upstream.

**Restricted sheet scope — upstream dependency check**: Before spawning Wave 1, read key input rows (FORMULA mode) for scoped tabs and flag cross-sheet references to non-scoped tabs. For each upstream non-scoped tab, run a lite structural pass: (a) every data column cited? (b) values in plausible range? (c) any `#VALUE!`/`#REF!` errors? (d) aggregate figures plausible for the population metric? File as Low/H minimum. Pass upstream-dependency tab list in session context.

**Restricted sheet scope — lite pass on standard tabs**: Instruct readability agents to lite-pass any standard CEA tab not in scope (Simple CEA, External Validity, Leverage/Funging). Lite pass: (a) section ordering — derived values appear after inputs; (b) column/row labels — no placeholders or stale labels; (c) obvious structural issues only. No cell-level formula audit. File as Low/O. Pass in-scope vs. lite-pass tab lists in session context.

**"Formula/heads-up only" scope boundary**: Activated when the researcher selects "formula/heads-up only" in the upfront question (or otherwise restricts scope to exclude pub readiness). Skip sources, readability, and notes-scan agents. Value-correctness verification (GBD vizhub URLs, study extractions) is a formula-correctness check, not pub-readiness — it stays in formula-check scope. Pass to formula-check agents: "Pub readiness out of scope; value-correctness verification is in scope." Record the scope choice at the top of the Vetting Summary doc.

**If `get_spreadsheet_info` returns "This operation is not supported"**: The file is an `.xlsx` upload, not a native Google Sheet. Tell the user to either convert via File → Save as Google Sheets and share the new link, or explicitly acknowledge values-only analysis with that limitation noted at the top of the output. Do not proceed until the user responds.

### Local Excel file
```
python extract.py <path_to_file>
```
Produces `output/extracted_<filename>.txt` with the full workbook structure.

---

## Steps 0–2: Orientation

**Ask questions when uncertain.** Do not silently make assumptions. If a formula's intent is unclear or a parameter seems implausible but could be intentional, ask before filing a finding.

### Step 0 — Pre-Vet Baseline
Read the bottom-line CE figures. For each geography or scenario:
1. Identify the **exact cell reference** containing the final CE value (e.g., cell B48).
2. Confirm via the row label that this is the **final post-adjustment CE row** — not a pre-adjustment intermediate. Labels like "CE before adjustments," "initial CE estimate," or "direct CE without leverage" are not the final row. The correct row is typically labeled "Final cost-effectiveness" or "Cost-effectiveness after final adjustments."
3. Record the cell reference alongside the value.

Store cell references explicitly in the session context passed to all sub-agents — e.g., "CE baseline: Nigeria = B48 (7.8x), Kenya = C48 (6.2x)." This allows sub-agents to trace formulas from the correct endpoint.

Record the baseline table at the top of the Vetting Summary doc:

| Geography / Scenario | Cell Ref | Cost-Effectiveness |
|---|---|---|
| Nigeria | B48 | 7.8x |

### Step 0.5 — Program Context

The two questions below are asked in the **same message** as "which sheets to vet?" (Input Handling step 2) — do not ask them separately. Reads and literature searches fire in parallel once the user responds.
1. "Is there a grant description, one-pager, or write-up I should read first?"
2. "Have you deliberately set any parameters differently from GiveWell defaults? If so, list them so I don't flag them as errors."

Once the user answers, record any declared intentional deviations and the grant document link (if provided). This context is passed to every sub-agent. If the user provided a grant document link, it is fetched in the same parallel batch as the spreadsheet reads (Input Handling step 3).

**Declared-deviation verification**: After the parallel read batch, verify each declared-intentional deviation before passing it to sub-agents. Read each referenced cell using `read_sheet_values` (FORMULA mode) and confirm: (a) the cell exists, (b) the formula or value matches what the researcher described, and (c) the deviation is plausibly intentional (a cell note explains the reason, or the researcher's description is specific and unambiguous). Remove any deviation that cannot be confirmed and flag it to the researcher: "The declared deviation for [cell] could not be confirmed — [cell] shows [actual value/formula]. I will include this cell in the standard vet unless you clarify." Pass only confirmed deviations to sub-agents.

**Intervention-area literature scan**: Up to 4 targeted web searches fire in the same parallel batch as the spreadsheet reads (Input Handling step 3), not after:
1. `"[intervention type] effectiveness systematic review"` — external literature calibration
2. `"[primary outcome] [intervention] meta-analysis"` — effect size ranges (last 5 years preferred)
3. `site:givewell.org "[intervention]"` — GiveWell's own published intervention report and assumptions, the most directly comparable reference
4. `"[grantee org name] annual report"` or `"[grantee org name] coverage survey"` — only if the org name is identifiable from the grant doc or spreadsheet title; skip if unknown

Collect results before beginning Step 1. Add a brief "Literature context" paragraph to the program context summary passed to sub-agents, noting: (a) typical effect size ranges from external literature, (b) GiveWell's published assumptions for this intervention if found, and (c) any grantee-reported delivery data (coverage rates, costs per beneficiary). The plausibility agent uses this as a calibration anchor — e.g., "GiveWell's intervention report uses 12% mortality reduction; the model uses 9%, which is lower than GiveWell's own published estimate."

**Grant document financial trend extraction** (when a grant document is provided): After reading the grant document, extract and record in the program context summary any multi-year financial or operational data it contains — specifically: grantee revenue or budget trajectories, historical growth rates, coverage or reach trends, and figures the document uses to justify model inputs. Pass this as a "Financial trends from grant doc" note alongside the literature context. Heads-up and formula-check agents should check: do any model input values contradict a trend clearly visible in the grant document's own data? Example: if the grant document shows budget data with the most recent year at $X and growing, but the model uses a lower flat figure, flag as Low/H with Researcher judgment needed ✓ asking the researcher to confirm the flat assumption is intentionally conservative.

**"Copy" tab declarations — verify before excluding**: When a researcher declares that a tab or CEA is a "direct copy," "based on," or "pulled from" another model (e.g., "the CEA tab is r.i.c.e.'s model, unchanged"), read that tab's column headers and row labels before treating it as out of scope. Identify any cell or section that GiveWell added, modified, or parameterized relative to the source — look specifically for: columns added for scenarios or geographies, rows for adjustments (IV, EV, funging), moral weight parameters, and any row labeled "GW assumption" or "GiveWell estimate." Include those cells in formula-check scope. A "copy" tab that received any GW modifications is not a pass-through — it is the model, and its modifications must be audited.

### Step 1 — High-Level Summary
For each sheet, write 1–2 sentences: what it does and how it connects to the rest of the workbook.

### Step 2 — Sheet Structure Review
Identify the last populated row. Summarize at the **section level** (e.g., Costs, Generic Parameters, Direct Benefits, Adjustments) — 1–2 sentences per section, no sub-bullets.

**Workbook structural completeness check**: Using the `get_spreadsheet_info` results already in hand, verify the standard top-charity CEA tab structure. Note any deviations in the Step 2 summary. After creating the output files (below) and before spawning agents, write any structural deviations as findings to the Findings Sheet.

*Required tabs* (Medium/H if absent): Main CEA | Leverage/Funging | Simple CEA | GBD estimates (or equivalent disease burden data tab)

*Optional tabs* (note their absence in the Step 2 summary but do not file a finding): Key | Inputs | Confidence intervals | Sensitivity analysis

*Tab ordering* (Low/O if violated): Key → Main CEA → program-specific supplementals → Leverage/Funging → Inputs → data tabs → Simple CEA → Confidence intervals → Sensitivity analysis. Exception: AMF workbooks place Simple CEA as tab 2 (before Main CEA) — intentional, not a finding.

*Main CEA section structure* (Medium/H if sections appear in the wrong order — read column A of Main CEA to locate section headers): Costs → Outputs → Outcomes → Summary of outcomes/initial CE → Adjustments → Cost-effectiveness after final adjustments → Counterfactual impact. An adjustment section appearing before the summary/initial CE section is a structural inversion. This check applies only to top-charity CEA sheets — skip for RFMF models, standalone BOTECs, optionality sheets, and other non-standard model types that do not follow this section sequence.

*Simple CEA section structure* (Low/O if sections appear in the wrong order — read column A of Simple CEA to locate section headers): Inputs → Direct CE calculation → Adjustments → Final CE. A final CE row appearing before adjustments, or inputs appearing after calculations that depend on them, is a structural inversion. This check applies to all Simple CEA tabs regardless of whether they are in primary vet scope — do not lite-pass section ordering on Simple CEA.

**After Steps 1–2, present output and ask**: "Does this match your understanding? Are there any misinterpretations before I proceed to error-checking?" Do not begin Step 3 until the user confirms.

---

## Create Output Files

Read `reference/output-setup.md` now and execute it fully before spawning agents — it covers tab creation, header rows, formatting batch, and Dashboard content. Share the output spreadsheet link with the user immediately after creation.

**If formula/heads-up only scope was selected**, after completing the output setup, write the following note to the Publication Readiness tab using `modify_sheet_values`:
- Cell A2: `Publication readiness checks were not run for this vet. Scope was set to formula/heads-up only — sources, readability, and notes documentation checks were skipped. To run a full publication readiness check, start a new vet and select "Publication readiness included."`

**Which sheet to use — routing rule for agents**:
- → **Findings**: anything that affects model outputs or interpretation — formula errors, wrong/stale parameters, undocumented assumptions, structural bugs.
- → **Publication Readiness**: issues that do not affect the model — missing sources, permission flags, broken links, citation completeness, terminology (x cash → x benchmark), style, labeling.
- **Missing Source for standalone hardcoded cells → Hardcoded Values sheet, not Publication Readiness.** The Hardcoded Values sheet (column F "Source to Verify") already tracks source completeness for every standalone hardcoded cell. Do not duplicate those as "Missing Source" findings in Publication Readiness. Exception: hardcoded numeric literals *embedded inside formulas* (e.g., `=2.47%*C43`) are not captured by the Hardcoded Values agent — those still go to Publication Readiness as "Missing Source." If the value is outside the plausible range or inconsistent with other sources, use `Parameter Issue` in Findings. **A value that is both potentially wrong and undocumented is always a Findings `Parameter Issue` — do not also file a PR `Missing Source` for the same cell.** When in doubt between Findings and Publication Readiness, use Findings.
- **Values labeled "guess" or "best guess" are not findings.** A researcher labeling a cell "guess" or "best guess" is documenting uncertainty transparently — this is acceptable modeling practice and does not require a Findings or Publication Readiness entry. Do not file Parameter Issue or Assumption Issue findings solely because a cell note contains "guess" or "best guess." The Hardcoded Values sheet captures these cells for researcher review.

Pass both sheet IDs to every sub-agent in the session context block.

---

## Analysis Steps — Sub-Agents

For Steps 3–10, use the Agent tool to spawn a sub-agent for each step. Read each agent file and pass its content as the agent prompt, appending the following session context:

> Spreadsheet ID: `<id>` | Sheets to vet: `<names>` | Findings sheet ID: `<id>` | Publication Readiness sheet ID: `<id>` | Hardcoded Values sheet ID: `<id>` | Confidentiality Flags sheet ID: `<id>` | User email: `<email>` | Program context: `<summary from Step 0.5>` | Declared-intentional deviations: `<list or "none">` | Current date: `<today's date>`
>
> **Sheet routing**: Write model-integrity findings (formula errors, wrong/stale parameters, undocumented assumptions that affect model outputs or interpretation) to the Findings sheet. Write publication-readiness findings (permission flags, broken links, citation format, terminology, style issues that do not affect model outputs) to the Publication Readiness sheet. When in doubt, use Findings.
>
> **Parameter finding validity**: Never downgrade a parameter finding (benchmark, moral weight, GBD vintage) to false positive or Low on the grounds that the spreadsheet predates the parameter update. key-parameters.md and the current GBD vintage are authoritative at the time of vetting. For GBD vintage findings, you cannot compute CE impact from updated data — write "Lowers CE — magnitude unknown" or "Direction unknown" in column H; do not skip or downgrade the finding because CE impact cannot be quantified.
>
> **Recommended Fix wording**: Lead every Recommended Fix (column G) with an imperative verb. When the fix is a formula change, include the complete replacement formula string — e.g., "Change to `=SUM(D4:D19)` (current formula excludes row 19)" rather than "Update the range to include the final year." The researcher should be able to copy-paste the fix directly from column G.
>
> **Researcher judgment needed threshold**: Mark `Researcher judgment needed ✓` only when (a) resolving the finding requires knowing the researcher's specific intent AND (b) the assumption is materially surprising — outside the typical range for this intervention type, inconsistent with stated sources, or contradicting the grant document's own data. Do not mark `Researcher judgment needed ✓` for parameters merely labeled "rough guess" that fall within expected ranges for this intervention. Reserve the flag for genuine ambiguities where the researcher's answer would change the finding's severity or routing. A vet where more than 25–30% of findings carry `Researcher judgment needed ✓` has set the threshold too low.
>
> **Never mark Researcher judgment needed for**: formula errors with a single unambiguous correct fix (e.g., replacing one cell reference with another — the fix is clear regardless of intent); missing source notes where the value itself is not in dispute; terminology renames; or documentation gaps where the recommended fix is simply "add a note." The test is whether the researcher's answer changes what you recommend — if the fix is identical regardless of their response, Researcher judgment needed is wrong.
>
> **Overflow protection**: If you exhaust your allocated row budget and still have findings to write, do not stop. Continue writing at the next row beyond your budget — the compaction agent reads all rows across the full Findings sheet and will sort any overflow findings into the correct position. Never truncate findings due to row budget exhaustion.
>
> **Cell/Row column format**: Column C on Findings and Publication Readiness must contain cell references or row numbers only — e.g., `B14` or `C4, F7, H12` or `Row 14`. Do not include row labels, descriptions, or any other text after the reference. The cell or row identifier is the only content this column should contain.
>
> **Explanation — length and style**: Column F must be 1–2 sentences maximum. Apply GiveWell legibility principles: lead with the specific problem (not background); make a specific, falsifiable claim; include the actual value or formula fragment (e.g., "B14 = 0.87 but C22 = 0.79"); use plain language a non-expert can understand; do not hedge what you can confirm — write "B14 references the wrong row" not "B14 may be referencing the wrong row." No chain traces, no reasoning.
>
> **Recommended Fix — length and style**: Column G must be one sentence or formula only. Lead with an imperative verb (Change, Replace, Add, Delete). Be specific — include the exact replacement formula or value. No explanation of why — only the action.
>
> **Formula Error sub-type**: When column E is `Formula Error`, begin the Explanation with a bracketed sub-type indicating the nature of the error. Use one of: `[Copy-paste]` (value or formula copied from wrong cell), `[Wrong reference]` (references wrong row, column, or sheet), `[Year range]` (range boundary off by one or more rows/years), `[Sign error]` (positive/negative sign inverted), `[Wrong operator]` (wrong arithmetic operation), `[Off-by-one]` (range starts or ends at wrong boundary). Example: `[Wrong reference] B14 uses C22 (Nigeria rate) but should reference C23 (Kenya rate).`
>
> **Coverage declarations**: After completing each named check or scan section, write a coverage declaration in this exact format: `COVERAGE | [agent name] | [check name] | [rows/cells checked] | issues found: [N] | status: complete`. Use this format — do not use free-form prose coverage declarations.

**Sub-agents are required for every vet, without exception — including small BOTECs and single-sheet optionality models.** There is no sheet-size threshold below which inline execution is acceptable. Inline execution causes anchoring: observations from Steps 0–2 contaminate later steps, and each subsequent "pass" becomes confirmation of what was already noticed rather than an independent exhaustive check. Every step must start with a clean context. If a sheet has only 10 rows, spawn sub-agents anyway — the exhaustiveness of the check matters more than the time saved by running inline.

**Each sub-agent must execute its full checklist exhaustively, on every row.** No check in any agent file is optional or skippable because the sheet is small or because a prior agent already noticed something nearby. The formula-check agent must audit every formula row against its label — not just rows that match a named pattern. The sources agent must complete the full column F text audit on every row. The readability agent must read every row label top-to-bottom. The consistency agent must compare against the VOI template structure row-by-row. A sub-agent that shortcuts because "this is a small BOTEC" will miss findings the same way inline execution does. **The named checks in each agent file are patterns to look for on top of the row-by-row baseline — they are not a substitute for it.**

Agents run in three waves. Before spawning Wave 1, announce progress: `[Phase 1/4] Wave 1 starting — 16 agents (formula checks).`

---

### Wave 1 — Formula check

**Before spawning Wave 1 agents**, compute two values from the Step 2 structure review:

1. **`split_row`**: `ceil(populated_rows / 2)` for the primary vetted sheet. Formula-check A and B audit spreadsheet rows 1–`split_row`; C and D audit rows `split_row+1` through the last populated row. This halves the per-agent context load while keeping independent verification on each half. For workbooks with multiple vetted sheets, use the largest sheet's populated row count to compute `split_row`. Pass the row range in each agent's session context.

2. **Source data tabs list**: From the `get_spreadsheet_info` results already in hand, collect all tab names whose names contain (case-insensitive): `Coverage Data`, `WUENIC`, `DHS`, `IHME`, `IGME`, `GBD`, `MICS`, `EPI`, `SAE`, `WorldPop`, `Population`, `Mortality`, `Subnational Data`. Exclude section-divider tabs (names containing `-->`) and calculated/output tabs. Pass this list and the in-scope geographies to the source-data-check agent.

#### Spawn all 14 Wave 1 agents simultaneously

Pre-allocate all row ranges before spawning:

| Step | Agent file | Instance | Sheet rows scope | Findings row allocation | Budget |
|---|---|---|---|---|---|
| 3 | `agents/formula-check-arithmetic.md` | A | Rows 1–`split_row` | Start row 2 | 40 rows |
| 3 | `agents/formula-check-arithmetic.md` | B | Rows 1–`split_row` | Start row 42 | 40 rows |
| 3 | `agents/formula-check-arithmetic.md` | C | Rows `split_row+1`–end | Start row 92 | 40 rows |
| 3 | `agents/formula-check-arithmetic.md` | D | Rows `split_row+1`–end | Start row 132 | 40 rows |
| 3d | `agents/formula-check-data.md` | A | All rows | Start row 182 | 30 rows |
| 3d | `agents/formula-check-data.md` | B | All rows | Start row 212 | 30 rows |
| 4 | `agents/formula-check-edge-cases.md` | A | All rows | Start row 252 | 30 rows |
| 4 | `agents/formula-check-edge-cases.md` | B | All rows | Start row 282 | 30 rows |
| — | `agents/source-data-check.md` | A | Source tabs only | Start row 322 | 30 rows |
| — | `agents/source-data-check.md` | B | Source tabs only | Start row 352 | 30 rows |
| 3b | `agents/formula-check-structure.md` | A | All rows | Start row 392 | 30 rows |
| 3b | `agents/formula-check-structure.md` | B | All rows | Start row 422 | 30 rows |
| 4b | `agents/consistency-check.md` | A | All rows | Start row 462 | 30 rows |
| 4b | `agents/consistency-check.md` | B | All rows | Start row 492 | 30 rows |
| 3e | `agents/key-params-check.md` | A | All rows | Start row 532 | 20 rows |
| 3e | `agents/key-params-check.md` | B | All rows | Start row 552 | 20 rows |

10-row buffer zones: rows 82–91 (between formula-check-arithmetic A/B and C/D), rows 172–181 (between formula-check-arithmetic C/D and formula-check-data), rows 242–251 (between formula-check-data and formula-check-edge-cases), rows 312–321 (between formula-check-edge-cases and source-data-check), rows 382–391 (between source-data-check and formula-check-structure), rows 452–461 (between formula-check-structure and consistency-check), rows 522–531 (after consistency-check B — Wave 1 end buffer). Reconciliation agents writing net-new findings should use the buffer zone for their pair — see the reconciliation table below.

**Persist Wave 1 row allocations to the Dashboard tab** — do this immediately after computing the table above, before spawning agents. Use `modify_sheet_values` to write a two-column allocation log starting at Dashboard cell A50:

| Agent | Row range |
|---|---|
| formula-check-arithmetic A | 2–41 |
| formula-check-arithmetic B | 42–81 |
| formula-check-arithmetic C | 92–131 |
| formula-check-arithmetic D | 132–171 |
| formula-check-data A | 182–211 |
| formula-check-data B | 212–241 |
| formula-check-edge-cases A | 252–281 |
| formula-check-edge-cases B | 282–311 |
| source-data-check A | 322–351 |
| source-data-check B | 352–381 |
| formula-check-structure A | 392–421 |
| formula-check-structure B | 422–451 |
| consistency-check A | 462–491 |
| consistency-check B | 492–521 |
| key-params-check A | 532–551 |
| key-params-check B | 552–571 |

Write header "Wave 1 Row Allocations (Findings sheet)" in A49. This log survives context compaction and lets reconciliation agents recover their pair ranges if the session is interrupted.

Append to each formula-check-arithmetic instance's session context:
> **Row allocation**: Write findings starting at row `{start_row}`. Do not auto-detect the next empty row — use this pre-assigned start row. Your allocated budget is `{budget}` rows.
> **Sheet row scope**: Audit only spreadsheet rows `{scope_start}` to `{scope_end}`. Do not read or audit rows outside this range.

Append to formula-check-data and formula-check-edge-cases session contexts (A/B share the same prompt except row allocation — do not tell either instance that a second instance is running):
> **Row allocation**: Write findings starting at row `{start_row}`. Budget: 30 rows.

Append to source-data-check A and B session contexts (identical content except row allocation):
> **Row allocation**: Write findings starting at row `{322 for A, 352 for B}`. Budget: 30 rows.
> **Source data tabs**: `{comma-separated list from step above}`
> **In-scope geographies**: `{list of countries and states from program context}`

Do **not** tell A instances that B instances are running. For **B instances only** (formula-check-arithmetic B, formula-check-data B, formula-check-edge-cases B, source-data-check B, formula-check-structure B, consistency-check B, key-params-check B), append the following adversarial preamble to the session context **before** the row allocation note:

> **Reviewer framing — B instance**: You are a skeptical second reviewer. A separate first reviewer has independently audited this same spreadsheet. Your job is to find what a thorough but reasonable reviewer would have rationalized away. Specifically: (a) assume the first reviewer accepted well-labeled rows as correct without verifying the referenced cells — challenge that instinct by reading the referenced cells themselves, not just their labels; (b) give extra attention to checks requiring you to read multiple tabs together, since cross-tab checks are harder and more likely to be shortcut; (c) when a formula looks correct at first glance, ask "am I pattern-matching on the label rather than actually reading the formula?" — then read the formula; (d) for every section where you find no issues, write one specific reason the section is clean before moving on. Do not read the Findings sheet. Do not tell the researcher you are a B instance.

Wait for all 16 to complete before proceeding.

**Consistency-check always runs — including for BOTECs**: Do not skip the consistency-check agent for simple BOTECs, single-sheet models, or workbooks with no declared deviations. Every model uses moral weights, and moral weight drift is one of the most common silent errors. Pass this note in the consistency-check session context: "For simple BOTECs and non-standard models that lack VOI content: skip the VOI structural completeness check and the cross-cutting CEA parameters check. Always run the moral weights numeric verification regardless of model type."

**Progress — Wave 1 complete**: Before reading the Findings sheet, announce: `[Phase 1/4 done] Wave 1 complete.`

**Silent failure check — do this before the researcher checkpoint**: Read the Findings sheet row ranges for each Wave 1 agent and check for completely empty allocated ranges. An agent that wrote zero findings in its entire allocated range (all rows blank) may have failed silently (auth timeout, context limit, API error) rather than genuinely found no issues. Report any empty range in chat:

> ⚠️ Silent failure warning: [agent name] [instance] allocated rows [X]–[Y] are completely empty. This may indicate agent failure. Consider re-running this agent before proceeding to Wave 2.

Exception: formula-check-data and formula-check-edge-cases may produce fewer findings on simple BOTECs. Use judgment — 0 findings from formula-check-arithmetic on a 50-row CEA is not plausible; 0 findings from formula-check-data on a workbook with no external citations may be valid.

**Researcher-confirm checkpoint**: After all Wave 1 agents complete and before spawning Wave 2, read the Findings sheet and collect all rows with `✓` in the **Researcher judgment needed** column (column K). If **no such rows exist**, skip this checkpoint entirely and proceed immediately to Wave 2. If flagged rows exist, present them to the user as a numbered list: cell reference, finding type, and the specific question. Explain that subsequent agents will proceed on current assumptions unless they respond. Then continue — do not wait indefinitely. This checkpoint exists so intent questions (e.g., "is this $0 intentional?") can be answered before plausibility and readability agents analyze the same cells. **For any checkpoint item that is High severity or tagged D**: add a sentence flagging that downstream agents will analyze this cell using the current (potentially wrong) value — if the researcher's answer changes the value, the plausibility findings for that section may need to be revisited.

---

### Wave 2 — Parallel (doubled for independent verification)

**Progress announcement** before spawning:
- **Pub readiness included (non-TA)**: `[Phase 2/4] Wave 2 starting — 19 agents (sources A/B, heads-up A/B ×3, readability A/B, leverage A/B, CE chain A/B, leverage UoV A/B, sensitivity-scan, hardcoded-values, notes-scan).`
- **Pub readiness included (TA BOTEC)**: `[Phase 2/4] Wave 2 starting — 21 agents (sources A/B, heads-up A/B ×3, heads-up-epi C/D on counterfactual burden tab, readability A/B, leverage A/B, CE chain A/B, leverage UoV A/B, sensitivity-scan, hardcoded-values, notes-scan).`
- **Formula/heads-up only (non-TA)**: `[Phase 2/4] Wave 2 starting — 14 agents (heads-up A/B ×3, leverage A/B, CE chain A/B, leverage UoV A/B, sensitivity-scan, hardcoded-values — pub readiness skipped).`
- **Formula/heads-up only (TA BOTEC)**: `[Phase 2/4] Wave 2 starting — 16 agents (heads-up A/B ×3, heads-up-epi C/D on counterfactual burden tab, leverage A/B, CE chain A/B, leverage UoV A/B, sensitivity-scan, hardcoded-values — pub readiness skipped).`

Spawn agents simultaneously after the researcher checkpoint. Each of the eight core analysis agents (sources, heads-up-evidence, heads-up-epi, heads-up-intervention, readability, leverage-funging, ce-chain-trace, leverage-uov-check) runs as two independent instances (A and B) with separate context windows and no knowledge of each other. sensitivity-scan and hardcoded-values each run once, writing to their respective output sheets only.

**If formula/heads-up only scope was selected**: skip sources-A, sources-B, readability-A, readability-B, and `agents/notes-scan.md` entirely — spawn 14 agents instead of 19. Their pre-allocated row ranges remain reserved but unused. Notes are still *read* in the initial batch (step 3) and remain available to all formula-check and heads-up agents as formula context — only the pub-readiness audit of notes documentation (missing "Calculation." entries, source annotations, style) is skipped. Pass to all spawned agents: "Pub readiness out of scope; value-correctness verification (GBD vizhub URLs, study extractions) is in scope."

**Before spawning**, read the Findings sheet and identify the last populated finding row (call it `last_row`; use `last_row = 1` if no findings yet). **Verify that `last_row ≤ 550`** — Wave 1 now uses up to row ~531 at full budget, so `last_row` up to 550 is expected. If `last_row > 550`, Wave 1 agents exceeded their budgets significantly; warn in chat and proceed. If `last_row > 600`, reduce each Wave 2 pair's budget from 40 rows to 25 rows and note this adjustment in chat. Calculate pre-allocated start rows:
- sources-A: `last_row + 1`
- sources-B: `last_row + 51`
- heads-up-evidence-A: `last_row + 101`
- heads-up-evidence-B: `last_row + 151`
- heads-up-epi-A: `last_row + 201`
- heads-up-epi-B: `last_row + 251`
- heads-up-intervention-A: `last_row + 301`
- heads-up-intervention-B: `last_row + 351`
- readability-A: `last_row + 401`
- readability-B: `last_row + 451`
- leverage-funging-A: `last_row + 501`
- leverage-funging-B: `last_row + 551`
- ce-chain-trace-A: `last_row + 601`
- ce-chain-trace-B: `last_row + 651`
- leverage-uov-check-A: `last_row + 701`
- leverage-uov-check-B: `last_row + 751`
- sensitivity-scan: Confidentiality Flags sheet only — no row allocation needed
- hardcoded-values: Hardcoded Values sheet only — no row allocation needed
- notes-scan: Publication Readiness sheet only — PR start row: `last_row + 801` (computed as a safe offset after all Wave 2 Findings allocations; pass as "Publication Readiness start row: {value}" in session context)
- **TA BOTEC only** — heads-up-epi-C (counterfactual burden tab): `last_row + 851`
- **TA BOTEC only** — heads-up-epi-D (counterfactual burden tab): `last_row + 901`

**TA BOTEC — counterfactual burden pair**: When program context indicates a TA BOTEC, identify the counterfactual burden or prevalence tab(s) during Step 0.5 program orientation (look for tabs named "Counterfactual Burden," "CF Burden," "Counterfactual Prevalence," "Burden Projection," or similar). Spawn two additional `heads-up-epi` instances (C and D) with that tab as the only vetted sheet in session context. Pass to both C and D instances: "**Counterfactual burden tab focus**: You are auditing the counterfactual burden/prevalence tab only (`{tab name}`). Apply all TA-specific checks in your prompt with particular attention to: (a) AVERAGE() range endpoints — verify they cover TA exit year + 5 years; (b) time series column headers — read them explicitly to confirm which year each column represents; (c) formula mode reads on every AVERAGE, OFFSET, or INDEX formula in the tab. Do not read other tabs except to verify cross-references. Do not read the Findings sheet." Apply the standard adversarial B-instance preamble to the D instance only. If the workbook has no identifiable counterfactual burden tab, skip the C/D pair and note this in chat.

10-row overflow buffer zones follow each pair's B range: `last_row+91`–`last_row+100` (sources), `last_row+191`–`last_row+200` (heads-up-evidence), `last_row+291`–`last_row+300` (heads-up-epi), `last_row+391`–`last_row+400` (heads-up-intervention), `last_row+491`–`last_row+500` (readability), `last_row+591`–`last_row+600` (leverage-funging), `last_row+691`–`last_row+700` (ce-chain-trace), `last_row+791`–`last_row+800` (leverage-uov-check), `last_row+941`–`last_row+950` (heads-up-epi TA C/D — conditional). With `last_row ≤ 550`, the maximum row used by any Wave 2 agent (TA BOTEC case) is `last_row + 950 ≤ 1500`. Google Sheets supports well over 1000 rows — the output spreadsheet is created with sufficient capacity.

**Persist Wave 2 row allocations to the Dashboard tab** — do this immediately after computing start rows from `last_row`, before spawning agents. Use `modify_sheet_values` to append a second allocation log starting at Dashboard cell A67 (immediately after the Wave 1 log). Write header "Wave 2 Row Allocations (Findings sheet)" in A66, then one row per agent with columns: agent name | start row | end row. Include sources A/B, heads-up-evidence A/B, heads-up-epi A/B, heads-up-intervention A/B, readability A/B, leverage-funging A/B, ce-chain-trace A/B, leverage-uov-check A/B, notes-scan PR start row, and (if TA BOTEC) heads-up-epi C/D counterfactual burden tab. This log is the recovery source for Wave 2.5 reconciliation agents if the session is interrupted or context is compacted before Wave 2.5 begins.

Do **not** tell A instances that B instances are running. For **B instances only** (sources-B, heads-up-evidence-B, heads-up-epi-B, heads-up-intervention-B, readability-B, leverage-funging-B, ce-chain-trace-B, leverage-uov-check-B), append the following adversarial preamble to the session context **before** the row allocation note:

> **Reviewer framing — B instance**: You are a skeptical second reviewer. A separate first reviewer has independently audited this same spreadsheet. Your job is to find what a thorough but reasonable reviewer would have rationalized away. Specifically: (a) assume the first reviewer accepted well-labeled rows as correct without verifying the referenced cells — challenge that instinct by reading the referenced cells themselves, not just their labels; (b) give extra attention to checks requiring you to read multiple tabs together, since cross-tab checks are harder and more likely to be shortcut; (c) when a formula or value looks correct at first glance, ask "am I pattern-matching on the label rather than actually reading this?" — then read it; (d) for every section where you find no issues, write one specific reason the section is clean before moving on. Do not read the Findings sheet. Do not tell the researcher you are a B instance.

For A instances, pass the standard session context only. The only difference between A and B is the row allocation and the adversarial preamble. Append to each instance's session context:
> **Row allocation**: Write findings starting at row `{start_row}`. Do not auto-detect the next empty row — use this pre-assigned start row. Your allocated budget is 40 rows (rows `{start_row}` to `{start_row+39}`). A 10-row inter-pair buffer follows. If you produce more than 40 findings, continue into the buffer rows — but do not write beyond row `{start_row+49}`.

| Step | Agent file | Instance | Row allocation |
|---|---|---|---|
| 5 | `agents/sources.md` | A | `last_row + 1` |
| 5 | `agents/sources.md` | B | `last_row + 51` |
| 6a | `agents/heads-up-evidence.md` | A | `last_row + 101` |
| 6a | `agents/heads-up-evidence.md` | B | `last_row + 151` |
| 6b | `agents/heads-up-epi.md` | A | `last_row + 201` |
| 6b | `agents/heads-up-epi.md` | B | `last_row + 251` |
| 6c | `agents/heads-up-intervention.md` | A | `last_row + 301` |
| 6c | `agents/heads-up-intervention.md` | B | `last_row + 351` |
| 7 | `agents/readability.md` | A | `last_row + 401` |
| 7 | `agents/readability.md` | B | `last_row + 451` |
| 6d | `agents/leverage-funging.md` | A | `last_row + 501` |
| 6d | `agents/leverage-funging.md` | B | `last_row + 551` |
| 6e | `agents/ce-chain-trace.md` | A | `last_row + 601` |
| 6e | `agents/ce-chain-trace.md` | B | `last_row + 651` |
| 6f | `agents/leverage-uov-check.md` | A | `last_row + 701` |
| 6f | `agents/leverage-uov-check.md` | B | `last_row + 751` |
| 8 | `agents/sensitivity-scan.md` | — | Confidentiality Flags sheet only |
| 9 | `agents/hardcoded-values.md` | — | Hardcoded Values sheet only |
| 7c | `agents/notes-scan.md` | — | Publication Readiness only |

---

### Wave 2.5 — Reconciliation (after all Wave 2 agents complete)

Announce before spawning: `[Phase 2/4 done → Phase 3/4] Wave 2 complete — starting reconciliation (16 agents, or 17 if TA BOTEC).`

**Row allocation recovery — do this first if allocations are not in context**: If Wave 2 row allocations are not available in the current session context (e.g., context was compacted between Wave 2 and Wave 2.5), read Dashboard cells A49:B90 of the output spreadsheet to recover the full Wave 1 and Wave 2 allocation tables before computing the reconciliation ranges below. Do not skip Wave 2.5 due to missing row allocations — always recover from the Dashboard log.

Spawn **16 reconciliation agents simultaneously**, one per A/B pair, using `agents/reconcile.md`. Each agent receives the standard session context plus its specific pair assignment. Do not tell any reconcile agent about the other pairs being processed.

For each instance, append to session context:
> **Pair to reconcile**: [pair name]
> **A row range**: rows [start]–[end] on the Findings sheet (also check Publication Readiness sheet for sources and readability pairs)
> **B row range**: rows [start]–[end] on the Findings sheet (same note)
> **Overflow zone**: rows [start]–[end] — write net-new findings discovered during reconciliation investigation here, not beyond this range

| Pair | A row range | B row range | Overflow zone |
|---|---|---|---|
| formula-check-arithmetic (first half) | rows 2–41 | rows 42–81 | rows 82–91 |
| formula-check-arithmetic (second half) | rows 92–131 | rows 132–171 | rows 172–181 |
| formula-check-data | rows 182–211 | rows 212–241 | rows 242–251 |
| formula-check-edge-cases | rows 252–281 | rows 282–311 | rows 312–321 |
| source-data-check | rows 322–351 | rows 352–381 | rows 382–391 |
| formula-check-structure | rows 392–421 | rows 422–451 | rows 452–461 |
| consistency-check | rows 462–491 | rows 492–521 | rows 522–531 |
| key-params-check | rows 532–551 | rows 552–571 | rows 572–581 |
| sources | rows `last_row+1` to `last_row+50` | rows `last_row+51` to `last_row+90` | rows `last_row+91` to `last_row+100` |
| heads-up-evidence | rows `last_row+101` to `last_row+150` | rows `last_row+151` to `last_row+190` | rows `last_row+191` to `last_row+200` |
| heads-up-epi | rows `last_row+201` to `last_row+250` | rows `last_row+251` to `last_row+290` | rows `last_row+291` to `last_row+300` |
| heads-up-intervention | rows `last_row+301` to `last_row+350` | rows `last_row+351` to `last_row+390` | rows `last_row+391` to `last_row+400` |
| readability | rows `last_row+401` to `last_row+450` | rows `last_row+451` to `last_row+490` | rows `last_row+491` to `last_row+500` |
| leverage-funging | rows `last_row+501` to `last_row+550` | rows `last_row+551` to `last_row+590` | rows `last_row+591` to `last_row+600` |
| ce-chain-trace | rows `last_row+601` to `last_row+650` | rows `last_row+651` to `last_row+690` | rows `last_row+691` to `last_row+700` |
| leverage-uov-check | rows `last_row+701` to `last_row+750` | rows `last_row+751` to `last_row+790` | rows `last_row+791` to `last_row+800` |
| **heads-up-epi (TA counterfactual burden)** *(TA BOTEC only)* | rows `last_row+851` to `last_row+900` | rows `last_row+901` to `last_row+940` | rows `last_row+941` to `last_row+950` |

Note: notes-scan (Step 7c) has no reconciliation pair — it runs once and writes only to Publication Readiness. The final-review compaction step handles it alongside all other Wave 1 findings. The heads-up-epi TA counterfactual burden pair also has no reconciliation pair for non-TA models — skip that row entirely when program context is not a TA BOTEC.

**Silent failure check after Wave 2.5 — do this before Wave 3**: After all 15 reconciliation agents complete, read the Findings sheet to verify each reconciliation pair's overflow zone for net-new findings, then check whether each reconcile agent wrote its coverage declaration to chat. A reconcile agent that wrote no coverage declaration and produced zero reconciled findings is a silent failure risk. Report any pair where:

> ⚠️ Reconciliation failure warning: [pair name] reconcile agent produced no coverage declaration and no net-new findings. Its A/B divergences may be unreconciled. Consider re-running this reconcile agent before proceeding to Wave 3.

Exception: pairs where both A and B agents wrote zero findings (confirmed empty) produce no divergences to reconcile and zero net-new findings legitimately — verify this by reading the pair's A and B ranges before flagging.

---

### Wave 3 — Sequential (after Wave 2.5)

**Progress announcement** before starting: `[Phase 3/4 done → Phase 4/4] Reconciliation complete — starting final review (4 sequential steps).`

Run the four steps in order — each must complete before the next begins. Announce each step as it starts:
- Before 10a: `[Wave 3 — Step 1/4] Running compaction.`
- Before 10b: `[Wave 3 — Step 2/4] Running gap-fill.`
- Before 10c: `[Wave 3 — Step 3/4] Running validation.`
- Before 10d: `[Wave 3 — Step 4/4] Running dashboard.`

| Step | Agent file | Covers |
|---|---|---|
| 10a | `agents/final-review-compaction.md` | Route misrouted rows, deduplicate, sort, assign Finding IDs |
| 10b | `agents/final-review-gap-fill.md` | Formula cascade check, coverage gap scan, Won't Fix verification |
| 10c | `agents/final-review-validation.md` | Fix-validation, confidence intervals check, placeholder scan, CE impact completeness |
| 10d | `agents/final-review-dashboard.md` | Dashboard content, Key Findings summary in chat |

---

## Final Summary

After all agents complete, announce `[Vet complete — Phase 4/4 done]`, then read the findings sheet and present to the user:

**Findings Sheet (Google Sheet):** [link]

One-line count: e.g., "13 findings: 2 High, 6 Medium, 5 Low — 4 require researcher input"
