# Key Parameters Quick Reference

Flag deviations from these values unless the sheet provides an explicit documented rationale.

| Parameter | Current Value | Notes |
|---|---|---|
| Benchmark (UoV per $) | **0.00333** | Updated Nov 2025; old value 0.003355 — flag if stale. **KEY-6**: Any deviation from 0.00333 (even to the old value 0.003355) is always **High/D** — no tolerance zone, no documented-rationale exception. The benchmark is cross-cutting; a miscalibration propagates to every CEA that uses it. See also the Acceptable Ranges table below — the Flag severity column confirms High/D for this parameter. |
| Neonatal moral weight (under 1 month) | **84** | Source: GW Moral Weights by age band table below. Values significantly below 84 (e.g., 70) are not valid age-weighted variants — flag as Parameter unless the researcher provides an explicit documented rationale. |
| Discount rate | **4%** | Components: 1.7% + 0.9% + 1.4%; pure time preference = 0%. **Filing calibration**: if a model has a multi-year benefit stream (>3 years) and applies no discount rate, file as **Low/H** — do not file as Medium or High. GiveWell intentionally omits time discounting in some newer-intervention CEA types. Escalate to Medium only if the researcher confirms discount rates should apply and they are absent. |
| Avert under-5 death (malaria/vaccines) | **116 UoV** | |
| Avert over-5 death (malaria) | **73 UoV** | = 63% of under-5 value |
| Avert death, 6–59 month child (VAS) | **119 UoV** | |
| Avert maternal death (MNH/reproductive health) | **125 UoV** | From GW Facility-based MNH BOTEC; higher than over-5 value due to DALYs per maternal death calculation. Use this when a model cites GW MNH BOTEC as the source — do not infer from general age-specific tables |
| Long-term income ratio (SMC/VAS/New Incentives) | **0.3064** | |
| Income effects — % increase in ln(income) per malaria case averted (children under 15) | **0.58088%** | From GW ITN CEA; used in malaria programs (ITNs, case management, SMC). Pre-Nov 2025 models may use 0.65% — flag as **Medium/H** if value deviates from 0.58088% |
| p(update) cap (VOI/optionality) | **≤ 50%** | Above 50% implies program should be funded directly |
| VOI adjustment application | Apply wrong-risk + influencing-other-funders to VoI component; funging to total | Do not apply all adjustments to the aggregate CE |
| VOI adjustment scope (detail) | wrong-risk and influencing-other-funders apply to VOI component **only**; funging applies to the **total** CE | Do NOT dismiss as equivalent even when wrong-risk and other-funders numerically cancel — the funging adjustment must be correctly scoped away from direct benefits. Applying all three to total CE is a structural error. |
| VOI — probability trial fails | Default **10%** | Speculative; update upward for politically unstable contexts |
| VOI — probability we influence other funders | Default **20%** | Highly speculative; adjust based on total RFMF landscape and whether the study is answering a field-relevant question |
| VOI — probability we're wrong (t-stat rules of thumb) | t≥3: **−10%**; t≈2: **−20%**; t≈1.7: **−30%**; t≈1.2: **−50%** | Downward adjustment to VOI for risk of acting on a biased/noisy trial result; larger penalty for less precise trials |
| VOI — how long we fund after study | Default **10 years** | Highly speculative; update downward if program has a clearly finite implementation window |
| VOI — CE of reallocated funding | Default **1–2× above bar** | E.g., if bar is 6×, assume program is 7–8×; conservative assumption |
| Discount rate — income benefits | **4%** per year | Standard for income/consumption benefits over any time horizon |
| Discount rate — long-term health benefits | **0.5%** per year | Only for health benefits spanning several decades or more; do not discount near-term health benefits |
| Resource sharing multiplier — household income effect | **×5** (typical household size) | Use when relying on household income/consumption effects. **KEY-4**: The three resource-sharing rows (household, individual, development/children) are the complete standard set. If a model uses a resource-sharing multiplier not matching one of these three types, flag as **Medium/H** and verify the model's stated rationale. If a model uses resource sharing but does not cite which multiplier applies, flag as **Low/H** (documentation gap). |
| Resource sharing multiplier — individual income effect | **~×2.5** (50% share × 5 HH members) | Use when relying on effects on individual income |
| Resource sharing multiplier — development effects (children) | **×2** (50% share × ~4 HH members over time) | For children who will eventually form own households |
| Treatment costs averted — top 4 child health charities | **+20%** supplemental adjustment | **KEY-5**: This is the treatment-cost parameter for the top 4 child health charities (AMF, Malaria Consortium, HKI, New Incentives). Standard value: **+20%** supplemental adjustment to benefits. Source: GiveWell cross-cutting parameter docs. Acceptable range: 15%–25% (flag deviations outside this range as **Medium/H**; flag absence entirely as **Medium/H** for programs in scope). If the model applies a different treatment-cost figure with documented rationale, flag as **Low/H** rather than Medium. |
| Discount rate — TA death-averting programs | **1.4%** per year | Temporal uncertainty component only; used for TA grants where the primary benefit is near-term mortality reduction; use **4%** for income/consumption streams in the same model |
| TA — p(failure to shift status quo) | Default **30%** | **KEY-3 — TA p(failure) definition**: `p(failure)` in the TA context means the probability that the TA engagement fails to change government behavior — i.e., the government does not adopt or scale the program that GiveWell's grant is intended to accelerate. It is distinct from `VOI p(trial fails)` (10%), which is the probability that a study produces an uninformative or wrong result. The GiveWell-standard default value is **30%**, calibrated for scale-up TA grants. **TA p(failure) is model-specific** — verify against the grant's TA modeling assumptions before filing. For quality-improvement TA (improving an existing program rather than scaling a new one), the 30% default may not apply; flag absence as **Low/H** only, not Medium, without confirmation from the researcher. |
| TA speed-up benchmarks (years to reach steady-state coverage) | RTS,S: **2**; DtW: **4**; IFA: **4**; Dual tests: **5**; HPV: **6**; ILC: **13** | Cross-program reference for the "speed-up of steady state due to TA" parameter; ILC is high due to dual steady-state structure |
| Years to benefits | **10** | Years from grant disbursement until the program's benefits start flowing. ANY deviation from 10 years triggers at minimum **Medium/H**, even if the value falls within the Min/Max range in the acceptable-ranges table. The finding may be downgraded to **Low/H** only if the researcher explicitly provides a rationale in Step 0.5 or in a cell note — do not omit the finding on the grounds that the value is "within range" or that program context justifies it absent an explicit documented rationale. |

## Moral Weights by Age Band (UoV per death averted)

Source: https://www.givewell.org/how-we-work/our-criteria/cost-effectiveness/moral-weights  
These are the authoritative per-death moral weights by age group in units of doubling consumption (UoV). Any deviation from these values in a model is **High/D**. When a model uses a composite moral weight (e.g., "116 UoV for under-5 malaria deaths"), it should be derivable as a weighted average of the relevant age-band values below — check both the composite value and the age-band inputs when they are visible.

**KEY-7 — Composite moral weight handling**: When a model uses a composite moral weight (an average of adult + child + neonatal weights, or a weighted average across age bands), verify in two steps: (1) Check each individual age-band component against the table below — any individual component that deviates from the table value is **High/D** in its own right. (2) Check the composition formula — verify that the composite value is correctly computed as a weighted average of the checked components using the model's stated population weights. A correct composite derived from correct components = no finding. A correct composite derived from wrong components = flag the components (High/D each). A wrong composite even if components are correct = flag the composition formula (Medium/H or High/D depending on CE chain confirmation). Do not assume a composite value is correct without tracing to its components.

| Age band | Moral weight (UoV) |
|---|---|
| Stillbirth | 33 |
| Early Neonatal | 84 |
| Late Neonatal | 84 |
| Post Neonatal | 101 |
| 1 to 4 | 127 |
| 5 to 9 | 134 |
| 10 to 14 | 133 |
| 15 to 19 | 126 |
| 20 to 24 | 118 |
| 25 to 29 | 113 |
| 30 to 34 | 106 |
| 35 to 39 | 100 |
| 40 to 44 | 86 |
| 45 to 49 | 76 |
| 50 to 54 | 65 |
| 55 to 59 | 55 |
| 60 to 64 | 40 |
| 65 to 69 | 31 |
| 70 to 74 | 21 |
| 75 to 79 | 16 |
| 80 to 84 | 12 |
| 85 plus | 12 |

**How to use**: When a model stores age-band moral weights directly (not composite values), compare each against the exact value above. Cross-check using the GiveWell Moral Weights doc (ID: `1GAcGQSyBQxcB6oGJFGGWCYqwY-jW7oahJJK-cTZOkMc`) to confirm the values remain current.

---

**KEY numbering note**: KEY-1 and KEY-2 were retired; the active sequence begins at KEY-3. Do not reuse KEY-1 or KEY-2 for new entries.

## Acceptable Ranges for Algorithmic Comparison

Deviations from the Exact Value column trigger a finding at the severity shown in the Flag severity column. The benchmark, moral weights, and direct-program parameters trigger **High/D**. Discount rate, income effects, and years-to-benefits trigger **Medium/H** (intentional-choice parameters that vary by program type). The Min/Max columns are reference context only — they do NOT define a tolerance zone. A value within the range that is not the Exact Value still triggers a finding at the stated severity.

| Parameter | Exact Value | Min | Max | Flag severity |
|---|---|---|---|---|
| Benchmark (UoV per $) | 0.00333 | 0.003 | 0.0034 | Yes — High/D |
| Avert under-5 death (malaria/vaccines) | 116 | 110 | 122 | Yes — High/D |
| Avert over-5 death (malaria) | 73 | 69 | 77 | Yes — High/D |
| Avert death 6–59m VAS | 119 | 113 | 125 | Yes — High/D |
| Avert maternal death | 125 | 119 | 131 | Yes — High/D |
| Discount rate (general) | 4% | 3% | 5% | Yes — Medium/H |
| Discount rate (TA death-averting) | 1.4% | 1% | 2% | Yes — Medium/H |
| Discount rate (long-term health) | 0.5% | 0.3% | 0.8% | Yes — Medium/H |
| Discount rate — absent / 0% / omitted | N/A | — | — | Yes — **Low/H** (model-completeness gap; escalate to Medium only if researcher confirms discounting should apply) |
| Income effects malaria — absent / not applied | N/A | — | — | Yes — **Low/H** (not all malaria models apply income effects; flag as Low documentation gap, not Medium — escalate only if researcher confirms income effects should apply and are absent) |
| Years to benefits — absent / not applied | N/A | — | — | Yes — **Low/H** (documentation gap; absence alone does not meet the Medium/H threshold; confirm with researcher whether a different benefit timing assumption applies before escalating) |
| Income effects malaria | 0.58088% | 0.55% | 0.65% | Yes — Medium/H. **KEY-8**: Max acceptable value is **0.65%** (symmetric upper bound around standard value). The range 0.55%–0.65% is approximately symmetric around 0.58088%. There is no directional constraint — both upward and downward deviations are equally flaggable at Medium/H. The pre-Nov 2025 value of 0.65% falls at the upper edge of the acceptable range and should still be flagged as Medium/H since it is not the exact standard value. |
| Long-term income ratio | 0.3064 | 0.25 | 0.35 | Yes — High/D |
| Years to benefits | 10 | 8 | 15 | Yes — Medium/H |
| Moral weight — Stillbirth | 33 | — | — | Yes — High/D |
| Moral weight — Early Neonatal | 84 | — | — | Yes — High/D |
| Moral weight — Late Neonatal | 84 | — | — | Yes — High/D |
| Moral weight — Post Neonatal | 101 | — | — | Yes — High/D |
| Moral weight — 1 to 4 | 127 | — | — | Yes — High/D |
| Moral weight — 5 to 9 | 134 | — | — | Yes — High/D |
| Moral weight — 10 to 14 | 133 | — | — | Yes — High/D |
| Moral weight — 15 to 19 | 126 | — | — | Yes — High/D |
| Moral weight — 20 to 24 | 118 | — | — | Yes — High/D |
| Moral weight — 25 to 29 | 113 | — | — | Yes — High/D |
| Moral weight — 30 to 34 | 106 | — | — | Yes — High/D |
| Moral weight — 35 to 39 | 100 | — | — | Yes — High/D |
| Moral weight — 40 to 44 | 86 | — | — | Yes — High/D |
| Moral weight — 45 to 49 | 76 | — | — | Yes — High/D |
| Moral weight — 50 to 54 | 65 | — | — | Yes — High/D |
| Moral weight — 55 to 59 | 55 | — | — | Yes — High/D |
| Moral weight — 60 to 64 | 40 | — | — | Yes — High/D |
| Moral weight — 65 to 69 | 31 | — | — | Yes — High/D |
| Moral weight — 70 to 74 | 21 | — | — | Yes — High/D |
| Moral weight — 75 to 79 | 16 | — | — | Yes — High/D |
| Moral weight — 80 to 84 | 12 | — | — | Yes — High/D |
| Moral weight — 85 plus | 12 | — | — | Yes — High/D |

**Discount rate filing exception**: If a model has a multi-year benefit stream and applies NO discount rate at all (absent, not present at 0%), file as **Low/H** — do not file Medium. GiveWell intentionally omits discounting in some newer-intervention CEA types. Escalate to Medium only if the researcher confirms discount rates should apply and they are absent. The Medium flag severity in the table above applies only when a discount rate IS present but deviates from the expected value.

---

## Cross-Program CE Benchmarks (sideways check reference)

Reference ranges from GiveWell's live top-charity CEAs. Used by `heads-up-evidence` for sideways CE sanity checks. **Skill maintainer: update this table when GiveWell publishes revised top-charity estimates.**

Last updated: 2026-06-21

| Program type | Typical CE range (× GiveDirectly benchmark) | Notes |
|---|---|---|
| SMC (malaria chemoprevention) | 8–20× | West Africa context; varies by country and season |
| AMF (insecticide-treated nets) | 7–20× | Most malaria-endemic countries |
| New Incentives (vaccine incentives) | 10–25× | Nigeria; conditional on program scale |
| Malaria Consortium SMC | 8–17× | West Africa core countries |
| Vitamin A supplementation (HKI) | 5–15× | Sub-Saharan Africa |
| Deworming (Evidence Action) | 3–8× | Wide range; highly model-dependent |
| GiveDirectly (cash transfers) | 1× (benchmark) | By definition |
| Sightsavers / IDinsight trachoma | 10–30× | High uncertainty; limited evidence base |

These ranges are approximate and shift with each GiveWell CEA update cycle. A model whose CE falls far outside the typical range for its intervention type (e.g., 2× for SMC, or 50× for deworming) warrants scrutiny regardless of whether individual cells look correct.
