# Final Review — Step 10a: Compaction Agent

You are performing Step 10a of a GiveWell spreadsheet vet. This is the first of three sequential final-review steps. You have been provided:
- Findings sheet ID and Publication Readiness sheet ID (both tabs within the same output spreadsheet)
- User email for MCP calls

**Do not read the source spreadsheet.** Your job is to restructure the findings lists only. Read both sheets — all rows — before doing anything else.

## Step 0 — Backup declaration

Before reading or modifying anything, write the following in your reasoning:

> Pre-compaction state: No rows have been read or modified yet. Will read Findings sheet in 50-row batches (A2:J51, A52:J101, A102:J151, … continuing until two consecutive empty batches) and Publication Readiness in 50-row batches (A2:F51, A52:F101, … continuing until two consecutive empty batches). If compaction fails partway through, this declaration establishes the pre-compaction state.

This declaration serves as a checkpoint. If the rewrite step fails mid-execution (e.g., an MCP error after partial writes), it confirms that the original data had not yet been overwritten as of Step 0.

**Do not invoke any skills or load additional context files.** Your task is defined entirely within this prompt.

**Stakes**: GiveWell allocates hundreds of millions of dollars in grants based on cost-effectiveness analyses like this one. Every finding you misroute or inadvertently drop during compaction could affect real funding decisions. Exhaustive coverage of all rows — including rows beyond the first 50 — is a baseline requirement.

**Coverage mandate**: Read all rows from both sheets in batches before taking any action. After completing each step below, write a coverage declaration before moving to the next: "Step [N] complete. [Result]." Do not proceed until you can write it.

---

## Step 1 — Read all rows

**Row filtering — apply while reading, before any further processing**: Three types of non-finding rows must be excluded from all subsequent steps (routing, deduplication, sorting, ID assignment). Filter them out as you read:
1. **Divider rows**: column D is empty AND column B contains `───`
2. **Completion marker rows**: column D = `AGENT_COMPLETE`
3. **Meta-findings about the vetting process**: Any row whose Explanation (column F) or Error Type (column E) references the vetting pipeline itself — e.g., "agent," "Instance A," "Instance B," "readability agent," "vetting process," "this agent," "pipeline," or any description whose subject is how the vet was conducted rather than the model being vetted. These are process quality observations, not model findings. Discard them entirely.

Completion marker rows are written by Wave 2 agents as their final action to signal a clean run. They are metadata, not findings. Do not route, deduplicate, sort, or assign IDs to them — discard them entirely after noting their presence in your coverage declaration.

Read the Findings sheet in **50-row batches**: `A2:J51`, `A52:J101`, `A102:J151`, and so on in 50-row increments. **The MCP tool returns at most 50 rows per call — larger ranges silently truncate.** Continue until two consecutive batches return no non-empty rows.

**Do not stop after one empty batch.** Buffer zones between pre-allocated agent ranges produce empty batches in the middle of the sheet — data may resume after a gap. Stop only after two consecutive empty batches.

After each batch completes, write the line: `"Batch [N] (rows [start]–[end]): [X] non-empty rows found."` Do this before reading the next batch. If you proceed to processing without reading until two consecutive empty batches, you will silently miss findings — and GiveWell may act on an incomplete vet.

Read the Publication Readiness sheet the same way: `A2:F51`, `A52:F101`, `A102:F151`, continuing in 50-row increments until two consecutive batches return no non-empty rows.

Coverage declaration: "Read complete. Findings: [N] batches read, total non-empty rows: [N] ([X] divider rows, [Y] AGENT_COMPLETE markers, [Z] finding rows). Completion markers present for: [list agent names or 'none found']. Publication Readiness: [M] batches read, [M] total non-empty rows."

---

## Step 2 — Route misrouted rows

Check each row:
- Findings sheet rows whose **sole** issue is citation format, link permissions, terminology, labeling, or style (no model impact) → move to Publication Readiness.
- Findings sheet rows where **Estimated CE Impact (column H) is blank or "No CE impact"** AND the explanation describes only a documentation gap (missing source, missing cell note, missing label) → move to Publication Readiness. A finding that does not change CE and only recommends adding a note belongs in Publication Readiness regardless of how its Error Type is worded.
- Publication Readiness sheet rows that affect model outputs or interpretation → move to Findings.
- **Adjustment Issue and double-count findings always stay in Findings** — never route an `Adjustment Issue` finding to Publication Readiness on the basis of "No CE impact" or a blank CE impact column. Adjustment double-counts and scope errors are model-integrity issues by definition; their CE impact is often non-zero but hard to quantify at the time of filing. A blank CE impact column for an Adjustment Issue finding means the impact is unknown, not zero — leave it in Findings with "Direction unknown" in column H.
- When in doubt, leave in Findings.

**Column remapping when moving Findings → Publication Readiness**: The Findings sheet has 10 columns (A–J); the Publication Readiness sheet has exactly 6 (A–F). When moving a row, remap as follows — do not copy extra Findings columns into PR:
- PR A (Finding #): leave blank
- PR B (Sheet): = Findings B
- PR C (Cell/Row): = Findings C
- PR D (Error Type/Issue): = Findings E
- PR E (Explanation): = Findings F
- PR F (Recommended Fix): = Findings G

Do not write column G or beyond in Publication Readiness under any circumstances. There is no Status or Researcher judgment needed column in Publication Readiness.

**Routing audit — after all moves are complete**: Before writing the coverage declaration, perform three explicit spot-checks:

1. Scan all remaining Findings rows for any whose Error Type (column E) is `Missing Source`, `Broken Link`, `Permission Issue`, `Readability`, or `Terminology` AND whose Estimated CE Impact (column H) is blank or "No CE impact" — these are candidates that should have been moved to Publication Readiness. Move any found.
2. Scan all Publication Readiness rows for any whose Explanation (column E) describes a formula error, parameter mismatch, or value that affects CE — these belong in Findings. Move any found, writing all ten columns.
3. **Adjustment Issue audit**: Confirm zero `Adjustment Issue` rows remain in Publication Readiness. If any are found, move them to Findings unconditionally — adjustment scope errors are model-integrity issues regardless of whether their CE impact appears zero.

Coverage declaration: "Routing complete. [N] rows moved to Publication Readiness. [M] rows moved to Findings. Routing audit: [K] additional moves after spot-check. Adjustment Issue rows in PR after audit: 0. No other misrouted rows."

---

## Step 3 — Deduplicate

Scan all rows across both sheets for duplicates — rows where Cell/Row (column C) and Error Type/Issue (column E on Findings, column D on Publication Readiness) are substantively identical. Parallel Wave 2 agents cannot see each other's findings, so duplicates are most common between sources and readability (both check Notes columns) and between plausibility agents (both may flag the same cell).

When duplicates are found: keep the finding with the more complete Explanation and Recommended Fix; merge any unique detail from the other row into the surviving row's Explanation field. Do not merge near-duplicates that are complementary — a broken link and a stale value at the same cell are distinct issues and should both be kept.

**Root-cause / symptom consolidation** — after the standard duplicate pass, apply a second pass:

1. **Symptom absorbed by root cause**: If an `Inconsistency` finding and a `Structural Issue` or `Formula Error` finding both exist, AND the structural/formula finding's explanation identifies the formula-level cause of the discrepancy the `Inconsistency` finding describes, AND they reference overlapping or closely related cells: keep only the root-cause finding. Merge any output-level detail from the `Inconsistency` finding (e.g., "this causes X and Y to diverge by [amount]") into the root-cause finding's explanation if it adds specificity. Drop the `Inconsistency` finding. Rationale: fixing the root cause automatically resolves the symptom — a separate symptom finding adds no action item.

2. **Same-parameter multi-cell consolidation**: If two or more `Parameter Issue` findings reference **different** cells but describe the same parameter (matching parameter name in the explanation AND the same recommended replacement value), consolidate them into a single finding: list all affected cells comma-separated in column C, write a unified explanation noting each cell and its current value, and write a single recommended fix that covers all cells. Apply the higher severity if they differ. Drop all but the consolidated finding.

After this pass, write: "Semantic consolidation complete. [N] root-cause/symptom pairs consolidated. [M] same-parameter multi-cell groups consolidated."

**Synthesis false-positive guard**: After deduplication and consolidation, scan for any finding whose Explanation (column F) contains language suggesting it was assembled by combining signals from two agents rather than directly observed — phrases like "both instances flagged," "A noted X while B noted Y," "combining these observations suggests," or any claim at High/D severity that is not supported by a specific cell value read in FORMULA or FORMATTED_VALUE mode. For each such finding: (a) if you can verify the claim by calling `read_sheet_values` on the referenced cell — do so now, and either confirm the finding (retain at its severity) or downgrade it; (b) if the claim cannot be verified without reading the source spreadsheet — downgrade to Medium/H with Researcher judgment needed ✓ and add to the Explanation: "Synthesized from two partial agent observations — researcher to confirm before treating as confirmed error." Do not retain a High/D synthesized finding that was not directly verified. Rationale: the compaction agent in a prior vet elevated a Low observation to High/D by combining two partial signals, producing a false positive that the human vet did not catch — and which caused the researcher to distrust the adjacent real findings.

Coverage declaration: "Deduplication complete. [N] exact duplicates merged. [See semantic consolidation above.] Synthesis guard: [M] unverified High/D findings downgraded. No other duplicates found."

---

## Step 3.3 — Researcher-to-confirm audit

Count all rows with ✓ in column I. If the ✓ count exceeds 20% of all findings rows, apply the following triage pass before proceeding to Step 3.5.

For each ✓ row, ask: **can this question be answered by (a) reading another cell or formula in the spreadsheet, (b) checking a cited URL, or (c) applying standard GW methodology documented in key-parameters.md or GW guidance?** If yes to any of these, the ✓ mark should not have been filed — the agent had enough information to either confirm or dismiss the finding without researcher input.

Action for each ✓ row reviewed:
- If the question is answerable from the spreadsheet → remove the ✓ mark. If the finding is still valid, it remains as a confirmed finding. If the finding was only a hypothesis that the spreadsheet contradicts, remove the entire row.
- If the question genuinely requires the researcher to explain their analytical intent or confirm an assumption not determinable from the spreadsheet → retain ✓.
- If uncertain, retain ✓ but add a note in the Explanation: "Researcher to confirm — [specific question]."

Write: "Step 3.3 complete. ✓ findings before audit: [N]. ✓ marks removed (determinable from spreadsheet): [M]. Rows removed entirely: [K]. ✓ marks retained (genuine intent questions): [N-M-K]."

Skip this step (write "Step 3.3: skipped — ✓ count [N] is ≤20% of total findings [T]") when ✓ count / total findings ≤ 20%.

---

## Step 3.5 — Normalize category labels

Before rewriting, scan every row in memory and normalize the Error Type/Issue field to the exact standard label. Agents frequently append descriptive text after the label (e.g., "Permission Issue — internal document may need publish access" or "Readability — duplicate header"). Strip everything after the first recognized label word.

**Findings sheet column E** — replace any value that *starts with or contains* one of these labels with the label alone:
- `Formula Error` | `Parameter Issue` | `Adjustment Issue` | `Assumption Issue` | `Structural Issue` | `Inconsistency`

**Publication Readiness sheet column D** — replace any value that *starts with or contains* one of these labels with the label alone:
- `Missing Source` | `Broken Link` | `Permission Issue` | `Readability` | `Terminology`

If a value does not match any recognized label, keep it as-is and flag it in your coverage declaration so it can be reviewed.

Coverage declaration: "Label normalization complete. Findings: [N] labels normalized. Publication Readiness: [M] labels normalized. Unrecognized labels: [list or 'none']."

---

## Step 4 — Rewrite and sort both sheets

Rewrite both sheets sequentially from row 2, closing all gaps left by Wave 2's pre-allocated row ranges.

Sort all Findings rows in memory using four sort keys:
1. **Primary**: Severity (High → Medium → Low)
2. **Secondary**: Estimated CE Impact (column H) — within each severity tier, apply this order: numeric magnitude findings first (rows where column H contains a specific estimate, e.g., "Raises CE — 2.5x" or "Lowers CE — 1.3x"), then magnitude-unknown findings ("Raises CE — magnitude unknown", "Lowers CE — magnitude unknown"), then "Direction unknown", then "No CE impact", then blank
3. **Tertiary**: Error Type/Issue (column E, alphabetical)
4. **Quaternary**: Researcher judgment needed (column I) — within the same severity, CE impact tier, and error type, place findings WITHOUT ✓ before findings WITH ✓. Confirmed findings should appear before researcher-to-confirm items so reviewers encounter actionable findings first without having to skip over speculative ones.

Then rewrite the Findings sheet from row 2 with section dividers:
- Before the first High finding: divider row with column B = `─── High (N findings) ───`, all other columns blank.
- All High findings follow.
- Before the first Medium finding: `─── Medium (N findings) ───`.
- All Medium findings follow.
- Before the first Low finding: `─── Low (N findings) ───`.

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
