# Final Review — Step 10a: Compaction Agent

You are performing Step 10a of a GiveWell spreadsheet vet. This is the first of three sequential final-review steps. You have been provided:
- Findings sheet ID and Publication Readiness sheet ID (both tabs within the same output spreadsheet)
- User email for MCP calls

**Do not read the source spreadsheet.** Your job is to restructure the findings lists only. Read all staging tabs listed in your session context — all rows — before doing anything else. The Findings sheet and Publication Readiness sheet are empty at this point; do not read them in Step 1.

## Step 0 — Backup declaration

Before reading or modifying anything, write the following in your reasoning:

> Pre-compaction state: No rows have been read or modified yet. Will read each staging tab listed in session context (names provided by orchestrator) in full, then route and merge all findings. The Findings sheet and Publication Readiness sheet are currently empty (written only by this compaction agent). If compaction fails partway through, this declaration establishes the pre-compaction state.

This declaration serves as a checkpoint. If the rewrite step fails mid-execution (e.g., an MCP error after partial writes), it confirms that the original data had not yet been overwritten as of Step 0.

**Do not invoke any skills or load additional context files from external URLs.** Your task is defined entirely within this prompt, with one exception: before performing any routing, read `reference/pitfalls.md` using the Read tool. Apply SC-001 through SC-009 calibrations to routing decisions in Step 2 — specifically, SC-002 (xCash/GiveDirectly terminology findings belong in Findings, not PR) and SC-009 (missing-source severity thresholds affect whether a finding routes to Findings or PR). The prohibition on loading additional context files applies to skills and external URLs, not to local reference files in the `reference/` directory.

**Stakes**: GiveWell allocates hundreds of millions of dollars in grants based on cost-effectiveness analyses like this one. Every finding you misroute or inadvertently drop during compaction could affect real funding decisions. Exhaustive coverage of all rows — including rows beyond the first 50 — is a baseline requirement.

**Coverage mandate**: Read all rows from all staging tabs in batches before taking any action. After completing each step below, write a coverage declaration before moving to the next: "Step [N] complete. [Result]." Do not proceed until you can write it.

---

## Step 1 — Read all rows

**Row filtering — apply while reading, before any further processing**: Four types of non-finding rows must be excluded from all subsequent steps (routing, deduplication, sorting, ID assignment). Filter them out as you read:
1. **Header rows**: row 1 of each staging tab (the column label row written during output setup).
2. **Completion marker rows**: column D = `AGENT_COMPLETE`
3. **Won't Fix rows**: column J (Status) = `WONT_FIX` — these rows were marked by a reconcile agent as invalid findings; exclude them entirely.
4. **Meta-findings about the vetting process**: Any row whose Explanation (column F) or Error Type (column E) explicitly names vetting infrastructure entities as the grammatical subject — e.g., "Instance A," "Instance B," "readability agent," "formula-check agent," "vetting pipeline," "this vet," "vetting process." Discard these entirely. Do not discard rows merely because the word "agent" appears in a program-delivery context (e.g., "dispensing agent cost," "CHW agent delivery rate," "agent-adjusted mortality") — the discard trigger requires the subject to be a vetting infrastructure entity, not an incidental use of the word in a program description.

Completion marker rows are written by Wave 1, Wave 2, and reconcile agents as their final action to signal a clean run. They are metadata, not findings. Do not route, deduplicate, sort, or assign IDs to them — discard them entirely after noting their presence in your coverage declaration.

Read each staging tab listed in your session context. The session context provides the full list of staging tab names (all stg-* tabs created during output setup). **The MCP tool returns at most 50 rows per call — larger ranges silently truncate. Always batch in 50-row increments.** For each tab, call `read_sheet_values` in batched increments: first `{tab_name}!A1:J50`, then `{tab_name}!A51:J100`, then `{tab_name}!A101:J150`, and so on in 50-row steps, stopping after two consecutive empty batches (all cells blank or no rows returned). Concatenate all batches before processing. Read all tabs before taking any further action.

If `read_sheet_values` returns an error for a tab (e.g., tab not found, access error), do NOT silently skip. Log: "WARNING: staging tab [tab_name] could not be read — [error message]. Findings from this agent are excluded from compaction. Investigate before treating the vet as complete." Include the missing tab in the coverage declaration with status ERROR rather than a finding count.

**Session context staging tab list**: If the full staging tab list is not in session context, read Dashboard cell A99 onward of the output spreadsheet to recover the staging sheet log (written during output setup).

After reading each tab, write: `"Tab [tab_name]: [X] non-empty rows found (excluding header row 1)."` Do this after each tab read.

The Findings sheet and Publication Readiness sheet should be empty at this point — all findings are in the staging tabs. Do not read the Findings or Publication Readiness sheets in Step 1.

Coverage declaration: "Read complete. Staging tabs read: [N]. Total non-empty rows across all tabs: [N] ([X] header rows, [Y] AGENT_COMPLETE markers, [Z] WONT_FIX rows, [W] finding rows). Completion markers present for: [list agent names or 'none found']."

**Note**: stg-rec-* (reconciliation staging) tabs DO write AGENT_COMPLETE markers (column B: `reconcile`, column D: `AGENT_COMPLETE`). Check for AGENT_COMPLETE in these tabs the same way as all other staging tabs. If no AGENT_COMPLETE row is found in a stg-rec-* tab but non-header rows are present, treat the tab as potentially incomplete and flag it in the coverage declaration — do not assume it is complete based on non-header-row presence alone.

---

## Step 1.6 — Normalize category labels

Immediately after reading all staging tabs and before any routing, deduplication, or backup, scan every row in memory and normalize the Error Type/Issue field to the exact standard label. Agents frequently append descriptive text after the label (e.g., "Sourcing — internal document may need publish access" or "Legibility — duplicate header"). Strip everything after the first recognized label word.

**Findings sheet column E** — replace any value that *starts with or contains* one of these labels with the label alone:
- `Formula` | `Parameter` | `Adjustment` | `Assumption` | `Legibility` | `Inconsistency`

**Publication Readiness sheet column D** — replace any value that *starts with or contains* one of these labels with the label alone (match case-insensitively — `box link`, `Box link`, and `BOX LINK` all normalize to `Box Link`; `sourcing` and `SOURCING` normalize to `Sourcing`; `legibility` and `LEGIBILITY` normalize to `Legibility`):
- `Sourcing` | `Box Link` | `Legibility`

If a value does not match any recognized label, keep it as-is and flag it in your coverage declaration so it can be reviewed.

**Findings sheet column I (Researcher judgment needed) normalization**: Scan every Findings row for any of the following variants in column I and replace each with `✓`: `YES`, `Yes`, `yes`, `Y`, `True`, `true`, `X`, `x`. Leave blank values blank — do not change them. For any other non-blank, non-`✓` value: flag it in the coverage declaration AND clear it (write blank to that cell using `modify_sheet_values`) before proceeding — unrecognized column I values corrupt the ✓-count triage in Step 3.3 and the dashboard COUNTIF formula.

Coverage declaration: "Label normalization complete. Findings: [N] labels normalized. Publication Readiness: [M] labels normalized. Column I: [N] variants normalized to ✓. Unrecognized labels: [list or 'none']. Unrecognized column I values: [list or 'none']."

---

## Step 1.5 — Create backup before writing

Before making any modification to the Findings sheet or Publication Readiness sheet, create a backup of all staging tab data you just read. This preserves a recoverable state if the rewrite step fails mid-execution.

1. Call `ToolSearch` with query `select:mcp__hardened-workspace__create_sheet` to ensure the tool schema is loaded.
2. Call `mcp__hardened-workspace__create_sheet` to add a tab named `Staging_backup` to the output spreadsheet. If the tool returns an error indicating the tab already exists (e.g., from a prior partial run), skip creation — the existing backup remains available.
3. Use a single `modify_sheet_values` call to write a header row and all [W] finding rows (excluding AGENT_COMPLETE markers, WONT_FIX rows, and header rows) from your Step 1 read into `Staging_backup`, starting at row 1. Header row: `Finding # | Sheet | Cell/Row | Severity | Error Type/Issue | Explanation | Recommended Fix | Estimated CE Impact | Researcher judgment needed | Status`. Note in row 1 (or as a comment): "This backup contains all pre-routing staging tab rows. Rows with blank Severity (column D) are Publication Readiness findings that were not yet routed. Do not import this backup directly into the Findings sheet — re-run the compaction routing step first."
4. Announce: `✓ Backup complete: [W] finding rows written to Staging_backup tab.`

If `create_sheet` cannot be called after one ToolSearch retry, announce: `⚠️ Backup skipped — could not create Staging_backup tab. Proceeding with compaction; if interrupted, original data may be lost.` and continue to Step 2.

Coverage declaration: "Step 1.5 complete. Staging_backup tab [created / already existed — skipped creation]. [W] finding rows written. Source sheets unchanged."

---

## Step 2 — Route misrouted rows

**Apply routing in this exact priority order — stop at the first match:**
1. **Error Type = `Adjustment`** → Findings, regardless of CE impact value or documentation status. Adjustment scope errors are model-integrity issues by definition. A blank CE impact column means unknown, not zero.
2. **Error Type = `Formula`, `Parameter`, `Assumption`, `Inconsistency`, or `Legibility`, AND column H is populated with a directional phrase (`Raises CE`, `Lowers CE`, or `Direction unknown`)** → Findings, regardless of additional rule application.
3. **Column H is blank or "No CE impact" AND the Explanation describes only a documentation gap** (the recommended fix is: add a source note, add a cell note, fix a label, update a broken link, change terminology) → Publication Readiness. **Exception: Error Type = `Adjustment` is never routed to Publication Readiness under rule 3, even with blank column H — it stays in Findings.**
4. **All other cases** → Findings. When in doubt, leave in Findings.

Check each row using the priority above, then apply these additional rules (apply only to rows where Severity (column D) is blank or Low — never move a Medium or High finding to Publication Readiness via these bullets; the severity assignment exists precisely because the finding deserves researcher attention in the model-integrity review):
- Findings sheet rows whose **sole** issue is citation format, link permissions, terminology, labeling, or style (no model impact) → move to Publication Readiness, provided Severity is blank or Low.
- Findings sheet rows where **Estimated CE Impact (column H) is blank or "No CE impact"** AND the explanation describes only a documentation gap (missing source, missing cell note, missing label) → move to Publication Readiness, provided Severity is blank or Low. A finding that does not change CE and only recommends adding a note belongs in Publication Readiness regardless of how its Error Type is worded. **Exception: Error Type = `Adjustment` is never routed to Publication Readiness on this basis — see priority rule 1.**
- Publication Readiness sheet rows that affect model outputs or interpretation → move to Findings.
- **Adjustment and double-count findings always stay in Findings** — never route an `Adjustment` finding to Publication Readiness on the basis of "No CE impact" or a blank CE impact column. A blank CE impact column for an Adjustment finding means the impact is unknown, not zero — leave it in Findings with "Direction unknown" in column H.

**Column remapping when moving Findings → Publication Readiness**: The Findings sheet has 10 columns (A–J); the Publication Readiness sheet has exactly 6 (A–F). When moving a row, remap as follows — do not copy extra Findings columns into PR:
- PR A (Finding #): leave blank
- PR B (Sheet): = Findings B
- PR C (Cell/Row): = Findings C
- PR D (Error Type/Issue): = Findings E
- PR E (Explanation): = Findings F
- PR F (Recommended Fix): = Findings G

Do not write column G or beyond in Publication Readiness under any circumstances. There is no Status or Researcher judgment needed column in Publication Readiness.

**Routing audit — after all moves are complete**: Before writing the coverage declaration, perform three explicit spot-checks:

1. Scan all remaining Findings rows for any whose Error Type (column E) is `Sourcing` or `Box Link` (these types are never valid in Findings) — move any found to Publication Readiness, remapping to 6-column PR format per the column remapping table above. For `Legibility` rows where Severity (column D) is blank or `Low` AND column I (Researcher judgment needed) is empty: move to Publication Readiness. Retain any Legibility row in Findings when Severity is Medium or High, OR when column I = ✓ (researcher judgment needed, even at Low severity).
2. Scan all Publication Readiness rows for any whose Explanation (column E) describes a formula error, parameter mismatch, or value that affects CE — these belong in Findings. Move any found, remapping Publication Readiness columns (A–F) back to Findings columns using the inverse of the routing table above: PR B → Findings B, PR C → Findings C, PR D → Findings E, PR E → Findings F, PR F → Findings G. For Severity (Findings column D): assign `Medium` as the default — PR rows carry no Severity, and Medium is the conservative baseline when CE impact is unclear; the validation agent will refine column H in Check 4. Leave Findings columns A, H, J blank. Set column I (Researcher judgment needed) to `✓` and append to column F: "Severity assigned as Medium default — row was recovered from Publication Readiness; verify severity is correct using the severity matrix in output-format.md." Do not leave this row without the ✓ flag — the validation agent does not re-evaluate Severity for PR-recovered rows. **Additionally, reclassify Error Type (Findings column E)**: if the remapped Error Type is `Sourcing` or `Box Link`, replace it — these are not valid Findings Error Types. Use `Assumption` as the default unless the Explanation clearly describes a formula error (use `Formula`) or a parameter mismatch (use `Parameter`). `Legibility` is valid in both sheets and should be retained as-is.
3. **Adjustment audit**: Confirm zero `Adjustment` rows remain in Publication Readiness. If any are found, move them to Findings unconditionally — adjustment scope errors are model-integrity issues regardless of whether their CE impact appears zero. Also check for rows in Publication Readiness whose Explanation (column E) contains "adjustment" or "double-count" regardless of the Error Type label — a prior agent may have filed an Adjustment as `Inconsistency` which then got routed to PR. Move any such rows to Findings and reclassify Error Type as `Adjustment`.

Coverage declaration: "Routing complete. [N] rows moved to Publication Readiness. [M] rows moved to Findings. Routing audit: [K] additional moves after spot-check. Adjustment rows in PR after audit: 0. No other misrouted rows."

---

## Step 3 — Deduplicate

Scan all rows across both sheets for duplicates — rows where Cell/Row (column C) and Error Type/Issue (column E on Findings, column D on Publication Readiness) are substantively identical. Parallel Wave 2 agents cannot see each other's findings, so duplicates are most common between sources and readability (both check Notes columns) and between plausibility agents (both may flag the same cell). Additionally, the notes-scan agent (stg-nscn-A and stg-nscn-B) has no reconcile agent — both instances may flag the same cell note issue. Apply the same substantive-identity dedup test to these two tabs explicitly.

**Cross-sheet deduplication**: only deduplicate rows that will route to the same output sheet. Do not treat a Findings-destined row and a PR-destined row as duplicates even if they reference the same cell and same issue type — they represent different resolution paths (model fix vs. publication checklist item) and should both be kept.

When duplicates are found (same destination sheet): keep the finding with the more complete Explanation and Recommended Fix; merge any unique detail from the other row into the surviving row's Explanation field. Do not merge near-duplicates that are complementary — a broken link and a stale value at the same cell are distinct issues and should both be kept.

**Root-cause / symptom consolidation** — after the standard duplicate pass, apply a second pass:

1. **Symptom absorbed by root cause**: If an `Inconsistency` finding and a `Legibility` or `Formula` finding both exist, AND the structural/formula finding's explanation identifies the formula-level cause of the discrepancy the `Inconsistency` finding describes, AND they reference overlapping or closely related cells: before dropping the `Inconsistency` finding, confirm the surviving root-cause finding will route to Findings (Error Type is `Formula`, `Parameter`, `Adjustment`, or `Assumption`, OR column H is populated with a directional phrase). If the surviving root-cause finding would route to PR (e.g., its H is blank and description is a documentation gap), do not consolidate — retain the `Inconsistency` finding separately. If the root-cause finding will stay in Findings: keep only the root-cause finding. Merge any output-level detail from the `Inconsistency` finding (e.g., "this causes X and Y to diverge by [amount]") into the root-cause finding's explanation if it adds specificity. Drop the `Inconsistency` finding. Rationale: fixing the root cause automatically resolves the symptom — a separate symptom finding adds no action item.

2. **Same-parameter multi-cell consolidation**: If two or more `Parameter` findings reference **different** cells but describe the same parameter (matching parameter name in the explanation AND the same recommended replacement value), consolidate them into a single finding: list all affected cells comma-separated in column C, write a unified explanation noting each cell and its current value, and write a single recommended fix that covers all cells. Apply the higher severity if they differ. Drop all but the consolidated finding.

After this pass, write: "Semantic consolidation complete. [N] root-cause/symptom pairs consolidated. [M] same-parameter multi-cell groups consolidated."

**High-severity protection during consolidation**: When consolidating findings at different severities (root-cause/symptom grouping or same-parameter multi-cell grouping), always retain the higher severity. Any downgrade from High → Medium during consolidation must be documented with a specific evidentiary reason in column F (e.g., "CE impact computed as 1.3%, below 2% threshold; downgraded to Medium"). Do not downgrade based on scope judgment ("this is a documentation issue") without verifying the CE chain impact is truly <2%. If the CE impact cannot be computed, retain High.

**Synthesis false-positive guard**: After deduplication and consolidation, scan for any finding whose Explanation (column F) contains explicitly cross-agent language — phrases like "both instances flagged," "A noted X while B noted Y," "combining these observations suggests," "Instance A," or "Instance B." For each such finding: downgrade to Medium severity with Researcher judgment needed ✓ and add to the Explanation: "Synthesized from two partial agent observations — researcher to confirm before treating as confirmed error." Do not attempt to verify by reading the source spreadsheet — this agent's scope restriction prohibits reading source spreadsheet values. The final-review-validation agent (Step 10c) performs source-value verification on all High findings; flag synthesized findings as Medium so the validation agent can re-examine them with full source-read access. Rationale: the compaction agent in a prior vet elevated a Low observation to High by combining two partial signals, producing a false positive that the human vet did not catch — and which caused the researcher to distrust the adjacent real findings.

Coverage declaration: "Deduplication complete. [N] exact duplicates merged. [See semantic consolidation above.] Synthesis guard: [M] unverified High findings downgraded. No other duplicates found."

---

## Step 3.3 — Researcher-to-confirm audit

Count all rows with ✓ in column I among Findings sheet rows only (not Publication Readiness rows; not divider rows; not AGENT_COMPLETE rows). Calculate total findings rows as all non-divider, non-AGENT_COMPLETE Findings sheet rows. If the ✓ count is **strictly greater than 20%** of total findings rows (✓ count / total findings > 0.20; at exactly 20%, skip this step), apply the following triage pass before proceeding to Step 4.

For each ✓ row, ask: **can this question be answered by (a) the Explanation text and recommended fix being fully self-contained and unambiguous, (b) checking a cited URL using WebFetch (if WebFetch is in permitted tools), or (c) the finding description referencing a value that is explicitly stated in key-parameters.md?** If yes to any of these, the ✓ mark should not have been filed — the agent had enough information to either confirm or dismiss the finding without researcher input. Do not attempt to read the source spreadsheet to answer this question — this agent's scope restriction prohibits reading source spreadsheet values. When uncertain, retain ✓.

Action for each ✓ row reviewed:
- If the question is answerable from criteria (a), (b), or (c) above → remove the ✓ mark. If the finding is still valid, it remains as a confirmed finding.
- If the question genuinely requires the researcher to explain their analytical intent or confirm an assumption not determinable from the available information → retain ✓.
- If uncertain, retain ✓ but add a note in the Explanation: "Researcher to confirm — [specific question]."

Write: "Step 3.3 complete. ✓ findings before audit: [N]. ✓ marks removed (determinable from spreadsheet): [M]. Rows removed entirely: [K]. ✓ marks retained (genuine intent questions): [N-M-K]."

Skip this step (write "Step 3.3: skipped — ✓ count [N] is ≤20% of total findings [T]") when ✓ count / total findings ≤ 20%.

---

## Step 4 — Rewrite and sort both sheets

Rewrite both sheets sequentially from row 2. The Findings sheet and Publication Readiness sheet are initially empty (all findings were in staging tabs until this step) — write directly from row 2 with no gaps to close.

Sort all Findings rows in memory using four sort keys:
1. **Primary**: Severity (High → Medium → Low)
2. **Secondary**: Estimated CE Impact (column H) — within each severity tier, apply this order: numeric magnitude findings first (rows where column H contains a specific estimate, e.g., "Raises CE — 2.5x" or "Lowers CE — 1.3x"), then magnitude-unknown findings ("Raises CE — magnitude unknown", "Lowers CE — magnitude unknown"), then "Direction unknown", then "No CE impact", then blank. Within the numeric magnitude tier, sort "Raises CE" entries before "Lowers CE" entries (findings that overstate CE are higher priority for correction). Within the magnitude-unknown tier, similarly sort "Raises CE — magnitude unknown" before "Lowers CE — magnitude unknown."
3. **Tertiary**: Error Type/Issue (column E, alphabetical)
4. **Quaternary**: Researcher judgment needed (column I) — within the same severity, CE impact tier, and error type, place findings WITHOUT ✓ before findings WITH ✓. Confirmed findings should appear before researcher-to-confirm items so reviewers encounter actionable findings first without having to skip over speculative ones.

Then rewrite the Findings sheet from row 2 with section dividers. **If no findings exist at a given severity level, skip that divider entirely — do not write an empty `─── High (0 findings) ───` row.** Only write a divider when at least one finding of that severity is present.

- Before the first High finding (if any): divider row with column B = `─── High (N findings) ───`, all other columns blank.
- All High findings follow.
- Before the first Medium finding (if any): `─── Medium (N findings) ───`.
- All Medium findings follow.
- Before the first Low finding (if any): `─── Low (N findings) ───`.

Divider rows are auto-styled by conditional formatting (gray background — triggered when column B contains `───`). Divider rows are not finding rows — skip them when counting for the N values above.

Sort the Publication Readiness sheet by Error Type/Issue (column D, alphabetical) and rewrite without dividers.

Coverage declaration: "Sort and rewrite complete. Findings: [N] High, [M] Medium, [L] Low, [D] divider rows. Publication Readiness: [N] rows."

---

## Step 5 — Assign Finding IDs

After sort is complete, write sequential IDs to column A. Skip divider rows — a row is a divider if column D (Severity) is empty and column B contains `───`.

- Findings sheet: write `F-001`, `F-002`, `F-003`, … for each non-divider row from row 2 onward.
- Publication Readiness sheet: write `PR-001`, `PR-002`, … from row 2 onward (no dividers to skip).

Use a single `modify_sheet_values` call per sheet to write all IDs at once. Confirm `Finding #` is the column A header on both sheets (row 1).

Final coverage declaration: "Compaction complete. [N] Findings IDs assigned (F-001 through F-[NNN]). [M] Publication Readiness IDs assigned (PR-001 through PR-[MMM]). [X] rows misrouted and moved. [Y] duplicates merged."

---

## Step 6 — Write AGENT_COMPLETE marker

After ID assignment is complete and the coverage declaration is written, write one final row to the Findings sheet immediately after the last assigned Finding ID row: column B = `final-review-compaction`, column D = `AGENT_COMPLETE`, column F = `COVERAGE_ROWS: Findings sheet rows 2–[last_finding_row] | Staging tabs read: [N]. [N] Findings IDs assigned (F-001–F-[NNN]). [M] Publication Readiness IDs assigned. [X] rows misrouted and moved. [Y] duplicates merged. Staging_backup created.`

Use a single `modify_sheet_values` call. This marker lets the gap-fill and validation agents confirm compaction ran and completed normally before they begin their passes. Do not write it before Step 5 is complete — the row count and ID range must be accurate.
