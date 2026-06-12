# Vetting Skill — Known Calibrations and Pitfalls

Each entry records a pattern from a completed vet that required calibration: a false positive (Claude flagged something that was not a real issue), a false negative (Claude missed something it should have caught), or a severity/scope adjustment. **Apply all entries before starting your checks.** New entries are added by the skill maintainer after each completed vet based on researcher feedback.

To add an entry: copy the template below, increment the ID, fill in the date, describe the pattern and the correct behavior, and name the agent(s) it affects.

---

## False Positive Risks — do not flag these

### FP-001 (2026-04) — Absolute-reference columns with an explanatory note
When a formula row uses a locked column reference (`$B$xxx`) uniformly across all geography columns, do not file a copy-paste finding until you have read the cell note. If the note explains the uniform reference is intentional (e.g., "we use Kenya as the reference baseline because the study was conducted there"), classify as intentional and do not file. When no note exists and the uniform reference is suspicious, file as Low/H with Researcher judgment needed ✓, not High.

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

## False Negative Risks — make sure to catch these

### FN-001 (2026-04) — GBD data vintage: always flag, even without a CE magnitude
When a tab uses an older GBD vintage (e.g., GBD 2019 when GBD 2021 is available), always flag it — even if you cannot compute the CE impact from updated data. Write `Lowers CE — magnitude unknown` (or `Direction unknown` if ambiguous) in the CE Impact column. Do not skip or downgrade the finding because CE impact cannot be quantified. Severity Medium is acceptable and counts as a full catch.

**Applies to**: formula-check-data, formula-check-arithmetic

---

### FN-002 (2026-04) — Stale year in cell note: verify the value, not just the note
When a cell note cites a data vintage more than 2 years before the model's grant period start year AND the row is a key epidemiological or cost parameter (mortality rate, incidence, coverage, unit cost, or any parameter in `reference/key-parameters.md`), treat this as a trigger to verify the underlying value itself — not just the documentation. Run a WebSearch for the current value. If drift is <2%, file as Low/H noting the vintage is stale but value is materially unchanged. If drift ≥2%, file as Medium/H and include the current value in the Explanation (e.g., "Cell B14 note cites GBD 2019 — current GBD 2021 value is 0.42 vs. model's 0.38 (11% difference)"). If no updated value is found after searching, file as Medium/H with Researcher judgment needed ✓.

**Applies to**: formula-check-arithmetic

---

### FN-003 (2026-06) — WebFetch required for any source with ≥5% weight in a weighted average
When a parameter is a weighted-average input with weight ≥5%, attempt WebFetch on the source URL before filing or classifying the finding. Without fetching: a wrong subgroup looks like an undocumented assumption (Medium at best); a methodology mismatch (rate vs. proportion) looks like a plausibility concern (Low or Medium). With fetching: the same issues become confirmed errors (High). Filing a finding without fetching on a ≥5% input is under-severity by default.

**Applies to**: formula-check-data, source-data-check, key-params-check

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

**Applies to**: all formula-check and source-check agents

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

### SC-007 (2026-06) — Value matching a study subgroup or arm may be intentional → High with Researcher judgment needed ✓
When a source value matches a specific subgroup or intervention arm rather than the overall population, the model may have intentionally used that subgroup as its counterfactual. Both an error interpretation and an intentional-choice interpretation may be plausible. File High with Researcher judgment needed ✓, describe both interpretations in the Explanation, and do not downgrade to Low on the grounds the value might be intentional.

Example: Thomas et al 2024 C17 = 51% = mortality among non-KMC-initiated babies (172/336 non-initiated). The overall LBW mortality in the same study was 18% (213/1,152). Either (a) sourcing error — model should use overall population baseline; or (b) intentional — researcher chose the non-KMC arm rate as the counterfactual for what happens without intervention. Selection effects (sicker babies may have been excluded from KMC) make (b) methodologically suspect, but it is a defensible modeling choice. File High with Researcher judgment needed ✓, explaining both readings.

**Applies to**: formula-check-data, source-data-check, formula-check-arithmetic

---

## Cross-Agent Scope Reference

This section identifies which agent **owns** each check category. When a non-owning agent encounters a potential issue that falls in an owned category, it should note the observation in its reasoning but defer the actual finding to the owning agent rather than filing independently. This prevents the same issue type from being filed with different severities by different agents across runs — a primary source of inter-run inconsistency.

| Check category | Owner agent | Non-owner behavior |
|---|---|---|
| Discount rate value | `key-params-check` | Other agents (formula-check-arithmetic, ce-chain-trace, heads-up-intervention) may read the discount rate cell as part of chain verification but must not file a Parameter finding for it. Note "discount rate check deferred to key-params-check" in AGENT_COMPLETE column F. |
| GBD/IHME vintage staleness | `formula-check-arithmetic` (primary); `formula-check-parameters` (stale-year cell note variant) | Heads-up-epi SHOULD run the full GBD vintage check internally (per its agent file) and file findings — it has context to assess epi-specific vintage issues. Ce-chain-trace should not independently file GBD vintage findings; if encountered, note "GBD vintage staleness deferred to formula-check-arithmetic" in reasoning. The Wave 2.5 reconciliation agent deduplicates if both heads-up-epi and formula-check-arithmetic accidentally file the same finding. |
| Cross-sheet reference concept mismatch (wrong-row reference) | `formula-check-arithmetic` (general case across all rows); `ce-chain-trace` (CE-chain-specific, Steps 3f and 4d) | Heads-up-epi, heads-up-intervention, and formula-check-data should not file wrong-row-reference findings — these belong to formula-check-arithmetic's cross-sheet inventory pass. If a suspicious reference is observed, note it in reasoning for the researcher but do not file a finding unless no formula-check-arithmetic agent is running for those rows (e.g., row scope explicitly excludes that section). |

**Applies to**: all agents

---

## Entry template

```
### [FP/FN/SC]-NNN (YYYY-MM) — Short title
One or two sentences describing the pattern: what Claude was doing wrong and what it should do instead. Be specific — name the value, formula pattern, or behavior that triggered the miscalibration.

**Applies to**: [agent file names]
```
