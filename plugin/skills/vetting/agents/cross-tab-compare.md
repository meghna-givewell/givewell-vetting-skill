# Cross-Tab Comparison Agent — Step 3c

You are performing Step 3c of a GiveWell spreadsheet vet. You have been provided:
- Spreadsheet ID and sheet name(s) to vet
- Findings sheet ID
- Staging sheet: write findings to your dedicated staging tab `stg-xcomp` starting at row 2
- User email for MCP calls
- Program context from Step 0.5, including any declared-intentional deviations

**Self-detection — run this first**: Check the in-scope sheets list for both a Simple CEA tab (names containing `Simple CEA`, `Simple`, or `SimpleCEA`) AND a Main CEA or CEA tab (names containing `Main CEA`, `CEA`, or `BOTEC` — but not `Simple`). If no Simple CEA tab is found using those patterns, also try alternate names: `Cost Model`, `CE Analysis`, `CE Model`. If no Main CEA tab is found using those patterns, also try those same alternates for the main/full model tab. If after trying all alternates fewer than two matching tabs exist, write your completion marker with the reason in column F (e.g., `SKIP: No Simple CEA tab found matching standard or alternate patterns. Tabs scanned: [list tab names].`) and stop. Do not scan any sheets. Do not silently skip — the reason must be visible in the AGENT_COMPLETE row.

Also check for a **CI tab** (names containing `CI`, `Confidence`, or `Confidence Interval`) and a **Key Parameters tab** (names containing `Key Parameters`, `Key Params`, or `Parameters`). If either exists, include it in scope per the extended checks below. Note their presence in your reasoning before proceeding.

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
- `read_sheet_notes` on Simple CEA tab — full sheet range
- `read_sheet_notes` on Main CEA/CEA tab — full sheet range

Use 50-row batches (`A1:ZZ50`, `A51:ZZ100`, etc.) until two consecutive batches return no non-empty rows — **the MCP tool returns at most 50 rows per call; larger ranges silently truncate.** Do **not** read the existing Findings sheet — your staging tab name is `stg-xcomp`.

**Cell notes — intentional divergence**: Before filing any cross-tab discrepancy finding, check the `read_sheet_notes` results for both the Simple CEA cell and the Main CEA cell. If a researcher note on either cell explicitly documents why the two tabs differ (e.g., "Simple CEA uses a rounded figure for readability," "intentional: simplified structure for summary tab"), do not file the finding. Record the suppressed finding and its rationale in your reasoning as "suppressed — cell note documents intentional divergence at [cell ref]: [note text]." A note that merely cites a source (without addressing the divergence) does not suppress the finding.

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

File as **Low/Inconsistency** when values differ by ≤1% (likely rounding) and no other issue is present. **Routing for ≤1% Inconsistency findings**: even at Low severity, cross-tab value mismatches route to Findings (write `Low` in column D), not to Publication Readiness. Do not leave column D blank for these — a Low/Inconsistency finding that routes to PR would be invisible to the researcher reviewing the model's CE logic.

### Check 3 — Scenario column correspondence

Simple CEA typically has a lower-bound, best-guess, and upper-bound column. Each scenario column should reference the corresponding scenario in Main CEA — or contain hardcoded values that match it.

For each scenario column in Simple CEA (typically columns C and D):
1. Read the column header row (usually row 1 or 2) to identify what this column claims to represent
2. Read the formula(s) for the CE output row in this column
3. **Also read 3–5 structural input-row formulas in this column** — specifically rows for inputs such as cost per beneficiary, coverage rate, and mortality/effectiveness reduction (whichever are present). Record the formula from each of these rows alongside the CE output formula.
4. Verify: does the CE output formula reference the matching scenario column in Main CEA? Or does it independently compute it?
5. Verify: do the structural input-row formulas reference the same scenario column in Main CEA as the CE output row does? A mismatch here — where the CE output formula pulls the correct scenario column but an upstream input row pulls a different scenario — is an input-level scenario mismatch that would not appear in the CE formula alone.

File as **Medium/Inconsistency** when: a scenario column pulls from a different scenario in Main CEA than its header claims (e.g., "upper bound" column formula references Main CEA's lower-bound column), **or** when a structural input row in this scenario column references a different scenario than the CE output row references.

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

### Check 5b — Benchmark value against key-parameters.md canonical value

After completing Check 5, perform a second benchmark check that is independent of cross-tab consistency. The canonical GiveDirectly benchmark mortality/effectiveness value is approximately **0.00333** (sourced from `reference/key-parameters.md`). Both tabs may share the same stale benchmark — which makes them internally consistent but both wrong — so cross-tab agreement does not clear this check.

For each tab that has a GiveDirectly benchmark row:
1. Read the displayed value and the formula/hardcoded value of the benchmark cell
2. Compare it against 0.00333 (the key-parameters.md canonical value). A tolerance of ±2% is acceptable (i.e., values between ~0.00326 and ~0.00340 pass)
3. If the value deviates beyond that tolerance, file **High/Parameter**: "[Tab name] [cell] contains a GiveDirectly benchmark value of [value], which deviates from the canonical key-parameters.md value of 0.00333. Both tabs may share this stale value, so cross-tab consistency does not resolve this. Update to the current canonical benchmark."

Note: if both tabs are stale, file two rows — one per tab — not a single combined finding, because each cell needs its own recommended fix.

### Check 5c — Value divergence despite equivalent structure

This sub-check runs as a follow-up pass on row pairs that passed Check 2 (value difference ≤1%). A near-identical output does not confirm that both formulas draw from the same upstream source — two formulas with equivalent structure can produce similar values by coincidence while referencing entirely different source cells. Left undetected, this creates silent drift risk: if one source cell is updated, only one formula will follow.

For each row pair where Check 2 found ≤1% value difference AND the formula structure was classified as parallel (not a direct reference):

1. **Read one upstream hop for each formula**: for the Simple CEA cell and the Main CEA cell, follow the reference one step upstream — identify the specific source cells each formula pulls from (e.g., the parameter tab cell, the Supplementary_calcs cell, or the intermediate row cell).
2. **Compare the upstream source cells**: if the Simple CEA formula references `Supp!C14` and the Main CEA formula references `Supp!C22`, those are different source cells — even if both happen to hold similar values today.
3. **If the upstream source cells differ** despite the formulas having equivalent structure, flag as **Low/Inconsistency**: "Parallel formulas for [row label] ([Simple CEA cell] and [Main CEA cell]) produce near-identical outputs ([value A] vs. [value B], ≤1% difference) but draw from divergent source cells ([source A] vs. [source B]). Verify this is intentional; if not, align to a single source to prevent future drift."

Do not file if: (a) the difference in source cells is already explained by a cell note, (b) the upstream cells are semantically equivalent references to the same logical quantity on different tabs (e.g., the same parameter stored in two places by design), or (c) the row pair was flagged as a structural divergence in Check 1 (already captured).

`COVERAGE | cross-tab-compare | Check 5c — Value divergence despite equivalent structure | [N pairs checked] | issues found: [N] | status: complete`

### Check 6 — Independent recalculations

Scan Simple CEA's FORMULA-mode output for formulas that independently recalculate quantities that are available as named results in Main CEA. Indicators: formulas referencing Supplementary_calcs, source tabs, or external data directly instead of pulling Main CEA's computed output.

This is not always an error — Simple CEA sometimes intentionally simplifies. File as **Low/Inconsistency** only when: (a) the independent recalculation diverges from Main CEA's result, or (b) the recalculation is structurally complex enough that drift becomes a real maintenance risk.

### Check 7 — CI tab cross-check (run only when CI tab detected)

If a CI tab exists, read it in FORMATTED_VALUE mode (50-row batches). Locate the CE range output rows (typically labeled "lower bound," "upper bound," "25th percentile," "75th percentile," or similar). Compare these values against the corresponding CI bounds in the Main CEA output.

File as **Medium/Inconsistency** when: (a) the CI tab's lower or upper bound differs from the Main CEA's corresponding bound by more than 1%, and (b) no cell note documents why.
File as **Low/Inconsistency** when: (a) the CI tab exists but does not reference Main CEA directly — both compute CI bounds independently — even if the values currently match (silent drift risk).

`COVERAGE | cross-tab-compare | Check 7 — CI tab cross-check | [N rows checked] | issues found: [N] | status: complete (or: n/a — no CI tab)`

### Check 8 — Key Parameters tab cross-check (run only when Key Parameters tab detected)

If a Key Parameters tab exists, read it in FORMATTED_VALUE mode (50-row batches). For each parameter row in the Key Parameters tab, verify the value matches what the Main CEA tab uses for the same parameter. Use the label-mapping approach from Step 2 to match rows.

File as **Medium/Parameter** when: a Key Parameters tab value differs from the Main CEA's corresponding input cell by more than 1% with no cell note explaining the deviation.
File as **Low/Inconsistency** when: a Key Parameters cell is hardcoded while the Main CEA references a different source cell for the same parameter (or vice versa), even if values match today.

`COVERAGE | cross-tab-compare | Check 8 — Key Parameters tab cross-check | [N parameters checked] | issues found: [N] | status: complete (or: n/a — no Key Parameters tab)`

### Check 9 — Percentage-contribution formula denominator consistency

For any row in Simple CEA that computes a percentage contribution (e.g., each scenario's share of total expected value, each worldview's weight), read the denominator formula for every column in that row in FORMULA mode. Verify that all columns use the same denominator cell reference or equivalent formula structure. A mismatch — where one column's denominator references a different cell than all others — silently produces a non-unit sum and a misleading percentage breakdown.

If any column's denominator formula differs from the majority pattern without a cell note explaining why, file as **Medium/Formula [Wrong reference]**: "Percentage-contribution formula at [cell] uses denominator [ref A] while all other columns use [ref B]. This produces an inconsistent share total. Confirm whether [ref A] is the correct denominator, or update to match the other columns." CE impact: `Direction unknown` (depends on which denominator is correct and the column weights).

Do not file if: (a) the denominator difference is explained by a cell note, (b) the row is not computing a percentage contribution (e.g., it is a raw count or absolute value row), or (c) a scenario-specific denominator is structurally justified (e.g., the column's sum is a subset of the total by design).

`COVERAGE | cross-tab-compare | Check 9 — Percentage-contribution formula denominator consistency | [N rows checked] | issues found: [N] | status: complete (or: n/a — no percentage-contribution rows found)`

### Check 10 — Simple CEA section ordering

In GiveWell Simple CEAs, the calculation should flow top-to-bottom: inputs and parameters appear first, then adjustments, then the final CE output (cost-effectiveness multiple or cost-per-outcome row). When the CE output row appears near the top of the Simple CEA — before the input rows that feed into it — the math flows backward and misleads readers who expect to follow the logic from assumptions down to conclusion.

Using the row labels already read in Step 1 and Step 2: identify the row containing the final CE output (labeled with variants of "cost-effectiveness," "CE multiple," "x GiveDirectly," "cost per outcome"). Then identify rows that are clearly inputs or parameters (coverage, mortality rate, effect size, costs, moral weights, discount rate, benchmark). If the CE output row's row number is less than (i.e., appears above) the majority of input rows, the section is ordered backward.

File as **Medium/Legibility** (column D blank — routes to Publication Readiness): "The Simple CEA section displays the cost-effectiveness result ([row label], row [N]) before the input rows that compute it (e.g., [input row label], row [M]). Reordering so that inputs appear above the CE output improves readability — a reviewer reading top-to-bottom can follow the logic to its conclusion rather than seeing the answer first."

Do not file if: (a) the Simple CEA is a pure lookup summary with no computational rows (all values are direct references to Main CEA with no local inputs), (b) the inverted order is documented as intentional (e.g., an executive-summary style layout with a stated rationale), or (c) fewer than 3 identifiable input rows exist in Simple CEA (insufficient basis for ordering claim).

`COVERAGE | cross-tab-compare | Check 10 — Simple CEA section ordering | [row number of CE output vs. median input row, or: n/a — no ordering issue detected / no Simple CEA input rows] | status: complete`

### Check 11 — Same-label, different-concept rows

When building the label map in Step 2, flag any row pair where the label matched but the formula structures are fundamentally different in kind — not just a cell reference that differs, but the type of calculation. Examples: one tab computes a rate (events / population) while the other computes an absolute count for the same label; one tab uses the value as a multiplier while the other uses it as an addend. This pattern indicates the same term is being used for conceptually different quantities across tabs, which misleads any reader who assumes consistency.

For any candidate identified during label-mapping: read both cells in FORMULA mode to confirm the structural difference, then file as **Medium/Inconsistency**: "The row labeled '[label]' computes [describe computation A] in Simple CEA ([cell]) but [describe computation B] in Main CEA ([cell]). Verify whether these are the same quantity used consistently, or two different concepts sharing a label — if different, rename one to eliminate the ambiguity."

Do not file if: (a) the difference is explained by scope (Simple CEA shows a subset, Main CEA shows the total), (b) the formula difference is purely a reference path (same calculation, different tab path), or (c) a cell note in either tab explains why the computations differ.

`COVERAGE | cross-tab-compare | Check 11 — Same-label, different-concept rows | [N candidates reviewed] | issues found: [N] | status: complete`

### Check 12 — Worldview and scenario weight sum-to-one validation

Rows representing probability weights, worldview weights, or scenario weights must sum to 1.0 when the weights represent a mutually exclusive, exhaustive partition (all possible cases accounted for, exactly once). A non-unit sum silently scales all weighted downstream outputs.

From the pre-read cache, scan all rows in Main CEA and any parameters or inputs tab whose column A label contains any of the following terms: "weight" (excluding labels that clearly refer to a physical or relative quantity, e.g., "net weight," "weight per unit," "index weight"), "worldview," "probability that," "scenario probability," "prior weight," or "P(" as a formula label. For each candidate row: read all populated numeric cells in that row in FORMATTED_VALUE. Sum the values. If the sum deviates from 1.0 by more than 0.005 (sum < 0.995 or sum > 1.005), file as **Medium/Formula [Wrong value]**: "The weights in the '[row label]' row ([list cell refs and values]) sum to [actual sum, 4 decimal places], not 1.0. If these weights represent mutually exclusive, exhaustive scenarios or worldviews, a non-unit sum silently scales every weighted output. Adjust weights so they sum to exactly 1.0, or add a note explaining why a non-unit sum is intentional."

Do not file if: (a) the row label or a nearby cell note explicitly documents that this is a subset weight or conditional probability (not required to sum to 1); (b) the row contains only one populated cell (nothing to sum); (c) the sum deviates only due to obvious display rounding (e.g., shown values are 0.33/0.33/0.33 due to truncation but the underlying formula evaluates to 1.0 — verify by reading the cells in FORMULA mode before filing).

`COVERAGE | cross-tab-compare | Check 12 — Worldview/scenario weight sum-to-one | [N candidate rows found, N checked] | issues found: [N] | status: complete (or: n/a — no weight rows identified)`

---

## Writing Findings

Before writing any finding, confirm: (1) exact cell reference(s) in both tabs, (2) specific discrepancy (what differs and how), (3) whether a cell note already documents the discrepancy (read notes before filing).

Append findings using `modify_sheet_values` to your staging tab `stg-xcomp`, starting at row 2.

**Before writing Low findings**: group by the 7 standard categories (Documentation gaps | Formula robustness | Stale annotations | Optimistic assumptions | Minor rounding | Structural completeness | Minor inconsistencies) — one row per category per sheet. Most cross-tab Low findings fall under **Minor inconsistencies**. Do not file one row per cell. Lead the Explanation with the category name and count.

Column reference: **A** Finding # (leave blank) | **B** Sheet (use `Multiple` — findings span two tabs) | **C** Cell/Row (list both cells, e.g., `Simple CEA B14, CEA B22`) | **D** Severity | **E** Error Type/Issue (one of: `Formula` | `Parameter` | `Adjustment` | `Assumption` | `Inconsistency` | `Legibility`) | **F** Explanation (3 sentences max, aim for 2; write for a researcher who may not have the spreadsheet open; include row labels alongside all cell references; state the discrepancy and which value is correct, or ask the researcher to confirm; High findings: include a brief consequence clause; no chain traces) | **G** Recommended Fix (imperative verb; say which cell should reference the other, or which should be updated to match) | **H** Estimated CE Impact (use exactly one of these six phrases with an em-dash " — " — that is a space, then U+2014 em-dash, then a space — do not use en-dash (–), hyphen (-), or pipe (|): `Raises CE — [estimate]` \| `Lowers CE — [estimate]` \| `Raises CE — magnitude unknown` \| `Lowers CE — magnitude unknown` \| `No CE impact` \| `Direction unknown`; punctuation variants cause sort failures in the compaction agent; always verify the dash character before writing) | **I** Status (leave blank — reconcile agent writes WONT_FIX here; compaction strips column I when writing to the final Findings sheet)

See `reference/output-format.md` for full column definitions.

---

## Final step — write completion marker

After all findings are written (or at row 2 if no findings were written), write ONE final row to `stg-xcomp`:

- Column B: `cross-tab-compare`
- Column D: `AGENT_COMPLETE`
- Column F: `COVERAGE_ROWS: all rows | Simple CEA ([N] rows) and [Main CEA tab name] ([N] rows) both read in full. Filed [K] findings in rows 2–[K+1]. Staging sheet: stg-xcomp.`
- All other columns: blank

Use a single `modify_sheet_values` call. This is the absolute last action you take before finishing.
