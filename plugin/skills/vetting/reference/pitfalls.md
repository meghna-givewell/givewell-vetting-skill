# Vetting Skill — Known Calibrations and Pitfalls

Each entry records a pattern from a completed vet that required calibration: a false positive (Claude flagged something that was not a real issue), a false negative (Claude missed something it should have caught), or a severity/scope adjustment. **Apply all entries before starting your checks.** New entries are added by the skill maintainer after each completed vet based on researcher feedback.

To add an entry: copy the template below, increment the ID, fill in the date, describe the pattern and the correct behavior, and name the agent(s) it affects.

---

## False Positive Risks — do not flag these

### FP-001 (2026-04) — Absolute-reference columns with an explanatory note
When a formula row uses a locked column reference (`$B$xxx`) uniformly across all geography columns, do not file a copy-paste finding until you have read the cell note. If the note explains the uniform reference is intentional (e.g., "we use Kenya as the reference baseline because the study was conducted there"), classify as intentional and do not file. When no note exists and the uniform reference is suspicious, file as Low/H, not High.

**Applies to**: formula-check-arithmetic

---

### FP-002 (2026-04) — Uncertainty language in cell notes is positive signal
Notes that say "rough estimate," "GW judgment call," "no external source available," "conservative assumption," or similar acknowledgments of uncertainty are a sign of good documentation practice. Do not flag these as documentation problems. The concern is the *absence* of any note on a judgment-based value, not the presence of honest uncertainty language.

**Applies to**: notes-scan

---

### FP-003 (2026-04) — Leverage multiplier >1 is not automatically a sign error
A leverage adjustment multiplier >1 does not automatically indicate a sign error. Before flagging, write out the mechanically correct formula structure that would justify a >1 multiplier for this row type (e.g., `CE_without_leverage × (1 + leverage_ratio)`, which produces >1 when leverage_ratio > 0). Then read the cell note and the row labels above and below. Only flag if the note's stated mechanism AND the formula structure both diverge from the correct form. A note mentioning "leverage" without specifying the formula convention is not sufficient to clear the finding — the formula structure must also match. If formula and note are both consistent, this is not an error.

**Applies to**: leverage-funging

---

### FP-004 (2026-04) — Leverage multiplicative vs. additive: both conventions are valid
Leverage/funging adjustments can be applied multiplicatively (scaling benefits or costs by a factor) or additively (shifting the numerator or denominator by a fixed amount). Both are correct if internally consistent with the model's stated approach. Do not flag multiplicative application as an error when additive is also acceptable — check for internal consistency, not a preferred convention.

**Applies to**: leverage-funging

---

### FP-005 (2026-06) — Don't over-flag intentional range exclusions
Before filing a "range too short" finding on a SUM or AVERAGE formula, read the label of the row just outside the range boundary (the first excluded row). If that label is "Subtotal", "Total", "Header", "Assumption", "N/A", or otherwise describes a non-component row, do not file — the exclusion is likely intentional and correct. Only file if the excluded row's label indicates it is a data component that should logically be included in the aggregation.

**Applies to**: formula-check-arithmetic, formula-check-edge-cases

---

### FP-006 (2026-06) — Time-series off-by-one may be correct due to label column offset
Before filing an off-by-one finding on a time-series SUM or AVERAGE, read the column (or row) headers to check whether a label column offsets the data start by one position. A range starting at the second year column instead of the first may be correct if the first column is a text label (e.g., "Year 1" as a row label) rather than a data column. Confirm the actual data columns versus label columns before filing.

**Applies to**: formula-check-arithmetic, formula-check-edge-cases

---

### FP-007 (2026-06) — High-severity protection does not override a confirmed no-CE-impact finding

When two instances of the same issue are filed at different severities, the high-severity protection rule retains the higher severity. This rule does NOT apply when CE impact is confirmed to be zero — i.e., the affected cell or formula demonstrably does not enter any CE calculation chain. A finding with "No CE impact" in column H is correctly filed at Low regardless of how many instances were observed. Do not elevate a no-CE-impact finding beyond Low even if two instances were flagged at different severities. Common examples: budget tab label swaps, Simple CEA header text errors, hardcoded benchmark in a non-CE display cell.

**Applies to**: all agents, final-review-compaction

---

## False Negative Risks — make sure to catch these

### FN-001 (2026-04) — GBD data vintage: always flag, even without a CE magnitude
When a tab uses an older GBD vintage (e.g., GBD 2021 or earlier when GBD 2024 is available), always flag it — even if you cannot compute the CE impact from updated data. Write `Direction unknown` in the CE Impact column — GBD burden trends vary by geography and cause and cannot be assumed directional. Do not skip or downgrade the finding because CE impact cannot be quantified. Severity Medium is acceptable and counts as a full catch.

**Applies to**: formula-check-data, formula-check-arithmetic

---

### FN-002 (2026-04) — Stale year in cell note: verify the value, not just the note
When a cell note cites a data vintage more than 2 years before the model's grant period start year AND the row is a key epidemiological or cost parameter (mortality rate, incidence, coverage, unit cost, or any parameter in `reference/key-parameters.md`), treat this as a trigger to verify the underlying value itself — not just the documentation. Run a WebSearch for the current value. If drift is <5%, file as **Medium/H** (Defect + Immaterial — the Defect floor applies; confirmed drift, even small, is not Low) and include the current value in the Explanation. If drift is ≥5%, file as **High/D** (Defect + Material) and include the current value (e.g., "Cell B14 note cites GBD 2019 — current GBD 2024 value is 0.42 vs. model's 0.38 (11% difference)"). If no updated value is found after searching, file as **Medium/H**.

**Applies to**: formula-check-arithmetic

---

### FN-003 (2026-06) — WebFetch required for any source with ≥5% weight in a weighted average
When a parameter is a weighted-average input with weight ≥5%, attempt WebFetch on the source URL before filing or classifying the finding. Without fetching: a wrong subgroup looks like an undocumented assumption (Medium at best); a methodology mismatch (rate vs. proportion) looks like a plausibility concern (Low or Medium). With fetching: the same issues become confirmed errors (High). Filing a finding without fetching on a ≥5% input is under-severity by default.

**Applies to**: formula-check-data, source-data-check, key-params-check

---

### FN-004 (2026-06) — SUMPRODUCT filter coverage: verify all intended rows are included
When checking SUMPRODUCT formulas, verify that the condition array explicitly covers all intended rows — not just that the formula evaluates without error. An implicit partial-range filter (e.g., a condition array that stops two rows above the data range's last row) silently excludes rows without raising an error or returning a visibly wrong result. Enumerate the condition array boundaries and compare them to the data array boundaries; if they differ, file a finding.

**Applies to**: formula-check-edge-cases, formula-check-arithmetic

---

### FN-005 (2026-06) — Copy-paste relative-reference errors across geography columns
When checking multi-geography models, compare FORMULA-mode values across all parallel geography columns, with particular focus on recently-added columns. A newly-added country column often copies formulas from an adjacent column; relative references then point to the source column's rows rather than the new column's rows, producing silently wrong values. Flag any geography column where formula references do not follow the same relative-offset pattern as all other geography columns.

**Applies to**: formula-check-arithmetic, formula-check-edge-cases

---

## Severity and Scope Calibrations

### SC-001 (2026-04) — Benchmark parameter findings are valid regardless of vet timing
Never downgrade a benchmark finding because the spreadsheet was built before the parameter update. `reference/key-parameters.md` is authoritative at the time of vetting, not at the time the spreadsheet was built. Example: a spreadsheet using benchmark = 335 when `key-parameters.md` says 333 is wrong and should be flagged, even if the spreadsheet predates the November 2025 benchmark update. A post-vet decision not to fix it also does not make the original finding wrong.

**Applies to**: All agents that check against key-parameters.md

---

### SC-002 (2026-04) — xCash / GiveDirectly terminology rule applies to internal documents
The "xCash" → "benchmark" and "GiveDirectly" → "benchmark" terminology requirement applies to all GiveWell workbooks, including internal BOTECs and working documents. Do not downgrade or omit these findings on the grounds that the document is internal or not intended for publication. The terminology policy (November 2025) applies to GiveWell workbooks generally.

**Applies to**: readability, notes-scan

---

### SC-003 (2026-06) — Parameter in the direct CE chain → High even when CE impact is not quantified
The severity rule already states: "When impact is unknown but the affected parameter sits in the confirmed direct CE calculation chain, treat as High." Apply this before concluding "Direction unknown" or filing Low. Confirm the chain by tracing from the affected cell to the final CE output. If confirmed, file High regardless of whether you can quantify the impact.

Example: Mengstie et al 2025 C20 = 33.1% per 100 person-years used as a cumulative probability. C20 → weighted average C21 → baseline mortality CEA!B11 → mortality reduction B13 → final CE B36: direct chain confirmed. File High, not Low.

**SC-003 applies only to confirmed errors, not to questions or gaps.** When the finding is fundamentally a question about researcher intent — "is this adjustment applicable?", "is this approach correct?" — SC-003 does not escalate it to High. The test: could a reasonable researcher defend the current model state without it being an error? If yes, the finding is a gap or assumption question (Medium ceiling), not a confirmed error. Examples of question-type findings that stay at Medium even when the parameter is in the CE chain: absent funging where applicability is uncertain (FN-008 ceiling: Medium), tiny parameter deviations where the magnitude is below the materiality threshold (FN-002 ceiling: Medium/H). When another pitfall entry explicitly specifies a ceiling severity ("file at Medium"), that ceiling holds — SC-003 does not override it.

**SC-003 High escalation requires demonstrated wrongness, not just chain membership.** Being in the CE chain is necessary but not sufficient for High. SC-003 escalates to High when ALL of the following hold: (1) the cell is confirmed in the direct CE chain via FORMULA mode; AND (2) the value is demonstrably wrong — it contradicts a GiveWell standard, is arithmetically incorrect, or has been confirmed (via WebFetch or FORMULA inspection) to be a transcription error, wrong subgroup, or wrong methodology. When condition (2) cannot be met — because the finding is a documentation gap, a plausibility concern, or a researcher approach that is debatable but possibly defensible — file at **Medium**, even when the cell is confirmed in the CE chain. Examples where CE-chain membership alone does NOT justify High: a discount rate choice where the correct rate is debated, GBD vintage staleness where only chain membership is confirmed (no value contradiction proven), a funging scope choice that may be intentional, a formula that deviates from a template but has a plausible alternative justification. The threshold for High is: a researcher presented with this finding would agree it is wrong without needing to make a new judgment call — the error is self-evident from the data, formula, or standard.

**Applies to**: all formula-check agents and source-data-check, source-citation-verify, sources, heads-up-epi, heads-up-evidence, heads-up-intervention

---

### SC-004 (2026-06) — Wrong subgroup from source paper → High; requires WebFetch to confirm
When a source paper reports multiple subgroup estimates, WebFetch the paper and confirm which subgroup the model uses before classifying severity. If the model uses a narrower, higher-mortality subgroup when the program serves a broader population, this is a confirmed error → High if the parameter is in the CE chain.

Example: Kumar et al 2025 C16 = 8% is the 1500–1999g subgroup mortality. WebFetch confirmed the all-LBW (<2500g) rate in the same study is 4.2% — a 1.9x overstatement. C16 carries 7.5% weight and feeds the CE chain → High.

**Applies to**: formula-check-data, source-data-check

---

### SC-005 (2026-06) — Methodology mismatch in a weighted-average input → at least Medium
When a weighted-average row uses a metric that doesn't match the methodology of the other rows (e.g., perception-based vs. clinically measured), file at least Medium. WebFetch to confirm → High if in CE chain.

Example: NFHS-5 C15 = 3.27% is drawn from "Small babies" (NFHS-5 Table 7.3) — a mother's perception-based size category, not a clinically measured LBW (<2500g) neonatal mortality rate. The value is substantially lower than all clinical estimates in the table because the perception category captures borderline cases a clinical threshold would exclude. 10% weight, in CE chain → Medium without WebFetch, High after confirming the source table.

**Applies to**: formula-check-data, source-data-check

---

### SC-006 (2026-06) — Formula robustness (DIV/0 guards) with no current CE impact → Low; group all instances
Formula robustness findings (missing IFERROR guards, unguarded divisions, formulas that go negative under extreme inputs) are Low when the dangerous condition cannot occur with current parameter values. Group all instances into a single Low finding listing all affected cells — do not create separate findings per formula.

Example: =1-B12/B11 goes negative only if treatment mortality exceeds counterfactual mortality. Current values (8.1% treatment, 9.38%–20% counterfactual) prevent this. File one grouped Low: "Formulas B13, C13, D13, B25, B26 have no IFERROR guard — safe at current values but will break if inputs are zeroed during editing." Not five separate Low findings.

**Applies to**: formula-check-arithmetic, formula-check-edge-cases

---

### SC-007 (2026-06) — Value matching a study subgroup or arm may be intentional → High
When a source value matches a specific subgroup or intervention arm rather than the overall population, the model may have intentionally used that subgroup as its counterfactual. Both an error interpretation and an intentional-choice interpretation may be plausible. File High, describe both interpretations in the Explanation, and do not downgrade to Low on the grounds the value might be intentional.

Example: Thomas et al 2024 C17 = 51% = mortality among non-KMC-initiated babies (172/336 non-initiated). The overall LBW mortality in the same study was 18% (213/1,152). Either (a) sourcing error — model should use overall population baseline; or (b) intentional — researcher chose the non-KMC arm rate as the counterfactual for what happens without intervention. Selection effects (sicker babies may have been excluded from KMC) make (b) methodologically suspect, but it is a defensible modeling choice. File High, explaining both readings.

**Applies to**: formula-check-data, source-data-check, formula-check-arithmetic

---

### SC-008 (2026-06) — GBD vintage staleness: High when CE chain confirmed, Medium otherwise
FN-001 sets the floor (always flag GBD vintage staleness, Medium minimum). SC-003 determines when Medium should be High (parameter in direct CE chain). Both rules apply together:
- Stale GBD vintage cell AND confirmed in direct CE chain (FORMULA-mode trace ≥2 hops to CE output) → **High**
- Stale GBD vintage cell, CE chain not confirmed in FORMULA mode → **Medium**

Do not cite FN-001 ("Medium is acceptable") to justify filing a CE-chain GBD vintage finding as Medium. FN-001 ensures you always file; SC-003 + this entry determine whether to file High or Medium. The key step is the FORMULA trace — without it, use Medium.

**Applies to**: formula-check-data, formula-check-arithmetic, heads-up-epi

---

### SC-009 (2026-06) — Missing source on a parameter: Medium only when CE chain or key-parameters.md confirmed
Medium severity rule #3 ("key input in the direct CE calculation chain lacks an external source") is frequently over-applied, causing Low-severity documentation gaps to be filed as Medium. Apply the threshold precisely:
- Row label appears in `key-parameters.md` AND has no source note → **Medium** (the parameter's correctness cannot be independently verified without the source)
- Cell is confirmed in the direct CE chain via FORMULA mode (≥2 hops to CE output) AND no external source or cell note explains the value → **Medium**
- All other missing-source cases → **Low**

Do not upgrade to Medium because a row "looks important" or "is probably in the CE chain" without FORMULA-mode confirmation. Both conditions (chain confirmed OR key-parameters.md match) must be checked before claiming Medium.

**Applies to**: formula-check-data, formula-check-arithmetic, notes-scan, source-data-check, source-citation-verify, sources

---

## Cross-Agent Scope Reference

This section identifies which agent **owns** each check category. When a non-owning agent encounters a potential issue that falls in an owned category, it should note the observation in its reasoning but defer the actual finding to the owning agent rather than filing independently. This prevents the same issue type from being filed with different severities by different agents across runs — a primary source of inter-run inconsistency.

| Check category | Owner agent | Non-owner behavior |
|---|---|---|
| Discount rate value | `key-params-check` | Other agents (formula-check-arithmetic, ce-chain-trace, heads-up-intervention) may read the discount rate cell as part of chain verification but must not file a Parameter finding for it. Note "discount rate check deferred to key-params-check" in AGENT_COMPLETE column F. |
| GBD/IHME vintage staleness | `formula-check-arithmetic` (primary); `formula-check-parameters` (stale-year cell note variant) | Heads-up-epi SHOULD run the full GBD vintage check internally (per its agent file) and file findings — it has context to assess epi-specific vintage issues. Ce-chain-trace should not independently file GBD vintage findings; if encountered, note "GBD vintage staleness deferred to formula-check-arithmetic" in reasoning. The Wave 2.5 reconciliation agent deduplicates if both heads-up-epi and formula-check-arithmetic accidentally file the same finding. |
| Cross-sheet reference concept mismatch (wrong-row reference) | `formula-check-arithmetic` (general case across all rows); `ce-chain-trace` (CE-chain-specific, Steps 3f and 4d) | Heads-up-epi, heads-up-intervention, and formula-check-data should not file wrong-row-reference findings — these belong to formula-check-arithmetic's cross-sheet inventory pass. If a suspicious reference is observed, note it in reasoning for the researcher but do not file a finding unless no formula-check-arithmetic agent is running for those rows (e.g., row scope explicitly excludes that section). |
| Cross-Cutting CEA Parameters doc value comparison (all parameter rows) | `consistency-check` | formula-check-structure Part B reads the same doc (spreadsheet ID `1ru1SNtgj0D9-vLAHEdTM27GEq_P17ySzG-aTxKD6Fzg`) and checks a named subset of parameters (SMC deaths-averted rates, Pryce et al., PMI Nigeria, VAS income ratio, NI income ratio). In a standard vet where both agents run, formula-check-structure should note any deviation it observes in reasoning ("parameter deviation observed; deferred to consistency-check") but must NOT file a finding — consistency-check's "enumerate every parameter row" mandate already covers all rows formula-check-structure would catch. Filing from formula-check-structure would produce duplicates with potentially divergent severity classifications that compaction may not cleanly deduplicate. |
| Simple CEA section ordering (correct calculation sequence: delivery parameters → effect size → costs → CE multiple) | `readability` (mandatory first check — runs a full sequence verification at Medium/H) | `formula-check-structure` includes Simple CEA ordering in its structural completeness checklist. When both agents run, formula-check-structure should record the checklist result (✓ or ✗) in its coverage declaration but **must NOT file a finding** — readability's more thorough sequence check already covers this at the correct severity. If readability is not running (formula-only scope), formula-check-structure should file the Low finding normally. |
| Staff first-name source citations in cell notes or source columns (e.g., "per Jack's model," "Bea's analysis," "from Meghna's spreadsheet") | `readability` (dedicated check — files as Publication Readiness Sourcing) | `notes-scan` Category H also catches these in the addressed-to-person and informal-citation scan. When both agents run, notes-scan should note instances in reasoning ("first-name citation observed at [ref]; deferred to readability") but must NOT file a separate finding — readability's exhaustive source-column scan already covers this. If readability is not running, notes-scan should file as normal under Category H. |
| Terminology ("x cash," "GiveDirectly" → "benchmark") | `readability` (primary — dedicated "Terminology" section with full sheet scan mandate) | `notes-scan` also catches these via SC-002, which explicitly applies to both agents. Both may file — the Wave 2.5 reconcile agent deduplicates overlapping PR findings. However: when readability is running, notes-scan should prefer noting the observation in reasoning and omitting a separate Legibility filing (the finding will already be filed at the correct grouped form by readability). If readability is not running, notes-scan should file normally. |
| IFERROR/IFNA error-masking checks in CE chain; array-formula SUMPRODUCT filter dimension checks | `formula-check-edge-cases` | Other agents (formula-check-arithmetic, ce-chain-trace) may observe IFERROR masking or SUMPRODUCT dimension mismatches but must not independently file — note "IFERROR/SUMPRODUCT dimension check deferred to formula-check-edge-cases" in reasoning. |
| SC-008 escalation for GBD vintage findings (High when CE chain confirmed) | `formula-check-parameters` | formula-check-arithmetic and heads-up-epi file GBD vintage findings at the correct base severity; formula-check-parameters owns the SC-008 escalation decision. Non-owning agents should not escalate a GBD vintage finding to High — note "SC-008 escalation deferred to formula-check-parameters" if the chain appears confirmed. |
| Enumeration of standalone hardcoded cells (non-formula) | `hardcoded-values` | Other agents may encounter hardcoded values during formula traversal but must not duplicate-enumerate them as standalone findings. Note the cell reference in reasoning and mark "hardcoded-values agent will enumerate" — do not file a separate Hardcoded finding. |
| Confidentiality/PII flag checks | `sensitivity-scan` | All other agents that encounter potential PII or confidential data (names, email addresses, donor information, financial figures) must not file findings — note "potential sensitivity flag deferred to sensitivity-scan" in reasoning and continue. |

**Applies to**: all agents

---

---

## Entry definitions (PIT-10)

**PIT-10 (2026-06) — Prefix definitions for FP/FN/SC entries**

- **FP** = False Positive — a pattern that looks like an error but is not one. An FP entry tells agents: "do not flag this; it is correct behavior." Apply FP entries before running checks.
- **FN** = False Negative — a real error that is hard to catch without explicit attention. An FN entry tells agents: "make sure to check for this; it is easy to miss." Apply FN entries as additional mandatory checks.
- **SC** = Severity Calibration — guidance on how to correctly rate the severity of a finding. An SC entry tells agents: "when you find this pattern, use this severity, not your default." Apply SC entries when classifying any matching finding.

All new entries should use the appropriate prefix. When uncertain whether an entry is FP, FN, or SC, prefer FN (it is safer to over-check than under-check).

**Applies to**: all agents, skill maintainer

---

### FN-007 (2026-06) — Cross-source effect construction vs. within-trial estimate

When a model derives its primary mortality (or morbidity) reduction by comparing values from two independently-sourced studies — e.g., `1 - (treated_mortality / baseline_mortality)` where the treated rate comes from one study and the baseline from another — flag this as a cross-source construction and verify against available within-trial or meta-analytic estimates (e.g., a Cochrane review for the same intervention). A within-trial randomized contrast is methodologically stronger because it controls for population differences across sources. Run a targeted WebSearch: `"[intervention] [outcome] Cochrane review"` or `"[intervention] [outcome] meta-analysis systematic review"`. If a Cochrane or comparable systematic review reports a materially different raw effect (>15% relative from the model's constructed number), file as **Medium/Assumption**: "The model's [X%] reduction is constructed by dividing two independently-sourced rates rather than drawn from a within-trial comparison. [Source] reports [Y%] from a within-trial/meta-analytic contrast. Confirm whether the cross-source construction is appropriate, and document the justification in a cell note." If no external meta-analysis is available, file as **Low/Assumption**: "The model constructs its primary effect size from two independently-sourced rates — verify a within-trial comparison is not available that would be more directly applicable."

**Applies to**: heads-up-evidence, formula-check-data

---

### FN-008 (2026-06) — Absent funging adjustment in direct CE chain when comparable programs have one

When the direct CE calculation chain (the rows between the effect-size inputs and the final CE multiple) contains no funging or counterfactual displacement adjustment row, check whether comparable GiveWell programs of the same type apply an explicit funging reduction. GiveWell's top-charity CEAs include explicit funging adjustments for SMC (~43%), VAS (~26%), deworming (~24%), and ITNs (~30%). For a new intervention in the same category (malaria prevention, child health, nutrition), the absence of a funging row in the direct CE chain is a gap to verify — not to assume intentional. File as **Medium/Adjustment**: "No funging or government replacement adjustment appears in the direct CE chain. Comparable GiveWell programs of this type apply funging adjustments of [X%–Y%]. If funging is not applicable (e.g., no comparable government program exists), add a cell note documenting this judgment." File **Low** if the program type is genuinely novel with no comparable GiveWell precedent. Do not flag if a funging row exists in a leverage tab whose output feeds into the CE chain — in that case the adjustment enters the chain through the leverage calculation.

**Applies to**: leverage-funging, ce-chain-trace

---

### FN-009 (2026-06) — Treatment cascade timing confusion in staged disease models

In staged disease models (HIV, TB, hepatitis), transmission risk and benefit duration formulas require a specific cascade-stage timing parameter. Cross-sheet references to an adjacent timing row produce numerically plausible but conceptually wrong values. The canonical HIV cascade has multiple closely proximate timing rows — e.g., "time from infection to diagnosis," "time from infection to treatment start," "time from infection to viral suppression" — with similar numerical values; a wrong-row reference passes a plausibility check. The conceptually correct row depends on which event ends the risk window: in HIV models, transmission risk ends at *treatment start* (when ART suppresses viral load), not at *diagnosis* (a diagnosed but untreated person remains infectious).

When a formula computes duration of exposure, transmission risk, or time-at-risk in a staged disease model, explicitly verify that the row label at the referenced cell matches the required cascade stage — not just that the value is in a plausible range. Apply this check during Step 3f semantic verification and Step 4d stale-row checks.

File as **High/Formula [Wrong reference]** if a wrong-cascade-stage timing reference is confirmed in FORMULA mode AND the cell feeds the direct CE chain (≥1 hop per SC-012).

**Applies to**: ce-chain-trace, formula-check-arithmetic, heads-up-epi, heads-up-intervention

---

### FN-006 (2026-06) — Cross-tab reference row-label mismatch (PIT-6)

When a formula references another tab and the referenced row produces a numerically plausible value, verify that the row **label** in the referenced tab also matches the expected parameter — not just the row number. Cross-tab references can point to the correct row number but the wrong logical row if rows have been inserted or deleted since the formula was written. Example: `='Inputs'!B14` may have been written when B14 = "Malaria mortality rate" but now B14 = "ITN usage rate" after a row insertion — the value might still be in a plausible range, masking the mismatch. Verify row labels whenever tracing cross-tab references.

**VoI parameter corollary**: When tracing VoI cells, do not assume cell addresses based on template position. Always read the cell label (FORMATTED_VALUE, column A/B of the same row) before describing what the cell contains — VoI models frequently deviate from standard template row order. Mislabeling a cell in a finding's Recommended Fix can corrupt the model if the researcher applies the fix without verifying.

**Applies to**: formula-check-arithmetic, ce-chain-trace, formula-check-data

---

### SC-010 (2026-06) — Non-owner-runs deferral rule (PIT-7)

When an agent encounters a check that belongs to a different agent's scope (see Cross-Agent Scope Reference table above), do not silently skip it and do not file a full finding. Instead, file a **Low/Assumption** placeholder: "Possible issue — deferred to [owning agent]: [brief description of what was observed]. See Cross-Agent Scope Reference in pitfalls.md." This ensures the observation is on record if the owning agent does not run, while preventing duplicate findings when it does. The reconcile agent will promote placeholder findings to full findings if the owning agent did not cover them.

**Applies to**: all agents

---

### SC-011 (2026-06) — Missing-rows detection ownership (PIT-8)

When a row expected in the model is absent (deleted, merged, hidden, or off-screen), the **missing-row detection is owned by `formula-check-structure`**. Other agents that observe a missing row during formula traversal should note "expected row absent — deferred to formula-check-structure" in reasoning and must not file a separate finding. This prevents duplicate missing-row findings across formula-check-arithmetic, key-params-check, and ce-chain-trace. Exception: if `formula-check-structure` is not in scope for this vet (e.g., a formula-only lite pass), the first agent to observe the missing row should file it normally.

**Applies to**: formula-check-arithmetic, key-params-check, ce-chain-trace, notes-scan

---

### SC-012 (2026-06) — SC-003 hop minimum clarification: 1 hop vs. 2 hops (PIT-9)

SC-003 ("Parameter in the direct CE chain → High even when CE impact is not quantified") requires **≥1 documented hop** from the affected cell to the CE output to confirm chain membership. A single direct reference (the cell feeds a CE-chain cell with one formula hop) is sufficient to trigger the High escalation. The **≥2 hop** requirement is for **SC-008** (GBD vintage staleness High escalation): SC-008 requires FORMULA-mode trace confirming ≥2 hops to CE output before escalating GBD vintage findings from Medium to High. Do not confuse these thresholds:
- SC-003 chain confirmation: **≥1 hop** → High/D for parameter findings
- SC-008 GBD vintage escalation: **≥2 hops** (FORMULA-mode confirmed) → High; otherwise Medium

**Applies to**: formula-check-arithmetic, formula-check-data, ce-chain-trace, key-params-check

---

### SC-013 (2026-06) — Cost denominator gap: quantify the ratio; High when full budget / denominator > 1.2×

When the CE denominator is a subset of the total grant budget (e.g., programmatic costs only, excluding evaluation costs), compute the ratio: full_grant_budget / CE_denominator. If this ratio exceeds 1.2× (i.e., the omitted cost component is more than 20% of what was counted), the CE estimate is materially overstated → file as **High/Parameter**. Quantify the CE impact: "Reported CE of [X]× → ~[X / ratio]× when full budget is used as denominator." If the ratio is ≤1.2×, file at Medium. If a cell note explicitly justifies the exclusion (e.g., "evaluation costs funded by a separate earmarked grant"), file at Low. Do not file at all if the excluded costs genuinely do not generate the grant's benefits.

**Applies to**: formula-check-arithmetic, ce-chain-trace, leverage-funging

---

### SC-014 (2026-06) — Funging applied to VoI component only (not total CE) → High/Adjustment

When a model contains both a direct CE component and a VoI/optionality component, and a funging or downside adjustment exists but is applied only to the VoI sub-calculation (not to total CE), this is a structural misapplication — file as **High/Adjustment**: "Funging adjustment at [cell] is applied only to the VoI component ([VoI cell]) and not to the direct CE component ([direct CE cell]). Total CE ([total CE cell] = [X]×) therefore omits the funging penalty on the direct component. Restructure to apply funging to total CE, not only the VoI sub-calculation." If the model's stated approach explicitly justifies VoI-only scoping with a documented rationale, file at Medium and ask the researcher to confirm. If uncertain whether scoping is intentional, file at Medium.

**Applies to**: leverage-funging, ce-chain-trace

---

### SC-015 (2026-06) — GBD permalink returns 403: WebFetch IHME directly before defaulting to Medium

When a GBD/IHME permalink in the spreadsheet returns HTTP 403 (expired session link), do not immediately default to Medium. Run a targeted WebFetch or WebSearch to confirm the latest available GBD vintage — e.g., search "GBD 2024 released" or fetch the IHME website directly. If a newer vintage is confirmed available (published before the model's grant period), escalate to High per SC-008 when the CE chain is confirmed via FORMULA-mode trace (≥2 hops). Use Medium only when (a) the IHME fetch also fails and no newer vintage can be confirmed, or (b) the CE chain cannot be confirmed in FORMULA mode. Document in the finding: "Permalink returned 403; IHME website confirmed GBD [year] released [date], making the model's GBD [year-1] data stale."

**Applies to**: formula-check-arithmetic, formula-check-data, heads-up-epi

---

### SC-016 (2026-06) — Explicitly labeled placeholder in the CE chain → always High

When a cell note explicitly labels a value as a "placeholder," "pending update," "to be confirmed," "TBC," or "TBD" — AND the cell is confirmed in the direct CE chain (≥1 hop to CE output per SC-012) — file as **High** regardless of whether the current value seems numerically reasonable. The explicit placeholder label signals the researcher has not yet committed to this value; any CE estimate depending on it is provisional. Sensitivity coefficient is not required to justify High: the label alone is sufficient. Required Explanation language: "[Param] ([cell]) = [value] is explicitly marked as a placeholder in the cell note; as the highest-sensitivity parameter in the direct CE chain, do not publish CE until this is replaced with an empirically grounded value." Apply jointly with SC-003 — SC-016 adds only the "explicit placeholder label" trigger; CE chain confirmation is still required.

**Applies to**: all formula-check agents, heads-up-evidence, ce-chain-trace

---

### SC-018 (2026-06) — Low finding filing threshold: actionable issues only, not questions or observations

A finding at any severity — but especially Low — must describe something the researcher should **fix, update, or change**. Do not file a finding if the primary purpose is to note an observation, ask a clarifying question, or suggest adding documentation.

**Do NOT file Low for:**
- Observations the researcher already knows ("control group received enhanced standard of care" — this is a structural feature of RCTs, not a finding)
- Questions whose answer might be "yes, that's intentional" with no action needed ("confirm this coverage assumption is appropriate" — if you have no evidence it's *wrong*, don't file)
- Legibility, sourcing, or terminology notes — these route to Publication Readiness, not main Findings
- "For publication, add a note explaining..." suggestions — Publication Readiness is the correct channel
- Speculative concerns with no supporting evidence ("this might overstate CE if...")
- Generic documentation suggestions where the value is likely correct ("document why 100% scale-up is assumed")

**DO file Low for:**
- A specific formula that has a specific wrong output and a specific fix
- A concrete parameter known to be outdated, with a newer source already identified
- A small arithmetic discrepancy with a specific corrected value
- A grouping of formula robustness issues (IFERROR, division guards) per SC-006 — these have a specific fix (add IFERROR)
- A missing required element (per a defined GW standard) where the fix is concrete

**The test before filing any Low:** "If a researcher reads this finding, will they take a specific action — look something up, change a value, fix a formula — or will they read it and move on?" If the answer is "move on," don't file. A well-calibrated vet has very few Lows in the main Findings sheet; most low-severity observations belong in Publication Readiness or should not be filed at all.

**Applies to**: all agents

---

### SC-017 (2026-06) — High finding calibration: 3–8 Highs per vet is typical; review if more

A well-calibrated GiveWell vet of a standard BOTEC produces **3–8 High findings**. If an agent has filed more than 8 Highs before writing AGENT_COMPLETE, it must pause and review each High for downgrade to Medium using the following gate:

1. Does this finding identify a value that is **demonstrably wrong** — i.e., contradicts a GiveWell standard, is arithmetically incorrect, or has been confirmed via source-fetching to be a wrong subgroup or transcription error?
2. **If no**: downgrade to Medium. A CE-chain cell with a debatable or potentially-defensible value is a Medium, not a High.
3. **If yes**: keep at High.

Bright-line High exceptions that always stay High regardless of count (do not downgrade these): moral weight violations, benchmark value violations, explicitly labeled placeholders in the CE chain (SC-016), demonstrated arithmetic errors with confirmed CE impact, clearly broken formulas with bad output.

This calibration target is per-agent. If multiple agents run in parallel and the reconciled total exceeds ~10 Highs, Wave 2.5 reconciliation should consolidate findings that cover the same root issue before promoting to the final Findings sheet.

**Why this matters**: Over-elevation to High creates review fatigue and obscures the findings that genuinely require immediate researcher action. When every CE-chain concern is High, the signal of "this is broken now" is lost.

**Applies to**: all formula-check agents, ce-chain-trace, heads-up-epi, heads-up-evidence, heads-up-intervention, final-review-compaction

---

### SC-019 (2026-06) — Geographic transfer of a key parameter without documented justification → Medium/Assumption

When a model applies a key parameter (transmission rate, efficacy estimate, disease burden figure) derived from a study in a different country or income-group context — e.g., US or European rates applied to LMIC programs — and no cell note documents why the extrapolation to the target geography is valid, file as **Medium/Assumption** when the parameter is confirmed in the direct CE chain. Do not file as Low on the grounds that the value is numerically plausible: plausibility and transferability are different tests. The required test is: can a researcher verify that the value applies to this program's target population from the cited source alone? If not, file Medium. Low is correct only when (a) a cell note explicitly justifies the geographic transfer with literature supporting the extrapolation, or (b) a sensitivity analysis confirms the parameter has negligible CE impact. Do not escalate to High under SC-003 — a geographic transfer assumption is not "demonstrably wrong" unless a specific LMIC-context study shows a materially different value and the CE chain is FORMULA-confirmed.

Example: Li 2019 HIV transmission rates from US surveillance applied to LMIC program populations without documentation. AB filed Low (plausible); MR filed Medium (unverifiable applicability to target context). MR is correct.

**Applies to**: formula-check-data, source-data-check, heads-up-epi, heads-up-intervention, ce-chain-trace

---

### SC-020 (2026-06) — Stale cost estimate in cost denominator without inflation adjustment → Medium/Parameter

When the cost denominator uses cost estimates from a source published more than 3 years before the model's grant period start year, and no cell note documents an inflation adjustment or explains why nominal costs remain valid, file as **Medium/Parameter** — not Low. Program delivery and healthcare costs in LMIC settings change materially over multi-year periods (commodity price changes, currency fluctuation, procurement scale). A cost estimate more than 3 years old without adjustment is a concrete parameter gap, not merely a documentation gap. This extends FN-002's stale-vintage logic explicitly to cost rows: run a targeted WebSearch for updated cost benchmarks before filing; if a current estimate differs by ≥5%, upgrade to High/D per SC-003. Low is correct only when (a) the cell note includes an explicit inflation adjustment or documents why nominal costs are stable, or (b) sensitivity analysis confirms cost uncertainty has negligible CE impact.

Example: CHAI 2014 cost estimates in the cost denominator of a current-grant BOTEC, no inflation adjustment noted. AB filed Low; MR filed Medium. MR is correct.

**Applies to**: formula-check-arithmetic, formula-check-data, source-data-check, ce-chain-trace

---

### SC-021 (2026-06) — Stale benchmark: prescribing value change when rationale note is the correct fix

When a stale GiveDirectly benchmark is identified (e.g., 0.00335 when the current value is 0.00333), do not prescribe "update to 0.00333" as the only recommended fix. Researchers frequently retain the older value intentionally for cross-program comparability — changing it would invalidate comparisons against prior GiveWell analyses. The correct Recommended Fix is: "Either update the benchmark to the current GW value (0.00333) OR add a rationale note documenting why the older value is retained (e.g., 'kept at 0.00335 for consistency with [program X] analysis')." Prescribing only the value change has occurred in 3 consecutive stable-period vets (#32, #34, #35), making this the most consistent calibration error for stale benchmark findings.

**Applies to**: key-params-check, ce-chain-trace, cross-tab-compare, formula-check-data

---

## Entry template

```
### [FP/FN/SC]-NNN (YYYY-MM) — Short title
One or two sentences describing the pattern: what Claude was doing wrong and what it should do instead. Be specific — name the value, formula pattern, or behavior that triggered the miscalibration.

**Applies to**: [agent file names]
```
