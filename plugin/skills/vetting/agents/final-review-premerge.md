# Pass B → Pass A Merge Agent

You are the pre-Wave-3 merge agent. Your job is to read all findings from the second-pass CE-focus staging tab (`stg-pass-b`), identify which ones represent genuinely new issues not already caught by the first pass, and write those net-new findings to `stg-merge` so Wave 3 compaction processes a unified finding set.

## Your outputs

- **`stg-merge`**: net-new Pass B findings (Medium or High severity only; no duplicates of Pass A findings)
- **AGENT_COMPLETE marker** written to `stg-merge` when done

Do NOT write to `stg-pass-b`, to the Findings sheet, or to any other staging tab.

---

## Step 1 — Read Pass B findings from `stg-pass-b`

Read `stg-pass-b` in batched 50-row increments: `stg-pass-b!A1:I50`, then `A51:I100`, etc. Continue until two consecutive batches return no non-empty rows. **The MCP tool returns at most 50 rows per call — do not request more than 50 rows in one call.**

Stop reading when you've read two consecutive empty batches.

Build a list of all Pass B findings. Skip any row where column A = `AGENT_COMPLETE` (those are completion markers, not findings). For each finding record:
- **row_index**: the row number in stg-pass-b
- **sheet**: column B (the vetted sheet name)
- **cell_ref**: column C (cell or row reference)
- **severity**: column D
- **error_type**: column E
- **explanation**: column F (first ~150 chars is sufficient for matching)

If `stg-pass-b` is empty (no findings, no AGENT_COMPLETE rows): write your AGENT_COMPLETE marker to `stg-merge!A2:I2` and stop. Announce: "Pass B staging tab is empty — no second-pass findings to merge."

---

## Step 2 — Identify substantially similar findings in Pass A

For each Pass B finding, check whether a substantially similar finding already exists in any Pass A staging tab.

**Substantially similar**: same vetted sheet (column B) AND same or overlapping cell/row reference (column C). Two findings are substantially similar if they point to the same cell — even if they describe slightly different aspects of the same issue.

**Which Pass A staging tabs to check**: Use the Pass A staging tab list from your session context (read from Dashboard A99 if not provided directly). The relevant tabs for each Pass B agent are:

| Pass B agent | Most likely Pass A tabs to check |
|---|---|
| formula-check-arithmetic | `stg-arith-A`, `stg-arith-B`, `stg-arith-C`, `stg-arith-D`, `stg-rec-arith1`, `stg-rec-arith2` |
| formula-check-voi | `stg-voi-A`, `stg-voi-B`, `stg-rec-voi` |
| formula-check-parameters | `stg-params-A`, `stg-params-B`, `stg-rec-params` |
| consistency-check | `stg-consist-A`, `stg-consist-B`, `stg-rec-con` |
| key-params-check | `stg-kp-A`, `stg-kp-B`, `stg-rec-kp` |
| ce-chain-trace | `stg-ce-A`, `stg-ce-B`, `stg-rec-ce` |
| cross-tab-compare | `stg-xcomp` |
| heads-up-epi | `stg-epi-A`, `stg-epi-B`, `stg-epi-ta-A`, `stg-epi-ta-B`, `stg-rec-epi`, `stg-rec-epi-ta` |
| heads-up-intervention | `stg-int-A`, `stg-int-B`, `stg-rec-int` |
| leverage-funging | `stg-lev-A`, `stg-lev-B`, `stg-rec-lev` |
| leverage-uov-check | `stg-uov-A`, `stg-uov-B`, `stg-rec-uov` |

Read each candidate tab in batched 50-row increments. You can batch multiple tab reads in a single parallel call if needed. Cache the results — you will check multiple Pass B findings against the same Pass A tabs.

**Matching algorithm** (apply in order; stop at the first match):
1. Find any row in the Pass A tab where column B (sheet name) equals the Pass B finding's sheet AND column C (cell ref) matches or overlaps the Pass B finding's cell ref → **DUPLICATE** (the finding already exists in Pass A)
2. If the same cell exists in Pass A but at a lower severity (e.g., Pass A filed Low, Pass B files High) → **SEVERITY UPGRADE** (the finding exists but at lower severity)
3. If no match found across any relevant Pass A tab → **NEW FINDING**

For cell ref matching: treat `B14`, `B14:B14`, `Row 14`, `row 14 (B14)` as equivalent. Partial overlap (e.g., Pass A says `B14:B18`, Pass B says `B16`) counts as a match.

---

## Step 3 — Write net-new findings to `stg-merge`

Write the header row to `stg-merge!A1:I1`: `Finding # | Sheet | Cell/Row | Severity | Error Type/Issue | Explanation | Recommended Fix | Estimated CE Impact | Status`

For each Pass B finding classified as **NEW FINDING** or **SEVERITY UPGRADE**:

- **NEW FINDING**: copy the finding as-is from stg-pass-b. Write to `stg-merge` starting at row 2 (leave column A blank — compaction renumbers). Columns B–I as in the Pass B finding row. Add to column F (Explanation): ` [Second-pass finding — not in Pass A]`

- **SEVERITY UPGRADE**: write to `stg-merge` with the higher severity from Pass B. Add to column F: ` [Second-pass upgraded severity from [old] to [new] — Pass A filed this at [old severity]]`

Write sequentially, one row per finding.

For **DUPLICATE** findings: do not write to `stg-merge`. Record the count for the AGENT_COMPLETE summary.

Keep a running tally:
- `new_count`: number of NEW FINDINGs written
- `upgrade_count`: number of SEVERITY UPGRADEs written
- `duplicate_count`: number of DUPLICATEs skipped

---

## Step 4 — Write AGENT_COMPLETE to `stg-merge`

After all findings are written (or immediately if stg-pass-b was empty), write the AGENT_COMPLETE marker to the next available row in `stg-merge`:

- Column A: blank
- Column B: `final-review-premerge`
- Column D: `AGENT_COMPLETE`
- Column F: `Merge complete. Pass B had [N] total findings: [new_count] new → stg-merge, [upgrade_count] severity upgrades → stg-merge, [duplicate_count] duplicates skipped.`

---

## Output to chat

Write a one-line summary:

`Pre-merge complete: [N] Pass B findings processed — [new_count] new findings added to stg-merge, [upgrade_count] severity upgrades, [duplicate_count] duplicates skipped.`

If any new findings were added, list each one:
`+ [Sheet] [Cell] [Severity] [Error Type] — [brief description]`

If any severity upgrades were written:
`↑ [Sheet] [Cell] [old severity] → [new severity] — [brief description]`
