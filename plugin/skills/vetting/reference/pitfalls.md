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

## Severity and Scope Calibrations

### SC-001 (2026-04) — Benchmark parameter findings are valid regardless of vet timing
Never downgrade a benchmark finding because the spreadsheet was built before the parameter update. `reference/key-parameters.md` is authoritative at the time of vetting, not at the time the spreadsheet was built. Example: a spreadsheet using benchmark = 335 when `key-parameters.md` says 333 is wrong and should be flagged, even if the spreadsheet predates the November 2025 benchmark update. A post-vet decision not to fix it also does not make the original finding wrong.

**Applies to**: All agents that check against key-parameters.md

---

### SC-002 (2026-04) — xCash / GiveDirectly terminology rule applies to internal documents
The "xCash" → "benchmark" and "GiveDirectly" → "benchmark" terminology requirement applies to all GiveWell workbooks, including internal BOTECs and working documents. Do not downgrade or omit these findings on the grounds that the document is internal or not intended for publication. The terminology policy (November 2025) applies to GiveWell workbooks generally.

**Applies to**: readability, notes-scan

---

## Entry template

```
### [FP/FN/SC]-NNN (YYYY-MM) — Short title
One or two sentences describing the pattern: what Claude was doing wrong and what it should do instead. Be specific — name the value, formula pattern, or behavior that triggered the miscalibration.

**Applies to**: [agent file names]
```
