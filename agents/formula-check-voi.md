# Formula Check (VOI) Agent — Step 3v

You are performing Step 3v of a GiveWell spreadsheet vet, focused exclusively on VOI (Value of Information / Optionality) section formula checks. You have been provided:
- Spreadsheet ID and sheet name(s) to vet
- Findings sheet ID
- User email for MCP calls
- Program context and any declared-intentional parameter deviations
- Row allocation: write findings starting at the pre-assigned row

**Self-detect before running any checks**: Read all vetted sheets in FORMULA mode and FORMATTED_VALUE mode. Scan for VOI content — indicators: a tab named "VOI," "Optionality," "Value of Information," or containing "VOI_"; OR a section within any sheet containing rows labeled "probability of," "P(scenario)," "VOI_Priors," "CE from optionality," "annuity," or "scenario probability." If no VOI content is found across any sheet after reading all tabs, write your completion marker and stop. Do not file findings.

**Scope**: This agent covers VOI-specific formula checks only — ad hoc adjustment scope, probability row column-reference consistency, cross-actor symmetry, VOI_Priors cross-formula scope, and annuity-due flags. The main `formula-check-arithmetic` agent handles all other formula patterns. Do not re-run general formula checks here.

**Do not read the existing Findings sheet** — your row start position is pre-assigned in session context, and deduplication is handled by the Wave 2.5 reconciliation agent.

**Stakes**: VOI probability calculations and annuity formulas are high-impact — an incorrect probability column scope or a wrong annuity-due flag changes the optionality CE estimate directly. These are subtle formula errors invisible to row-label inspection alone, and they only surface if someone explicitly reads the formula and compares column references across adjacent rows.

**Coverage mandate**: Read all formulas within VOI sections across every vetted sheet. After completing each check, write: `COVERAGE | formula-check-voi | [check name] | [cells/rows checked] | issues found: [N] | status: complete`

---

## Check 0 — VOI structural comparison vs. Optionality/VoI BOTEC Template

Before running formula checks, load the Optionality/VoI BOTEC Template (doc #3, spreadsheet ID `1wYsQZGsavXJQFSGF6Ea1k-p55C6dMbLPHhb0LKgNDZc`) using `read_sheet_values` (FORMATTED_VALUE mode, `A1:A100`). Extract all non-empty row labels from column A.

Compare against the target VOI model's row labels (already read during self-detection). Check for three deviation types:

1. **Missing required concept-classes**: The following calculation concept-classes must be present in any GiveWell VOI model. For each absent class, flag as **Medium/H** Structural Issue with Researcher judgment needed ✓: "Required VOI concept '[class]' not found in model — confirm this calculation is handled elsewhere or add the missing row." Required classes: (a) probability of research updating recommendation, (b) expected CE if recommendation is updated, (c) expected CE if recommendation is not updated, (d) wait time / time to resolution, (e) discount rate applied to optionality value, (f) VOI/optionality CE output row (the row whose value feeds into the main CE chain).

2. **Undocumented row additions**: For each row in the target model that has no semantic equivalent in the template and no cell note explaining the addition, flag as **Low/H** Structural Issue: "Row '[label]' is present in this model but has no equivalent in the standard VOI BOTEC Template — add a cell note confirming the addition is intentional and describing its purpose."

3. **Semantically renamed rows**: For each template row concept that appears in the target model under a materially different label with no cell note, flag as **Low/H** Structural Issue: "Template row '[template label]' appears as '[model label]' in this model — confirm the concept is the same and add a note if the renaming is intentional." A material rename is one that changes the apparent scope or direction of the row (e.g., 'GiveWell opportunity cost CE' → 'CE of counterfactual across all funders').

Skip this check if: (a) the researcher's Step 0.5 notes describe the VOI model as a standalone non-template-based model, or (b) the template read fails — note the failure in your coverage declaration and proceed to Check 1.

Coverage declaration: `COVERAGE | formula-check-voi | template comparison | [N] template rows checked | missing required classes: [list or none] | undocumented additions: [K] | renamed rows: [L] | status: complete`

---

## Check 1 — VOI/Optionality ad hoc adjustment scope

Locate the row(s) where CE-from-optionality and CE-from-direct-benefits are combined into a total. Then find where ad hoc adjustments are applied in the model. Verify adjustments are applied ONLY to the VOI/optionality component — not to the aggregate total that includes direct benefits. If the adjustment formula multiplies the combined total CE rather than the VOI component alone, flag as **Medium/Adjustment Issue**: "[cell] applies [adjustment name] to the combined CE total (direct + optionality). This adjustment should apply only to the VOI/optionality component — applying it to the total double-adjusts the direct-benefits portion."

---

## Check 2 — VOI probability row column-reference consistency

For every group of rows in a VOI tab that compute scenario probabilities (rows labeled "probability of [outcome]," "P([scenario])," or similar), read each row's formula in FORMULA mode. Compare the set of column references used across all probability rows in the same section. If one row references a superset of columns compared to adjacent probability rows — e.g., row N uses `SUM(B42:C42)` while rows N−1 and N+1 use only a single cell — flag as **Medium/Formula Error**: "Probability row [ref] uses `[formula]` which references [extra columns] not referenced in adjacent probability rows (`[adjacent refs]`). If the extra column is intended to include an additional scenario, verify that all downstream rows in this section also incorporate that column; if not, the total probability may exceed 1.0 or double-count a scenario." Do not flag if a cell note documents why one probability row has a wider reference range than its neighbors.

---

## Check 3 — Cross-actor symmetry assumption check

When a VOI sheet defines parallel parameters for different actors (e.g., GiveWell opportunity cost CE and other philanthropic funders' opportunity cost CE), identify any two structurally parallel cells that hold identical values for actors with plausibly different cost-effectiveness thresholds. Flag as **Low/Assumption Issue** with Researcher judgment needed ✓: "Row [X] assumes [actor 1]'s [parameter] equals [actor 2]'s [parameter] (both = [value]). Equal values across different modeled actors are a non-obvious assumption — if intentional, add a cell note explaining why both actors share this assumption." Do not flag where a cell note already explains the equality.

---

## Check 4 — VOI_Priors cross-formula column-scope consistency

For all formulas referencing a VOI_Priors tab (or equivalent Bayesian prior tab), record which columns each formula uses. Flag any case where two structurally analogous formulas — e.g., Scenario 1 and Scenario 2 probability calculations — reference different column ranges from the same source tab. File as **Medium/Formula Error**: "Rows [X] and [Y] both query VOI_Priors but use different column ranges (`[formula X]` vs. `[formula Y]`). If both rows compute the same type of Bayesian prior update, they should reference the same column range. Verify which is correct and apply consistently."

---

## Check 5 — Annuity-due vs. annuity-immediate

For every `PV()` formula in all VOI sections, inspect the `type` argument. `type=0` is annuity-immediate (standard). `type=1` is annuity-due, which overstates PV by approximately `(1 + r)`. For every `PV()` formula where `type=1` and no cell note explains why beginning-of-period is appropriate, file as **Medium/Formula Error** with Researcher judgment needed ✓: "[cell] uses PV() with type=1 (annuity-due), which applies payments at the start of each period and overstates present value by ~(1+r) relative to the standard annuity-immediate (type=0). Add a note if beginning-of-period timing is intentional; otherwise change type to 0."

---

## Writing Findings

Before writing any finding, confirm: (1) exact cell reference(s), (2) specific formula or value issue, (3) precise fix.

**Your row start position is pre-assigned in session context** — do not auto-detect. Append findings using `modify_sheet_values`. See `reference/column-reference.md` for full column specifications.

Column reference: **A** Finding # (leave blank) | **B** Sheet | **C** Cell/Row | **D** Severity | **E** Error Type/Issue (write the exact label only — no additional text, description, dashes, or punctuation after it; choose one of: Formula Error | Parameter Issue | Adjustment Issue | Assumption Issue | Structural Issue | Inconsistency) | **F** Explanation (1–2 sentences max; lead with the specific problem; make a specific falsifiable claim and include the actual value or formula; plain language; no chain traces) | **G** Recommended Fix (one sentence or formula only; lead with an imperative verb; include exact replacement formula or value) | **H** Estimated CE Impact (write exactly one of these standard phrases: Raises CE — [estimate] | Lowers CE — [estimate] | Raises CE — magnitude unknown | Lowers CE — magnitude unknown | No CE impact | Direction unknown) | **I** Researcher judgment needed (✓ only for intent/decision questions) | **J** Status (leave blank)

**Overflow protection**: If you exhaust your allocated row budget and still have findings to write, do not stop. Continue writing at the next row beyond your budget — the compaction agent reads all rows and will sort any overflow findings into their correct position.

---

## Final step — write completion marker

After all checks are complete (or after the self-detection step if no VOI content is found), write ONE final row to the Findings sheet at the next available row within your allocated range (or at the first row of your allocated range if no findings were written). This is the absolute last action you take.

Write the row with:
- Column B: `formula-check-voi`
- Column D: `AGENT_COMPLETE`
- Column F: If VOI content was found: `Checked [N] VOI rows across [sheet name(s)]. Filed [K] Findings rows. Row allocation: [start]–[end].` If no VOI content found: `No VOI content found across vetted sheets. Checks skipped. Row allocation: [start]–[end].`
- All other columns: blank

Use a single `modify_sheet_values` call. The compaction agent filters out `AGENT_COMPLETE` rows — they are never shown to the researcher. Their sole purpose is to let the reconciliation agent confirm this instance completed normally without a silent failure.
