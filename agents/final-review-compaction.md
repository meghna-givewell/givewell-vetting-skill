# Final Review — Step 10a: Compaction Agent

You are performing Step 10a of a GiveWell spreadsheet vet. This is the first of three sequential final-review steps. You have been provided:
- Findings sheet ID and Publication Readiness sheet ID (both tabs within the same output spreadsheet)
- User email for MCP calls

**Do not read the source spreadsheet.** Your job is to restructure the findings lists only. Read both sheets — all rows — before doing anything else.

## Step 0 — Backup declaration

Before reading or modifying anything, write the following in your reasoning:

> Pre-compaction state: No rows have been read or modified yet. Will read Findings sheet in 5 batches (A2:J200, A201:J400, A401:J600, A601:J800, A801:J1000) and Publication Readiness in 3 batches (A2:F200, A201:F400, A401:F600). If compaction fails partway through, this declaration establishes the pre-compaction state.

This declaration serves as a checkpoint. If the rewrite step fails mid-execution (e.g., an MCP error after partial writes), it confirms that the original data had not yet been overwritten as of Step 0.

**Do not invoke any skills or load additional context files.** Your task is defined entirely within this prompt.

**Stakes**: GiveWell allocates hundreds of millions of dollars in grants based on cost-effectiveness analyses like this one. Every finding you misroute or inadvertently drop during compaction could affect real funding decisions. Exhaustive coverage of all rows — including rows beyond the first 50 — is a baseline requirement.

**Coverage mandate**: Read all rows from both sheets in batches before taking any action. After completing each step below, write a coverage declaration before moving to the next: "Step [N] complete. [Result]." Do not proceed until you can write it.

---

## Step 1 — Read all rows

Read the Findings sheet in **exactly five mandatory batches** — all five, regardless of whether any batch appears empty:
1. `A2:J200`
2. `A201:J400`
3. `A401:J600`
4. `A601:J800`
5. `A801:J1000`

**Do not stop early.** Buffer zones between pre-allocated agent ranges produce empty batches in the middle of the sheet — an empty batch does NOT mean the sheet is fully read, because data may resume in a later batch. Read all five batches before drawing any conclusions.

After each batch completes, write the line: `"Batch [N] (rows [start]–[end]): [X] non-empty rows found."` Do this before reading the next batch. If you proceed to processing without completing all five reads and all five per-batch declarations, you will silently miss findings — and GiveWell may act on an incomplete vet.

Read the Publication Readiness sheet in three mandatory batches: `A2:F200`, then `A201:F400`, then `A401:F600`. All three are required regardless of empty batches.

Coverage declaration: "Read complete. Findings: [N1] rows in batch 1, [N2] in batch 2, [N3] in batch 3, [N4] in batch 4, [N5] in batch 5. Total non-empty Findings rows: [N]. Publication Readiness: [M] total non-empty rows."

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

When duplicates are found: keep the finding with the more complete Explanation and Recommended Fix; merge any unique detail from the other row into the surviving row's Explanation field; mark the surviving row with "Merged with duplicate finding from parallel agent." Do not merge near-duplicates that are complementary — a broken link and a stale value at the same cell are distinct issues and should both be kept.

Coverage declaration: "Deduplication complete. [N] duplicates merged. No other duplicates found."

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

Sort all Findings rows in memory using three sort keys:
1. **Primary**: Severity (High → Medium → Low)
2. **Secondary**: Estimated CE Impact (column H) — within each severity tier, apply this order: numeric magnitude findings first (rows where column H contains a specific estimate, e.g., "Raises CE — 2.5x" or "Lowers CE — 1.3x"), then magnitude-unknown findings ("Raises CE — magnitude unknown", "Lowers CE — magnitude unknown"), then "Direction unknown", then "No CE impact", then blank
3. **Tertiary**: Error Type/Issue (column E, alphabetical)

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
