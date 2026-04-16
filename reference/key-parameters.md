# Key Parameters Quick Reference

Flag deviations from these values unless the sheet provides an explicit documented rationale.

| Parameter | Current Value | Notes |
|---|---|---|
| Benchmark (UoV per $) | **0.00333** | Updated Nov 2025; old value 0.003355 — flag if stale |
| Discount rate | **4%** | Components: 1.7% + 0.9% + 1.4%; pure time preference = 0% |
| Avert under-5 death (malaria/vaccines) | **116 UoV** | |
| Avert over-5 death (malaria) | **73 UoV** | = 63% of under-5 value |
| Avert death, 6–59 month child (VAS) | **119 UoV** | |
| Avert maternal death (MNH/reproductive health) | **125 UoV** | From GW Facility-based MNH BOTEC; higher than over-5 value due to DALYs per maternal death calculation. Use this when a model cites GW MNH BOTEC as the source — do not infer from general age-specific tables |
| Long-term income ratio (SMC/VAS/New Incentives) | **0.3064** | |
| Income effects — % increase in ln(income) per malaria case averted (children under 15) | **0.58088%** | From GW ITN CEA; used in malaria programs (ITNs, case management, SMC). Pre-Nov 2025 models may use 0.65% — flag as Medium/H if value deviates >5% |
| p(update) cap (VOI/optionality) | **≤ 50%** | Above 50% implies program should be funded directly |
| VOI adjustment application | Apply wrong-risk + other-funders to VoI component; funging to total | Do not apply all adjustments to the aggregate CE |
| VOI adjustment scope (detail) | wrong-risk and influencing-other-funders apply to VOI component **only**; funging applies to the **total** CE | Do NOT dismiss as equivalent even when wrong-risk and other-funders numerically cancel — the funging adjustment must be correctly scoped away from direct benefits. Applying all three to total CE is a structural error. |
| VOI — probability trial fails | Default **10%** | Speculative; update upward for politically unstable contexts |
| VOI — probability we influence other funders | Default **20%** | Highly speculative; adjust based on total RFMF landscape and whether the study is answering a field-relevant question |
| VOI — probability we're wrong (t-stat rules of thumb) | t≥3: **−10%**; t≈2: **−20%**; t≈1.7: **−30%**; t≈1.2: **−50%** | Downward adjustment to VOI for risk of acting on a biased/noisy trial result; larger penalty for less precise trials |
| VOI — how long we fund after study | Default **10 years** | Highly speculative; update downward if program has a clearly finite implementation window |
| VOI — CE of reallocated funding | Default **1–2× above bar** | E.g., if bar is 10×, assume program is 11–12×; conservative assumption |
| Discount rate — income benefits | **4%** per year | Standard for income/consumption benefits over any time horizon |
| Discount rate — long-term health benefits | **0.5%** per year | Only for health benefits spanning several decades or more; do not discount near-term health benefits |
| Resource sharing multiplier — household income effect | **×5** (typical household size) | Use when relying on household income/consumption effects |
| Resource sharing multiplier — individual income effect | **~×2.5** (50% share × 5 HH members) | Use when relying on effects on individual income |
| Resource sharing multiplier — development effects (children) | **×2** (50% share × ~4 HH members over time) | For children who will eventually form own households |
| Treatment costs averted — top 4 child health charities | **+20%** supplemental adjustment | Applies to AMF, Malaria Consortium, HKI, New Incentives; accounts for medical costs averted by prevention |
| Discount rate — TA death-averting programs | **1.4%** per year | Temporal uncertainty component only; used for TA grants where the primary benefit is near-term mortality reduction; use **4%** for income/consumption streams in the same model |
| TA — p(failure to shift status quo) | Default **30%** | Probability TA engagement fails to change government behavior; distinct from VOI p(trial fails) = 10%; calibrate lower if government is already publicly committed or has co-funded the program |
| TA speed-up benchmarks (years to reach steady-state coverage) | RTS,S: **2**; DtW: **4**; IFA: **4**; Dual tests: **5**; HPV: **6**; ILC: **13** | Cross-program reference for the "speed-up of steady state due to TA" parameter; ILC is high due to dual steady-state structure |
