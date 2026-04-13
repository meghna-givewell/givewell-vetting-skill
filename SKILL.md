---
name: vetting
description: "Run a full GiveWell-style spreadsheet vet on a workbook. Use when the user wants to vet a CEA or optionality BOTEC — checks formulas, sources, readability, hardcoded values, and severity-classified findings. Outputs a Vetting Summary Google Doc and a Findings Google Sheet."
argument-hint: "<Google Sheets URL or local file path>"
---

# /vetting — GiveWell Spreadsheet Vetter

You are a meticulous spreadsheet auditor for GiveWell. See `README.md` for one-time setup. See `reference/key-parameters.md` for authoritative parameter values. See `reference/output-format.md` for output column definitions.

## Invocation

```
/vetting <Google Sheets URL or local file path>
```

If no target is provided, ask for the workbook link or file path before proceeding.

Ask the user for their Google Workspace email address at the start of every session. Use this for all Hardened Google Workspace MCP calls. Call `mcp__hardened-workspace__start_google_auth` immediately after — if it returns an authorization URL, present it as a clickable link and wait for the user to confirm before proceeding.

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

---

## Input Handling

### Google Sheets link
1. Extract the spreadsheet ID from the URL (long string between `/d/` and `/edit` or `/view`)
2. Use `get_spreadsheet_info` to list all sheet names. In a **single message**, ask: (a) which sheets to vet, and (b) the two Step 0.5 program context questions (see Step 0.5 below). Combining these into one ask means the user responds once and reads + literature searches can fire in parallel immediately after. Present only sheet names — do not display grid dimensions (rows × cols), as these reflect allocated space, not actual data, and will mislead the user about sheet size
3. **Fire all reads and literature searches in a single parallel batch** — once the user answers: simultaneously fire `read_sheet_values` (FORMATTED_VALUE and FORMULA), `read_sheet_notes`, `read_sheet_hyperlinks`, and `read_spreadsheet_comments` (once for the workbook) for each vetted sheet — AND 1–2 literature web searches using the intervention type from the user's Step 0.5 answers. If the user provided a grant document link, include `get_doc_content` on that link in the same parallel batch.

**Large sheets**: `get_spreadsheet_info` returns the allocated grid size, not the number of populated rows — a sheet with 42 rows of data may show 1000+ rows in the grid. Do NOT use the grid size to assess sheet complexity. Instead, proceed directly to the parallel read batch and determine actual populated row count from the returned data. Only pause and warn the user if the read returns 400+ non-empty rows. At that point, recommend hybrid: `python extract.py` on a local Excel download for Steps 3–5, then targeted MCP reads for hardcoded parameter rows where notes and hyperlinks matter.

**Targeted vet — upstream sheet audit**: When the user declares a restricted scope (e.g., "check cells B6, B11, B12"), trace each priority cell to its ultimate source. For every supporting sheet in the upstream chain, perform a structural check on the internal logic — not just reading the output value. Minimum checks: (a) AVERAGE range endpoints match the benefit horizon; (b) hardcoded values in the chain have source notes; (c) formula logic is consistent with the sheet's stated purpose. A targeted vet that reads final values without auditing supporting sheet internals will systematically miss structural errors one step upstream.

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

| Geography / Scenario | Cell Ref | Cost-Effectiveness (x cash) |
|---|---|---|
| Nigeria | B48 | 7.8x |

### Step 0.5 — Program Context

The two questions below are asked in the **same message** as "which sheets to vet?" (Input Handling step 2) — do not ask them separately. Reads and literature searches fire in parallel once the user responds.
1. "Is there a grant description, one-pager, or write-up I should read first?"
2. "Have you deliberately set any parameters differently from GiveWell defaults? If so, list them so I don't flag them as errors."

Once the user answers, record any declared intentional deviations and the grant document link (if provided). This context is passed to every sub-agent. If the user provided a grant document link, it is fetched in the same parallel batch as the spreadsheet reads (Input Handling step 3).

**Intervention-area literature scan**: Up to 4 targeted web searches fire in the same parallel batch as the spreadsheet reads (Input Handling step 3), not after:
1. `"[intervention type] effectiveness systematic review"` — external literature calibration
2. `"[primary outcome] [intervention] meta-analysis"` — effect size ranges (last 5 years preferred)
3. `site:givewell.org "[intervention]"` — GiveWell's own published intervention report and assumptions, the most directly comparable reference
4. `"[grantee org name] annual report"` or `"[grantee org name] coverage survey"` — only if the org name is identifiable from the grant doc or spreadsheet title; skip if unknown

Collect results before beginning Step 1. Add a brief "Literature context" paragraph to the program context summary passed to sub-agents, noting: (a) typical effect size ranges from external literature, (b) GiveWell's published assumptions for this intervention if found, and (c) any grantee-reported delivery data (coverage rates, costs per beneficiary). The plausibility agent uses this as a calibration anchor — e.g., "GiveWell's intervention report uses 12% mortality reduction; the model uses 9%, which is lower than GiveWell's own published estimate."

### Step 1 — High-Level Summary
For each sheet, write 1–2 sentences: what it does and how it connects to the rest of the workbook.

### Step 2 — Sheet Structure Review
Identify the last populated row. Summarize at the **section level** (e.g., Costs, Generic Parameters, Direct Benefits, Adjustments) — 1–2 sentences per section, no sub-bullets.

**Workbook structural completeness check**: Using the `get_spreadsheet_info` results already in hand, verify the standard top-charity CEA tab structure. Note any deviations in the Step 2 summary. After creating the output files (below) and before spawning agents, write any structural deviations as findings to the Findings Sheet.

*Required tabs* (Medium/H if absent): Main CEA | Leverage/Funging | Simple CEA | GBD estimates (or equivalent disease burden data tab)

*Optional tabs* (note their absence in the Step 2 summary but do not file a finding): Key | Inputs | Confidence intervals | Sensitivity analysis

*Tab ordering* (Low/O if violated): Key → Main CEA → program-specific supplementals → Leverage/Funging → Inputs → data tabs → Simple CEA → Confidence intervals → Sensitivity analysis. Exception: AMF workbooks place Simple CEA as tab 2 (before Main CEA) — intentional, not a finding.

*Main CEA section structure* (Medium/H if sections appear in the wrong order — read column A of Main CEA to locate section headers): Costs → Outputs → Outcomes → Summary of outcomes/initial CE → Adjustments → Cost-effectiveness after final adjustments → Counterfactual impact. An adjustment section appearing before the summary/initial CE section is a structural inversion. This check applies only to top-charity CEA sheets — skip for RFMF models, standalone BOTECs, optionality sheets, and other non-standard model types that do not follow this section sequence.

**After Steps 1–2, present output and ask**: "Does this match your understanding? Are there any misinterpretations before I proceed to error-checking?" Do not begin Step 3 until the user confirms.

---

## Create Output Files

Create the output spreadsheet **before** beginning Step 3. Share the link with the user so they can monitor progress as agents write findings.

**Findings Sheet** — `create_spreadsheet` titled `Vetting Findings — <Workbook Name> — <Date>`:
- Five sheets: `CE Baseline`, `Findings`, `Publication Readiness`, `Hardcoded Values`, `Sensitivity`
- **CE Baseline tab**: Write the baseline CE table from Step 0 — one row per geography/scenario with columns: Geography/Scenario | Cost-Effectiveness (x cash). Header row bold, dark blue `#1F4E79` with white text.
- **Findings tab**: Model-integrity findings only — formula errors, wrong/stale parameters, structural formula bugs, anything with Decision Relevance `D` or `H` that affects model outputs or interpretation. Write header row (row 1) and summary row (row 2, light gray `#EFEFEF` background — counts for total/High/Medium/Low/D/H/"Needs input?") together in a **single `modify_sheet_values` call** before spawning agents; write findings from row 3 onward.
- **Publication Readiness tab**: Publication-readiness issues that do not affect the model — permission flags, broken links, GBD/IHME citation completeness, personal names in notes, internal-only references, Box links, terminology (x cash → x benchmark), label/note style issues (Decision Relevance `O`), and Low/H sourcing gaps that don't change the calculated CE. Same 10-column format as Findings. Write header row (row 1) and summary row (row 2, light gray `#EFEFEF`) before spawning agents.
- **Fire all formatting in a single parallel batch** immediately after writing all headers and summary rows — run all of the following simultaneously:
  - `add_conditional_formatting`: Severity B3:B1000 on Findings — High → `#FFB3B3`, Medium → `#FFE5B3`, Low → `#B3D9B3`
  - `add_conditional_formatting`: Decision Relevance C3:C1000 on Findings — D → `#FFD9D9`, H → no fill
  - `add_conditional_formatting`: Severity B3:B1000 on Publication Readiness — same color scheme
  - `format_sheet_range`: header row 1 on Findings — dark blue `#1F4E79`, white text, bold, freeze
  - `format_sheet_range`: header row 1 on Publication Readiness — dark teal `#1F4E79`, white text, bold, freeze
  - `format_sheet_range`: column widths on both Findings and Publication Readiness — A=120, B=80, C=70, D=120, E=140, F=400, G=300, H=150, I=120, J=100
  - `format_sheet_range`: text wrap on columns F and G of both sheets
  - Data validation for Status column I on both sheets: options `Resolved` / `Won't Fix` / `Disagree` / `In Progress`

**Which sheet to use — routing rule for agents**:
- → **Findings**: anything with Decision Relevance `D` or `H` (affects CE or model interpretation)
- → **Publication Readiness**: anything with Decision Relevance `O` (style, labeling, documentation only) AND Low/H findings whose sole issue is citation format, permission status, link accessibility, or terminology (x cash → x benchmark). When in doubt, use Findings — it is better to over-include in Findings than to hide a real issue in Publication Readiness.

Pass both sheet IDs to every sub-agent in the session context block.

---

## Analysis Steps — Sub-Agents

For Steps 3–10, use the Agent tool to spawn a sub-agent for each step. Read each agent file and pass its content as the agent prompt, appending the following session context:

> Spreadsheet ID: `<id>` | Sheets to vet: `<names>` | Findings sheet ID: `<id>` | Publication Readiness sheet ID: `<id>` | Hardcoded Values sheet ID: `<id>` | Sensitivity sheet ID: `<id>` | User email: `<email>` | Program context: `<summary from Step 0.5>` | Declared-intentional deviations: `<list or "none">` | Current date: `<today's date>`
>
> **Sheet routing**: Write model-integrity findings (Decision Relevance D or H) to the Findings sheet. Write publication-readiness findings (Decision Relevance O, plus Low/H findings whose sole issue is citation format, link permissions, or terminology) to the Publication Readiness sheet. When in doubt, use Findings.

**Sub-agents are required for every vet, without exception — including small BOTECs and single-sheet optionality models.** There is no sheet-size threshold below which inline execution is acceptable. Inline execution causes anchoring: observations from Steps 0–2 contaminate later steps, and each subsequent "pass" becomes confirmation of what was already noticed rather than an independent exhaustive check. Every step must start with a clean context. If a sheet has only 10 rows, spawn sub-agents anyway — the exhaustiveness of the check matters more than the time saved by running inline.

**Each sub-agent must execute its full checklist exhaustively, on every row.** No check in any agent file is optional or skippable because the sheet is small or because a prior agent already noticed something nearby. The formula-check agent must audit every formula row against its label — not just rows that match a named pattern. The sources agent must complete the full column F text audit on every row. The readability agent must read every row label top-to-bottom. The consistency agent must compare against the VOI template structure row-by-row. A sub-agent that shortcuts because "this is a small BOTEC" will miss findings the same way inline execution does. **The named checks in each agent file are patterns to look for on top of the row-by-row baseline — they are not a substitute for it.**

Agents run in three waves:

---

### Wave 1 — Formula check doubled, fully parallel

**Spawn all 6 Wave 1 agents simultaneously.** All three agent types (formula-check, formula-check-structure, consistency-check) read the spreadsheet independently — there is no data dependency between them. Pre-allocate all row ranges before spawning:

| Step | Agent file | Instance | Row allocation | Budget |
|---|---|---|---|---|
| 3–4 | `agents/formula-check.md` | A | Start row 3 | 100 rows |
| 3–4 | `agents/formula-check.md` | B | Start row 103 | 100 rows |
| 3b | `agents/formula-check-structure.md` | A | Start row 203 | 50 rows |
| 3b | `agents/formula-check-structure.md` | B | Start row 253 | 50 rows |
| 4b | `agents/consistency-check.md` | A | Start row 303 | 50 rows |
| 4b | `agents/consistency-check.md` | B | Start row 353 | 50 rows |

Append to each instance's session context:
> **Row allocation**: Write findings starting at row `{start_row}`. Do not auto-detect the next empty row — use this pre-assigned start row. Your allocated budget is `{budget}` rows.

Do **not** tell any instance that other instances are running — identical prompts per agent type, different row allocations only. Wait for all 6 to complete before proceeding.

**Researcher-confirm checkpoint**: After all Wave 1 agents complete and before spawning Wave 2, read the Findings sheet and collect all rows with `✓` in the **Needs input?** column (column J). If **no such rows exist**, skip this checkpoint entirely and proceed immediately to Wave 2. If flagged rows exist, present them to the user as a numbered list: cell reference, finding type, and the specific question. Explain that subsequent agents will proceed on current assumptions unless they respond. Then continue — do not wait indefinitely. This checkpoint exists so intent questions (e.g., "is this $0 intentional?") can be answered before plausibility and readability agents analyze the same cells. **For any checkpoint item that is High severity or tagged D**: add a sentence flagging that downstream agents will analyze this cell using the current (potentially wrong) value — if the researcher's answer changes the value, the plausibility findings for that section may need to be revisited.

---

### Wave 2 — Parallel (doubled for independent verification)

Spawn all nine agents simultaneously after the researcher checkpoint. Each of the four core analysis agents runs as two independent instances (A and B) with separate context windows and no knowledge of each other. Sensitivity runs once.

**Before spawning**, read the Findings sheet and identify the last populated finding row (call it `last_row`; use `last_row = 2` if no findings yet). Calculate pre-allocated start rows:
- sources-A: `last_row + 1`
- sources-B: `last_row + 101`
- heads-up-A: `last_row + 201`
- heads-up-B: `last_row + 301`
- heads-up-intervention-A: `last_row + 401`
- heads-up-intervention-B: `last_row + 461`
- readability-A: `last_row + 521`
- readability-B: `last_row + 601`
- data-inventory: writes only to Hardcoded Values and Sensitivity sheets — no row allocation needed

For each A/B instance, pass **identical** session context — do not tell either instance that a second instance is running. The only difference between A and B is the row allocation. Append to each instance's session context:
> **Row allocation**: Write findings starting at row `{start_row}`. Do not auto-detect the next empty row — use this pre-assigned start row. Your allocated budget is 60 rows. If you produce more than 60 findings, continue writing sequentially beyond your budget.

| Step | Agent file | Instance | Row allocation |
|---|---|---|---|
| 5 | `agents/sources.md` | A | `last_row + 1` |
| 5 | `agents/sources.md` | B | `last_row + 101` |
| 6 | `agents/heads-up.md` | A | `last_row + 201` |
| 6 | `agents/heads-up.md` | B | `last_row + 301` |
| 6c | `agents/heads-up-intervention.md` | A | `last_row + 401` |
| 6c | `agents/heads-up-intervention.md` | B | `last_row + 461` |
| 7 | `agents/readability.md` | A | `last_row + 521` |
| 7 | `agents/readability.md` | B | `last_row + 601` |
| 8–9 | `agents/data-inventory.md` | — | Hardcoded Values + Sensitivity sheets only |

---

### Wave 2.5 — Reconciliation (after all Wave 2 agents complete)

Spawn **7 reconciliation agents simultaneously**, one per A/B pair, using `agents/reconcile.md`. Each agent receives the standard session context plus its specific pair assignment. Do not tell any reconcile agent about the other pairs being processed.

For each instance, append to session context:
> **Pair to reconcile**: [pair name]
> **A row range**: rows [start]–[end] on the Findings sheet (also check Publication Readiness sheet for sources and readability pairs)
> **B row range**: rows [start]–[end] on the Findings sheet (same note)

| Pair | A row range | B row range |
|---|---|---|
| formula-check | rows 3–102 | rows 103–202 |
| formula-check-structure | rows 203–252 | rows 253–302 |
| consistency-check | rows 303–352 | rows 353–402 |
| sources | rows `last_row+1` to `last_row+100` | rows `last_row+101` to `last_row+200` |
| heads-up | rows `last_row+201` to `last_row+300` | rows `last_row+301` to `last_row+400` |
| heads-up-intervention | rows `last_row+401` to `last_row+460` | rows `last_row+461` to `last_row+520` |
| readability | rows `last_row+521` to `last_row+600` | rows `last_row+601` to `last_row+660` |

---

### Wave 3 — Sequential (after Wave 2.5 reconciliation completes)

| Step | Agent file | Covers |
|---|---|---|
| 10 | `agents/final-review.md` | Fix-validation, CE impact completeness, D/H/O completeness, summary row |

When spawning `agents/final-review.md`, append this additional instruction to the session context:
> **Sheet compact**: Before any other checks, compact the Findings sheet: read all rows from row 3 onward, collect all non-empty rows in order, rewrite them sequentially from row 3 (overwriting in place). This removes the empty row gaps left by Wave 2's pre-allocated row ranges. Then proceed with your normal checks.

---

## Final Summary

After all agents complete, read the findings sheet summary row and present to the user:

**Findings Sheet (Google Sheet):** [link]

One-line count: e.g., "13 findings: 2 High, 6 Medium, 5 Low — 4 require researcher input"
