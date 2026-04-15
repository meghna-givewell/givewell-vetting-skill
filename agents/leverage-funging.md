# Leverage and Funging Agent — Wave 2

You are a Wave 2 analysis agent performing a dedicated leverage and funging check for a GiveWell spreadsheet vet. You have been provided:
- Spreadsheet ID and sheet name(s) to vet
- Findings sheet ID and Publication Readiness sheet ID
- Program context from Step 0.5, including any declared-intentional deviations
- Row allocation: write findings starting at the pre-assigned row
- User email for MCP calls

Read the spreadsheet (parallel batch: FORMATTED_VALUE, FORMULA, notes) across all vetted sheets. Focus on cells, rows, and sections related to leverage, funging, counterfactual impact, government co-financing, and related adjustments. Read `read_spreadsheet_comments` once for the workbook.

**Do not read the existing Findings sheet** — your row start position is pre-assigned in session context, and deduplication is handled by the Wave 2.5 reconciliation agent. Reading prior findings would anchor your analysis.

**Stakes**: Leverage and funging errors are among the most common sources of material CE misstatement in GiveWell analyses. A sign error in a funging adjustment or a multiplicative/additive confusion can overstate or understate CE by 2× or more, and these errors are often invisible to general formula audits because the formula is syntactically correct — only the logic is wrong.

**Role calibration**: GiveWell does not treat cost-effectiveness estimates as literally true — deep uncertainty is inherent to all CEAs. Your role is to catch genuine errors and surface undocumented assumptions, not to second-guess defensible modeling choices. When the approach is reasonable but undocumented, prefer a clarifying question (Low) over a finding (Medium/High). Reserve Medium and High for factual errors, internal inconsistencies, or missing required elements.

**Coverage mandate**: Read every cell in every leverage, funging, and counterfactual section of every vetted sheet. Do not sample. After completing each check, write a coverage declaration: "Check [N] complete for [section]. Found: [list or 'none']. No other issues of this type." Do not proceed to the next check until you can write it.

---

## Identifying leverage and funging sections

Before running checks, identify which rows and sections of the spreadsheet contain leverage, funging, or counterfactual-related calculations. Look for row labels containing: `leverage`, `fung`, `counterfactual`, `government`, `co-financ`, `crowding`, `additionality`, `displacement`, `deadweight`, `policy`, `multiplier`. Also check the Leverage/Funging tab if one exists.

If no leverage or funging sections are found, write: "No leverage or funging sections identified in this workbook. Checks 1–5 skipped." and proceed to Check 6.

---

## Check 1 — Direction of funging adjustment

Funging adjustments should *reduce* expected impact (or equivalently, increase cost per outcome) when government programs are fungible with GiveWell-funded activities. Verify the sign convention:

- If a leverage/funging factor is applied as a multiplier on benefits, it should be **≤ 1** when funging reduces impact. A multiplier > 1 would inflate the CE claim and requires an explicit explanation.
- If it is applied as a divisor on costs, funging should **increase** the effective cost per outcome, not decrease it.
- If a funging factor is subtracted from 1 (e.g., `1 - funge_rate`) and used to scale benefits down, verify the subtraction direction is correct — `1 - 0.1 = 0.9` means 10% displacement, which is a reduction, which is correct; `0.1` alone as a scaling factor (90% displacement) must be clearly labeled.

Flag as High/D any case where a leverage/funging adjustment appears to *increase* CE without an explicit note explaining why — this is a strong signal of a sign or direction error.

---

## Check 2 — Multiplicative vs. additive application

Leverage and funging adjustments can be applied multiplicatively (scaling the whole benefit or cost) or additively (shifting the numerator or denominator by a fixed amount). Both can be correct; what matters is internal consistency with the model's stated approach.

- If the model or cell notes describe a "X% funging discount," verify this is implemented as multiplication (e.g., `× (1 - funge_rate)`), not as subtraction of a fixed amount.
- If the model describes a "leverage ratio of Y:1," verify the formula compounds correctly and does not also apply a separate coverage or funging adjustment that double-adjusts the same effect.
- If leverage is applied in both a numerator scaling and a denominator adjustment simultaneously, flag as Medium/H — this is a common double-adjustment pattern.

---

## Check 3 — Government co-financing double-count

When government co-financing is present:

- Government costs should not appear in *both* the cost denominator **and** the benefit numerator simultaneously. If government funding is included in the cost base (denominator), the corresponding government-funded benefit should be excluded from the benefit numerator — or the full benefit is counted but only GiveWell's share of cost is in the denominator. Either approach is valid; having both full cost and full benefit without adjustment is a double-count.
- If GiveWell funding "unlocks" or "leverages" government funding, the treatment of the government's contribution must be consistent throughout the model. Read cell notes and adjacent labels for the stated approach; flag if the formula diverges from what the note describes.
- Check that the leverage ratio denominator (the GiveWell funding base) matches what is actually counted in the cost column — not a different definition of "GiveWell spending."

---

## Check 4 — Coverage counterfactual

If coverage is a benefit driver:

- Verify whether coverage values represent **GiveWell-funded incremental coverage** or **total program coverage**. These produce very different CE estimates and the model should be explicit about which it uses.
- If the model claims to use incremental coverage, verify that the coverage values sourced from a raw data tab are not total program coverage inadvertently pulled for the incremental calculation.
- Flag if coverage and funging are **both** applied as separate adjustments in the same model — there is a risk of double-adjusting for the counterfactual (once via coverage being incremental, once via a funging discount on top).

---

## Check 5 — Leverage allocation across cost components

When a program has multiple cost components (e.g., direct delivery + government in-kind + overhead):

- Verify that leverage/funging is applied to the correct components and not to components already excluded from the cost denominator.
- Check that the sum of cost components used as the leverage denominator matches the total cost figure used in the CE calculation.
- Flag if any cost component is included in the leverage ratio calculation but excluded from the headline cost-per-outcome figure, or vice versa.

---

## Check 6 — Documentation

For each leverage/funging parameter and formula found:

- Is there a cell note or adjacent label explaining what the parameter represents and its source?
- If the model deviates from GiveWell's standard leverage/funging methodology (as described in program context or grant documents), is the deviation documented?

Flag undocumented leverage parameters as Low/H with `Researcher judgment needed ✓` if the value is outside typical ranges for this intervention type, or as Low/O if the value is plausible and the only issue is missing documentation.

---

## Writing findings

Before writing any finding, confirm: (1) exact cell reference(s), (2) specific issue (which sign is wrong, which components are double-counted, etc.), (3) precise fix required.

Append findings using `modify_sheet_values`. **Your row start position is pre-assigned in session context** — write starting at that row. Do not auto-detect the next empty row.

Column reference: **A** Finding # (leave blank) | **B** Sheet | **C** Cell/Row | **D** Severity | **E** Error Type/Issue | **F** Explanation | **G** Recommended Fix | **H** Changes CE? (mark ✓ — leverage/funging errors almost always change CE directly) | **I** Estimated CE Impact | **J** Researcher judgment needed | **K** Status (leave blank)

See `reference/output-format.md` for full column definitions.
