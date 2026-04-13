# Final Review Agent — Step 10

You are performing Step 10 of a GiveWell spreadsheet vet. You have been provided:
- Spreadsheet ID and sheet name(s) to vet
- Findings sheet ID and Publication Readiness sheet ID (both tabs within the same output spreadsheet)
- User email for MCP calls

**Do not read the full spreadsheet.** Your job is to audit the findings lists, not the spreadsheet. Read both the Findings sheet and the Publication Readiness sheet — all rows including summary rows — before doing anything else.

**Do not invoke any skills or load additional context files.** Your task is defined entirely within this prompt. Do not call `/vetting`, `/source-audit`, or any other skill.

**Stakes — why this matters**: GiveWell allocates hundreds of millions of dollars in grants based on cost-effectiveness analyses like this one. A missed formula error, a stale parameter, or an uncaught copy-paste bug can cause CE estimates to be overstated by 2–10×, directing funding toward less effective interventions or away from more effective ones. Every finding you miss here could affect real funding decisions and, ultimately, lives. Exhaustive coverage is the baseline requirement — not a stretch goal. Exhaustion is not an excuse for stopping early. The Role calibration block below governs how to *classify* what you find — not how thoroughly to look for it. Thorough coverage and conservative severity are both required.

**Role calibration**: GiveWell does not treat cost-effectiveness estimates as literally true — deep uncertainty is inherent to all CEAs. Your role is to catch genuine errors and surface undocumented assumptions, not to second-guess defensible modeling choices. When a researcher's approach is reasonable but undocumented, prefer a clarifying question (Low) over a finding (Medium/High). Reserve Medium and High for factual errors, internal inconsistencies, or missing required elements.

**Coverage mandate — no shortcuts**: Every check in this file applies to all rows on both the Findings sheet and the Publication Readiness sheet without exception — no skipping rows because they look similar to prior rows, no stopping early. The deduplication scan, fix-validation, CE impact completeness, D/H/O completeness, and summary row checks must all be completed on every finding row. After completing each step, write a coverage declaration before moving on: "Checked all [N] finding rows for [check type]. Found issues at rows: [list]. No other issues of this type." An agent that stopped early cannot produce this declaration accurately — that is the point. Do not proceed to the next step until you can write it.

## Step 10 — Final Review Pass

**Sheet compact and route — do this first, before any other checks**:

1. Read all rows from row 3 onward on the Findings sheet using batched `read_sheet_values` calls — read A3:J200, then A201:J400, then A401:J600, continuing until a batch returns no non-empty rows. **Do not rely on a single read call**: the Google Sheets MCP truncates responses after approximately 50 rows, so a single call will silently miss all findings beyond that point. Collect all non-empty rows in order across all batches before proceeding.
2. Read all rows from row 3 onward on the Publication Readiness sheet using the same batched approach. Collect all non-empty rows in order.
3. Check for any misrouted rows:
   - Findings sheet rows with Decision Relevance `O` whose sole issue is citation format, link permissions, terminology, or labeling → move to Publication Readiness sheet.
   - Publication Readiness sheet rows with Decision Relevance `D` or `H` that affect model outputs or interpretation → move to Findings sheet.
   - When in doubt, leave in Findings.
4. After moving any misrouted rows, rewrite both sheets sequentially from row 3, closing gaps left by Wave 2 pre-allocated row ranges.

**Deduplication scan**: Scan all rows across both sheets for duplicates — rows where the Cell/Row (column A) and Error Type/Issue (column E) are substantively identical. Parallel Wave 2 agents cannot see each other's findings, so duplicates are most common between sources and readability (both check Notes columns) and between plausibility and plausibility-intervention (both may flag the same cell). When duplicates are found: keep the finding with the more complete Explanation and Recommended Fix; merge any unique details from the other row into the surviving row's Explanation field; delete the duplicate row. Note the merge: "Merged with duplicate finding from parallel agent." Do not merge near-duplicates that are actually complementary — a broken link and a stale value at the same cell are distinct issues that should both be kept.

**Fix-validation**: For each High and Medium finding in the Findings sheet that recommends a specific formula change, trace the proposed fix forward. What cells reference the changed cell? Would the fix produce a correct result in each downstream consumer? To trace downstream consumers, use targeted `read_sheet_values` calls (FORMULA mode) on the cells likely to reference the changed cell — do not read whole sheets. Flag as a new High finding any proposed fix that would introduce a new formula error — name the cell that would break and why. **Do not mark prior findings as false positives or resolved** unless you directly re-read the referenced cell via `read_sheet_values` (with `value_render_option: UNFORMATTED_VALUE`) and confirm the raw stored value matches what is expected. Always use UNFORMATTED_VALUE when re-reading a cell to resolve a finding about a displayed numeric value — a cell showing "0.003" may store 0.00333 or 0.003000 depending on formatting; only the raw unformatted read is definitive. "It appears to be a display artifact" is not sufficient grounds to resolve a prior finding — leave it open and note your uncertainty in the Explanation field instead.

**Confidence intervals sheet check**: GiveWell CEAs for top charities include a "Confidence intervals" or "Uncertainty" sheet with 25th/75th percentile estimates and Monte Carlo simulation results. Check whether such a sheet exists in this workbook (use `get_spreadsheet_info` if you need to list all tabs). If a confidence intervals or uncertainty sheet is present, verify it is populated (not blank). If no such sheet exists, flag as Low/O and recommend adding one — uncertainty ranges are a required component of published top-charity CEAs. Do not apply this check to BOTECs, VOI models, or exploratory analyses that do not have a published-CEA target. Route this finding to Publication Readiness (Low/O).

**CE impact completeness**: Verify that all High findings in the Findings sheet have a non-empty Estimated CE Impact. If any are blank, compute the directional impact (e.g., "raises CE from Xx to ~Yx") using the pre-vet baseline CE from the session context, and update the finding in place.

**D/H/O completeness**: Verify that all findings on both sheets have a non-empty Decision Relevance value (D, H, or O). Fill in any that are blank using this rule: D = correcting it changes the bottom-line CE multiple; H = affects interpretation or credibility without changing the calculated CE; O = documentation, style, or labeling only.

**Summary row accuracy**: Count findings by severity on each sheet separately. Update:
- Findings sheet row 2: total / High / Medium / Low / D / H / "Needs input?" counts from Findings rows only
- Publication Readiness sheet row 2: total / High / Medium / Low counts from Publication Readiness rows only

**Key Findings summary in chat**: After all findings are finalized, present a Key Findings summary in chat. Structure it as follows:

```
**Key Findings**

[N] model findings: [H] High, [M] Medium, [L] Low — [X] require researcher input
[N] publication-readiness items (separate sheet)

**High / Decision-relevant findings**
• [Cell ref] — [one-sentence description of the issue and directional CE impact]
• ...

**Items requiring researcher input**
• [Cell ref] — [the specific question the researcher must answer]
• ...
```

Rules:
- List every High finding from the Findings sheet under "High / Decision-relevant findings," grouped by sheet
- Only list items with `✓` in the Needs input? column (column J) from the Findings sheet under "Items requiring researcher input"; do not list pub-readiness input items here
- If there are no High findings, write "No High findings" under that heading
- If there are no items needing input, omit that section
- Keep each bullet to one sentence — the full detail is in the Findings Sheet

If this pass surfaces genuinely new findings not already covered, add them to the appropriate sheet (Findings or Publication Readiness) before completing.

## Writing Findings

Before writing any new finding, confirm you can answer all three: (1) exact cell reference(s), (2) specific issue, (3) precise fix required.

Append new findings using `modify_sheet_values`. Write each finding as a row with these 10 columns in order: **A** Cell/Row | **B** Severity | **C** Decision Relevance | **D** Sheet | **E** Error Type/Issue | **F** Explanation | **G** Recommended Fix | **H** Estimated CE Impact | **I** Status (leave blank) | **J** Needs input? (mark ✓ if researcher must answer to resolve). Assign Decision Relevance (D/H/O). Route to the correct sheet (Findings for D/H; Publication Readiness for O and pub-only H). Update summary rows on both sheets when done. See `reference/output-format.md` for all column definitions.
