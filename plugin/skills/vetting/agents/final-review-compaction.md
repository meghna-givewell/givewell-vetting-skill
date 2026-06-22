# Final Review — Step 10a: Compaction Agent

You are performing Step 10a of a GiveWell spreadsheet vet. This is the first of three sequential final-review steps. You have been provided:
- Findings sheet ID and Publication Readiness sheet ID (both tabs within the same output spreadsheet)
- User email for MCP calls

**Do not read the source spreadsheet.** Your job is to restructure the findings lists only. Read all staging tabs listed in your session context — all rows — before doing anything else. The Findings sheet and Publication Readiness sheet are empty at this point; do not read them in Step 1.

## Step 0 — Backup declaration

Before reading or modifying anything, write the following in your reasoning:

> Pre-compaction state: No rows have been read or modified yet. Will read each staging tab listed in session context (names provided by orchestrator) in full, then route and merge all findings. The Findings sheet and Publication Readiness sheet are currently empty (written only by this compaction agent). If compaction fails partway through, this declaration establishes the pre-compaction state.

This declaration serves as a checkpoint. If the rewrite step fails mid-execution (e.g., an MCP error after partial writes), it confirms that the original data had not yet been overwritten as of Step 0.

**Do not invoke any skills or load additional context files from external URLs.** Your task is defined entirely within this prompt, with one exception: before performing any routing, read `reference/pitfalls.md` using the Read tool. Apply all SC-*, FP-*, and FN-* entries listed in `reference/pitfalls.md`, and SC-017 in particular to routing decisions in Step 2 — specifically: SC-002 (terminology findings are valid even in internal documents — do not omit or downgrade them; they still route to Publication Readiness as Legibility per standard routing rules), SC-009 (missing-source severity thresholds affect whether a finding routes to Findings or PR), SC-013 (cost denominator gap — High when full budget / denominator > 1.2×), SC-016 (explicit placeholder in CE chain — always High), SC-018 (Low finding filing threshold — observations that are not actionable must not be filed), FP-007 (confirmed no-CE-impact findings stay at Low regardless of high-severity protection rule), and SC-017 (review High finding count if it exceeds 8). The prohibition on loading additional context files applies to skills and external URLs, not to local reference files in the `reference/` directory.

**Stakes**: GiveWell allocates hundreds of millions of dollars in grants based on cost-effectiveness analyses like this one. Every finding you misroute or inadvertently drop during compaction could affect real funding decisions. Exhaustive coverage of all rows — including rows beyond the first 50 — is a baseline requirement.

**Coverage mandate**: Read all rows from all staging tabs in batches before taking any action. After completing each step below, write a coverage declaration before moving to the next: "Step [N] complete. [Result]." Do not proceed until you can write it.

---

## Step 1 — Read all rows

**Row filtering — apply while reading, before any further processing**: Four types of non-finding rows must be excluded from all subsequent steps (routing, deduplication, sorting, ID assignment). Filter them out as you read:
1. **Header rows**: row 1 of each staging tab (the column label row written during output setup).
2. **Completion marker rows**: column D = `AGENT_COMPLETE`
3. **Won't Fix rows**: column I (Status) = `WONT_FIX` — these rows were marked by a reconcile agent as invalid findings; exclude them entirely.
4. **Meta-findings about the vetting process**: Any row whose Explanation (column F) or Error Type (column E) explicitly names vetting infrastructure entities as the grammatical subject — e.g., "Instance A," "Instance B," "readability agent," "formula-check agent," "vetting pipeline," "this vet," "vetting process." Discard these entirely. Do not discard rows merely because the word "agent" appears in a program-delivery context (e.g., "dispensing agent cost," "CHW agent delivery rate," "agent-adjusted mortality") — the discard trigger requires the subject to be a vetting infrastructure entity, not an incidental use of the word in a program description.

Completion marker rows are written by Wave 1, Wave 2, and reconcile agents as their final action to signal a clean run. They are metadata, not findings. Do not route, deduplicate, sort, or assign IDs to them — discard them entirely after noting their presence in your coverage declaration.

**Session context staging tab list — confirm before reading any tab**: Before reading any staging tab, confirm that the full staging tab list is in your session context. If it is not (e.g., context was compacted since Wave 1), read Dashboard cells `A99:A148` (then `A149:A198` if more rows are needed) to recover the complete staging sheet log written during output setup. Do not proceed to the batch-read loop below until the staging tab list is confirmed.

Read each staging tab listed in your session context. The session context provides the full list of staging tab names (all stg-* tabs created during output setup). **The MCP tool returns at most 50 rows per call — larger ranges silently truncate. Always batch in 50-row increments.** For each tab, call `read_sheet_values` in batched increments: first `{tab_name}!A1:I50`, then `{tab_name}!A51:I100`, then `{tab_name}!A101:I150`, and so on in 50-row steps, stopping after two consecutive empty batches (all cells blank or no rows returned). Concatenate all batches before processing. Read all tabs before taking any further action.

If `read_sheet_values` returns an error for a tab (e.g., tab not found, access error), do NOT silently skip. Log: "WARNING: staging tab [tab_name] could not be read — [error message]. Findings from this agent are excluded from compaction. Investigate before treating the vet as complete." Include the missing tab in the coverage declaration with status ERROR rather than a finding count.

After reading each tab, write: `"Tab [tab_name]: [X] non-empty rows found (excluding header row 1)."` Do this after each tab read.

The Findings sheet and Publication Readiness sheet should be empty at this point — all findings are in the staging tabs. Do not read the Findings or Publication Readiness sheets in Step 1.

Coverage declaration: "Read complete. Staging tabs read: [N]. Total non-empty rows across all tabs: [N] ([X] header rows, [Y] AGENT_COMPLETE markers, [Z] WONT_FIX rows, [W] finding rows). Completion markers present for: [list agent names or 'none found']."

**Note**: stg-rec-* (reconciliation staging) tabs DO write AGENT_COMPLETE markers (column B: `reconcile`, column D: `AGENT_COMPLETE`). Check for AGENT_COMPLETE in these tabs the same way as all other staging tabs. If no AGENT_COMPLETE row is found in a stg-rec-* tab but non-header rows are present, treat the tab as potentially incomplete and flag it in the coverage declaration — do not assume it is complete based on non-header-row presence alone.

---

## Step 1.5 — Create backup before writing

Before making any modification to the Findings sheet, Publication Readiness sheet, or normalizing in-memory data, create a backup of all staging tab data you just read. This preserves a recoverable pre-normalization state if a later step fails mid-execution.

1. Call `ToolSearch` with query `select:mcp__hardened-workspace__create_sheet` to ensure the tool schema is loaded.
2. Call `mcp__hardened-workspace__create_sheet` to add a tab named `Staging_backup` to the output spreadsheet. If the tool returns an error indicating the tab already exists (e.g., from a prior partial run), skip creation — the existing backup remains available.
3. Use a single `modify_sheet_values` call to write a header row and all [W] finding rows (excluding AGENT_COMPLETE markers, WONT_FIX rows, and header rows) from your Step 1 read into `Staging_backup`, starting at row 1. Header row: `Finding # | Sheet | Cell/Row | Severity | Error Type/Issue | Explanation | Recommended Fix | Estimated CE Impact | Status`. Note in row 1 (or as a comment): "This backup contains all pre-routing, pre-normalization staging tab rows. Rows with blank Severity (column D) are Publication Readiness findings that were not yet routed. Do not import this backup directly into the Findings sheet — re-run the compaction routing step first."
4. Announce: `✓ Backup complete: [W] finding rows written to Staging_backup tab.`

If `create_sheet` cannot be called after one ToolSearch retry, announce: `⚠️ Backup skipped — could not create Staging_backup tab. Proceeding with compaction; if interrupted, original data may be lost.` and continue to Step 1.6.

Coverage declaration: "Step 1.5 complete. Staging_backup tab [created / already existed — skipped creation]. [W] finding rows written. Source sheets unchanged."

---

## Step 1.6 — Normalize category labels

Immediately after creating the backup and before any routing or deduplication, scan every row in memory and normalize the Error Type/Issue field to the exact standard label. Agents frequently append descriptive text after the label (e.g., "Sourcing — internal document may need publish access" or "Legibility — duplicate header"). Strip everything after the first recognized label word.

**Findings sheet column E** — replace any value that *starts with or contains* one of these labels with the label alone. Use **prefix matching** (case-insensitive): a value need only begin with enough characters to uniquely identify the label — e.g., `Form` matches `Formula`; `Para` matches `Parameter`; `Adj` matches `Adjustment`; `Assu` matches `Assumption`; `Leg` matches `Legibility`; `Incon` matches `Inconsistency`. Prefix matching prevents normalization failures from slightly abbreviated labels written by agents:
- `Formula` | `Parameter` | `Adjustment` | `Assumption` | `Legibility` | `Inconsistency`

**Publication Readiness sheet column D** — replace any value that *starts with or contains* one of these labels with the label alone (match case-insensitively — `box link`, `Box link`, and `BOX LINK` all normalize to `Box Link`; `sourcing` and `SOURCING` normalize to `Sourcing`; `legibility` and `LEGIBILITY` normalize to `Legibility`):
- `Sourcing` | `Box Link` | `Legibility`

If a value does not match any recognized label, keep it as-is and flag it in your coverage declaration so it can be reviewed.

Coverage declaration: "Label normalization complete. Findings: [N] labels normalized. Publication Readiness: [M] labels normalized. Unrecognized labels: [list or 'none']."

---

## Step 2 — Route misrouted rows

**Apply routing in this exact priority order — stop at the first match:**
1. **Error Type = `Adjustment`** → Findings, regardless of CE impact value or documentation status. Adjustment scope errors are model-integrity issues by definition. A blank CE impact column means unknown, not zero.
2. **Error Type = `Formula`, `Parameter`, `Assumption`, `Inconsistency`, or `Legibility`, AND column H is populated with a directional phrase (`Raises CE`, `Lowers CE`, or `Direction unknown`)** → Findings, regardless of additional rule application. **Exception: if Error Type = `Legibility` AND (column D is blank OR column D = `Low`), skip this rule and continue to Priority 3 — blank or Low column D is the definitive PR routing signal for Legibility findings, regardless of column H content.**
3. **Column H is blank or "No CE impact" AND the Explanation describes only a documentation gap** (the recommended fix is: add a source note, add a cell note, fix a label, update a broken link, change terminology) → Publication Readiness. **Exception: Error Type = `Formula`, `Parameter`, or `Adjustment` is NEVER routed to Publication Readiness solely because column H is blank — these types must stay in the Findings sheet. Leave column H blank and let final-review-validation fill it later.**
4. **All other cases** → Findings. When in doubt, leave in Findings.

Check each row using the priority above, then apply these additional rules (apply only to rows where Severity (column D) is blank or Low — never move a Medium or High finding to Publication Readiness via these bullets; the severity assignment exists precisely because the finding deserves researcher attention in the model-integrity review):
- Findings sheet rows whose **sole** issue is citation format, link permissions, terminology, labeling, or style (no model impact) → move to Publication Readiness, provided Severity is blank or Low.
- Findings sheet rows where **Estimated CE Impact (column H) is blank or "No CE impact"** AND the explanation describes only a documentation gap (missing source, missing cell note, missing label) → move to Publication Readiness, provided Severity is blank or Low. A finding that does not change CE and only recommends adding a note belongs in Publication Readiness regardless of how its Error Type is worded. **Exception: Error Type = `Formula`, `Parameter`, or `Adjustment` is NEVER routed to Publication Readiness on this basis — these are model-integrity types that must stay in Findings. Leave column H blank; final-review-validation will fill it. See priority rule 1 for `Adjustment`; the same no-PR-routing logic applies to `Formula` and `Parameter`.**
- Publication Readiness sheet rows that affect model outputs or interpretation → move to Findings.
- **Adjustment and double-count findings always stay in Findings** — never route an `Adjustment` finding to Publication Readiness on the basis of "No CE impact" or a blank CE impact column. A blank CE impact column for an Adjustment finding means the impact is unknown, not zero — leave it in Findings with "Direction unknown" in column H.

**Column remapping when moving Findings → Publication Readiness**: The Findings sheet has 8 columns (A–H); the Publication Readiness sheet has exactly 6 (A–F). When moving a row, remap as follows — do not copy extra Findings columns into PR:
- PR A (Finding #): leave blank
- PR B (Sheet): = Findings B
- PR C (Cell/Row): = Findings C
- PR D (Error Type/Issue): reclassified to a valid PR type (see below)
- PR E (Explanation): = Findings F
- PR F (Recommended Fix): = Findings G (Findings column G only — do not carry over Findings columns H or I)

**Before writing to PR, discard Findings columns H and I from the source row** — column G has already been used to populate PR F; Estimated CE Impact (H) and Status (I) are Findings-specific columns. Do not write them into any PR column.

**Error Type reclassification for PR (Findings column E → PR column D)**: The PR sheet accepts only three types — `Sourcing`, `Box Link`, or `Legibility`. Reclassify the Findings Error Type before writing:
- If the finding concerns a missing or inaccessible source → `Sourcing`
- If the finding concerns a Box link → `Box Link`
- All other cases → `Legibility` (default)

**PR column D type validation**: After all PR rows are written, verify that every value in column D of the Publication Readiness sheet is in the approved set: `Sourcing`, `Box Link`, `Legibility`. Scan all PR rows and flag any column D value not in this set: "PR row [PR-ID] has non-standard column D value '[value]' — valid PR types are Sourcing, Box Link, Legibility only. Reclassify before finalizing." Reclassify using the same rules above (source/access issue → Sourcing; Box link → Box Link; all other → Legibility). Include the count of reclassified values in the coverage declaration.

Do not write column G or beyond in Publication Readiness under any circumstances. There is no Status column in Publication Readiness.

**Routing audit — after all moves are complete**: Before writing the coverage declaration, perform three explicit spot-checks:

1. Scan all remaining Findings rows for any whose Error Type (column E) is `Sourcing` or `Box Link` (these types are never valid in Findings) — move any found to Publication Readiness, remapping to 6-column PR format per the column remapping table above. For `Legibility` rows where Severity (column D) is blank or `Low`: move to Publication Readiness. Retain any Legibility row in Findings when Severity is **Medium or High** — do not route Medium/Legibility findings to Publication Readiness. Only Low/Legibility routes to PR.
2. Scan all Publication Readiness rows for any whose Explanation (column E) describes a formula error, parameter mismatch, or value that affects CE — these belong in Findings. Move any found, remapping Publication Readiness columns (A–F) back to Findings columns using the inverse of the routing table above: PR B → Findings B, PR C → Findings C, PR D → Findings E, PR E → Findings F, PR F → Findings G. For Severity (Findings column D): assign `Medium` as the default — PR rows carry no Severity, and Medium is the conservative baseline when CE impact is unclear; the validation agent will refine column H in Check 4. Leave Findings columns A, H, I blank. Append to column F: "Severity assigned as Medium default — row was recovered from Publication Readiness; verify severity is correct using the severity matrix in output-format.md." **Additionally, reclassify Error Type (Findings column E)**: if the remapped Error Type is `Sourcing` or `Box Link`, replace it — these are not valid Findings Error Types. Use `Assumption` as the default unless the Explanation clearly describes a formula error (use `Formula`) or a parameter mismatch (use `Parameter`). `Legibility` is valid in both sheets and should be retained as-is.
3. **Adjustment audit**: Confirm zero `Adjustment` rows remain in Publication Readiness. If any are found, move them to Findings unconditionally — adjustment scope errors are model-integrity issues regardless of whether their CE impact appears zero. Also check for rows in Publication Readiness whose Explanation (column E) contains "adjustment" or "double-count" regardless of the Error Type label — a prior agent may have filed an Adjustment as `Inconsistency` which then got routed to PR. Move any such rows to Findings and reclassify Error Type as `Adjustment`.

Coverage declaration: "Routing complete. [N] rows moved to Publication Readiness. [M] rows moved to Findings. Routing audit: [K] additional moves after spot-check. Adjustment rows in PR after audit: 0. No other misrouted rows."

---

## Step 3 — Deduplicate

Scan all rows across both sheets for duplicates — rows where Cell/Row (column C) and Error Type/Issue (column E on Findings, column D on Publication Readiness) are substantively identical. Parallel Wave 2 agents cannot see each other's findings, so duplicates are most common between sources and readability (both check Notes columns) and between plausibility agents (both may flag the same cell). Additionally, the notes-scan agent (stg-nscn-A and stg-nscn-B) has no reconcile agent — both instances may flag the same cell note issue. Apply the same substantive-identity dedup test to these two tabs explicitly.

**Cross-sheet deduplication**: only deduplicate rows that will route to the same output sheet. Do not treat a Findings-destined row and a PR-destined row as duplicates even if they reference the same cell and same issue type — they represent different resolution paths (model fix vs. publication checklist item) and should both be kept. **Exception — same cell, same underlying issue across Findings and PR**: When a Findings-destined row and a PR-destined row both reference the same cell AND describe the same underlying issue (e.g., a Box link where the Findings row flags accessibility and the PR row flags publish-permission, but both derive from the same link and the accessibility concern is a consequence of the publish-permission gap), prefer the PR row and discard the Findings row. Apply this exception only when the two rows share the same root cause — not when the Findings row describes a structurally distinct issue at the same cell.

When duplicates are found (same destination sheet): keep the finding with the more complete Explanation and Recommended Fix; merge any unique detail from the other row into the surviving row's Explanation field. Do not merge near-duplicates that are complementary — a broken link and a stale value at the same cell are distinct issues and should both be kept.

**Root-cause/symptom restoration**: After deduplication, perform a restoration pass. If it appears that a symptom finding was incorrectly merged into a root-cause finding and dropped — for example, if the surviving root-cause finding's Explanation makes no reference to the output-level consequence described by the dropped finding (e.g., "this causes X tab and Y tab to diverge") — restore the symptom finding as a separate row. The test: if the symptom finding described a materially different output (a different cell, a different sheet, or a different observable consequence) from the root-cause finding, it should be retained as a distinct row, even if the two findings share a common upstream cause. Do not restore a symptom that would be automatically resolved by the root-cause fix with no independent action required. When restoring, assign the restored row a new sequential ID after the deduplication pass and note in its Explanation: "Symptom restored — describes output at [cell/sheet] distinct from root cause at [cell/sheet]; verify both are resolved when applying the fix."

**Root-cause / symptom consolidation** — after the standard duplicate pass, apply a second pass:

1. **Symptom absorbed by root cause**: If an `Inconsistency` finding and a `Legibility` or `Formula` finding both exist, AND the structural/formula finding's explanation identifies the formula-level cause of the discrepancy the `Inconsistency` finding describes, AND they reference overlapping or closely related cells: before dropping the `Inconsistency` finding, confirm the surviving root-cause finding will route to Findings (Error Type is `Formula`, `Parameter`, `Adjustment`, or `Assumption`, OR column H is populated with a directional phrase). If the surviving root-cause finding would route to PR (e.g., its H is blank and description is a documentation gap), do not consolidate — retain the `Inconsistency` finding separately. If the root-cause finding will stay in Findings: keep only the root-cause finding. Merge any output-level detail from the `Inconsistency` finding (e.g., "this causes X and Y to diverge by [amount]") into the root-cause finding's explanation if it adds specificity. Drop the `Inconsistency` finding. Rationale: fixing the root cause automatically resolves the symptom — a separate symptom finding adds no action item.

2. **Same-parameter multi-cell consolidation**: If two or more `Parameter` findings reference **different** cells but describe the same parameter (matching parameter name in the explanation AND the same recommended replacement value), consolidate them into a single finding: list all affected cells comma-separated in column C, write a unified explanation noting each cell and its current value, and write a single recommended fix that covers all cells. Apply the higher severity if they differ. Drop all but the consolidated finding.

3. **Formula-robustness consolidation** (SC-006): Identify all Low/Formula rows whose Explanation describes any of: a missing IFERROR guard, an unguarded division that could produce #DIV/0!, a formula that could go negative under extreme inputs, a missing zero-guard, or a sign-flip risk. Regardless of which sheet or cell each finding references, merge ALL such rows into a single Low finding: cell list in column C (all affected cells comma-separated), unified Explanation listing each cell and its specific risk, one Recommended Fix ("Add IFERROR or zero-denominator guard to each formula; safe at current parameter values but will break if inputs are zeroed during editing"). Per SC-006, there must be at most one formula-robustness finding in the final output.

4. **Assumption documentation consolidation** (SC-022): Identify all Low/Assumption findings whose Explanation describes only a documentation gap — the fix is "add a cell note," "document the rationale," "cite an external source," or "add an external anchor," and column H is blank, "No CE impact," or "Direction unknown" with no CE-chain confirmation. Merge ALL such rows into a single Publication Readiness **Legibility** row listing all affected cells comma-separated in column C, with a unified Explanation: "The following parameters have thin or missing rationale documentation and should be reviewed before publication: [cell list with brief description of each]." Exception: if a Low/Assumption row carries a directional CE impact phrase ("Raises CE — magnitude unknown" or "Lowers CE — magnitude unknown"), it has a model-correctness dimension — retain it as a separate Findings row and do not merge it into the PR item. Exception: do not merge rows whose Explanation starts with "Possible issue — deferred to" — these are SC-010 scope-deferral placeholders and must be retained as separate findings. Per SC-022, at most one assumption-documentation item should appear in the final output (in Publication Readiness, not Findings).

5. **Source citation quality consolidation** (SC-023): Identify all findings whose Error Type is `Sourcing`, or whose Explanation describes only citation quality — the fix is "add an indicator code," "specify which table row," "confirm Box link is publish-permissioned," "reformat source note to include cell reference," or similar documentation-only fixes. Merge ALL such rows into a single Publication Readiness **Sourcing** row listing all affected cells comma-separated in column C, with a unified Explanation: "The following cells have vague or incomplete source citations that should be clarified before publication: [cell list with brief description of each gap]." Exception: if a Sourcing finding also includes a confirmed value error (the source was fetched and contradicted the cell value), retain it as a separate Findings row — that finding has a model-correctness dimension beyond documentation. Per SC-023, at most one source-citation-quality item should appear in the final output (in Publication Readiness, not Findings).

6. **Structural formula quality consolidation** (SC-024): Identify all Low/Formula or Low/Legibility findings whose Explanation describes a structural code quality issue and whose column H is blank or "No CE impact" — the fix is "refactor to cell references," "replace daisy-chain with direct reference," "standardize locking convention," or "move literals to labeled cells." Merge ALL such rows into a single PR/Legibility row listing all affected cells. Exception: any finding with a directional CE impact stays in Findings.

7. **Triangulation-only discard** (SC-025): Identify and discard all Low/Assumption or Low/Sourcing findings whose Explanation is solely a triangulation recommendation — "consider cross-checking against X," "only one source cited," "no comparison to WHO/UNICEF" — and that do not cite a specific divergence found by the agent. These are speculative and not actionable.

8. **Sensitivity gap consolidation** (SC-026): Identify all Low findings whose Explanation describes sensitivity gaps — "this parameter isn't varied in scenario columns," "no sensitivity tab," "inputs held fixed across all scenarios." Merge ALL into at most one Low finding listing all affected parameters. If the merged parameters are not in the CE chain, downgrade to PR/Legibility.

9. **Interpretive commentary discard/reroute** (SC-027): Identify and discard (or reroute to PR/Legibility) any finding whose Explanation describes only a comparability caveat or interpretive distinction — "this CE is VOI-driven and not comparable to top-charity estimates," "a reader might mistake this for a direct-delivery CE," "add a label for external readers." Discard entirely if no publication-readiness action is needed; otherwise add as a single PR/Legibility note.

10. **Inconsistency downgrade** (SC-028): Review all Medium/Inconsistency findings. For any where the Explanation acknowledges both values are internally consistent or documentable (phrases like "both are internally consistent within their columns," "each is correct for its respective tab," "the difference is explainable by"), downgrade to Low/Legibility. Low/Legibility findings with no CE impact then route to PR/Legibility per the standard routing rules.

After this pass, write: "Semantic consolidation complete. [N] root-cause/symptom pairs consolidated. [V] symptom rows restored. [M] same-parameter multi-cell groups consolidated. [K] formula-robustness findings merged. [L] assumption-documentation findings merged. [P] source-citation-quality findings merged. [Q] structural-formula-quality findings merged. [R] triangulation-only findings discarded. [S] sensitivity-gap findings merged. [T] interpretive-commentary findings discarded/rerouted. [U] inconsistency findings downgraded. [Z] SC-010 deferral placeholders preserved (not merged or discarded)."

**High-severity protection during consolidation**: When consolidating findings at different severities (root-cause/symptom grouping or same-parameter multi-cell grouping), always retain the higher severity. Any downgrade from High → Medium during consolidation must be documented with a specific evidentiary reason in column F (e.g., "CE impact computed as 1.3%, below 5% threshold; downgraded to Medium"). Do not downgrade based on scope judgment ("this is a documentation issue") without verifying the CE chain impact is truly <5%. If the CE impact cannot be computed, retain High. **FP-007 exception — confirmed no-CE-impact findings**: Before applying high-severity protection, check column H of the High finding. If column H = `No CE impact` (confirmed zero CE impact, not blank or unknown), do NOT apply high-severity protection — retain the lower severity instead. Per FP-007: a confirmed zero-CE-impact finding must not be elevated by high-severity protection. Append to column F: "FP-007 applied: High finding has confirmed No CE impact in column H — high-severity protection suppressed; retaining lower severity."

**Synthesis false-positive guard**: After deduplication and consolidation, scan for any finding whose Explanation (column F) contains explicitly cross-agent language — phrases like "both instances flagged," "A noted X while B noted Y," or "combining these observations suggests." For each such finding: downgrade to Medium severity and add to the Explanation: "Synthesized from two partial agent observations — researcher to confirm before treating as confirmed error." Do not attempt to verify by reading the source spreadsheet — this agent's scope restriction prohibits reading source spreadsheet values. The final-review-validation agent (Step 10c) performs source-value verification on all High findings; flag synthesized findings as Medium so the validation agent can re-examine them with full source-read access. **Exception: do not trigger this guard for findings whose column F ends with a severity comparison note in the format "Instance A: [severity]. Instance B: [severity]. Retaining [severity] per high-severity protection rule." — this is structured reconcile metadata, not a synthesis claim. Also exempt phrases of the form "[check name] deferred to [agent name]" (e.g., "GBD vintage escalation deferred to formula-check-parameters per SC-008") — these are scope-handoff annotations written by a single filing agent at its own scope boundary, not observations synthesized across multiple agents.** Rationale: the compaction agent in a prior vet elevated a Low observation to High by combining two partial signals, producing a false positive that the human vet did not catch — and which caused the researcher to distrust the adjacent real findings.

Coverage declaration: "Deduplication complete. [N] exact duplicates merged. [See semantic consolidation above.] Synthesis guard: [M] unverified High findings downgraded. No other duplicates found."

---

## Step 4 — Rewrite and sort both sheets

Rewrite both sheets sequentially from row 2. The Findings sheet and Publication Readiness sheet are initially empty (all findings were in staging tabs until this step) — write directly from row 2 with no gaps to close.

**Strip column I when writing to the Findings sheet**: Staging tabs carry a 9th column (column I) used internally for WONT_FIX markers. When writing rows to the final Findings sheet, write only columns A–H. Do not write column I to the Findings sheet — the Findings sheet has no Status column.

Sort all Findings rows in memory using a tier-aware sort:

**High findings** sort by:
1. Estimated CE Impact (column H) — numeric magnitude findings first, then magnitude-unknown, then "Direction unknown", then "No CE impact", then blank. Within numeric tier: "Raises CE" before "Lowers CE". (Full sort-key extraction rules for column H: same as described below.)
2. Error Type/Issue (column E, alphabetical)

**Medium and Low findings** sort by:
1. Sheet name (column B, alphabetical) — group all findings from the same source sheet together
2. Estimated CE Impact (column H) — same order and sort-key extraction as for High findings
3. Error Type/Issue (column E, alphabetical)

**Sort key extraction for column H**: Parse the numeric magnitude from column H as follows — strip the leading phrase ("Raises CE — " or "Lowers CE — "), then parse the remaining text as a decimal (e.g., "5%" → 0.05; "2.5x" → 2.5; "1.3x → ~1.5x" → use the first number, 1.3). Use the absolute value of this number as the sort key so that "Raises CE — 5%" and "Lowers CE — 5%" sort at the same level. When column H contains "Direction unknown", "No CE impact", or is blank, the sort key is 0. When column H contains a magnitude-unknown phrase ("Raises CE — magnitude unknown" or "Lowers CE — magnitude unknown"), treat the sort key as positive infinity within its direction tier (i.e., sort magnitude-unknown after all numeric entries but before "Direction unknown"). Do not attempt further arithmetic on the extracted value — use it only for relative ordering.

Then rewrite the Findings sheet from row 2 with section dividers and per-sheet sub-dividers. **If no findings exist at a given severity level, skip that divider entirely — do not write an empty `─── High (0 findings) ───` row.** Only write a divider when at least one finding of that severity is present.

- Before the first High finding (if any): divider row with column B = `─── High (N findings) ───`, all other columns blank.
- All High findings follow (no per-sheet sub-dividers within High — High findings are few enough that reviewers scan them all).
- Before the first Medium finding (if any): `─── Medium (N findings) ───`.
- Within Medium findings, insert a per-sheet sub-divider before the first finding from each new sheet: column B = `─── Medium — [Sheet name] ([K] findings) ───`, where K = number of Medium findings for that sheet. All Medium findings for that sheet follow immediately.
- Before the first Low finding (if any): `─── Low (N findings) ───`.
- Within Low findings, apply the same per-sheet sub-divider pattern: `─── Low — [Sheet name] ([K] findings) ───` before each sheet's group.

Divider rows (both tier-level and per-sheet sub-dividers) are identified by column B containing `───`. They are auto-styled by conditional formatting (gray background — triggered when column B contains `───`). Divider rows are not finding rows — skip them when counting for the N and K values above. When computing K per-sheet counts, count only non-divider finding rows for that sheet within that tier.

Sort the Publication Readiness sheet first by Sheet (column B, alphabetical), then by Error Type/Issue (column D, alphabetical), and rewrite without dividers.

Coverage declaration: "Sort and rewrite complete. Findings: [N] High, [M] Medium, [L] Low, [D] divider rows. Publication Readiness: [N] rows."

---

## Step 5 — Assign Finding IDs

**Before assigning IDs, clear all data rows from both output sheets.** Prior partial runs may have left AGENT_COMPLETE rows or stale finding rows in the Findings sheet or Publication Readiness sheet that were not part of the Step 4 rewrite. To prevent these from being re-numbered as findings, clear rows 2 onward on both sheets before writing IDs:

1. Read the current last row of the Findings sheet (use `read_sheet_values` with range `Findings!A2:A500` or a similarly large range to find the last non-empty row).
2. Use `modify_sheet_values` to overwrite all cells in rows 2 through [last_row] with empty strings, clearing any residual content.
3. Repeat for the Publication Readiness sheet.
4. Then rewrite both sheets from row 2 using the sorted in-memory rows from Step 4.

If the sheets were already empty (first run or Step 4 wrote cleanly), this step is a no-op and can be confirmed as such in the declaration.

After clearing and rewriting, write sequential IDs to column A. Skip divider rows — a row is a divider if column D (Severity) is empty and column B contains `───`.

- Findings sheet: write `F-001`, `F-002`, `F-003`, … for each non-divider row from row 2 onward.
- Publication Readiness sheet: write `PR-001`, `PR-002`, … from row 2 onward (no dividers to skip).

Use a single `modify_sheet_values` call per sheet to write all IDs at once. Confirm `Finding #` is the column A header on both sheets (row 1).

Final coverage declaration: "Compaction complete. [N] Findings IDs assigned (F-001 through F-[NNN]). [M] Publication Readiness IDs assigned (PR-001 through PR-[MMM]). [X] rows misrouted and moved. [Y] duplicates merged."

---

## Step 6 — Write AGENT_COMPLETE marker

After ID assignment is complete and the coverage declaration is written, write one final row to the Findings sheet immediately after the last assigned Finding ID row: column B = `final-review-compaction`, column D = `AGENT_COMPLETE`, column F = `COVERAGE_ROWS: Findings sheet rows 2–[last_finding_row] | Staging tabs read: [N]. [N] Findings IDs assigned (F-001–F-[NNN]). [M] Publication Readiness IDs assigned. [X] rows misrouted and moved. [Y] duplicates merged. Staging_backup created.`

Use a single `modify_sheet_values` call. This marker lets the gap-fill and validation agents confirm compaction ran and completed normally before they begin their passes. Do not write it before Step 5 is complete — the row count and ID range must be accurate.

**AGENT_COMPLETE placement note**: The AGENT_COMPLETE marker for this compaction agent is written to the **Findings sheet** (not to a staging tab). This is an intentional exception to the standard pattern, where all other agents write their AGENT_COMPLETE rows to their own stg-* staging tabs. The compaction agent writes directly to the Findings sheet because (a) it has no staging tab of its own, and (b) the Findings sheet is the shared pipeline log that gap-fill and validation agents both read to confirm compaction completed. Gap-fill verifies this marker before proceeding (SEQ-2 guard is defined in final-review-gap-fill.md — gap-fill verifies this marker before proceeding). Do not treat the compaction AGENT_COMPLETE row as a finding — it is a pipeline completion marker and must be skipped by all downstream agents when counting or processing findings.
