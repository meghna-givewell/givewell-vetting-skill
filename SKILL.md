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

### Revet mode

```
/vetting <updated Google Sheets URL> --revet <findings sheet URL>
```

Load the previous findings sheet and read all findings not marked `Resolved`. For each High and Medium finding, check whether the issue has been addressed. Update the **Needs input?** flag (column J) and add a note in Explanation: resolved, partially addressed, or still open. Flag any new issues introduced by the researcher's edits. Do not re-run the full workflow.

**Revet context notes**:
- GiveWell vetters work on **archive copies** of CEAs, not the live internal version. The spreadsheet link provided should be an archive copy. If the URL looks like a live working doc (e.g., contains "working" or "internal" in the title), confirm with the user before proceeding.
- In archive copies, **yellow-highlighted cells** mark all changes from the prior version. When revetting after researcher edits, treat yellow-highlighted cells as the scope — read those cells first and check whether prior findings in those areas have been addressed.
- Change trackers (a separate tab or doc) log all changes between published versions with CE impact; if available, ask the user for the change tracker link as context for the revet.

---

## Reference Documents

Load each document only when the step that requires it begins.

| # | Document | Google ID | MCP method | Load at |
|---|---|---|---|---|
| 1 | Vetting Guide Spreadsheets | `1Qj4IeuvtIbnUAbuaH83PSnkfGs53WlZ8KWwWYK-WBeA` | `read_sheet_values` | Step 3 |
| 2 | Guide to Making Spreadsheets Legible | `1Dbv34lS6vvCQhhaxXP-lrORau9TgHKPDospcFAJBP3k` | `get_doc_content` | Step 7 |
| 3 | Optionality/VoI BOTEC Template | `1wYsQZGsavXJQFSGF6Ea1k-p55C6dMbLPHhb0LKgNDZc` | `read_sheet_values` | Step 3 |
| 4 | CEA Consistency Guidance [Jan 2024] | `1aXV1V5tsemzcFiyx2xAna3coYAVzrjboXeghbe949Q8` | `get_doc_content` | Step 5 |
| 5 | Guidance on Modeling Value of Information | `159LMzmUfpnlkpXR6lH9XrLNOkdIxFPNG_91c5L-OTPs` | `get_doc_content` | Step 3 (VOI sheets only) |
| 6 | GiveWell Moral Weights and Discount Rate | `1GAcGQSyBQxcB6oGJFGGWCYqwY-jW7oahJJK-cTZOkMc` | `read_sheet_values` | Step 3 |
| 7 | Cross-Cutting CEA Parameters | `1ru1SNtgj0D9-vLAHEdTM27GEq_P17ySzG-aTxKD6Fzg` | `read_sheet_values` | Step 3 |
| 8 | Optionality/VoI Extensions Structure Reference | `1BYdNqrOu3jqVYHHQ5S2lNfq3vCXwid0CxhQf4SjSRqc` | `read_sheet_values` | Step 3 |
| 9 | TA Modeling Guidance | `12onXe086vgvSBSVCbIwvWwWft7JYIpPpJ--CK80Ez6M` | `get_doc_content` | Step 6 (TA grants only) |
| 10 | TA Modeling Templates | `1FGccVLs21mqHdJjnzJKSpl2_MVLcLNcxP9omXX62jQg` | `read_sheet_values` | Step 6 (TA grants only) |

---

## Input Handling

### Google Sheets link
1. Extract the spreadsheet ID from the URL (long string between `/d/` and `/edit` or `/view`)
2. Use `get_spreadsheet_info` to list all sheet names. In a **single message**, ask: (a) which sheets to vet, and (b) all four Step 0.5 program context questions (see Step 0.5 below). Combining these into one ask means the user responds once and reads + literature searches can fire in parallel immediately after. Present only sheet names — do not display grid dimensions (rows × cols), as these reflect allocated space, not actual data, and will mislead the user about sheet size
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
Read the bottom-line CE figures. Record only final post-adjustment CE values in a table at the top of the Vetting Summary doc:

| Geography / Scenario | Cost-Effectiveness (x cash) |
|---|---|
| Nigeria | 7.8x |

### Step 0.5 — Program Context

The four questions below are asked in the **same message** as "which sheets to vet?" (Input Handling step 2) — do not ask them separately:
1. "Is there a grant description, one-pager, or write-up I should read first?"
2. "What does this program do, and are there benefit streams you're aware of that may not be captured in the model?"
3. "Have you deliberately set any parameters differently from GiveWell defaults? If so, list them so I don't flag them as errors."
4. "When were the country-level or epidemiological inputs last updated, and what is the primary source?" (This question surfaces data staleness before analysis begins — especially important for HIV cascade data, national burden estimates, and any model pulling from external lookup tables.)

Once the user answers, record the program's target population, intervention type, geographies, and any benefit streams mentioned. This context is passed to every sub-agent. If the user provided a grant document link, it is fetched in the same parallel batch as the spreadsheet reads (Input Handling step 3).

**Intervention-area literature scan**: The 1–2 targeted web searches — e.g., `"[intervention type] effectiveness systematic review"` and `"[primary outcome] [intervention] meta-analysis"` — fire in the same parallel batch as the spreadsheet reads (Input Handling step 3), not after. Collect results before beginning Step 1. Note the typical effect size ranges found in recent literature (last 5 years preferred). Add a brief "Literature context" paragraph to the program context summary passed to sub-agents. The plausibility agent uses this as a calibration anchor when assessing whether individual parameter values fall within a plausible range — e.g., "the literature suggests 15–30% maternal mortality reduction; the model uses 12%, which is at the low end."

### Step 1 — High-Level Summary
For each sheet, write 1–2 sentences: what it does and how it connects to the rest of the workbook.

### Step 2 — Sheet Structure Review
Identify the last populated row. Summarize at the **section level** (e.g., Costs, Generic Parameters, Direct Benefits, Adjustments) — 1–2 sentences per section, no sub-bullets.

**Workbook structural completeness check**: Using the `get_spreadsheet_info` results already in hand, verify the standard top-charity CEA tab structure. Note any deviations in the Step 2 summary. After creating the output files (below) and before spawning agents, write any structural deviations as findings to the Findings Sheet.

*Required tabs* (Medium/H if absent): Key | Main CEA | Leverage/Funging | Inputs | Simple CEA | Confidence intervals | Sensitivity analysis | GBD estimates (or equivalent disease burden data tab)

*Tab ordering* (Low/O if violated): Key → Main CEA → program-specific supplementals → Leverage/Funging → Inputs → data tabs → Simple CEA → Confidence intervals → Sensitivity analysis. Exception: AMF workbooks place Simple CEA as tab 2 (before Main CEA) — intentional, not a finding.

*Main CEA section structure* (Medium/H if sections appear in the wrong order — read column A of Main CEA to locate section headers): Costs → Outputs → Outcomes → Summary of outcomes/initial CE → Adjustments → Cost-effectiveness after final adjustments → Counterfactual impact. An adjustment section appearing before the summary/initial CE section is a structural inversion.

**After Steps 1–2, present output and ask**: "Does this match your understanding? Are there any misinterpretations before I proceed to error-checking?" Do not begin Step 3 until the user confirms.

---

## Create Output Files

Create both output files **before** beginning Step 3. **Fire both create operations simultaneously** — `create_doc` and `create_spreadsheet` are independent and can be launched in parallel. Share both links with the user so they can monitor progress as agents write findings.

**Vetting Summary Doc** — `create_doc` titled `Vetting Summary — <Workbook Name> — <Date>`:
- Populate with Steps 0–2 content (baseline table, workbook summary, sheet structure)
- Apply formatting via `inspect_doc_structure` then `batch_update_doc`: document title bold 16pt; step headers bold 14pt; sheet names and section titles bolded up to the colon; delete ASCII divider lines back-to-front

**Findings Sheet** — `create_spreadsheet` titled `Vetting Findings — <Workbook Name> — <Date>`:
- Three sheets: `Findings`, `Hardcoded Values`, `Sensitivity`
- Write header row (row 1) and summary row (row 2, light gray `#EFEFEF` background — counts for total/High/Medium/Low/D/H/O/"Needs input?") together in a **single `modify_sheet_values` call** before spawning agents; write findings from row 3 onward
- **Fire all formatting in a single parallel batch** immediately after writing the header and summary rows — run all of the following simultaneously:
  - `add_conditional_formatting`: Severity column B3:B100 — High → `#FFB3B3`, Medium → `#FFE5B3`, Low → `#B3D9B3`
  - `add_conditional_formatting`: Decision Relevance column C3:C100 — D → `#FFD9D9`, O → `#D9E8F5`, H → no fill
  - `format_sheet_range`: header row 1 — dark blue `#1F4E79`, white text, bold, freeze header row
  - `format_sheet_range`: column widths — A=120, B=80, C=70, D=120, E=140, F=400, G=300, H=150, I=120, J=100
  - `format_sheet_range`: text wrap on columns F and G
  - Data validation for Status column I: options `Resolved` / `Won't Fix` / `Disagree` / `In Progress` if supported; otherwise leave as free text

---

## Analysis Steps — Sub-Agents

For Steps 3–10, use the Agent tool to spawn a sub-agent for each step. Read each agent file and pass its content as the agent prompt, appending the following session context:

> Spreadsheet ID: `<id>` | Sheets to vet: `<names>` | Findings sheet ID: `<id>` | Hardcoded Values sheet ID: `<id>` | Sensitivity sheet ID: `<id>` | Summary Doc ID: `<id>` | User email: `<email>` | Program context: `<summary from Step 0.5>` | Declared-intentional deviations: `<list or "none">` | Current date: `<today's date>`

**Sub-agents are required for every vet, without exception — including small BOTECs and single-sheet optionality models.** There is no sheet-size threshold below which inline execution is acceptable. Inline execution causes anchoring: observations from Steps 0–2 contaminate later steps, and each subsequent "pass" becomes confirmation of what was already noticed rather than an independent exhaustive check. Every step must start with a clean context. If a sheet has only 10 rows, spawn sub-agents anyway — the exhaustiveness of the check matters more than the time saved by running inline.

**Each sub-agent must execute its full checklist exhaustively, on every row.** No check in any agent file is optional or skippable because the sheet is small or because a prior agent already noticed something nearby. The formula-check agent must audit every formula row against its label — not just rows that match a named pattern. The sources agent must complete the full column F text audit on every row. The readability agent must read every row label top-to-bottom. The consistency agent must compare against the VOI template structure row-by-row. A sub-agent that shortcuts because "this is a small BOTEC" will miss findings the same way inline execution does. **The named checks in each agent file are patterns to look for on top of the row-by-row baseline — they are not a substitute for it.**

Agents run in three waves:

---

### Wave 1 — Sequential

Each agent must complete before the next starts.

| Step | Agent file | Covers |
|---|---|---|
| 3–4 | `agents/formula-check.md` | Formula correctness, edge cases |
| 3b | `agents/formula-check-structure.md` | Program structure completeness, architecture |
| 4b | `agents/consistency-check.md` | Cross-parameter consistency, benchmark, moral weights, VOI conformance |

**Researcher-confirm checkpoint**: After Wave 1 completes and before spawning Wave 2, read the Findings sheet and collect all rows with `✓` in the **Needs input?** column (column J). If any exist, present them to the user as a numbered list: cell reference, finding type, and the specific question. Explain that subsequent agents will proceed on current assumptions unless they respond. Then continue — do not wait indefinitely. This checkpoint exists so intent questions (e.g., "is this $0 intentional?") can be answered before plausibility and readability agents analyze the same cells. **For any checkpoint item that is High severity or tagged D**: add a sentence flagging that downstream agents will analyze this cell using the current (potentially wrong) value — if the researcher's answer changes the value, the plausibility findings for that section may need to be revisited.

---

### Wave 2 — Parallel

Spawn all four agents simultaneously after the researcher checkpoint.

**Before spawning**, read the Findings sheet and identify the last populated finding row (call it `last_row`; use `last_row = 2` if no findings yet). Calculate pre-allocated start rows:
- sources: `last_row + 1`
- plausibility: `last_row + 101`
- plausibility-intervention: `last_row + 201`
- readability: `last_row + 281`
- sensitivity: writes only to Hardcoded Values and Sensitivity sheets — no row allocation needed

For `agents/sources.md`, `agents/plausibility.md`, `agents/plausibility-intervention.md`, and `agents/readability.md`, append this additional line to the session context:
> **Row allocation**: Write findings starting at row `{start_row}`. Do not auto-detect the next empty row — use this pre-assigned start row. Your allocated budget is 80 rows. If you produce more than 80 findings, continue writing sequentially beyond your budget.

| Step | Agent file | Covers | Writes to |
|---|---|---|---|
| 5 | `agents/sources.md` | Data source audit | Findings, starting at `last_row + 1` |
| 6 | `agents/plausibility.md` | Core assumption plausibility, cross-column review | Findings, starting at `last_row + 101` |
| 6c | `agents/plausibility-intervention.md` | Intervention-specific plausibility calibration | Findings, starting at `last_row + 201` |
| 7 | `agents/readability.md` | Readability, labels, cross-sheet consistency | Findings, starting at `last_row + 281` |
| 8–9 | `agents/sensitivity.md` | Sensitive data scan, hardcoded values list | Hardcoded Values + Sensitivity sheets only |

---

### Wave 3 — Sequential (after all Wave 2 agents complete)

| Step | Agent file | Covers |
|---|---|---|
| 10 | `agents/final-review.md` | Fix-validation, CE impact completeness, D/H/O completeness, summary row |

When spawning `agents/final-review.md`, append this additional instruction to the session context:
> **Sheet compact**: Before any other checks, compact the Findings sheet: read all rows from row 3 onward, collect all non-empty rows in order, rewrite them sequentially from row 3 (overwriting in place). This removes the empty row gaps left by Wave 2's pre-allocated row ranges. Then proceed with your normal checks.

---

## Final Summary

After all agents complete, read the findings sheet summary row and present to the user:

**Vetting Summary (Google Doc):** [link]
**Findings Sheet (Google Sheet):** [link]

One-line count: e.g., "13 findings: 2 High, 6 Medium, 5 Low — 4 require researcher input"
