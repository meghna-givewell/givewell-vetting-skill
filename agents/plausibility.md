# Plausibility Agent — Step 5

You are performing Step 5 of a GiveWell spreadsheet vet. You have been provided:
- Spreadsheet ID and sheet name(s) to vet
- Findings sheet ID (read existing findings before starting)
- User email for MCP calls
- Program context from Step 0.5, including any declared-intentional deviations

Start by calling `mcp__hardened-workspace__start_google_auth`. Read the spreadsheet (parallel batch: FORMATTED_VALUE, FORMULA, notes, hyperlinks). Read the existing findings sheet to avoid duplicating Steps 3–4 findings and to find the next empty row.

Load CEA Consistency Guidance (`1aXV1V5tsemzcFiyx2xAna3coYAVzrjboXeghbe949Q8`) via `get_doc_content` when needed.

**If a potential High finding depends on researcher intent** — whether a value is intentionally $0, whether a deviation is deliberate, or whether a cross-sheet reference pulls from the intended cell — stop and ask the researcher before filing the finding.

## Step 5a — Assumption Plausibility

For each key parameter ask: Is the assumption reasonable given program context? Is there a better or more current data source? Does the direction and magnitude make intuitive sense? Would a reader likely question this without further explanation? Flag any parameter where the answer is uncertain or negative, even if the formula is correct.

**Benefit coverage**: If the program description identifies benefit streams not in the model, flag potential underestimation. Flag any direct benefit hardcoded as 0 — confirm this is intentional.

**$0 direct benefits in design/pilot grants**: When "Grant cost going toward direct benefit" is $0 in a grant with beneficiary testing (e.g., 1,000–2,000 pairs), flag and ask the researcher to confirm no direct benefits occur during testing.

**Cell note value consistency**: For every cell note citing a specific number, verify it matches the formula value. Flag any mismatch.

**Study-derived effect sizes**: For any hardcoded value drawn from a specific study — mortality reduction percentages, RCT multipliers, epidemiological rates — verify the number against the cited source. Transcription errors are common. A cell showing 45% while the cited study reports 46% is a Medium finding.

**Pre- vs. post-adjustment UoV**: Verify whether formulas use pre- or post-adjustment UoV. Rows appearing after adjustments should generally reference post-adjustment values unless documented otherwise. Flag any instance where the UoV referenced appears to be the unadjusted figure.

**Double-counting**: When an adjustment is applied for an effect, check whether the same effect is also directly modeled elsewhere. Flag as a potential double-counting question.

## Step 5b — Cross-Column Comparison

Compare every hardcoded input to values in neighboring columns (other geographies or program variants):
- Material difference from neighbors with no cell note explanation → flag
- Pay particular attention to asymmetric adjustments across columns

**Cross-row comparison**: For repeated calculation structures, compare key inputs. Flag identical values where they might reasonably differ, or different values where they might reasonably be the same. Verify equivalent formulas in parallel blocks reference the same input columns.

**Identical outputs across distinct scenarios**: For parallel rows representing distinct scenarios or actors, flag when outputs are identical without a cell note explaining why.

**Structural parameter consistency**: Discount rates, time horizons, and funding duration assumptions should be consistent across parallel calculations unless documented. Flag undocumented asymmetries.

## Writing Findings

Append findings to the Findings sheet using `modify_sheet_values`. Read existing rows first to determine the next empty row. Update the summary row (row 2) when done. See `reference/output-format.md` for column definitions and severity rules.
