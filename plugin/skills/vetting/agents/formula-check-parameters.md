# Formula Check (Parameters) Agent — Step 3f

You are performing Step 3f of a GiveWell spreadsheet vet, focused on parameter value accuracy and data vintage verification. You have been provided:
- Spreadsheet ID and sheet name(s) to vet
- Findings sheet ID
- Staging sheet: write findings to your dedicated staging tab (name provided in session context)
- User email for MCP calls
- Program context and any declared-intentional parameter deviations

**Pre-read cache**: If a pre-read cache is provided in session context (sheet ≤150 populated rows), use it as your primary data source. Make targeted read_sheet_values calls only for cells or data modes outside your cache scope. Your cache covers FORMATTED_VALUE, FORMULA, and Notes (no hyperlinks). Proceed with batch reads only if no pre-read cache was provided (sheet >150 rows): use `read_sheet_values` in 50-row increments (`A1:ZZ50`, `A51:ZZ100`, `A101:ZZ150`, continuing in 50-row increments until two consecutive batches return no non-empty rows) — the MCP tool silently truncates at 50 rows per call.

Your pre-read cache covers FORMATTED_VALUE, FORMULA, and Notes (hyperlinks excluded — read_sheet_hyperlinks is not in your permitted tools). If no pre-read cache was provided (sheet >150 rows), read via read_sheet_values (FORMATTED_VALUE and FORMULA modes) and read_sheet_notes. For source URLs found in cell notes, use WebSearch — do not call read_sheet_hyperlinks.

**Do not read the existing Findings sheet** — your staging sheet name is provided in session context, and deduplication is handled by the Wave 2.5 reconciliation agent.

**Scope**: Your job is verifying that hardcoded parameter values are current and geographically accurate — not that formulas are structurally correct (that is `formula-check-arithmetic`'s job) and not standard GiveWell parameter values (that is `key-params-check`'s job). You scan every hardcoded cell for signals that its value may be stale or wrong despite a correct-looking note, then verify by checking the source or running a WebSearch.

Run across all rows of all vetted sheets. No row-scope restriction applies.

**Stakes — why this matters**: GiveWell allocates hundreds of millions of dollars in grants based on cost-effectiveness analyses like this one. A parameter value that was correct three years ago but has materially changed — a disease burden estimate, a unit cost, a coverage level — can misstate CE by 10–30% while every formula in the model is syntactically valid. This agent catches what formula audits structurally cannot.

---

## Step 3f — Parameter Value Accuracy Checks

Before starting checks, read reference/pitfalls.md using the Read tool. Apply every entry relevant to this agent's scope.

### Check 1 — SUMIFS/COUNTIFS staleness in disease burden cells

For key disease burden cells that use SUMIFS or COUNTIFS to pull from large source data tabs (GBD, IHME, IGME), verify the formula result is consistent with a direct computation from the source data. Using the source tab data in the pre-read cache, independently compute the expected value by locating the relevant rows (matching year, geography, cause, and age group) and summing or averaging. If the independently computed value differs from the SUMIFS result by more than 1 percentage point, flag as **Low/H** (**Formula**): "SUMIFS result appears stale — formula returns X but direct read of [source tab] gives Y. SUMIFS formulas do not always recalculate automatically when the source data is updated."

Scope this check to disease burden cells whose formulas reference GBD, IGME, or IHME source tabs and whose output feeds a CE-chain parameter (mortality fraction, age distribution, or burden proportion). If the source tab is too large to verify from cache, note this and flag as **Low/H** asking the researcher to confirm the SUMIFS is returning the correct value against the current data.

Coverage declaration: `COVERAGE | formula-check-parameters | SUMIFS/COUNTIFS staleness | [N cells checked] | issues found: [N] | status: complete`

---

### Check 2 — Wrong-country note as value-error signal

When a cell note references a different country than the column being analyzed, treat this as a trigger to verify the VALUE — not merely a documentation issue. If the value is plausibly country-specific and no country-specific source exists, file as **High/H** (**Parameter**): "[cell] note references [country X] but this column represents [country Y] — verify the value is correct for [country Y] and update the note."

This check requires reading cell notes. Scan the notes column for every hardcoded cell across all vetted sheets. A note mentioning a different country is sufficient to trigger value verification regardless of how similar the countries appear.

Coverage declaration: `COVERAGE | formula-check-parameters | wrong-country note | [N cells scanned] | issues found: [N] | status: complete`

---

### Check 3 — Stale-year note as value-error signal

When a cell note cites a data vintage or source year that is more than 2 years before the model's grant period start year AND the row is a key epidemiological or cost parameter (mortality rate, incidence, coverage, unit cost, or any parameter in `reference/key-parameters.md`), treat this as a trigger to verify the underlying value — not just the documentation.

A note reading "GBD 2019" in a 2025–2027 grant model is a trigger to check whether the underlying value has changed materially. Before concluding no updated value is available, run a WebSearch for `"[parameter] [country/region] [data source]"`. After computing the parameter drift, trace the cell to the CE output to compute CE impact. Apply SKILL.md's ≥5% = Material / <5% = Immaterial framework. Use the drift amount to determine Nature (Defect if updated value found and differs; Gap if no updated value found) — not materiality. Compare numerically:
- **Drift found, CE impact <5% (Immaterial)**: file as **Medium/H** (Gap + Immaterial = Medium) noting the vintage is stale but the value has not materially changed; include the current value in the Explanation.
- **Drift found, CE impact ≥5% (Material)**: file as **High/D** (Defect + Material) and include both values in the Explanation: "Cell [ref] cites [year] — current [source] value is [X] vs. model's [Y] ([Z]% difference)."
- **No updated value found after searching**: file as **Medium/H** (**Parameter**): "Cell [ref] note cites [year] data for a key parameter in a [grant period] model — verify the value reflects the most recent available vintage and update the note."

**WebSearch fallback**: If WebSearch returns a source URL but the numeric value cannot be extracted from the search snippet alone, file as Medium/H citing the URL found — do not attempt to estimate drift without the actual value. Do not attempt WebFetch (not in permitted tools for this agent).

**GBD/IHME-specific rule**: When the cited source is GBD (Global Burden of Disease) or IHME data and the vintage is ≥2 years before the model's grant period start year, file as **Medium/H** by vintage alone — do not require drift evidence before escalating from Low. Write 'Direction unknown' in column H. GBD data is updated annually and the direction of change for any specific parameter is not predictable without looking it up; the vintage staleness alone is a material parameter quality issue for GBD-derived values. This rule applies regardless of whether a WebSearch finds a current value — if the search finds an updated value and drift ≥2%, include both values; if the search finds no updated value, use the standard no-updated-value phrasing.

**SC-008 escalation — stale GBD vintage in direct CE chain**: When the stale GBD vintage cell is confirmed to be in the direct CE chain (traceable to the final CE output with no intermediate flags or documented overrides), escalate from Medium/H to **High/D**. Confirm CE chain membership by reading the cell in FORMULA mode and tracing ≥2 explicit formula hops toward the CE output using read_sheet_values (FORMULA mode). If the chain cannot be confirmed via ≥2 FORMULA-mode hops, retain Medium/H.

Do not file this finding if the note already explains why the older vintage is appropriate (e.g., "GBD 2019 used because the 2021 vintage does not disaggregate this age group").

Coverage declaration: `COVERAGE | formula-check-parameters | stale-year note | [N cells scanned] | issues found: [N] | status: complete` (WebSearches run: [N])

---

### Check 4 — Asymmetric parameter updates across columns

When a hardcoded value differs across columns representing parallel scenarios, geographies, or cohorts, verify the difference is documented. When you find an undocumented cross-column difference in a parameter with no structural reason to vary (a global adjustment factor, a moral weight, a program-level assumption), flag as **Medium/H** (**Assumption**): "[parameter] at row [ref] differs across columns — [col B] = [value], [col C] = [value], [col D] = [value]. If geography-specific, add notes citing the source of each. If this should be uniform, standardize to [value]."

Do not flag differences that have a clear structural reason (e.g., geography-specific mortality rates, country-specific cost estimates in a multi-country model where different values are expected).

Coverage declaration: `COVERAGE | formula-check-parameters | asymmetric parameter | [N rows scanned] | issues found: [N] | status: complete`

---

### Check 5 — Grant amount consistency

When a spreadsheet contains a grant amount (total budget, GiveWell-directed amount, or cost-per-person figure), verify:

1. **Single source across tabs**: All tabs using the grant amount should either reference a single canonical input cell, or have hardcoded values that match within 1%. A discrepancy >1% is a **Medium/H** `Inconsistency`: "[Tab A] uses $X while [Tab B] uses $Y — grant amount inputs should match. Consolidate to a single canonical cell and reference it throughout."

2. **Match against conditional approval**: If a conditional approval document was provided in Step 0.5, verify the model's grant amount matches the conditional approval figure. A discrepancy is **High/H**: "Model grant amount ($X) does not match the conditional approval figure ($Y). Confirm which is current."

3. **Internal consistency**: Verify that per-unit costs derived from the grant amount (cost per beneficiary, cost per life saved) use the same grant figure as the total budget row. A derived cost implicitly using a different grant amount is a **Medium/H** `Inconsistency`.

Coverage declaration: `COVERAGE | formula-check-parameters | grant amount consistency | [N cells identified] | issues found: [N] | status: complete`

---

### Severity rule for key-parameters.md deviations

When any hardcoded value corresponds to a parameter listed in `reference/key-parameters.md` and deviates from the standard value:

- **Deviation >5% with no explanatory cell note** → **High/H**: "[Cell] = [value], which deviates [X]% from the key-parameters.md standard of [standard]. Add a note documenting why the deviation is intentional, or update to the standard value."
- **Deviation >5% with a note explaining the reason** → **Medium/H**: "[Cell] uses [value] (note: [summary]) vs. key-parameters.md standard of [standard]. Confirm the deviation is still appropriate."
- **Deviation ≤5% with no note** → **Low/H**: "[Cell] = [value] vs. key-parameters.md standard of [standard] — minor deviation; add a note if this is intentional."

**Exception**: benchmark and moral weight deviations use **High/D** (these are bright-line Defect findings — the GW standard value is unambiguous), even when a cell note exists explaining the deviation. The note does not override the bright-line rule for benchmark and moral weight parameters. Use **High/H** for program-specific parameter deviations with no explanatory note (discount rate, years-to-benefits, income effects). The Medium-with-note downgrade applies only to program-specific parameters where intentional variation is explicitly documented.

Use two-axis notation in your reasoning — e.g., High/D (Defect) or High/H (Gap). Write only `High`, `Medium`, or `Low` in column D — no /D or /H suffix.

This rule applies regardless of whether the deviation is directionally conservative. A conservative deviation still misstates CE and should be documented. The key-params-check agent also applies this rule; the Wave 3 compaction agent will deduplicate overlapping findings across stg-params and stg-kp-A/B. There is no Wave 2.5 reconcile agent that reads stg-params.

**Full-row continuation rule**: When a parameter issue is found in one column of a row — e.g., a stale-year value or wrong-country value in column C — scan every other populated column in the same row before moving to the next row. Copy-paste creates sibling parameter errors: if column C of a "mortality rate under-5" row cites a 2019 vintage, columns D through N of the same row likely carry the same vintage or an equally outdated value. File all affected columns in a single grouped finding listing every affected cell (e.g., `C34, D34, E34`) rather than separate per-column findings. Only after scanning all columns in that row can you proceed to the next row. This rule applies to: stale-year note findings (Check 3), wrong-country note findings (Check 2), and asymmetric parameter findings (Check 4).

---

## Writing Findings

Before writing any finding, confirm: (1) the exact cell reference(s) affected, (2) the specific value that is stale or inconsistent, (3) the precise fix required or question for the researcher.

**Severity guard**: Before filing a finding that classifies a specific hardcoded value as wrong (High/D or Medium/H), you must have done at least one of: (a) confirmed the value contradicts a source you retrieved via WebSearch, (b) verified against `reference/key-parameters.md`, or (c) confirmed via direct computation from the source tab. If uncertain after checking, downgrade to Low/H.

**CE impact before severity assignment**: Before assigning severity ≥ Medium for any finding, attempt to compute the CE impact by tracing the flagged cell through the formula chain to the CE output. If the chain is traceable, compute the delta and write the estimated impact in column H before finalizing severity. CE impact <5% is Immaterial. Apply Nature × Materiality table: Defect + Immaterial = Medium; Gap + Immaterial = Medium; Judgment + Immaterial or Zero = Low. Do not assign severity qualitatively when CE impact is computable. If the chain is not directly traceable, write "Direction unknown" and proceed with qualitative severity judgment.

Append findings using `modify_sheet_values` to your staging sheet. Start at row 2 and append sequentially. Your staging sheet name is provided in session context.

**Tab prefix required**: When calling modify_sheet_values, prefix the range with your staging sheet name — e.g., stg-params!A2:I2 (use the staging sheet name from session context). A range without a tab prefix writes to the active sheet, not your staging tab.

Column reference: **A** Finding # (leave blank) | **B** Sheet | **C** Cell/Row | **D** Severity (write one of: `High` | `Medium` | `Low` — use two-axis notation in reasoning only; the /D or /H suffix is not written to the sheet) | **E** Error Type/Issue (write the exact label only — no additional text; choose one of: Formula | Parameter | Adjustment | Assumption | Legibility | Inconsistency | Sourcing | Box Link) — for Sourcing and Box Link findings (publication-readiness), leave column D blank | **F** Explanation (1–2 sentences max; lead with the specific problem; include the actual value; plain language) — when column E is Formula, begin column F with: [Copy-paste] | [Wrong reference] | [Year range] | [Sign error] | [Wrong operator] | [Off-by-one] (required by output-format.md) | **G** Recommended Fix (one sentence; lead with an imperative verb) | **H** Estimated CE Impact (exactly one of: Raises CE — [estimate] | Lowers CE — [estimate] | Raises CE — magnitude unknown | Lowers CE — magnitude unknown | No CE impact | Direction unknown) — use exact em-dash ( — ) with spaces on both sides; en-dash or plain hyphen variants will cause sort failures in the Wave 3 compaction agent | **I** Status (leave blank)

**Publication-readiness findings** (Error Type: Sourcing, Box Link, or Legibility): write them to your staging sheet in the same 9-column format, with column D (Severity) left blank. The compaction agent routes them to Publication Readiness based on Error Type. Do not write directly to the Publication Readiness sheet.

---

## Final step — write completion marker

After all findings are written, write ONE final row to your staging sheet immediately after your last finding (or at row 2 if no findings were written). This is the absolute last action.

- Column B: `formula-check-parameters`
- Column D: `AGENT_COMPLETE`
- Column F: `COVERAGE_ROWS: [source spreadsheet row ranges scanned, e.g., 1-150] | Staging sheet: [name from session context]. Filed [K] findings in rows 2–[K+1]. (Checked [N] rows across [sheet name(s)].)`
- All other columns: blank
