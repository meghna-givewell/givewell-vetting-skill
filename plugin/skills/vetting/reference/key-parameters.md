# Key Parameters Quick Reference

Flag deviations from these values unless the sheet provides an explicit documented rationale.

| Parameter | Current Value | Notes |
|---|---|---|
| Benchmark (UoV per $) | **0.00333** | Updated Nov 2025; old value 0.003355 — flag if stale |
| Neonatal moral weight (under 1 month) | **84** | Source: GW Moral Weights by age band table below. Values significantly below 84 (e.g., 70) are not valid age-weighted variants — flag as Parameter unless the researcher provides an explicit documented rationale. |
| Discount rate | **4%** | Components: 1.7% + 0.9% + 1.4%; pure time preference = 0%. **Filing calibration**: if a model has a multi-year benefit stream (>3 years) and applies no discount rate, file as **Low/H with Researcher judgment needed ✓** — do not file as Medium or High. GiveWell intentionally omits time discounting in some newer-intervention CEA types. Escalate to Medium only if the researcher confirms discount rates should apply and they are absent. |
| Avert under-5 death (malaria/vaccines) | **116 UoV** | |
| Avert over-5 death (malaria) | **73 UoV** | = 63% of under-5 value |
| Avert death, 6–59 month child (VAS) | **119 UoV** | |
| Avert maternal death (MNH/reproductive health) | **125 UoV** | From GW Facility-based MNH BOTEC; higher than over-5 value due to DALYs per maternal death calculation. Use this when a model cites GW MNH BOTEC as the source — do not infer from general age-specific tables |
| Long-term income ratio (SMC/VAS/New Incentives) | **0.3064** | |
| Income effects — % increase in ln(income) per malaria case averted (children under 15) | **0.58088%** | From GW ITN CEA; used in malaria programs (ITNs, case management, SMC). Pre-Nov 2025 models may use 0.65% — flag as High/D if value deviates from 0.58088% |
| p(update) cap (VOI/optionality) | **≤ 50%** | Above 50% implies program should be funded directly |
| VOI adjustment application | Apply wrong-risk + other-funders to VoI component; funging to total | Do not apply all adjustments to the aggregate CE |
| VOI adjustment scope (detail) | wrong-risk and influencing-other-funders apply to VOI component **only**; funging applies to the **total** CE | Do NOT dismiss as equivalent even when wrong-risk and other-funders numerically cancel — the funging adjustment must be correctly scoped away from direct benefits. Applying all three to total CE is a structural error. |
| VOI — probability trial fails | Default **10%** | Speculative; update upward for politically unstable contexts |
| VOI — probability we influence other funders | Default **20%** | Highly speculative; adjust based on total RFMF landscape and whether the study is answering a field-relevant question |
| VOI — probability we're wrong (t-stat rules of thumb) | t≥3: **−10%**; t≈2: **−20%**; t≈1.7: **−30%**; t≈1.2: **−50%** | Downward adjustment to VOI for risk of acting on a biased/noisy trial result; larger penalty for less precise trials |
| VOI — how long we fund after study | Default **10 years** | Highly speculative; update downward if program has a clearly finite implementation window |
| VOI — CE of reallocated funding | Default **1–2× above bar** | E.g., if bar is 6×, assume program is 7–8×; conservative assumption |
| Discount rate — income benefits | **4%** per year | Standard for income/consumption benefits over any time horizon |
| Discount rate — long-term health benefits | **0.5%** per year | Only for health benefits spanning several decades or more; do not discount near-term health benefits |
| Resource sharing multiplier — household income effect | **×5** (typical household size) | Use when relying on household income/consumption effects |
| Resource sharing multiplier — individual income effect | **~×2.5** (50% share × 5 HH members) | Use when relying on effects on individual income |
| Resource sharing multiplier — development effects (children) | **×2** (50% share × ~4 HH members over time) | For children who will eventually form own households |
| Treatment costs averted — top 4 child health charities | **+20%** supplemental adjustment | Applies to AMF, Malaria Consortium, HKI, New Incentives; accounts for medical costs averted by prevention |
| Discount rate — TA death-averting programs | **1.4%** per year | Temporal uncertainty component only; used for TA grants where the primary benefit is near-term mortality reduction; use **4%** for income/consumption streams in the same model |
| TA — p(failure to shift status quo) | Default **30%** | Probability TA engagement fails to change government behavior; distinct from VOI p(trial fails) = 10%; calibrate lower if government is already publicly committed or has co-funded the program. **Quality-improvement TA scope**: The 30% default is calibrated for scale-up TA (shifting a government to adopt a new program or scale coverage). For grants that improve the quality of an existing program already in operation (e.g., fortification standards enforcement, improving quality of ongoing iron fortification delivery), the standard p(failure) framing may not apply. Flag absence as **Low/H with Researcher judgment needed ✓** only, not Medium — do not auto-file as Medium for quality-improvement TA structures without first confirming with the researcher that scale-up p(failure) logic applies. |
| TA speed-up benchmarks (years to reach steady-state coverage) | RTS,S: **2**; DtW: **4**; IFA: **4**; Dual tests: **5**; HPV: **6**; ILC: **13** | Cross-program reference for the "speed-up of steady state due to TA" parameter; ILC is high due to dual steady-state structure |

## Moral Weights by Age Band (UoV per death averted)

Source: https://www.givewell.org/how-we-work/our-criteria/cost-effectiveness/moral-weights  
These are the authoritative per-death moral weights by age group in units of doubling consumption (UoV). Any deviation from these values in a model is **High/D**. When a model uses a composite moral weight (e.g., "116 UoV for under-5 malaria deaths"), it should be derivable as a weighted average of the relevant age-band values below — check both the composite value and the age-band inputs when they are visible.

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

## Acceptable Ranges for Algorithmic Comparison

Any deviation from the Exact Value column triggers a High/D finding — there is no tolerance band. The Min/Max columns are reference context (e.g., to understand plausible rounding or rounding-adjusted values) but do NOT define a tolerance zone. A value within the range that is not the Exact Value is still High/D.

| Parameter | Exact Value | Min | Max | Flag severity |
|---|---|---|---|---|
| Benchmark (UoV per $) | 0.00333 | 0.003 | 0.0034 | Yes — High |
| Avert under-5 death (malaria/vaccines) | 116 | 110 | 122 | Yes — High |
| Avert over-5 death (malaria) | 73 | 69 | 77 | Yes — High |
| Avert death 6–59m VAS | 119 | 113 | 125 | Yes — High |
| Avert maternal death | 125 | 119 | 131 | Yes — High |
| Discount rate | 4% | 3% | 5% | Yes — High |
| Income effects malaria | 0.58088% | 0.55% | 0.65% | Yes — High |
| Long-term income ratio | 0.3064 | 0.25 | 0.35 | Yes — High |
| Years to benefits | 10 | 8 | 15 | Yes — High |
| Moral weight — Stillbirth | 33 | — | — | Yes — High |
| Moral weight — Early Neonatal | 84 | — | — | Yes — High |
| Moral weight — Late Neonatal | 84 | — | — | Yes — High |
| Moral weight — Post Neonatal | 101 | — | — | Yes — High |
| Moral weight — 1 to 4 | 127 | — | — | Yes — High |
| Moral weight — 5 to 9 | 134 | — | — | Yes — High |
| Moral weight — 10 to 14 | 133 | — | — | Yes — High |
| Moral weight — 15 to 19 | 126 | — | — | Yes — High |
| Moral weight — 20 to 24 | 118 | — | — | Yes — High |
| Moral weight — 25 to 29 | 113 | — | — | Yes — High |
| Moral weight — 30 to 34 | 106 | — | — | Yes — High |
| Moral weight — 35 to 39 | 100 | — | — | Yes — High |
| Moral weight — 40 to 44 | 86 | — | — | Yes — High |
| Moral weight — 45 to 49 | 76 | — | — | Yes — High |
| Moral weight — 50 to 54 | 65 | — | — | Yes — High |
| Moral weight — 55 to 59 | 55 | — | — | Yes — High |
| Moral weight — 60 to 64 | 40 | — | — | Yes — High |
| Moral weight — 65 to 69 | 31 | — | — | Yes — High |
| Moral weight — 70 to 74 | 21 | — | — | Yes — High |
| Moral weight — 75 to 79 | 16 | — | — | Yes — High |
| Moral weight — 80 to 84 | 12 | — | — | Yes — High |
| Moral weight — 85 plus | 12 | — | — | Yes — High |
