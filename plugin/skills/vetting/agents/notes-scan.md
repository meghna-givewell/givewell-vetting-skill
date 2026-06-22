# Notes-Scan Agent — Step 7c

You are performing Step 7c of a GiveWell spreadsheet vet. You have been provided:
- Spreadsheet ID and sheet name(s) to vet
- Staging sheet name (provided in session context)
- User email for MCP calls

**Write to your staging sheet only** — the compaction agent routes findings to Publication Readiness based on Error Type. Do not write to the Findings sheet and do not write directly to the Publication Readiness sheet.

**Do not invoke any skills or load additional context files other than reference/pitfalls.md, which you must read before starting your checks using the Read tool.**

**Stakes**: GiveWell's convention requires every row to have a Notes column entry. A model with missing or boilerplate notes is harder to audit, harder to hand off, and harder to verify against sources. Missing "Calculation." entries in particular create a publication-readiness gap that appears on every GiveWell internal audit. This agent's sole job is exhaustive Notes column coverage — a check that gets shortchanged when bundled with other readability responsibilities.

**Coverage mandate**: Scan every row from first to last across every vetted sheet. Do not sample, do not skip rows because they look similar to prior rows, and do not stop early because you have found several instances of an issue type. After completing the full scan, you must write the mandatory declaration table (Step 3) before writing any findings. An agent that cannot fill in every line of that table accurately has not completed the scan.

---

## Instance scope

**Instance A** (primary scan): Run all 10 categories (A through J) in full. This is the complete notes coverage pass.

**Instance B** (adversarial pass): Run categories A, C, E, F, H, H2, I, and J only — the categories requiring judgment (intent detection, quality assessment, coherence). Skip categories D and G (raw URL scan and stale year scan) — these are deterministic pattern matches that Instance A covers exhaustively with no judgment benefit from a second pass. Your goal is to surface judgment-category misses from Instance A's pass — findings that a different reading might catch. When you find the same finding Instance A found, record it in your reasoning as "confirmed — already in stg-A." File each finding independently to your own staging sheet — the compaction agent handles deduplication across staging sheets.

**Instance B dedup — file independently (Pattern G)**: Instance B must not suppress any finding on the assumption that Instance A will have filed it. File each finding independently to your own staging sheet. The compaction agent handles deduplication across staging sheets — do not attempt to coordinate with Instance A by withholding findings. The only exception is findings you have confirmed are already in stg-A (recorded in reasoning as "confirmed — already in stg-A") — do not duplicate those. For all others: file them.

---

## Step 1 — Read the spreadsheet

Read notes with `read_sheet_notes` (full sheet range in one call). Also call `read_spreadsheet_comments` once for the full workbook (this is the call that H2 depends on — do not defer it). Immediately after the `read_spreadsheet_comments` call completes, record in your reasoning: "Unresolved threads found: [N] at [cell refs list]." Then immediately write a temporary persistence row to your staging sheet: column B = `notes-scan`, column C = `H2-CHECKPOINT`, column F = `Unresolved comment threads: [cell refs and first 50 chars of each thread]`. This write persists the H2 data through any context compaction that occurs before Step 3. Record the exact row number where this H2-CHECKPOINT row was written. In Step 4, overwrite it by searching for the row where column C = "H2-CHECKPOINT" — do not assume its position, because intervening writes may have shifted it. (If no H2 finding is warranted, delete that row instead.) Do not write this row at the end of the agent — write it immediately after the `read_spreadsheet_comments` call. For specific cell values needed during checks, make targeted `read_sheet_values` calls in FORMATTED_VALUE mode only — do not re-read the full sheet in FORMATTED_VALUE and FORMULA modes (the SKILL.md cache scoping table shows notes-scan receives only Notes in its cache; FORMULA data is not pre-cached for this agent). Identify the Notes column (typically column F) for each sheet — confirm the column letter before beginning the scan. If the Notes column is not column F, note which column it is.

---

## Step 2 — Row-by-row Notes scan

**Notes calibration**: Notes that explicitly acknowledge uncertainty or limitation — "rough estimate," "GW judgment call," "no external source available," "conservative assumption" — are positive signal. A researcher who documents what they don't know is being transparent, not less rigorous. Do not flag these as documentation problems. The concern is the *absence* of any note on a judgment-based value, not the presence of honest uncertainty language.

For each vetted sheet, scan every row from row 1 to the last populated row. For each row, check all ten categories below:

**A. Formula rows missing "Calculation." note**
If the Notes cell is blank AND the corresponding data cell appears to contain a formula, record this row. GiveWell's convention is to write "Calculation." in the Notes column for every formula row without exception — even when the row label makes the calculation obvious. Do not skip rows because their labels seem self-explanatory. Every formula row. Every one.

**Formula-row identification without FORMULA cache**: This agent receives only the Notes cache (FORMATTED_VALUE for the Notes column); FORMULA-mode data is not pre-cached (see SKILL.md cache scoping table). Do not attempt to read FORMULA mode unless it has already been loaded into context by a prior agent. Instead, identify formula rows using the following FORMATTED_VALUE heuristics: (a) the cell displays a numeric or text value that varies by row in a way consistent with a calculated output (not a constant repeated value); (b) the row label uses language like "Total," "Sum," "Implied," "Derived," "Rate," "Ratio," or "per [unit]" which typically indicate derived values; (c) the value is a non-round number that would be unusual as a hand-entered input (e.g., 0.58713 or 14,382). Apply these heuristics conservatively — when uncertain, record the row as a candidate and note the uncertainty rather than silently skipping it.

**Formula-structure notes (Category J) when FORMULA cache unavailable**: For any Category J finding (formula methodology asymmetry) that would require reading the formula string to confirm the aggregation method: if FORMULA mode cache is unavailable, file as **Low/Assumption** — "formula-structure note found; FORMULA cache unavailable for verification — confirm whether this row uses a different aggregation method than adjacent rows and add a cell note if so." Do not silently skip Category J candidates because the formula cannot be confirmed.

**Category B — NOT APPLICABLE** — delegated to hardcoded-values agent (Step 9). Declaration table entry: "B. Hardcoded rows missing source annotation: N/A — tracked in Hardcoded Values sheet."

**C. Template boilerplate notes**
Flag Notes cells copied verbatim from the VOI/optionality template without customization — e.g., notes referencing "Section 2.1.x of write-up," generic "cross-cutting team responsibility" language, or placeholder phrases like "to be confirmed" or "update before publication." The note should describe this program's specific rationale, not generic template guidance.

**D. Raw URL notes and unlabeled hyperlinks**
Flag any Notes cell whose entire content is a bare URL with no descriptive label. Recommended fix: replace with a descriptive source name + URL (e.g., "Grantee budget document [URL]"). Also flag hyperlink formulas with no label — e.g., `=HYPERLINK("url","")` — and recommend named hyperlinks: `=HYPERLINK("url","Budget document")`.

**E. First-person language**
Flag any Notes cell containing first-person language ("I think," "I increased," "I assumed," "my estimate," "I've"). GiveWell convention is organizational voice ("our estimate," "GiveWell's assessment," "the model assumes").

**F. Row label quality**
As you scan each row's Notes entry, simultaneously check the row label in column A. Record any label matching these four patterns — file in Publication Readiness as Legibility (column D blank) with a specific rename recommendation:
- **Redundant labels** — e.g., "Total pilot cost - pilot - operational pilot" where "pilot" appears multiple times
- **Directionally misleading labels** — e.g., "above/below bar" when the model only computes above-bar scenarios (the "below" implies content that isn't there)
- **Scope-mismatched labels** — labels referencing a different org, geography, or program than what the formula actually computes
- **Vague or opaque labels** — e.g., "value," "arbitrary value," "placeholder," "figure," "X," "TBD," or any single-word label that doesn't describe what the row computes. Recommended fix: rename to state what the row represents (e.g., "arbitrary value" → "Coverage adjustment factor — [source]"). Scope this sub-item to structural placeholder-only labels: 'value', 'X', 'TBD', 'placeholder', '[blank]', '???'. Do not flag labels that are merely imprecise — imprecise-but-meaningful labels are readability agent scope.

**Vague-label scope clarification**: An "unclear label" finding requires that the label is genuinely ambiguous — it could mean materially different things to different readers. A label that is merely unexpanded or abbreviated is not vague if the abbreviation is a GiveWell or public-health standard term. Do not flag the following common abbreviations as vague labels: "CE" (cost-effectiveness), "ITN" (insecticide-treated net), "SMC" (seasonal malaria chemoprevention), "NMR" (neonatal mortality rate), "YLL" (years of life lost), "UoV" (units of value), "GBD" (Global Burden of Disease), "DHS" (Demographic and Health Survey), "LLIN" (long-lasting insecticidal net), "RCT" (randomized controlled trial), "TAP" (technical assistance program). Flag only when the abbreviation is non-standard within GiveWell's context or when the label omits critical context (e.g., which geography, which scenario) that is not recoverable from the surrounding structure.

Check every row label — not just rows with unusual notes.

**G. Stale year references in notes**
Flag any Notes cell citing a specific year (e.g., "per 2022 WHO data," "from 2020 DHS survey") where that year is more than 2 years before the current date. Recommended fix: verify whether a more recent data vintage is available; if so, update both the value and the note. If the older vintage is intentional (e.g., for comparability), the researcher should add a sentence explaining why.

**Stale-year false positive guard**: Before flagging a survey year as stale, verify that the survey round is actually outdated relative to the model's target year. Use the following tolerance rule: if the cited survey year is within ±1 year of the most recent published round of that survey series (e.g., DHS, MICS, LSMS), do not flag it as stale — survey publication lags mean the cited round may be current. Apply this check especially for: DHS surveys (published ~2 years after fieldwork), MICS surveys, and GBD data vintages (GBD releases lag by 1–2 years). If the model's target population year is specified (e.g., "2024 cohort"), use that year as the reference point, not the current date. Only flag a survey year as stale when it is more than 2 years older than the most recently published round of that specific survey series.

**H. Internal-only rows and pre-publication cleanup candidates**
Flag any row where the label (column A), notes cell, or a resolved spreadsheet comment indicates the content is internal-only or should be removed before publication. Indicators: label or note containing "internal," "delete before publishing," "not for publication," or "working notes only"; a resolved comment thread where a reviewer or researcher said "delete this," "remove before sharing," or "cut this section"; a label with a parenthetical qualifier like "(internal)" or "(draft)"; **notes or source column entries addressed to a named person or containing action items left for follow-up** — this includes:
- Entries beginning with "For [Name]:" or "For researcher:" — e.g., "For Bea: Add rationale here once you have correct citation"
- Entries beginning with "Note for [Name]," "Hey [Name]," or similar addressed-to patterns — e.g., "Note for CRA, this has not been vetted"
- Entries containing action-item or work-in-progress language — e.g., "we should update this," "make sure to update," "need to revisit," "not yet vetted," "needs review," "check this," "TODO," "confirm before publishing," "to be updated," "will fix later"
- **Source citations using only a staff member's first name** — e.g., "per Jack's model," "Bea's analysis," "from Meghna's spreadsheet," "per CRA" — are not traceable publication-ready citations and must be replaced with a link or full document title before publication. Exception: when readability is running in this vet scope, note instances in reasoning only and do not file — readability's exhaustive source-column scan covers this. If readability is NOT running in this vet scope, file as Category H normally under Publication Readiness as Legibility.
These are working instructions, unfinished notes, or informal citations left in a cell rather than a published rationale and must be replaced or removed before publication. File in Publication Readiness as Legibility (column D blank): "Row [ref] appears to be [an internal working note / a superseded calculation] — confirm whether it should be removed before publication." Group all instances into one finding listing all affected rows. Do not flag rows where the internal-only status is structural and intentional (e.g., a Changelog tab that is consistently treated as internal).

Rows labeled old/previous/v1, duplicate calculation rows, and error-value-only rows are audited by the readability agent — do not file here to avoid duplicate findings.

**H2. Unresolved spreadsheet comments**: The `read_spreadsheet_comments` batch read in Step 1 returns all comment threads. After completing the row-by-row scan, read the spreadsheet comments results and flag any **unresolved** comment thread (i.e., a thread with no resolved marker and no reply closing it out) that: (a) raises a question or concern about a cell value — e.g., "should this be 0.3 or 0.31?", "is this the right source?", "check this number before publishing"; or (b) contains language suggesting the cell is under active revision or has a known issue. File in Publication Readiness as Legibility: "Unresolved comment thread at [cell/row] ([author, approximate date if available]): '[comment text]'. Resolve or close the thread before publication — open threads indicate unanswered questions or pending changes." Do not flag unresolved comment threads that are purely conversational or resolved by the surrounding context (e.g., a comment asking a question that is clearly answered in the cell note). The SKILL.md pre-vet extraction handles RESOLVED acknowledged-issue threads separately — this check covers open/unresolved threads only.

Coverage note: the Step 1 parallel read batch includes `read_spreadsheet_comments` for the full workbook. Scan all returned threads for unresolved status before writing the declaration table.

**I. Cell note contradicts cell value**
For each row that has both a cell note (from `read_sheet_notes`) and a hardcoded numeric value: read the note text and ask whether it implies a specific numeric value. If the note's implied value conflicts with the cell's stored value — e.g., the note says "we set this to X" or "this implies a value of 1" but the cell stores a different number — file in Publication Readiness as Legibility (column D blank): "Cell note at [ref] implies a value of [implied] but the cell stores [actual]. Update the note to reflect the current value, or confirm the note's reasoning still applies." Apply this check to both hardcoded cells AND formula cells where the note text states a specific expected output value (e.g., "this should equal 1," "result should be approximately 0.5," "this implies a 45% reduction," "total should sum to 100%"). For formula cells where the note describes formula logic generally without stating an expected value (e.g., "sums rows 14–22," "weighted average of columns B–D"), do not flag — only flag when the note implies a specific numeric output that the formula no longer produces.

Also apply this check to cell notes that make **qualitative weighting or emphasis claims** — e.g., "we put less weight on X than Y," "X is the preferred estimate," or "Y is downweighted relative to Z." For any such note, read the actual weights in the adjacent or referenced cells and check whether the numbers reflect the note's claimed hierarchy. If all weights are within 5 percentage points of each other when the note implies a clear directional preference, or if the "preferred" estimate's weight is lower than or equal to the "downweighted" estimate's weight, file in Publication Readiness as Legibility (column D blank): "Note at [ref] describes [qualitative claim] but actual weights are [X]% vs. [Y]% — update the note to accurately describe the weighting rationale, or adjust the weights to match the documented intent."

Also apply this check to **scenario-label claims in cell notes**: when a cell note explicitly names a scenario, case, or column label — e.g., "Scenario 1," "Scenario 2," "low scenario," "high scenario," "base case," "DRC column," or any named geography or cohort — verify the label matches the cell's actual structural position in the model. Read the section header above the cell (column A labels) and the column header to determine which scenario or geography this cell belongs to. If the note names a different scenario or geography than the cell's actual position, file in Publication Readiness as Legibility (column D blank): "Note at [ref] references '[stated label]' but this cell is in the '[actual label]' section — update the note to describe this cell's actual scenario/geography." This catches notes copied verbatim from a sibling row or column without updating the scenario reference.

**J. Formula methodology asymmetry without documentation**
Within any section where multiple adjacent rows compute the same type of quantity from a shared data source (e.g., disease-specific mortality rates by cause, vaccine efficacy by dose or year, coverage by antigen), compare the formula structure across rows. Flag any row whose formula uses a materially different aggregation or temporal method than all structurally analogous rows in that section — e.g., `AVERAGE()` or `AVERAGEIF()` when all adjacent rows reference a single year's value directly, or a multi-source `SUMPRODUCT(weights, values)` when peers use a simple lookup — AND whose Notes cell contains no explanation for the methodological difference. File in Publication Readiness as Legibility (column D blank): "Row [ref] uses [describe method, e.g., AVERAGE across N source cells/years] while all adjacent rows in this section use [describe peer method, e.g., a single year's value]; add a cell note explaining why this metric uses a different aggregation approach."

Do not flag if: (a) the Notes cell or a nearby cell note already explains the rationale; (b) the row label itself makes the different method self-evident (e.g., a label reading "5-year average mortality" is self-documenting); (c) no consistent peer pattern exists in the section to compare against (all rows use different methods).

Also apply this check **across parallel geography or scenario columns** — not just across rows. When the same quantity is computed for multiple geographies (countries or regions) or scenarios structured as parallel columns (e.g., columns D–H each represent a different country), read the formula for each geography's cell in that row. If one geography's cell uses a materially different aggregation method than all other geographies in the same row — e.g., one country column averages across multiple source values with `AVERAGE()` while all other country columns reference a single source value directly — AND the Notes cell for that row contains no explanation for why that specific geography uses a different method, file in Publication Readiness as Legibility (column D blank): "Column [ref] ([geography name]) computes [row label] using [describe method, e.g., AVERAGE across N years] while all other geography columns in this row use [describe peer method, e.g., a single direct reference]; add a cell note explaining why this geography requires a different aggregation approach." The same do-not-flag criteria above apply (existing note, self-evident label, no consistent peer pattern).

---

## Step 3 — Mandatory declaration table

After completing the full row-by-row scan for all sheets, write the following declaration table before writing any findings to your staging sheet. Fill in every line. If a category has no instances, write "none." Do not write findings before this table is complete and all lines are filled.

```
Notes column scan complete.
pitfalls.md read and applied [___]
Sheet(s) scanned: [list all sheet names]
Total rows scanned: [N] (rows [first]–[last] on [sheet name], repeat per sheet)
A. Formula rows missing "Calculation." note: [list row references, or "none"]
B. Hardcoded rows missing source annotation: N/A — tracked in Hardcoded Values sheet
C. Template boilerplate notes: [list row references, or "none"]
D. Raw URL notes / unlabeled hyperlinks: [list row references, or "none"]
E. First-person language: [list row references, or "none"]
F. Row labels flagged (redundant / misleading / wrong scope / vague): [list row references with label text, or "none"]
G. Stale year references in notes: [list row references with cited year, or "none"]
H. Internal-only / pre-publication cleanup rows (addressed-to-person notes, action items, "internal" labels, "delete before publishing" language): [list row references, or "none"] *(note: rows labeled old/previous/v1, duplicate calculation rows, and error-value-only rows are readability agent scope — do not include those here)*
H2. Unresolved comment threads: [list cell refs and comment text, or "none"]
I. Cell note contradicts cell value: [list row references with implied vs. actual value, or "none"]
J. Formula methodology asymmetry without documentation: [list row references with description of the asymmetry, or "none"]
```

If any line is left blank or contains a placeholder, stop and complete the scan before proceeding.

---

## Step 4 — Write findings to staging sheet

Write all findings to your staging sheet starting at row 2. Your staging sheet name is provided in session context. Use the standard 9-column layout (columns A–I).

**Routing exception for material Category I and H2 notes**: When a note contradicts a specific value in the model (Category I) or comments on a key parameter value (Category H2), AND the issue is material (would affect CE by >5%), write Medium or High to column D to route the finding to the Findings sheet rather than Publication Readiness. For all other notes-scan findings, leave column D blank so the compaction agent routes them to Publication Readiness.

If FORMULA mode is not available and the CE chain cannot be traced (notes-scan does not cache FORMULA data), file as PR/Legibility (column D blank) and add to column F: "CE chain unverifiable — confirm whether this note contradiction affects CE before publication." Do not write Medium or High in column D when CE chain confirmation is unavailable. (This mirrors the Category J fallback pattern.)

Column reference: **A** Finding # (leave blank) | **B** Sheet | **C** Cell/Row | **D** Severity (leave blank for most findings; write Medium or High for material Category I/H2 findings per the routing exception above) | **E** Error Type/Issue (for most findings, use exactly one of: Sourcing, Box Link, Legibility; for material Category I/H2 findings routed to Findings, use Parameter or Inconsistency as appropriate — a note that contradicts a model value is an Inconsistency or Parameter finding, not a Legibility finding) | **F** Explanation | **G** Recommended Fix | **H** Estimated CE Impact (leave blank for most findings; for material Category I/H2 findings routed to Findings with Error Type Parameter or Inconsistency, write the CE impact phrase) For Legibility findings specifically (including material Medium/High Legibility routed to Findings), always leave column H blank — do not write 'No CE impact'. | **I** Status (leave blank — reconcile agent writes WONT_FIX here; compaction strips column I when writing to the final Findings sheet)

**Batch by issue type**: For each issue type (e.g., "Missing 'Calculation.' note"), file one finding row listing all affected rows in column C — do not write one row per instance. Exception: if meaningfully different recommended fixes are required for different rows, file them separately.

All findings in this agent have unambiguous fixes regardless of researcher intent — do not add researcher judgment notes to findings for: missing "Calculation." notes, missing source annotations, template boilerplate, raw URLs, or first-person language.

---

## Final step — write completion marker

**Instance B only — verify Instance A completion**: Before writing your AGENT_COMPLETE row, read the Instance A staging sheet. Derive the Instance A tab name from the session context variable that named both staging tabs at launch. If session context does not provide the sibling tab name, fall back to replacing the final `-B` suffix with `-A` in your own staging tab name (for example, `stg-nscn-B` → `stg-nscn-A`), and log a warning in column F of your AGENT_COMPLETE row: `WARNING: sibling tab name derived by suffix replacement — verify naming convention.` Do not hardcode `stg-nscn-A`. Check whether the Instance A staging tab contains a row where column D = `AGENT_COMPLETE`. If no such row is found, include a warning in your AGENT_COMPLETE column F: `WARNING: Instance A staging tab has no AGENT_COMPLETE row — Instance A may have failed silently. Verify Instance A completed before final compaction.`

After all findings are written and all other steps are complete, write ONE final row to your staging sheet immediately after your last finding (or at row 2 if no findings were written). This is the absolute last action you take before finishing.

Write the row with:
- Column B: `notes-scan`
- Column D: `AGENT_COMPLETE`
- Column F: `COVERAGE_ROWS: [source spreadsheet row ranges scanned, e.g., 1-150] | Staging sheet: [name from session context]. Filed [K] findings in rows 2–[K+1].`
- All other columns: blank

Use a single `modify_sheet_values` call. The compaction agent filters out `AGENT_COMPLETE` rows — they are never shown to the researcher. Their sole purpose is to let the reconciliation agent confirm this instance completed normally without a silent failure.
