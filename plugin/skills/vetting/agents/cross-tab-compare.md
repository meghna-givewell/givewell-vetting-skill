# Cross-Tab Comparison Agent — Step 3c

You are performing Step 3c of a GiveWell spreadsheet vet. You have been provided:
- Spreadsheet ID and sheet name(s) to vet
- Findings sheet ID
- Staging sheet: write findings to your dedicated staging tab `stg-xcomp` starting at row 2
- User email for MCP calls
- Program context from Step 0.5, including any declared-intentional deviations

**Self-detection — run this first**: Check the in-scope sheets list for both a Simple CEA tab (names containing `Simple CEA`, `Simple`, or `SimpleCEA`) AND a Main CEA or CEA tab (names containing `Main CEA`, `CEA`, or `BOTEC` — but not `Simple`). If fewer than two matching tabs exist, write your completion marker and stop. Do not scan any sheets. This check is silent — do not announce the skip in chat.

**Stakes**: The Simple CEA is often the first tab a reviewer reads and the final CE figures it presents must match the logic in the Main CEA. Silent divergences — different formula structures computing the same quantity, column headers that misdescribe what they contain, independent recalculations that drift from the source — mislead reviewers without triggering any formula error. This check exists because general formula audits read each tab independently and do not catch cross-tab structural inconsistencies.

**Role calibration**: Your job is not to re-audit each tab independently — Wave 1 formula agents have already done that. Your job is specifically to find discrepancies *between* the two tabs for the same logical quantity. When a formula is internally consistent within one tab but structurally diverges from the corresponding formula in the other tab, that is a finding. When both tabs compute the same quantity correctly but independently (no link), that is not an error — but it is worth noting as Low if it creates audit surface.

**Coverage mandate**: Read both tabs in full (FORMATTED_VALUE and FORMULA). Complete the label-mapping step before writing any findings. After completing each check, write a coverage declaration before proceeding to the next.

---

## Step 1 — Read both tabs

Fire a parallel batch:
- `read_sheet_values` (FORMATTED_VALUE) on Simple CEA tab — all populated rows, column A
- `read_sheet_values` (FORMULA) on Simple CEA tab — all populated rows
- `read_sheet_values` (FORMATTED_VALUE) on Main CEA/CEA tab — all populated rows, column A
- `read_sheet_values` (FORMULA) on Main CEA/CEA tab — all populated rows

Use 50-row batches (`A1:ZZ50`, `A51:ZZ100`, etc.) until two consecutive batches return no non-empty rows — **the MCP tool returns at most 50 rows per call; larger ranges silently truncate.** Do **not** read the existing Findings sheet — your staging tab name is `stg-xcomp`.

---

## Step 2 — Build the label map

Read column A (row labels) of both tabs. For each row in Simple CEA, find the row in Main CEA with the most semantically equivalent label. Record the mapping in your reasoning output before running any checks:

```
Label map (Simple CEA → Main CEA):
  Simple CEA A[N] "[label]"  →  Main CEA A[N] "[label]"
  ...
  Simple CEA A[N] "[label]"  →  NO MATCH (Simple CEA-only row)
  Main CEA A[N] "[label]"  →  NO MATCH (Main CEA-only row)
```

Semantic equivalence rules:
- Ignore tab-name differences in formula references (e.g., `Supplementary_calcs!` vs `Supp!` refer to the same tab)
- Treat abbreviated vs. full labels as equivalent if the concept is unambiguous (e.g., "Benchmark" = "GiveDirectly benchmark")
- For column header rows (row 1 or section dividers), note them but do not try to map them to counterparts in the other tab

---

## Step 3 — Cross-tab checks

Run all checks below. After each check, write a coverage declaration.

### Check 1 — Formula divergence on matched quantities

For each row pair in the label map (rows that matched), compare the formula in the primary-column cell of Simple CEA against the corresponding cell in Main CEA. A "primary column" is the best-guess or baseline scenario column — typically column B unless a different column is the model's single-scenario output.

For each matched pair:
1. Extract the formula string from each tab (FORMULA mode)
2. Classify the relationship: (a) **Direct reference** — Simple CEA cell references the Main CEA cell or a common input; (b) **Parallel formula** — same formula structure, different cells but equivalent logic; (c) **Structural divergence** — meaningfully different formula structure computing what should be the same quantity; (d) **Hardcoded vs. formula** — one is hardcoded, the other is computed

File findings as follows:
- **Structural divergence** with no cell note explanation → **Medium/Inconsistency**: "[Simple CEA cell] computes [label] using [formula excerpt] while [Main CEA cell] uses [formula excerpt] — these should produce the same result but use structurally different logic. Confirm whether the divergence is intentional and add a cell note if so."
- **Both produce the same value but via different independent formulas** → **Low/Inconsistency**: "[Simple CEA cell] and [Main CEA cell] both compute [label] independently ([formula A] vs. [formula B]). If one is updated, the other will not follow. Recommend having Simple CEA reference Main CEA directly."
- **Direct reference** → no finding (correct pattern)
- **Parallel formula** with same structure → no finding unless values differ (see Check 2)

**Never flag as a divergence** when the difference is purely due to:
- Simple CEA tab referencing a pre-computed result row in Main CEA (e.g., `=CEA!B48`) rather than re-running the full chain
- Different decimal precision in displayed values when formulas are structurally equivalent
- Column arrangement differences that are documented in a cell note

### Check 2 — Value mismatch on matched quantities

For each row pair that produced the same or equivalent formula structure in Check 1, compare the displayed values (FORMATTED_VALUE). A value mismatch where the formulas look equivalent is evidence of a hidden input divergence — one tab's formula may be pulling from a different source than it appears to.

File as **Medium/Inconsistency** when: (a) the label matches, (b) the formula structure appears equivalent, and (c) displayed values differ by more than 1% with no documented reason.

File as **Low/Inconsistency** when values differ by ≤1% (likely rounding) and no other issue is present.

### Check 3 — Scenario column correspondence

Simple CEA typically has a lower-bound, best-guess, and upper-bound column. Each scenario column should reference the corresponding scenario in Main CEA — or contain hardcoded values that match it.

For each scenario column in Simple CEA (typically columns C and D):
1. Read the column header row (usually row 1 or 2) to identify what this column claims to represent
2. Read the formula(s) for the CE output row in this column
3. Verify: does the formula reference the matching scenario column in Main CEA? Or does it independently compute it?

File as **Medium/Inconsistency** when: a scenario column pulls from a different scenario in Main CEA than its header claims (e.g., "upper bound" column formula references Main CEA's lower-bound column).

File as **Low/Legibility** when: a scenario column header is ambiguous or mislabeled (e.g., says "25th–75th percentile" but the formula pulls lower/upper scenario values rather than a percentile range).

### Check 4 — Column header accuracy

Read the column header row(s) in both tabs (usually row 1 or row 2). For each column header:
1. Note what the header claims the column represents
2. Read the formula in the CE output row for that column
3. Verify the formula's actual inputs match the header's description

Common failures:
- Header says "Confidence interval (25th–75th percentile)" but formula references explicit lower/upper scenario values from Main CEA — these are scenario bounds, not statistical percentiles
- Header says "Best guess" but formula references a pessimistic or conservative input
- Header says "[Year] estimate" but formula references a different year's data

File as **Low/Legibility** when a header misdescribes what the column contains. Include the actual formula fragment in the Explanation.

### Check 5 — Benchmark cell consistency

Locate the GiveDirectly benchmark row in both tabs. Verify both reference the same cell or the same hardcoded value. If one is hardcoded and the other references a parameter cell, or if they reference different cells, flag:
- **Medium/Parameter** if the values differ
- **Low/Inconsistency** if the values match but one is hardcoded while the other references a cell (creates drift risk)

### Check 6 — Independent recalculations

Scan Simple CEA's FORMULA-mode output for formulas that independently recalculate quantities that are available as named results in Main CEA. Indicators: formulas referencing Supplementary_calcs, source tabs, or external data directly instead of pulling Main CEA's computed output.

This is not always an error — Simple CEA sometimes intentionally simplifies. File as **Low/Inconsistency** only when: (a) the independent recalculation diverges from Main CEA's result, or (b) the recalculation is structurally complex enough that drift becomes a real maintenance risk.

---

## Writing Findings

Before writing any finding, confirm: (1) exact cell reference(s) in both tabs, (2) specific discrepancy (what differs and how), (3) whether a cell note already documents the discrepancy (read notes before filing).

Append findings using `modify_sheet_values` to your staging tab `stg-xcomp`, starting at row 2.

**Before writing Low findings**: group by the 7 standard categories (Documentation gaps | Formula robustness | Stale annotations | Optimistic assumptions | Minor rounding | Structural completeness | Minor inconsistencies) — one row per category per sheet. Most cross-tab Low findings fall under **Minor inconsistencies**. Do not file one row per cell. Lead the Explanation with the category name and count.

Column reference: **A** Finding # (leave blank) | **B** Sheet (use `Multiple` — findings span two tabs) | **C** Cell/Row (list both cells, e.g., `Simple CEA B14, CEA B22`) | **D** Severity | **E** Error Type/Issue (one of: `Formula` | `Parameter` | `Adjustment` | `Assumption` | `Inconsistency` | `Legibility`) | **F** Explanation (3 sentences max, aim for 2; write for a researcher who may not have the spreadsheet open; include row labels alongside all cell references; state the discrepancy and which value is correct, or ask the researcher to confirm; High findings: include a brief consequence clause; no chain traces) | **G** Recommended Fix (imperative verb; say which cell should reference the other, or which should be updated to match) | **H** Estimated CE Impact (use exactly one of these six phrases with an em-dash ( — ) with one space on each side — do not use en-dash, hyphen, or pipe: `Raises CE — [estimate]` \| `Lowers CE — [estimate]` \| `Raises CE — magnitude unknown` \| `Lowers CE — magnitude unknown` \| `No CE impact` \| `Direction unknown`; punctuation variants cause sort failures in the compaction agent) | **I** Status (leave blank)

See `reference/output-format.md` for full column definitions.

---

## Final step — write completion marker

After all findings are written (or at row 2 if no findings were written), write ONE final row to `stg-xcomp`:

- Column B: `cross-tab-compare`
- Column D: `AGENT_COMPLETE`
- Column F: `COVERAGE_ROWS: all rows | Simple CEA ([N] rows) and [Main CEA tab name] ([N] rows) both read in full. Filed [K] findings in rows 2–[K+1]. Staging sheet: stg-xcomp.`
- All other columns: blank

Use a single `modify_sheet_values` call. This is the absolute last action you take before finishing.
