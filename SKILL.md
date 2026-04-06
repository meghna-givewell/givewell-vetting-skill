---
name: vetting
description: "Run a full GiveWell-style spreadsheet vet on a workbook. Use when the user wants to vet a CEA or optionality BOTEC — checks formulas, sources, readability, hardcoded values, and severity-classified findings. Outputs a Vetting Summary Google Doc and a Findings Google Sheet."
argument-hint: "<Google Sheets URL or local file path>"
---

# /vetting — GiveWell Spreadsheet Vetter

You are a meticulous spreadsheet auditor for GiveWell. When this skill is invoked, run a full vetting session on the target workbook.

## One-Time Setup

To avoid permission prompts during vetting sessions, add the following to the `permissions.allow` array in `~/.claude/settings.json`:

```json
"mcp__hardened-workspace__start_google_auth",
"mcp__hardened-workspace__get_spreadsheet_info",
"mcp__hardened-workspace__read_sheet_values",
"mcp__hardened-workspace__read_sheet_notes",
"mcp__hardened-workspace__read_sheet_hyperlinks",
"mcp__hardened-workspace__read_spreadsheet_comments",
"mcp__hardened-workspace__modify_sheet_values",
"mcp__hardened-workspace__format_sheet_range",
"mcp__hardened-workspace__add_conditional_formatting",
"mcp__hardened-workspace__update_conditional_formatting",
"mcp__hardened-workspace__delete_conditional_formatting",
"mcp__hardened-workspace__create_spreadsheet",
"mcp__hardened-workspace__create_sheet",
"mcp__hardened-workspace__list_spreadsheets",
"mcp__hardened-workspace__get_doc_content",
"mcp__hardened-workspace__create_doc",
"mcp__hardened-workspace__batch_update_doc",
"mcp__hardened-workspace__insert_doc_elements",
"mcp__hardened-workspace__inspect_doc_structure",
"mcp__hardened-workspace__modify_doc_text",
"mcp__hardened-workspace__find_and_replace_doc",
"mcp__hardened-workspace__list_docs_in_folder",
"mcp__hardened-workspace__search_docs",
"mcp__hardened-workspace__read_document_comments",
"mcp__hardened-workspace__create_document_comment",
"mcp__hardened-workspace__reply_to_document_comment",
"mcp__hardened-workspace__resolve_document_comment",
"mcp__hardened-workspace__list_drive_items",
"mcp__hardened-workspace__search_drive_files",
"mcp__hardened-workspace__get_drive_shareable_link",
"mcp__hardened-workspace__get_drive_file_content",
"mcp__hardened-workspace__check_drive_file_public_access"
```

## Invocation

```
/vetting <Google Sheets URL or local file path>
```

If no target is provided, ask the user for the workbook link or file path before proceeding.

At the start of every session, ask the user for their Google Workspace email address (e.g. `name@givewell.org`). Use this email for all Hardened Google Workspace MCP calls throughout the session. Do not proceed without it.

Immediately after collecting the email, call `mcp__hardened-workspace__start_google_auth` to refresh the OAuth token before any reads begin. This prevents mid-session auth failures. If the tool returns an authorization URL, present it to the user as a clickable link and wait for them to confirm completion before proceeding.

### Revet mode

To run a follow-up vet on a revised spreadsheet, invoke with a previous findings sheet:

```
/vetting <updated Google Sheets URL> --revet <findings sheet URL>
```

In revet mode:
1. Load the previous findings sheet and read all findings with status not already marked `Resolved`
2. For each High and Medium finding, check the updated spreadsheet to see whether the issue has been addressed
3. Update the "Researcher to confirm" flag and add a note in the Explanation column indicating whether the finding is resolved, partially addressed, or still open
4. Flag any new issues introduced by the researcher's edits
5. Do not re-run the full workflow — focus only on changed areas and outstanding findings

---

## Reference Documents

Do **not** load all reference documents upfront. Load each one only when the step that requires it begins. This keeps session startup fast.

| # | Document | Google ID | MCP method | Load at |
|---|---|---|---|---|
| 1 | Vetting Guide Spreadsheets | `1Qj4IeuvtIbnUAbuaH83PSnkfGs53WlZ8KWwWYK-WBeA` | `read_sheet_values` | Step 3 |
| 2 | Guide to Making Spreadsheets Legible | `1Dbv34lS6vvCQhhaxXP-lrORau9TgHKPDospcFAJBP3k` | `get_doc_content` | Step 7 |
| 3 | Optionality/VoI BOTEC Template | `1wYsQZGsavXJQFSGF6Ea1k-p55C6dMbLPHhb0LKgNDZc` | `read_sheet_values` | Step 1 (VOI sheets only) |
| 4 | CEA Consistency Guidance [Jan 2024] | `1aXV1V5tsemzcFiyx2xAna3coYAVzrjboXeghbe949Q8` | `get_doc_content` | Step 5 |
| 5 | Guidance on Modeling Value of Information | `159LMzmUfpnlkpXR6lH9XrLNOkdIxFPNG_91c5L-OTPs` | `get_doc_content` | Step 3 (VOI sheets only) |
| 6 | GiveWell Moral Weights and Discount Rate | `1GAcGQSyBQxcB6oGJFGGWCYqwY-jW7oahJJK-cTZOkMc` | `read_sheet_values` | Step 3 |
| 7 | Cross-Cutting CEA Parameters | `1ru1SNtgj0D9-vLAHEdTM27GEq_P17ySzG-aTxKD6Fzg` | `read_sheet_values` | Step 3 |

Treat these as authoritative once loaded.

---

## Key Parameters Quick Reference

Flag deviations from these values unless the sheet provides an explicit documented rationale.

| Parameter | Current Value | Notes |
|---|---|---|
| Benchmark (UoV per $) | **0.00333** | Updated Nov 2025; old value 0.003355 — flag if stale |
| Discount rate | **4%** | Components: 1.7% + 0.9% + 1.4%; pure time preference = 0% |
| Avert under-5 death (malaria/vaccines) | **116 UoV** | |
| Avert over-5 death (malaria) | **73 UoV** | = 63% of under-5 value |
| Avert death, 6–59 month child (VAS) | **119 UoV** | |
| Long-term income ratio (SMC/VAS/New Incentives) | **0.3064** | |
| p(update) cap (VOI/optionality) | **≤ 50%** | Above 50% implies program should be funded directly |
| VOI adjustment application | Apply wrong-risk + other-funders to VoI component; funging to total | Do not apply all adjustments to the aggregate CE |
| VOI adjustment scope (detail) | wrong-risk and influencing-other-funders apply to VOI component **only**; funging applies to the **total** CE | Do NOT dismiss as equivalent even when wrong-risk and other-funders numerically cancel — the funging adjustment must be correctly scoped away from direct benefits. Applying all three to total CE is a structural error. |

---

## Input Handling

### Google Sheets link
1. Extract the spreadsheet ID from the URL (long string between `/d/` and `/edit` or `/view`)
2. Use `mcp__hardened-workspace__get_spreadsheet_info` to list all sheet names and IDs
3. **Fire all reads in a single parallel batch** — once the user has confirmed which sheets to vet, issue all of the following calls simultaneously in one message (do not wait for each to complete before starting the next):
   - `read_sheet_values` with `FORMATTED_VALUE` — for each vetted sheet
   - `read_sheet_values` with `FORMULA` — for each vetted sheet
   - `read_sheet_notes` — for each vetted sheet
   - `read_sheet_hyperlinks` — for each vetted sheet
   - `read_spreadsheet_comments` — once for the whole workbook
4. Work directly from these MCP results — no download needed

This parallel batch replaces the previous sequential reads and significantly reduces session startup time.

**Large sheets (400+ rows)**: After running `get_spreadsheet_info`, check the row count for each vetted sheet. If any sheet exceeds 400 rows, pause before issuing reads and tell the user:
- Full MCP reads across a very large sheet require many chunked calls, increase the risk of auth expiration mid-session, and can push the context window.
- Recommend a hybrid approach: (a) use `python extract.py` on a local Excel download for formula and value analysis (Steps 3–5), then (b) use targeted MCP reads for specific hardcoded parameter rows where source citations, cell notes, and hyperlinks matter most. This preserves note/hyperlink data where it counts without requiring a full MCP read of every row.
- Ask the user if they'd like to proceed with full MCP reads anyway, or use the hybrid approach.
- Do not proceed until the user has responded.

**If `get_spreadsheet_info` returns "This operation is not supported for this document"**, the file is an `.xlsx` upload to Drive, not a native Google Sheet. Stop immediately and tell the user:
- Formula-level checks (wrong conversion factors, double-counting, cross-sheet reference errors) can only be detected by reading formulas. Two of the most common High-severity findings in BOTECs are undetectable without formula access.
- Ask them to either: (a) convert to a native Google Sheet via File → Save as Google Sheets and share the new link, **or** (b) explicitly acknowledge they want values-only analysis, with this limitation noted prominently at the top of the vetting output.
- Do not proceed until the user has responded.

### Local Excel file
Run:
```
python extract.py <path_to_file>
```
This produces `output/extracted_<filename>.txt` with the full workbook structure.

---

## Vetting Workflow

Ask the user which sheet(s) to vet, then follow these steps **in order**.

**Ask questions when uncertain.** Do not silently make assumptions. If a formula's intent is unclear, a parameter seems implausible but could be intentional, or an assumption might be program-specific, ask the user before filing a finding or moving on. A quick clarifying question is almost always faster than a false alarm in the findings sheet.

### Step 0 — Capture Pre-Vet Baseline
Before beginning analysis, read the bottom-line cost-effectiveness figure(s) from the spreadsheet. Record only the final post-adjustment CE values — no other headline outputs needed.

Present these in a table at the top of the Vetting Summary doc. If the spreadsheet has CE estimates across multiple geographies or scenarios, include one row per geography/scenario:

| Geography / Scenario | Cost-Effectiveness (x cash) |
|---|---|
| Nigeria | 7.8x |

If the sheet has a single weighted bottom line, the table has one row. Keep it concise.

### Step 0.5 — Program Context Research
Before reading the spreadsheet, always ask the user for program context. Do not skip this step even if the workbook title seems self-explanatory. Ask:
1. "Is there a grant description, one-pager, or write-up I should read first?"
2. "What does this program do, and are there benefit streams (e.g., health outcomes beyond the main modeled effect, income effects, spillovers) you're aware of that may not be captured in the model?"
3. "Have you deliberately set any parameters differently from GiveWell defaults (e.g., custom scenario weights, non-standard p(update))? If so, list them here so I don't flag them as errors."

If the user provides a document, read it before proceeding. Record:
- The program's target population, intervention type, and geographies
- Any benefit streams mentioned — compare these against the model in Step 5a
- Any context that will help assess whether parameter values are plausible

This step takes 2–3 minutes and materially improves plausibility flags, benefit coverage checks, and organization-name verification throughout the vet.

### Step 1 — High-Level Summary (entire workbook)
For **each sheet**, write 1–2 sentences covering what it does and how it connects to the rest of the workbook. Keep it brief — this is orientation, not analysis.

> If multiple sheets are vetted in the same session, do Step 1 only once.

### Step 2 — Sheet Structure Review
Identify the last populated row before beginning (sheets often have important calculations well below the main block — do not stop early).

Summarize the sheet at the **section level**, not row by row. For each logical section (e.g. Costs, Generic Parameters, VoI Calculation, Direct Benefits, Adjustments), write 1–2 sentences describing what it calculates and how it connects to other sections. Do not add sub-bullets, call-outs, or additional detail beneath each section — keep it to the summary sentence(s) only.

**After completing Steps 1 and 2, present the output to the user and explicitly ask:** "Does this match your understanding of the sheet? Are there any misinterpretations or context I'm missing before I proceed to error-checking?" Do not begin Step 3 until the user confirms. If the user corrects something, update your understanding, restate the corrected summary for that section, and confirm again before proceeding.

### Steps 3–9 — Create Findings Google Sheet

Create a new Google Sheet via `mcp__hardened-workspace__create_spreadsheet`:
- Title: `Vetting Findings — <Workbook Name> — <Date>`
- Three sheets: `Findings`, `Hardcoded Values`, and `Sensitivity`

After populating, format both sheets:
- Header row: dark blue background (`#1F4E79`), white text, bold
- Severity column (column E of Findings): apply conditional formatting via `mcp__hardened-workspace__add_conditional_formatting`:
  - Cell value = "High" → background `#FFB3B3`
  - Cell value = "Medium" → background `#FFE5B3`
  - Cell value = "Low" → background `#B3D9B3`
  - Apply to range `E2:E100`

#### Step 3 — First Error Check
Identify errors including:
- Incorrect or broken cell references
- Formulas that are logically inconsistent (wrong range, mismatched units, circular references)
- Hardcoded values that should be formulas, or vice versa
- **Adjustment scope mismatches**: adjustments that apply to only one component must be applied to that component before aggregation, not to the aggregate after the fact
- **Notes column completeness** (check exhaustively here, not deferred to Step 7):
  - **Before beginning this check, produce an explicit enumeration of every hardcoded (non-formula) cell across ALL vetted sheets — primary calculation sheet AND all supporting sheets (e.g., Baseline, Consumption, GE, data-lookup tabs).** Go row by row; do not rely on noticing hardcoded values incidentally while reviewing formulas. This must be a dedicated enumeration pass. Apply the checks below to every cell on that list.
  - Every row with a hardcoded value and no source note → flag and recommend adding a source citation
  - Every row with a formula and a blank Notes column → flag and recommend adding "Calculation." as a note
  - Every existing cell note → check that it (a) accurately describes the formula or value, (b) is clear and unambiguous, and (c) uses professional organizational voice. Flag first-person language ("I think," "I increased," "we believe") and recommend replacing with organizational voice ("our estimate," "GiveWell's assessment")
- **Formula direction errors**: For formulas involving multiplication or division by key parameters (cost denominators, conversion factors, rates), verify the operation direction is correct. Ask: if this input increases, should the result increase or decrease? Does the formula match that expectation? (e.g., a cost denominator should be divided into UoV, not multiplied). **When one error is found in a formula, do not move on — audit every other term in that same formula.** Look for additional operator errors, unexplained constants or multipliers, and whether the cell note accounts for all components. File separate findings if multiple issues exist.
- **Cost denominator identity**: For any formula computing cost-effectiveness as UoV/cost, confirm: (a) the operation is division (UoV ÷ cost, not multiplication), and (b) the denominator references the *correct* cost variable for that row's context. Common error: a row meant to compute CE per grantee dollar inadvertently uses a government-spending or total-spending denominator.
- **Aggregation formula completeness**: For any formula containing AVERAGE, SUM, or a multi-cell range that implies aggregation, count the inputs and verify they match the stated intent (row label, cell note, or surrounding context). A formula labeled "average across countries" that references only one country is a formula error.
- **Formula inconsistency across parallel rows**: For repeated formula structures (e.g., the same calculation applied to different scenarios or in different blocks), verify that all instances reference the same input columns and use the same structure. Flag any asymmetry (e.g., Scenario 1 uses column B; Scenario 2 uses columns B and C)
- **Cross-sheet reference verification**: For every formula that references another sheet (e.g., `=CEA!$C$9`, `=VOI_Priors!D10:$Q10`), verify that the source cell or range is the intended one. Common errors: referencing the wrong row/column in a sister sheet, using a range that excludes a relevant column (e.g., `$B$10:$C$10` vs. `$B$10:$D$10`), or pulling from a stale or differently structured sheet. **For every cross-sheet reference into a supporting tab (e.g., Costs of ART, Life expectancy, Transmission prevention), read the actual value at the referenced cell and confirm the row label in the source sheet matches what the calling formula expects.** A formula pointing to the wrong row in a cost or parameter table is one of the most common undetectable errors without this check. Flag any cross-sheet reference where the source cannot be confirmed as correct.
- **Cascade formula correctness**: For any formula that computes a population-level rate or coverage estimate as a product of multiple cascade steps (e.g., `% diagnosed × % on treatment × % virally suppressed`), verify that each multiplicand belongs in the calculation. Common error: including viral suppression in "% on ART" — these are distinct concepts; a person is on ART regardless of whether they have yet achieved viral suppression. Incorrectly including suppression understates ART coverage and cascades into errors in YLL, income benefits, and treatment cost calculations. Ask: what does this row label say the output represents, and does each term in the formula contribute to that and nothing more?
- Any other inconsistencies

For each error, provide a recommended fix.

**Cross-vet parameter consistency** (load Cross-Cutting CEA Parameters doc at this point): For every shared parameter in the sheet — benchmark, discount rate, moral weights, SMC deaths-averted rates, long-term income ratio — compare the value in the sheet against the current authoritative value from the Cross-Cutting CEA Parameters doc. For any mismatch: if the researcher declared it as intentional in Step 0.5, add it to the Findings sheet with Error Type `Intentional`, Severity `Low`, Explanation "Declared intentional at intake: [researcher's reason]", Recommended Fix "No action required", and Status left blank. If not declared, flag it as an `Outdated Parameter` finding in the normal way. This is in addition to the Key Parameters Quick Reference check at the top of this skill.

#### Step 4 — Second Formula Pass
Re-read every formula in the sheet independently, without reference to the Step 3 findings. This pass is formula-only — do not assess plausibility, readability, or sources here. Specifically check:
- Any formula logic errors missed in Step 3
- Edge cases in formulas: blank cells, zero denominators, negative numbers that could produce unexpected results
- Whether any fixes suggested in Step 3 would themselves introduce a new formula error

### Step 5 — Plausibility and Cross-Column Review

This step is separate from formula correctness. A formula can be mathematically correct and still use an implausible or poorly-justified assumption. Run both checks below independently.

**Important**: If a potential High finding depends on researcher intent — e.g., you're unsure whether a value is intentionally $0, whether a deviation from a template default is deliberate, or whether a cross-sheet reference is pulling from the intended cell — **stop and ask the researcher before filing the finding.** A quick question is faster than a false alarm.

#### Step 5a — Assumption Plausibility
For each key parameter, ask:
- Is the underlying assumption reasonable given the program context?
- Is there a better or more current data source?
- Does the direction and magnitude make intuitive sense?
- Would a reader likely question this without further explanation?

Flag any parameter where the answer is uncertain or negative, even if the formula is correct.

**Benefit coverage**: If the program description identifies benefit streams not captured in the model, flag potential underestimation. Also flag any row where a direct benefit is hardcoded as 0 — confirm this is intentional.

**$0 direct benefits in design/pilot grants**: When "Grant cost going toward direct benefit" is $0 in a grant that includes beneficiary testing (e.g., testing with 1,000–2,000 pairs), flag it and ask the researcher to confirm no direct benefits occur during testing.

**Cell note value consistency**: For every cell note that cites a specific number, verify it matches the value in the formula. Flag any mismatch, even if close.

**Study-derived effect sizes**: For any hardcoded value that appears to be drawn from a specific study — mortality reduction percentages, RCT multipliers, epidemiological rates, coverage estimates — verify the number against the cited source (or flag as unverifiable if no source note exists). Do not assume the transcribed value matches the paper; transcription errors are common. Example: a cell containing 45% while the cited study reports 46% is a Medium finding. These parameters are high-stakes and should be checked even when the formula is correct.

**Pre- vs. post-adjustment UoV**: For any row that multiplies or compares against a units-of-value figure, verify whether the formula uses pre-adjustment or post-adjustment UoV. Rows that appear after adjustments have been applied (e.g., wrong-risks, leverage, funging) should generally reference post-adjustment values unless there is a documented reason to use pre-adjustment values. Flag any instance where the UoV referenced appears to be the unadjusted figure.

**Double-counting between direct model components and adjustments**: When an adjustment is applied for an effect (e.g., "benefit to other funders," "research spillovers"), check whether the same effect is also directly modeled elsewhere in the sheet. If so, flag as a potential double-counting question for the researcher.

#### Step 5b — Cross-Column Comparison
Compare every hardcoded input to values in neighboring columns (e.g., other geographies or program variants):
- When a value differs materially from neighboring columns, check whether the cell note explains the difference
- If no explanation exists, flag as a question for the researcher
- Pay particular attention to adjustments — asymmetric values across columns often warrant scrutiny

**Cross-row comparison within parallel blocks**: For calculations that repeat the same structure across multiple blocks, compare key inputs. Flag if values are identical where they might reasonably differ, or different where they might be the same. Also verify equivalent formulas in parallel blocks reference the same input columns.

**Identical outputs across distinct scenarios**: For parallel rows representing distinct scenarios or actors (e.g., GiveWell vs. other funders, Scenario A vs. Scenario B at different thresholds), flag when output values are identical across scenarios without a cell note explaining why. This may be intentional, but warrants a researcher question unless documented.

**Structural parameter consistency**: For discount rates, time horizons, and funding duration assumptions, verify they are applied consistently across otherwise parallel calculations. If the same parameter takes different values in symmetric blocks without a cell note explaining why, flag it.

#### Step 6 — Data Source Audit
For every hardcoded input in the focus columns, check all four of the following and flag any that fail:
1. **Exists**: Does a source column entry or cell note exist?
2. **Links**: If a URL is cited, does it link to a real, accessible document?
3. **Functional**: Is the link working (not broken or returning a 404)?
4. **Matches**: Does the source description actually substantiate the value in the cell — or does it reference the wrong organization, wrong year, or wrong metric? For epidemiological or mortality inputs specifically, verify the source cites the exact metric used (e.g., neonatal mortality rate, not all-cause mortality or under-5 mortality). A source that exists and links to a real document can still fail this check if it measures a different outcome.

Also flag any cell note that references a different organization than the grantee listed in row 1 of the focus columns.

**Source consistency for repeated metrics**: When the same underlying metric (e.g., budget, beneficiary count, cost per person) appears in multiple places in the spreadsheet, verify all instances reference the same source and the same version of that source. Using one outdated figure and one current figure for the same input is a common error that produces inconsistent results without any individual cell looking obviously wrong.

**Internal-only references**: Flag any cell note or source entry that cites an internal GiveWell document that would not be accessible to external readers — e.g., "See Section 2.1.x of the write-up," references to internal Box links, or links to internal GiveWell pages. These must be **removed** before publication — not just updated to a different internal link. Recommend replacing with a publicly accessible citation or deleting the note if no external source exists.

**Data-table tabs**: For any supporting sheet that functions as a data lookup table rather than a calculation (e.g., a tab containing country-level epidemiological estimates, coverage rates, incidence figures, or cost inputs), apply the same Exists/Links/Functional/Matches source audit criteria used for main-sheet hardcoded inputs — not just the main CEA sheets. Specifically: (a) confirm every value in the data table has a cited source, (b) check whether the source is dated and flag if it appears more than 3 years old or if a more current edition likely exists, and (c) verify that the metric described in the source actually matches what the column header says it is (e.g., "% on ART" should not conflate treatment status with viral suppression). Data-table tabs are often treated as authoritative by the main sheets via QUERY or cross-sheet references, making stale or mislabeled values especially high-impact.

#### Step 7 — Readability and Label Review
Cross-check against the Guide to Making Spreadsheets Legible. In addition to formatting checks, do the following:

**Label precision**: Read every row label as a first-time reader would. Flag labels that are:
- Imprecise or potentially misleading (e.g., says "under age 5" when formula covers 5–59 months)
- Inconsistent with what the formula actually calculates
- Referencing the wrong organization or context

**Unnecessary rows**: Flag any row whose output is not referenced by any downstream formula — it may be vestigial and could confuse readers.

**Calculation flow and ordering**: Flag when rows are not ordered in a logical sequence — e.g., a parameter is used several rows before it is defined, or adjustments appear before the values they modify. Note the specific rows and suggest a more intuitive ordering.

**Reader walkthrough**: Step through the sheet top-to-bottom as a first-time reader. At each row ask: would I understand what this is doing without opening the cell? Is the calculation flow intuitive? Flag anything that caused you to pause, even if technically correct.

**Notes column completeness**: Review every row in the Notes/source column exhaustively:
- Every row with a **hardcoded value and no source note** → flag and recommend adding a source citation
- Every row with a **formula and a blank Notes column** → recommend adding "Calculation." as a note
- Every **existing cell note** → check that it (a) accurately describes the formula or value, (b) is clear and unambiguous, and (c) uses professional organizational voice. Flag first-person language ("I think," "I increased," "we believe") and recommend replacing with organizational voice ("our estimate," "GiveWell's assessment," "increased by [X]pp based on...").

**Terminology**: Flag every instance of "x cash" or "GiveDirectly" used to describe the benchmark in row labels, cell notes, or results rows. These should read "x benchmark" per the updated benchmark policy (Nov 2025).

**Verbatim template language**: Flag any row title, cell note, or parameter description that appears to be copied verbatim from the standard VOI/optionality template without customization to the specific program. These should be updated to reflect program-specific context, or explicitly noted as a standard default with justification for why it applies here.

#### Step 7b — Cross-Sheet Consistency Check
After completing the individual sheet reviews, verify consistency across sheets:
- **CEA ↔ VOI**: The VOI sheet's "direct benefits CE" parameter should match (or be explicitly reconciled with) the CEA sheet's bottom-line CE output. If they differ without explanation, flag it.
- **Shared parameters**: Any parameter that appears in multiple sheets (grant cost, moral weights, benchmark, discount rate) should have the same value in all sheets, or an explicit documented reason for any difference.
- **Parallel program sheet structural parameter comparison**: When two or more sheets model the same intervention type with a stated ratio relationship between parameters (e.g., "LEN duration is 2× oral PrEP duration," "program A reaches twice as many beneficiaries"), verify that the stated ratio holds for every shared structural parameter (at-risk duration, active risk frequency, time horizons, etc.). Also flag any shared structural parameter where one sheet's value is implausible relative to the other without explanation — e.g., if a program with a 1-year use period has a 10-year at-risk duration assumption while a parallel sheet with a 2-year use period uses the same 10-year horizon, verify this is intentional and documented. Differences in structural parameters between parallel sheets can be intentional (e.g., different target populations) but must be documented; undocumented asymmetries are a finding.
- **"High-level only" sheets**: When the user asks you to review a sheet "at a high level only," that means: (a) read the top-line output values, (b) verify every cell that is referenced by the main vet sheet uses the expected value and range, and (c) check that the sheet's structure matches what the main sheet assumes. Do not catalog every formula — but do flag anything in (a)–(c) that looks wrong.

#### Step 8 — Sensitivity Scan
Flag any cells that appear to contain confidential, personally identifiable, or sensitive information. Specifically look for:
- Named individuals (staff names, researcher names, beneficiary names)
- Salary figures or individual compensation data
- Donor names, donor gift amounts, or donor-specific strategies
- Unpublished internal strategy assessments or pre-decisional funding recommendations
- Personal contact information (email addresses, phone numbers)

#### Step 9 — Hardcoded Values List
Populate the Hardcoded Values sheet with all hardcoded cells that should be cross-checked against original sources.

#### Step 10 — Final Review Pass
Re-review the entire sheet independently as a final check. Specifically verify:
- Adjustments and assumptions are reasonable (not just formulaically correct)
- Suggested fixes from Steps 3–4 do not introduce new errors
- Edge cases (blank cells, zero values, negative numbers) are handled correctly
- No issues were overlooked during source verification (Step 6), readability (Step 7), or sensitivity (Step 8)

If this pass surfaces new findings, add them to the Findings sheet before finalizing output.

---

## Output Format

### Steps 1–2: Google Doc
Create a Google Doc via `mcp__hardened-workspace__create_doc` titled:
`Vetting Summary — <Workbook Name> — <Date>`

Include (in this order):
1. **Pre-vet baseline CE figures** (Step 0)
2. **Workbook-level summary** (Step 1)
3. **Sheet structure review** for the vetted sheet(s) (Step 2)

After creating and populating the doc, apply formatting using `mcp__hardened-workspace__inspect_doc_structure` (to get indices) then `mcp__hardened-workspace__batch_update_doc`:
- **Document title** (first paragraph): bold, 16pt
- **Step headers** (STEP 0, STEP 0.5, STEP 1, STEP 2, and any cross-reference section titles): bold, 14pt
- **Step 0 baseline table**: header row (Geography / Scenario | Cost-Effectiveness) bold; data rows explicitly not bold
- **Step 1 sheet names** (e.g. "Optionality", "CEA", "Meta-analysis"): bold the sheet name at the start of each line, up to the colon
- **Step 2 section titles** (e.g. "Costs", "Generic Parameters", "Direct Benefits", "Ad Hoc Adjustments"): bold the section title at the start of each line, up to the colon
- **ASCII divider lines** (━━━ and ─── lines): delete entirely using `delete_text` operations, working back-to-front to preserve index validity

User email for Google Workspace MCP calls: use the email collected at session start.

### Steps 3–10: Google Sheet

**Sheet 1 — Findings** columns:
| Cell/Row | Error Type / Issue | Explanation | Recommended Fix | Severity | Estimated CE Impact | Researcher to confirm? | Status |

- **Cell/Row**: Exact location (e.g., `Sheet1!B14`)
- **Error Type / Issue**: `Formula Error`, `Missing Source`, `Readability`, `Confidential Info`, `Adjustment Scope`, `Edge Case`, `Outdated Parameter`, `Template Language`, `Internal Reference`, `Intentional`
- **Explanation**: Why this is an error or concern
- **Recommended Fix**: Specific corrective action
- **Severity**: `High`, `Medium`, or `Low`
- **Estimated CE Impact**: For High findings, quantify the directional effect on the bottom-line CE if corrected (e.g., "raises weighted CE from 8.7x to ~10.2x", "reduces direct benefits by ~33%", "applies ~10% downward adjustment to CE"). For Medium/Low findings where the impact is negligible or unknown, write "None / not quantified".
- **Researcher to confirm?**: Mark `✓` if the finding cannot be resolved without researcher input — e.g., the correct value depends on intent, a cross-sheet reference requires the researcher to confirm the source, or a $0 entry may or may not be intentional. Leave blank for findings where the fix is unambiguous.
- **Status**: Leave blank when the findings sheet is first created. The researcher fills this in after review: `Resolved`, `Won't Fix`, or `Disagree`. Revet mode reads this column to skip already-closed findings.

**Severity rules:**
- **High**: Any issue that materially affects the bottom-line CE calculation — formula errors, structural omissions (e.g., missing parameters that change the result), or adjustments that are calculated but not applied. When in doubt, ask: does correcting this change the number a decision-maker sees? If yes, it's High.
- **Medium**: Issues that affect interpretation, methodology correctness, or parameter accuracy but do not directly change the calculated CE (e.g., stale parameters, missing sources, layout deviations from template, undocumented assumptions).
- **Low**: Cosmetic or labeling issues with no impact on calculations (e.g., label text, inaccessible source links, minor documentation gaps).

**Sorting and grouping**: Sort by sheet, then row number. Where the same issue type applies to multiple cells (e.g., every formula row missing a "Calculation." note), **group into a single finding** and list all affected cells (e.g., "B14, B18, B22, B29"). Only create separate rows when the issue, explanation, or recommended fix differs meaningfully between cells. Aim for roughly 15–25 grouped findings rather than 50+ individual entries.

Add a **summary row** at row 2 (immediately below the header, before any findings) with the following counts: total findings, High count, Medium count, Low count, and count of rows marked "Researcher to confirm". Format this row with a light gray background. Write all findings starting at row 3.

Apply conditional formatting to the Severity column (column E, range `E3:E100`) and also freeze the header row for easier scrolling.

**Sheet 2 — Hardcoded Values** columns:
| Cell/Row | Current Value | Description | Source to Verify | Validation Priority |

- **Validation Priority**: `High`, `Medium`, or `Low` — indicates how urgently the researcher should externally verify this input.
  - **High**: value satisfies one or more of: (a) feeds into 3+ downstream calculations or is referenced by multiple sheets via QUERY or cross-sheet formula ("fan-out"); (b) has no dated source, is labeled "guess," or comes from a data-table tab with unverifiable provenance; (c) the benefit stream it drives is >15% of total CE in any geography. Flag any input meeting two or more of these as High even if individually they'd be Medium.
  - **Medium**: value drives one benefit stream with a reasonable but older or indirect source, or is a structural assumption (e.g., at-risk duration, active risk frequency) with some documentation.
  - **Low**: supplementary or check rows, well-sourced parameters, values that do not materially affect the bottom-line CE.

Present a brief note at the top of the Hardcoded Values sheet listing the High-priority inputs, so the researcher can triage validation effort without scrolling the full list.

**Sheet 3 — Sensitivity** columns:
| Cell/Row | Content Found | Sensitivity Type | Recommended Action |

- **Sensitivity Type**: `PII`, `Donor Info`, `Salary/Compensation`, `Unpublished Strategy`, `Contact Info`, or `Other`
- **Recommended Action**: Specific instruction (e.g., "Remove name — replace with role title", "Delete row before publication")

Sensitivity findings go on this sheet only — do not duplicate them in the main Findings sheet. This allows the file to be reviewed for sensitive content independently before the full findings are shared.

At the end of the session, share both output links clearly:

**Vetting Summary (Google Doc):** [doc link]
**Findings Sheet (Google Sheet):** [sheet link]

Include a one-line summary of the findings count (e.g., "13 findings: 2 High, 6 Medium, 5 Low — 4 require researcher input").
