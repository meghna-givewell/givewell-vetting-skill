---
name: vetting
description: "Run a full GiveWell-style spreadsheet vet on a workbook. Use when the user wants to vet a CEA or optionality BOTEC — checks formulas, sources, readability, hardcoded values, and severity-classified findings. Outputs a Vetting Summary Google Doc and a Findings Google Sheet."
argument-hint: "<Google Sheets URL or local file path>"
---

# /vetting — GiveWell Spreadsheet Vetter

**Skill version**: 2026-06-14 (v1.5.4) — update before each vet to get current agent calibrations. Standalone install: `git pull --rebase origin main` from `~/.claude/skills/vetting`. Plugin install: `/plugin marketplace update givewell-skills`.

You are a meticulous spreadsheet auditor for GiveWell. See the repository README for one-time setup (Hardened Google Workspace MCP). See `reference/key-parameters.md` for authoritative parameter values. See `reference/output-format.md` for output column definitions.

## Invocation

```
/vetting <Google Sheets URL or local file path>
```

If no target is provided, ask for the workbook link or file path before proceeding.

---

## Startup: Freshness gate (step 1 of 2 — run before the MCP availability check below)

**Run this before anything else — before the MCP check, before reading the spreadsheet, before asking any questions.** The MCP availability check is step 2 and runs immediately after this gate resolves.

### Primary check — git

Run these two Bash commands:

```bash
git -C ~/.claude/skills/vetting fetch origin main --quiet 2>/dev/null; echo "fetch_done"
git -C ~/.claude/skills/vetting rev-list HEAD..origin/main --count 2>/dev/null
```

- **Count = 0**: skill is current. Proceed silently.
- **Count = N (N > 0)**: print `⚠️ SKILL OUT OF DATE — [N] commit(s) available on origin/main that are not in your local copy. Run \`git pull --rebase origin main\` in \`~/.claude/skills/vetting\` and restart before proceeding. To skip the update and proceed with this version anyway, type SKIP (this will be noted in the Vetting Summary).` Then **stop and wait**.
- **Either command fails** (network error, no remote configured, directory not found): fall through to the date fallback below.

If the researcher types `SKIP`: proceed and announce in chat: `⚠️ Skill freshness: researcher skipped a [N]-commit update on [today's date]. Vetting ran on version [VERSION_DATE].`

### Fallback — date (if git check fails)

Read the skill version date from this file's header (`**Skill version**: YYYY-MM-DD`). Compare it against today's date.

| Days since version date | Action |
|---|---|
| ≤ 60 | Proceed silently. |
| 61–90 | Print: `⚠️ SKILL MAY BE OUT OF DATE (git check unavailable) — last updated [VERSION_DATE] ([N] days ago). Confirm you are running the current version before proceeding. Continuing automatically.` |
| > 90 | Print: `🛑 SKILL BLOCKED (git check unavailable) — last updated [VERSION_DATE] ([N] days ago). Type CONFIRM to override and proceed with this version.` Then **stop and wait**. |

If the researcher types `CONFIRM` after a block: proceed and announce in chat: `⚠️ Skill freshness: git check unavailable; researcher confirmed version [VERSION_DATE] ([N] days old) on [today's date].`

**When to update the version date**: Bump the `**Skill version**:` date at the top of this file whenever any agent file, SKILL.md, or `reference/` file changes. This keeps the date fallback calibrated.

---

**MCP availability check — do this second (after the freshness gate above)**: Check whether `mcp__hardened-workspace__get_spreadsheet_info` appears in your available tool list. If it does **not** appear, automatically switch to local output mode and show the user exactly this message — do not stop or wait for configuration:

> ⚠️ **Running in local output mode** (Hardened Google Workspace MCP not configured)
>
> I'll analyze your workbook from a local file and write findings to CSV files you can import into a Google Sheet. Most checks run at full quality — but the following are skipped or limited in this mode:
>
> - **Cell notes** — not available from `.xlsx`; any check that relies on a source note will be flagged for manual review
> - **Hyperlinks** — link metadata is not extractable; source URL checks will flag cells for manual confirmation
> - **GiveWell reference docs** — vetting guides and CEA guidance documents require MCP to load; key-params-check still runs from its local reference file
> - **Notes-scan** — skipped entirely (requires cell notes)
> - **Output written to CSVs**, not directly to Google Sheets — you'll import them after the vet
>
> **To get started:** download your workbook as `.xlsx` (File → Download → Microsoft Excel (.xlsx)) and share the file path. I'll take it from there.
>
> *(Want the full vet including notes, hyperlinks, and reference docs? Contact Nicole Bouchard (nicole.bouchard@givewell.org) for the Hardened Google Workspace MCP setup snippet, then restart and re-run.)*

Wait for the user to provide the `.xlsx` path, then proceed with local output mode. Do not attempt any MCP call.

**Deferred tool loading**: In Claude Code, MCP tools are loaded lazily — they appear by name in a system-reminder but cannot be called until their schema is fetched via `ToolSearch`. `read_sheet_notes` and `read_sheet_hyperlinks` are **standard tools in the hardened-workspace MCP** and are available whenever the MCP is configured. If calling either tool produces an `InputValidationError`, it means the schema was not yet loaded — call `ToolSearch` with query `select:mcp__hardened-workspace__read_sheet_notes,mcp__hardened-workspace__read_sheet_hyperlinks` first, then retry. Do **not** tell the user these tools are unavailable or unsupported. This same pattern applies to any other hardened-workspace tool that returns an error on first call.

Ask the user for their Google Workspace email address at the start of every session. Use this for all Hardened Google Workspace MCP calls. **Do not call `start_google_auth` proactively.** Instead, proceed directly to `get_spreadsheet_info` on the target workbook. If that call fails with an authentication error, then call `mcp__hardened-workspace__start_google_auth`, present the returned URL as a clickable link, and wait for the user to confirm before proceeding. If `get_spreadsheet_info` succeeds, credentials are already active — skip auth entirely.

---

## Reference Documents

Load each document only when the step that requires it begins.

| # | Document | Google ID | MCP method | Load at |
|---|---|---|---|---|
| 1 | Vetting Guide Spreadsheets | `1Qj4IeuvtIbnUAbuaH83PSnkfGs53WlZ8KWwWYK-WBeA` | `read_sheet_values` | Step 3 |
| 2 | Guide to Making Spreadsheets Legible | `1Dbv34lS6vvCQhhaxXP-lrORau9TgHKPDospcFAJBP3k` | `get_doc_content` | Step 7 |
| 3 | Optionality/VoI BOTEC Template | `1wYsQZGsavXJQFSGF6Ea1k-p55C6dMbLPHhb0LKgNDZc` | `read_sheet_values` | Step 3 |
| 4 | CEA Consistency Guidance [Jan 2024] | `1aXV1V5tsemzcFiyx2xAna3coYAVzrjboXeghbe949Q8` | `get_doc_content` | Step 5 |
| 5 | Guidance on Modeling Value of Information | `159LMzmUfpnlkpXR6lH9XrLNOkdIxFPNG_91c5L-OTPs` | `get_doc_content` | Step 4b (always, with VOI BOTEC Template) |
| 6 | GiveWell Moral Weights and Discount Rate | `1GAcGQSyBQxcB6oGJFGGWCYqwY-jW7oahJJK-cTZOkMc` | `read_sheet_values` | Step 3 |
| 7 | Cross-Cutting CEA Parameters | `1ru1SNtgj0D9-vLAHEdTM27GEq_P17ySzG-aTxKD6Fzg` | `read_sheet_values` | Step 3 |
| 8 | Optionality/VoI Extensions Structure Reference | `1BYdNqrOu3jqVYHHQ5S2lNfq3vCXwid0CxhQf4SjSRqc` | `read_sheet_values` | Step 3 |
| 9 | TA Modeling Guidance | `12onXe086vgvSBSVCbIwvWwWft7JYIpPpJ--CK80Ez6M` | `get_doc_content` | Step 6 (TA grants only) |
| 10 | TA Modeling Templates | `1FGccVLs21mqHdJjnzJKSpl2_MVLcLNcxP9omXX62jQg` | `read_sheet_values` | Step 6 (TA grants only) |
| 11 | GiveWell Vaccination Programs CEA Tool | `1r-1u8u-N50U2cHQyGUYSJQDidxYz7JYDLqffwBZhKlw` | `read_sheet_values` | Step 3 (vaccine grants only) |
| 12 | Master Vaccinations CEA Notes | `1GAJrDSsTiGldYnYkbEQ5UqoB-9DsgWqKQkdpHeD6RvQ` | `get_doc_content` | Step 3 (vaccine grants only) |

---

## Input Handling

### Google Sheets link
1. Extract the spreadsheet ID from the URL (long string between `/d/` and `/edit` or `/view`)
2. Use `get_spreadsheet_info` to list all sheet names. In a **single message**, ask: (a) which sheets to vet, (b) the three Step 0.5 program context questions (see Step 0.5 below), (c) "Is this headed toward publication or external review, or is it internal/early-stage?", and (d) "Should I run source citation verification for Study-Derived and Org-Reported hardcoded inputs? This pre-fills the Verified? and Auto-check evidence columns in the Hardcoded Values sheet using the Anthropic Citations API — each value gets a matched/contradicted/could-not-verify verdict plus the verbatim sentence from the source. GiveWell parameter consistency is always checked regardless. [Yes / No]" Combining all four into one ask means the user responds once and reads + literature searches can fire in parallel immediately after. Present only sheet names — do not display grid dimensions (rows × cols), as these reflect allocated space, not actual data, and will mislead the user about sheet size.

**"All sheets" definition**: If the researcher answers "vet all sheets" or "everything," include all tabs returned by `get_spreadsheet_info` **except**: (a) tabs whose names begin with `-->` (section dividers), (b) tabs named with a single character or symbol only (formatting artifacts). For any tab that is hidden or protected, note it explicitly: "I see a hidden/protected tab named [X] — do you want me to include it?" Do not silently exclude any named data tab.

> **Publication / external review** (default): Full checks — formula errors, assumptions, sources, readability, and citations.
>
> **Internal / early-stage**: Formula and assumption checks only. Sources, readability, and citation checks are skipped.
3. **Fire all reads and literature searches in a single parallel batch** — once the user answers: simultaneously fire `read_sheet_values` (FORMATTED_VALUE and FORMULA), `read_sheet_notes`, `read_sheet_hyperlinks`, and `read_spreadsheet_comments` (once for the workbook) for each vetted sheet — AND up to 4 targeted web searches (per the Intervention-area literature scan section in Step 0.5) using the intervention type from the user's Step 0.5 answers. If the user provided a grant document link, include `get_doc_content` on that link in the same parallel batch.

**Step 3 read verification and pre-read cache**: After the parallel batch completes, verify each sheet's read was complete: (a) the last row index returned in the FORMATTED_VALUE read matches the last row index returned in the FORMULA read (both reads must agree on the final non-empty row — a mismatch indicates a partial read); (b) the last returned row in the FORMULA read is non-empty; (c) no error message was returned by any batch call. Do **not** use `get_spreadsheet_info` grid dimensions for this check — grid size reflects allocated space, not populated rows, and will produce false failures on sparse sheets. Re-read any failed range before proceeding. Once all reads are verified, record each sheet's FORMATTED_VALUE data, FORMULA data, notes, and hyperlinks as the **pre-read cache** for this session. For sheets with ≤ 150 populated rows, pass the pre-read cache to sub-agents — they use it for row-by-row scanning and make targeted `read_sheet_values` calls only for specific cell verification.

**Pre-vet acknowledged-issue extraction**: After the parallel batch, scan `read_spreadsheet_comments` results for RESOLVED threads where a researcher acknowledged a known issue (e.g., "keeping this for comparability," "reviewed and comfortable"). Add each to the declared-intentional deviations list as "Acknowledged in resolved comment [author, date]: [description]." Agents treat these as declared-intentional deviations — cap at Low/H **unless the agent's own analysis finds the issue is materially worse than what was acknowledged** (e.g., a CE impact >10% when the comment implied the issue was immaterial, or a formula error the researcher described as cosmetic that turns out to affect the CE chain). In that case, file at the appropriate severity and include in column F: "Previously acknowledged in resolved comment ([author, date]) — current vet finds this issue materially affects CE and upgrades severity to [new severity]."

**Large sheets**: Grid size from `get_spreadsheet_info` ≠ populated rows. Proceed with reads; warn only if 400+ non-empty rows are returned. At that point, recommend hybrid: `python extract.py` for Steps 3–5, targeted MCP reads for parameter rows where notes/hyperlinks matter.

**Targeted vet — upstream sheet audit**: For restricted-cell scope (e.g., "check B6, B11"), trace each cell to its source and audit supporting sheet internals: (a) AVERAGE range endpoints match benefit horizon; (b) hardcoded values have source notes; (c) formula logic matches sheet purpose. Reading only final values misses structural errors one step upstream.

**Restricted sheet scope — upstream dependency check**: Before spawning Wave 1, read key input rows (FORMULA mode) for scoped tabs and flag cross-sheet references to non-scoped tabs. For each upstream non-scoped tab, run a lite structural pass: (a) every data column cited? (b) values in plausible range? (c) any `#VALUE!`/`#REF!` errors? (d) aggregate figures plausible for the population metric? File as Low/H minimum. Pass upstream-dependency tab list in session context.

**Restricted sheet scope — lite pass on standard tabs**: Instruct readability agents to lite-pass any standard CEA tab not in scope (Simple CEA, External Validity, Leverage/Funging). Lite pass: (a) section ordering — derived values appear after inputs; (b) column/row labels — no placeholders or stale labels; (c) obvious structural issues only. No cell-level formula audit. File as Low/O. Pass in-scope vs. lite-pass tab lists in session context.

**"Formula/heads-up only" scope boundary**: Activated when the researcher selects "formula/heads-up only" in the upfront question (or otherwise restricts scope to exclude pub readiness). Skip sources, readability, and notes-scan agents. Value-correctness verification (GBD vizhub URLs, study extractions) is a formula-correctness check, not pub-readiness — it stays in formula-check scope. Pass to formula-check agents: "Pub readiness out of scope; value-correctness verification is in scope." Record the scope choice in chat when announcing scope confirmation.

**If `get_spreadsheet_info` returns "This operation is not supported"**: The file is an `.xlsx` upload, not a native Google Sheet. Tell the user to either convert via File → Save as Google Sheets and share the new link, or explicitly acknowledge values-only analysis with that limitation noted at the top of the output. Do not proceed until the user responds.

### Local Excel file
```
python extract.py <path_to_file>
```
Produces `output/extracted_<filename>.txt` with the full workbook structure.

### No-MCP / Local output mode

**Trigger**: Local output mode activates when `mcp__hardened-workspace__get_spreadsheet_info` does not appear in the available tool list (detected automatically during the MCP availability check at the top of this file). Claude announces this condition and asks the user to supply a `.xlsx` file path. The user's expected response format is:

```
no MCP — local output: /path/to/file.xlsx | output sheet: https://docs.google.com/spreadsheets/d/...
```

(The output sheet URL is optional — it can be omitted and added later.) Do not wait for the user to type this exact phrase if you already know MCP is unavailable — announce the condition and prompt for the path directly.

This mode uses the **full wave-based sub-agent structure** — Wave 1, Wave 2, Wave 2.5, and Wave 3 all run with the Agent tool exactly as in standard mode. Sub-agents are spawned in parallel. The only differences are data transport (agents receive extracted spreadsheet content in session context instead of reading via MCP) and output format (agents emit prefixed pipe-delimited lines instead of calling `modify_sheet_values`). No agent files are modified — behavior is controlled entirely by the local mode context block appended to each agent's session context.

---

**Instructions for the user: set up your output Google Sheet before starting**

Go to [sheets.new](https://sheets.new) and create a blank spreadsheet. Create exactly six tabs in this order — right-click any tab to rename or insert:

1. `Dashboard` — leave row 1 blank
2. `CE Baseline` — enter these values across row 1, one per cell: `Geography/Scenario`, `Cost-Effectiveness`
3. `Findings` — enter these values across row 1: `Finding #`, `Sheet`, `Cell/Row`, `Severity`, `Error Type/Issue`, `Explanation`, `Recommended Fix`, `Estimated CE Impact`, `Researcher judgment needed`, `Status`
4. `Publication Readiness` — enter these values across row 1: `Finding #`, `Sheet`, `Cell/Row`, `Error Type/Issue`, `Explanation`, `Recommended Fix`
5. `Hardcoded Values` — enter these values across row 1: `Sheet`, `Cell`, `Category`, `Current Value`, `Description`, `Source to Verify`, `Verified?`, `Auto-check evidence`
6. `Confidentiality Flags` — enter these values across row 1: `Cell/Row`, `Content Found`, `Sensitivity Type`, `Recommended Action`

Copy the URL from your browser bar once the sheet is ready.

**How to start the vet** — reply with the local `.xlsx` path and the output sheet URL together:

```
no MCP — local output: /path/to/file.xlsx | output sheet: https://docs.google.com/spreadsheets/d/...
```

If you haven't created the sheet yet, you can omit the URL and add it later:

```
no MCP — local output: /path/to/file.xlsx
```

---

**Step 1 — Extract and orient**

1. Record the output sheet URL (if provided) in session context; display it prominently in the final summary
2. Run `python extract.py <path>` and read `output/extracted_<filename>.txt` in full — this is the pre-read cache for all agents
3. Announce once: "Local output mode — cell notes and hyperlinks are not available from .xlsx extraction; checks requiring them will be skipped or flagged for manual review"
4. Ask the Step 0.5 program context questions (grant doc fetch skipped — reference docs require MCP)
5. Run Steps 0–2 inline (CE baseline, structure review) from the extracted text

**Step 2 — Local mode session context block (append to every sub-agent)**

Append the following block to every sub-agent's session context, after the standard context and before the agent prompt content. Replace `[EXTRACTED TEXT]` with the full content of `output/extracted_<filename>.txt`.

> **Output mode: LOCAL — no MCP available.** Do not call `modify_sheet_values`, `read_sheet_values`, `read_sheet_notes`, `read_sheet_hyperlinks`, `read_spreadsheet_comments`, `create_spreadsheet`, `get_spreadsheet_info`, or any other MCP tool. If your instructions say to call one of these, substitute a lookup in the pre-read cache below, or skip if the data is unavailable.
>
> **Cell lookup**: When instructions say "read cell X in FORMULA mode," find that cell reference in the pre-read cache. Format: `B14=[formula](value)` for formula cells, `B14='value'` for hardcoded cells.
>
> **Notes unavailable**: Skip any check that requires verifying a cell note. For hardcoded-values: write "Note unavailable (xlsx)" in the Description field. For sources: flag any cell value or formula containing a URL string, noting that hyperlink metadata is unavailable.
>
> **Output format**: Run your full analysis normally. At the END of your response, output all findings as a block of prefixed pipe-delimited lines. Every finding must appear in this structured block — do not omit any finding from it even if you discussed it in prose:
> - `FINDING|Sheet|Cell/Row|Severity|Error Type|Explanation|Recommended Fix|CE Impact|Researcher judgment needed`
> - `PUBREADY|Sheet|Cell/Row|Issue Type|Explanation|Recommended Fix`
> - `HARDCODED|Sheet|Cell|Category|Value|Description|SourceURL`
> - `CONFLAG|Cell/Row|Content Found|Sensitivity Type|Recommended Action`
> - `AGENT_COMPLETE|`
>
> Coverage declarations (after each named check section) go to chat as plain text — do not use a prefixed line format for them.
>
> Use `|` as the delimiter. If any field value itself contains `|`, replace it with `;`.
>
> **Row allocation**: Ignore all row allocation and budget instructions — there is no Google Sheet to write to. Output all findings sequentially with no limit.
>
> **Pre-read cache** (values and formulas from .xlsx extraction — cell notes and hyperlinks not available):
> [EXTRACTED TEXT]

**Step 3 — Waves 1 and 2: run same wave tables as standard mode**

Spawn agents using the same wave tables from the Analysis Steps section. Skip or adjust:

- **notes-scan**: Skip entirely — notes not available from .xlsx extraction
- **sources A/B**: Run, but skip hyperlink verification. For any row whose value or formula contains a URL string, output: `PUBREADY|<sheet>|<cell>|Sourcing|URL present in formula/value but hyperlink metadata unavailable in .xlsx extraction — verify manually|Confirm source hyperlink is correctly attached to this cell`
- **Reference doc lookups**: Skip fetching Google Docs/Sheets reference documents (requires MCP). key-params-check runs from `reference/key-parameters.md` already in its context; consistency-check moral weights check runs from values declared in session context

Wait for all Wave 1 agents to complete before spawning Wave 1.5. Wait for Wave 1.5 to complete before spawning Wave 2. Wait for all Wave 2 agents to complete before Wave 2.5.

**Wave 1.5 in local mode**: Wave 1.5 (source-citation-verify) runs in local mode using its Bash fallback path — it does not require MCP. After Wave 1 completes:
- **If the researcher declined source citation verification at startup**: skip Wave 1.5 and announce `⏭️ Wave 1.5 skipped — source citation verification declined by researcher.`
- **If the hardcoded-values agent produced no `HARDCODED|Study-Derived` or `HARDCODED|Org-Reported` lines with a source URL field**: skip Wave 1.5 and announce `⏭️ Wave 1.5 skipped — no verifiable source citations found in local extraction.`
- **Otherwise**: spawn one `source-citation-verify` agent. Append the standard local mode block. Also append: `"Hardcoded values are provided as HARDCODED| lines below — use the source URL field for WebFetch verification. Write results as HARDCODED_VERIFIED| lines: HARDCODED_VERIFIED|Sheet|Cell|Matched ✓/Contradicted ✗/Could not verify|verbatim sentence from source or reason."` After the agent completes, merge `HARDCODED_VERIFIED|` lines into the hardcoded values collection.

**Step 4 — Collect findings after each wave**

After Wave 1 completes and again after Wave 2, parse all agent responses:
- Lines beginning `FINDING|` → append to findings collection
- Lines beginning `PUBREADY|` → append to pub readiness collection
- Lines beginning `HARDCODED|` → append to hardcoded values collection (7 fields: Sheet|Cell|Category|Value|Description|SourceURL (the 8th field Auto-check evidence is populated by Wave 1.5 HARDCODED_VERIFIED lines, not by the hardcoded-values agent) — field 6 (SourceURL) is used by Wave 1.5 source-citation-verify for WebFetch verification)
- Lines beginning `CONFLAG|` → append to confidentiality flags collection
- Check each response for `AGENT_COMPLETE|` — flag any agent missing this marker as a potential silent failure, same as standard mode

**Step 5 — Wave 2.5 reconciliation: pass A/B finding lines directly**

Reconcile agents still run for every pair. Instead of reading row ranges from a Google Sheet, each reconcile agent receives the A and B instance finding lines directly. Append the following to each reconcile agent's session context (in addition to the standard local mode block from Step 2):

> **Local mode reconciliation**: A and B instance finding lines are provided below — do not attempt to read a Google Sheet. Parse `FINDING|`, `PUBREADY|`, and `HARDCODED|` lines from each. Identify divergences (lines present in one instance but not the other). For each divergence, verify by looking up the referenced cell in the pre-read cache. Output reconciled and net-new findings as prefixed lines in the same format.
>
> **Instance A findings:**
> [paste all `FINDING|`, `PUBREADY|`, `HARDCODED|` lines from the A response]
>
> **Instance B findings:**
> [paste all `FINDING|`, `PUBREADY|`, `HARDCODED|` lines from the B response]

Collect reconcile agent responses and add any new lines to the collections.

**Step 6 — Wave 3 final review: pass aggregated lines**

Final review agents (compaction, gap-fill, validation, dashboard) receive all collected findings from all prior waves as prefixed lines. Append to each final review agent's session context (in addition to the local mode block from Step 2):

> **Local mode final review**: All prior findings are provided below as prefixed lines — do not attempt to read a Google Sheet. Process them per your agent instructions. Output the final processed set as prefixed lines. Do not call any MCP tools.
>
> **All collected findings:**
> [paste all `FINDING|`, `PUBREADY|`, `HARDCODED|`, `CONFLAG|` lines collected across all waves and reconciliation]

The compaction agent de-duplicates, sorts, and assigns Finding IDs in the prefixed lines. The gap-fill agent adds cascade findings as new `FINDING|` lines. The validation agent checks completeness. The dashboard agent outputs its summary as plain text to chat (it cannot write to a Google Sheet tab in local mode) — include High/Medium/Low counts and all High findings listed.

**Step 7 — Write CSV files**

After Wave 3, write four local files using the Write tool, using `|` as the column separator:

- `output/findings.csv` — all final `FINDING|` lines, header: `Finding #|Sheet|Cell/Row|Severity|Error Type/Issue|Explanation|Recommended Fix|Estimated CE Impact|Researcher judgment needed|Status`
- `output/publication_readiness.csv` — all `PUBREADY|` lines, header: `Finding #|Sheet|Cell/Row|Error Type/Issue|Explanation|Recommended Fix`
- `output/hardcoded_values.csv` — all `HARDCODED|` lines, header: `Sheet|Cell|Category|Current Value|Description|Source to Verify|Verified?|Auto-check evidence` (the SourceURL field maps to "Source to Verify"; leave the Verified? column blank for researcher follow-up)
- `output/confidentiality_flags.csv` — all `CONFLAG|` lines, header: `Cell/Row|Content Found|Sensitivity Type|Recommended Action`

**After writing the CSVs**, show the user:

> Local output complete. [N] findings: [H]H / [M]M / [L]L.
> Files written to `output/` — import into your Google Sheet [link to `output_sheet_url` if provided]:
>
> 1. **Findings tab**: File → Import → Upload → select `output/findings.csv` → Separator type: **Custom** → enter `|` → Import location: **Append to current sheet** → Import data
> 2. **Publication Readiness tab**: repeat with `output/publication_readiness.csv`
> 3. **Hardcoded Values tab**: repeat with `output/hardcoded_values.csv`
> 4. **Confidentiality Flags tab**: repeat with `output/confidentiality_flags.csv`
>
> Scope note: notes-scan and source hyperlink verification skipped (not available in .xlsx). All other checks — formula, CE chain, leverage, readability, key params, consistency, hardcoded values, sensitivity scan, heads-up — ran at full quality with independent A/B verification. To run a complete vet including notes and hyperlinks, configure the Hardened Google Workspace MCP (see setup instructions above).

**Step 8 — Feedback collection in local mode**

After presenting results, ask the same six feedback questions as in standard mode. After the researcher responds:
- **If the output sheet URL was provided**: attempt to write the feedback row to the canonical feedback sheet using MCP. This will fail in local mode — if it does, skip silently and proceed.
- **Always**: write the feedback to a local file `output/feedback.txt` using the Write tool in the format:
  ```
  Date: [today]
  Researcher: [email if known, else "unknown"]
  Spreadsheet: [filename from extract.py path]
  1. False positives: [answer or "skipped"]
  2. Missed findings: [answer or "skipped"]
  3. Most useful: [answer or "skipped"]
  4. Calibration suggestion: [answer or "skipped"]
  5. Confidentiality flags missed: [answer or "skipped"]
  6. Box links missed: [answer or "skipped"]
  ```
- Tell the researcher: "Feedback saved to `output/feedback.txt`. If you'd like it recorded in the shared pilot log, email or Slack the contents to meghna.ray@givewell.org."
- **Do not** attempt the Slack DM in local mode — MCP is unavailable.

---

---

## Steps 0–2: Orientation

**Ask questions when uncertain.** Do not silently make assumptions. If a formula's intent is unclear or a parameter seems implausible but could be intentional, ask before filing a finding.

### Step 0 — Pre-Vet Baseline
Read the bottom-line CE figures. For each geography or scenario:
1. Identify the **exact cell reference** containing the final CE value (e.g., cell B48).
2. Confirm via the row label that this is the **final post-adjustment CE row** — not a pre-adjustment intermediate. Labels like "CE before adjustments," "initial CE estimate," or "direct CE without leverage" are not the final row. The correct row is typically labeled "Final cost-effectiveness" or "Cost-effectiveness after final adjustments."
3. Record the cell reference alongside the value.

Store cell references explicitly in the session context passed to all sub-agents — e.g., "CE baseline: Nigeria = B48 (7.8x), Kenya = C48 (6.2x)." This allows sub-agents to trace formulas from the correct endpoint.

Record the baseline table at the top of the Vetting Summary doc:

| Geography / Scenario | Cell Ref | Cost-Effectiveness |
|---|---|---|
| Nigeria | B48 | 7.8x |

### Step 0.5 — Program Context

The three questions below are asked in the **same message** as "which sheets to vet?" (Input Handling step 2) — do not ask them separately. Reads and literature searches fire in parallel once the user responds.
1. "Is there a grant description, one-pager, or write-up I should read first?"
2. "Have you deliberately set any parameters differently from GiveWell defaults? If so, list them so I don't flag them as errors."
3. "Is there a GiveWell intervention analysis, internal research note, or prior-version CEA for this health area that establishes key parameter values — for example, a team-authored efficacy estimate, a meta-analysis working document, or an updated effectiveness calculation? If so, please share it so I can cross-reference the model's inputs against it."

Once the user answers, record any declared intentional deviations and any document links provided. This context is passed to every sub-agent. If the user provided any documents (grant write-up, internal analysis, prior CEA), fetch all of them in the same parallel batch as the spreadsheet reads (Input Handling step 3). Pass each document's key parameter values to sub-agents in the program context summary under "Internal reference values: [parameter name] = [value] per [document name]." The plausibility and CE chain trace agents compare model inputs against these values and flag any discrepancy as High/D with Researcher judgment needed ✓.

**Declared-deviation verification — 5-step checklist**: After the parallel read batch, verify each declared-intentional deviation before passing it to sub-agents. For each declaration:

1. **Read the cell**: Use `read_sheet_values` (FORMULA mode) on the referenced cell to confirm it exists.
2. **Confirm value matches declaration**: Verify the formula or value in the cell matches what the researcher described. If the value does not match, flag: "The declared deviation for [cell] could not be confirmed — [cell] shows [actual value/formula], not [what was declared]. I will include this cell in the standard vet unless you clarify." → status: **UNCONFIRMED**
3. **Read the cell note**: Use `read_sheet_notes` on that cell. A note explaining the reason for the deviation is the strongest confirmation.
4. **If cell exists, value matches, AND a note explains the reason** → status: **CONFIRMED** — include in the deviation list passed to sub-agents, capped at Low/H.
5. **If value matches but no note** → status: **NOTED-ABSENT** — include in the deviation list but add: "No cell note found — sub-agents should still verify the value is within plausible range for this intervention."

Pass only CONFIRMED and NOTED-ABSENT deviations to sub-agents. Do not pass UNCONFIRMED deviations — include those cells in the standard vet at full severity. **Surface UNCONFIRMED deviations to the researcher before proceeding**: if any declared deviation has status UNCONFIRMED, present them as a numbered list — "The following declared deviation(s) could not be confirmed: [cell] — [declared value] not found (actual: [actual value]). Clarify or I will vet these at full severity." Wait for the researcher's response before proceeding if they are online; otherwise proceed after one message and note in the deviation list that they were not confirmed.

**TA grant classification hint**: When Step 0.5 program orientation or the researcher's responses suggest the grant may involve technical assistance or capacity-building (e.g., the grant description or sheet title mentions "TA," "government capacity," "policy adoption," "program adoption," "speed-up," or "technical support"), set `is_ta_botec: true` in session context and pass it explicitly to ce-chain-trace-ta — the agent exits cleanly if no TA content is found after running, so false positives cost only time. Do not rely solely on tab naming conventions to determine TA status; researcher confirmation in Step 0.5 is authoritative. If the researcher's description is ambiguous (e.g., mentions "supporting government implementation" but no explicit TA language), ask: "Does this grant involve technical assistance activities that affect government program adoption rather than direct beneficiary delivery? If so, I'll run the TA-specific chain checks."

**TA routing for mixed programs**: If program context indicates both direct beneficiary delivery AND TA/government adoption components, set `is_ta_botec: true` and run both ce-chain-trace (direct delivery CE chain) and ce-chain-trace-ta (TA denominator consistency) in parallel. Neither agent should audit the other's scope. For genuinely ambiguous classifications: ask the researcher "Does this grant primarily work through (a) direct beneficiary delivery, or (b) government/policy adoption? Or both?" before spawning ce-chain-trace-ta — the answer determines which CE chain structure is primary and which agent should be weighted for reconciliation purposes.

**Intervention-area literature scan**: Up to 4 targeted web searches fire in the same parallel batch as the spreadsheet reads (Input Handling step 3), not after. **WebSearch does not require MCP — run these searches in both MCP and local mode.** Do not skip the literature scan when MCP is unavailable.
1. `"[intervention type] effectiveness systematic review"` — external literature calibration
2. `"[primary outcome] [intervention] meta-analysis"` — effect size ranges (last 5 years preferred)
3. `site:givewell.org "[intervention]"` — GiveWell's own published intervention report and assumptions, the most directly comparable reference
4. `"[grantee org name] annual report"` or `"[grantee org name] coverage survey"` — only if the org name is identifiable from the grant doc or spreadsheet title; skip if unknown

Collect results before beginning Step 1. Add a brief "Literature context" paragraph to the program context summary passed to sub-agents, noting: (a) typical effect size ranges from external literature, (b) GiveWell's published assumptions for this intervention if found, and (c) any grantee-reported delivery data (coverage rates, costs per beneficiary). The plausibility agent uses this as a calibration anchor — e.g., "GiveWell's intervention report uses 12% mortality reduction; the model uses 9%, which is lower than GiveWell's own published estimate."

**Grant document financial trend extraction** (when a grant document is provided): After reading the grant document, extract and record in the program context summary any multi-year financial or operational data it contains — specifically: grantee revenue or budget trajectories, historical growth rates, coverage or reach trends, and figures the document uses to justify model inputs. Pass this as a "Financial trends from grant doc" note alongside the literature context. Heads-up and formula-check agents should check: do any model input values contradict a trend clearly visible in the grant document's own data? Example: if the grant document shows budget data with the most recent year at $X and growing, but the model uses a lower flat figure, flag as Low/H with Researcher judgment needed ✓ asking the researcher to confirm the flat assumption is intentionally conservative.

**"Copy" tab declarations — verify before excluding**: When a researcher declares that a tab or CEA is a "direct copy," "based on," or "pulled from" another model (e.g., "the CEA tab is r.i.c.e.'s model, unchanged"), read that tab's column headers and row labels before treating it as out of scope. Identify any cell or section that GiveWell added, modified, or parameterized relative to the source — look specifically for: columns added for scenarios or geographies, rows for adjustments (IV, EV, funging), moral weight parameters, and any row labeled "GW assumption" or "GiveWell estimate." Include those cells in formula-check scope. A "copy" tab that received any GW modifications is not a pass-through — it is the model, and its modifications must be audited.

### Step 1 — High-Level Summary
For each sheet, write 1–2 sentences: what it does and how it connects to the rest of the workbook.

### Step 2 — Sheet Structure Review
Identify the last populated row. Summarize at the **section level** (e.g., Costs, Generic Parameters, Direct Benefits, Adjustments) — 1–2 sentences per section, no sub-bullets.

**Workbook structural completeness check**: Using the `get_spreadsheet_info` results already in hand, verify the standard top-charity CEA tab structure. Note any deviations in the Step 2 summary. After creating the output files (below) and before spawning agents, write any structural deviations as findings to the Findings Sheet.

*Required tabs* (Medium/H if absent): Main CEA | Leverage/Funging | Simple CEA | GBD estimates (or equivalent disease burden data tab)

*Optional tabs* (note their absence in the Step 2 summary but do not file a finding): Key | Inputs | Confidence intervals | Sensitivity analysis

*Tab ordering* (Low/O if violated): Key → Main CEA → program-specific supplementals → Leverage/Funging → Inputs → data tabs → Simple CEA → Confidence intervals → Sensitivity analysis. Exception: AMF workbooks place Simple CEA as tab 2 (before Main CEA) — intentional, not a finding.

*Main CEA section structure* (Medium/H if sections appear in the wrong order — read column A of Main CEA to locate section headers): Costs → Outputs → Outcomes → Summary of outcomes/initial CE → Adjustments → Cost-effectiveness after final adjustments → Counterfactual impact. An adjustment section appearing before the summary/initial CE section is a structural inversion. This check applies only to top-charity CEA sheets — skip for RFMF models, standalone BOTECs, optionality sheets, and other non-standard model types that do not follow this section sequence.

*Simple CEA section structure* (Low/O if sections appear in the wrong order — read column A of Simple CEA to locate section headers): Inputs → Direct CE calculation → Adjustments → Final CE. A final CE row appearing before adjustments, or inputs appearing after calculations that depend on them, is a structural inversion. This check applies to all Simple CEA tabs regardless of whether they are in primary vet scope — do not lite-pass section ordering on Simple CEA.

**Vet complexity estimate**: Before presenting Steps 1–2 output for confirmation, note which conditional skips will apply based on `get_spreadsheet_info` results and the Step 2 populated row count:
- *Source-data-check skip*: no source-data tabs detected (names containing Coverage Data, WUENIC, DHS, IHME, GBD, MICS, EPI, SAE, WorldPop, Population, Mortality, Subnational Data)
- *Formula-check-arithmetic 2-instance mode*: primary sheet ≤ 80 populated rows (skips C and D instances)
- *Key-params-check 1-instance mode*: primary sheet ≤ 80 populated rows (skips B instance)
- *Formula-check-voi*: always runs — agent self-detects VOI content and exits cleanly if none found
- *Leverage-uov-check skip*: no Leverage/Funging tab detected

Include in your Steps 1–2 summary one line: `Pipeline estimate: ~[N] agents. Reduced pipeline: [list applicable skips, or "none"].`

**After Steps 1–2, present output and ask**: "Does this match your understanding? Are there any misinterpretations before I proceed to error-checking?" Do not begin Step 3 until the user confirms.

---

## Create Output Files

Read `reference/output-setup.md` now and execute it fully before spawning agents — it covers tab creation, header rows, formatting batch, and Dashboard content. Share the output spreadsheet link with the user immediately after creation.

**Output setup failure handling**: If any `create_sheet` or `modify_sheet_values` call during output setup returns an error (auth failure, quota exceeded, permission denied), announce the error and ask: "Output sheet setup failed: [reason]. Would you like to (a) retry, (b) switch to local output mode, or (c) troubleshoot the spreadsheet permissions manually?" Do not proceed to spawn any agents until output setup completes without errors.

**If formula/heads-up only scope was selected**, after completing the output setup, write the following note to the Publication Readiness tab using `modify_sheet_values`:
- Cell A2: `Publication readiness checks were not run for this vet. Scope was set to formula/heads-up only — sources, readability, and notes documentation checks were skipped. To run a full publication readiness check, start a new vet and select "Publication readiness included."`

**Which sheet to use — routing rule for agents**:
- → **Findings**: anything that affects model outputs or interpretation — formula errors, wrong/stale parameters, undocumented assumptions, structural bugs.
- → **Publication Readiness**: issues that do not affect the model — missing sources, permission flags, broken links, citation completeness, terminology (x cash → x benchmark), style, labeling.
- **Sourcing for standalone hardcoded cells → Hardcoded Values sheet, not Publication Readiness.** The Hardcoded Values sheet (column F "Source to Verify") already tracks source completeness for every standalone hardcoded cell. Do not duplicate those as `Sourcing` findings in Publication Readiness. Exception: hardcoded numeric literals *embedded inside formulas* (e.g., `=2.47%*C43`) are not captured by the Hardcoded Values agent — those still go to Publication Readiness as `Sourcing`. If the value is outside the plausible range or inconsistent with other sources, use `Parameter` in Findings. **A value that is both potentially wrong and undocumented is always a Findings `Parameter` — do not also file a PR `Sourcing` for the same cell.** When in doubt between Findings and Publication Readiness, use Findings.
- **Values labeled "guess" or "best guess" are not findings.** A researcher labeling a cell "guess" or "best guess" is documenting uncertainty transparently — this is acceptable modeling practice and does not require a Findings or Publication Readiness entry. Do not file `Parameter` or `Assumption` findings solely because a cell note contains "guess" or "best guess." The Hardcoded Values sheet captures these cells for researcher review.

Pass both sheet IDs to every sub-agent in the session context block.

**Write vet metadata to Dashboard** — do this immediately after output setup completes, before spawning any agents. Use `modify_sheet_values` (USER_ENTERED) to write the following to the Dashboard tab. This block is read by `/vetting-finalize` to recover Wave 3 if the session is interrupted:

- A150: `VET METADATA — for /vetting-finalize recovery`
- A151: `Fully vetted tabs` | B151: comma-separated list of fully vetted tab names
- A152: `Lite-pass tabs` | B152: comma-separated list of lite-pass tab names, or `none`
- A153: `Vet scope` | B153: `full` or `formula-only`
- A154: `band1_end` | B154: the last row number of band 1 (e.g., `150`) — **write this only when `band_count > 1`**; leave A154 and B154 blank when band-split is not active. This value is read by the gap-fill agent (Step 10b) to run the cross-band root cause trace (Check 2.5) after context compaction.

---

**Create staging sheets — do this immediately after vet metadata, before spawning any agents.** Each Wave 1, Wave 2, and Reconcile agent writes its findings exclusively to its own dedicated staging tab, eliminating all concurrent write conflicts on the Findings sheet. Call `mcp__hardened-workspace__create_sheet` for each tab in the tables below — fire all creates in a parallel batch. After creation, write the 10-column header row to row 1 of each tab using `modify_sheet_values`: `Finding # | Sheet | Cell/Row | Severity | Error Type/Issue | Explanation | Recommended Fix | Estimated CE Impact | Researcher judgment needed | Status`.

Wave 1 staging tabs:

| Staging tab name | Agent |
|---|---|
| `stg-arith-A` | formula-check-arithmetic A |
| `stg-arith-B` | formula-check-arithmetic B |
| `stg-arith-C` | formula-check-arithmetic C |
| `stg-arith-D` | formula-check-arithmetic D |
| `stg-data-A` | formula-check-data A |
| `stg-data-B` | formula-check-data B |
| `stg-edge-A` | formula-check-edge-cases A |
| `stg-edge-B` | formula-check-edge-cases B |
| `stg-srcdt-A` | source-data-check A |
| `stg-srcdt-B` | source-data-check B |
| `stg-struct-A` | formula-check-structure A |
| `stg-struct-B` | formula-check-structure B |
| `stg-consist-A` | consistency-check A |
| `stg-consist-B` | consistency-check B |
| `stg-kp-A` | key-params-check A |
| `stg-kp-B` | key-params-check B |
| `stg-voi-A` | formula-check-voi A |
| `stg-voi-B` | formula-check-voi B |
| `stg-params` | formula-check-parameters |

Wave 2 staging tabs (always create these; skipped agents' tabs remain empty):

| Staging tab name | Agent |
|---|---|
| `stg-src-A` | sources A |
| `stg-src-B` | sources B |
| `stg-evid-A` | heads-up-evidence A |
| `stg-evid-B` | heads-up-evidence B |
| `stg-epi-A` | heads-up-epi A |
| `stg-epi-B` | heads-up-epi B |
| `stg-epi-C` | heads-up-epi C (TA BOTEC counterfactual burden) |
| `stg-epi-D` | heads-up-epi D (TA BOTEC counterfactual burden) |
| `stg-int-A` | heads-up-intervention A |
| `stg-int-B` | heads-up-intervention B |
| `stg-rdbl-A` | readability A |
| `stg-rdbl-B` | readability B |
| `stg-lev-A` | leverage-funging A |
| `stg-lev-B` | leverage-funging B |
| `stg-ce-A` | ce-chain-trace A |
| `stg-ce-B` | ce-chain-trace B |
| `stg-uov-A` | leverage-uov-check A |
| `stg-uov-B` | leverage-uov-check B |
| `stg-nscn-A` | notes-scan A |
| `stg-nscn-B` | notes-scan B |
| `stg-ceta-A` | ce-chain-trace-ta A |
| `stg-ceta-B` | ce-chain-trace-ta B |

Reconcile staging tabs (one per reconcile agent, for net-new findings discovered during reconciliation):

| Staging tab name | Pair |
|---|---|
| `stg-rec-arith1` | formula-check-arithmetic first half |
| `stg-rec-arith2` | formula-check-arithmetic second half |
| `stg-rec-data` | formula-check-data |
| `stg-rec-edge` | formula-check-edge-cases |
| `stg-rec-srcdt` | source-data-check |
| `stg-rec-struct` | formula-check-structure |
| `stg-rec-con` | consistency-check (part of combined reconcile agent) |
| `stg-rec-kp` | key-params-check (part of combined reconcile agent) |
| `stg-rec-voi` | formula-check-voi |
| `stg-rec-src` | sources |
| `stg-rec-evid` | heads-up-evidence |
| `stg-rec-epi` | heads-up-epi |
| `stg-rec-epi-ta` | heads-up-epi TA counterfactual burden |
| `stg-rec-int` | heads-up-intervention |
| `stg-rec-rdbl` | readability |
| `stg-rec-lev` | leverage-funging |
| `stg-rec-ce` | ce-chain-trace |
| `stg-rec-uov` | leverage-uov-check |
| `stg-rec-ceta` | ce-chain-trace-ta |

**Band-split extra staging tabs**: `band_count` is computable from `populated_rows`, which is known from the Step 2 structure review — before output setup runs. When `band_count > 1`, create all extra band staging tabs in the **same parallel batch** as the main staging tabs above. Do not defer this to just before spawning banded agents. Example for formula-check-data with 2 bands: create `stg-data-C`, `stg-data-D`. For reconcile staging, create `stg-rec-data-b2`, `stg-rec-data-b3`, etc. Follow the same naming convention for all banded agents. Write header rows to all extra tabs immediately after creation, in the same `modify_sheet_values` batch as the main header rows.

**Staging tab pre-expand**: Immediately after writing all header rows, write a single blank value to row 500 of each staging tab (e.g., `stg-arith-A!A500`, `stg-data-A!A500`, etc.) using `modify_sheet_values`. This forces Google Sheets to allocate at least 500 rows per staging tab and prevents silent row-drop failures for agents with large output sets. Fire all pre-expand writes in a single parallel batch.

**Persist staging tab log to Dashboard at A99**: Write "Staging Sheet Log" in A99, then one row per staging tab (agent name | staging tab name) — including all extra band tabs created above. This log survives context compaction and lets Wave 3 compaction recover the full staging tab list if the session is interrupted before Wave 3 begins. The log must be complete at the time of writing; do not append to it later.

---

## Analysis Steps — Sub-Agents

For Steps 3–10, use the Agent tool to spawn a sub-agent for each step. Read each agent file and pass its content as the agent prompt, appending the following session context:

> Spreadsheet ID: `<id>` | Sheets to vet: `<names>` | In-scope sheets: `<comma-separated list of sheet names being vetted>` | Out-of-scope sheets: `<comma-separated list of all other sheet names in the workbook>` | Findings sheet ID: `<id>` | Publication Readiness sheet ID: `<id>` | Hardcoded Values sheet ID: `<id>` | Confidentiality Flags sheet ID: `<id>` | User email: `<email>` | Program context: `<summary from Step 0.5>` | Declared-intentional deviations: `<list or "none">` | Current date: `<today's date>`
>
> **Scope enforcement**: There are two distinct rules — follow both.
>
> **(1) No proactive auditing of out-of-scope sheets.** Do not proactively scan, read top-to-bottom, or file independent findings about any sheet in `Out-of-scope sheets`. Do not call `read_sheet_notes` or `read_sheet_hyperlinks` with a full sheet range on out-of-scope sheets. The scope restriction defines which sheets you are auditing as a primary subject — not which cells you are allowed to read. Exception: when formula tracing lands on a hardcoded cell in an out-of-scope sheet, you may call `read_sheet_notes` for that specific cell only (e.g., `read_sheet_notes("Assumptions", "B12:B12")`) to check whether the value has a source note — this is part of the trace, not a sheet audit.
>
> **(2) Always trace formula inputs wherever they lead.** When a formula in an in-scope cell references a cell in an out-of-scope sheet (e.g., `=Assumptions!B12`), you MUST read that specific cell using `read_sheet_values` (FORMULA and FORMATTED_VALUE) to verify the value being pulled in is correct. Also read column A of the same row in the out-of-scope sheet to capture the row label — this is essential for confirming the referenced concept matches what the in-scope formula expects (e.g., a row labeled "Total expenditure" when "GiveWell expenditure" is what the formula claims to pull). Follow the chain recursively: if that cell also references another sheet, read it too. Tracing stops only when you reach a hardcoded value or a cell already verified in scope. File any finding against the in-scope cell that contains the reference — not against the out-of-scope sheet itself. The cell reference, row label, and sheet name should appear in the finding description as context (e.g., "in-scope cell B14 pulls from Assumptions!B12 (row label: 'Total expenditure') but the label claims GiveWell-only scope…").
>
> **Pre-read cache** (sheets ≤ 150 populated rows): Each agent receives a scoped subset — data modes and row range as specified in the **Cache scoping table** below (under "Analysis Steps — Sub-Agents" intro). Use the provided cache as your primary data source for row-by-row scanning. Make targeted `read_sheet_values` calls only for cells or data modes outside your cache scope (e.g., a formula referencing a row outside your assigned range, or a FORMULA-mode read not included in your cache). Do not re-read full sheet ranges. If no pre-read cache is provided, the sheet exceeds 150 populated rows — proceed with your normal batch reads.
>
> **Sheet routing**: Sheet routing for compaction (all findings go to your staging tab regardless of routing): model-integrity findings → Findings sheet (compaction routes these); publication-readiness findings → Publication Readiness sheet (compaction routes these). Do not write directly to either output sheet. When in doubt, use Findings routing.
>
> **Parameter finding validity**: Never downgrade a parameter finding (benchmark, moral weight, GBD vintage) to false positive or Low on the grounds that the spreadsheet predates the parameter update. key-parameters.md and the current GBD vintage are authoritative at the time of vetting. For GBD vintage findings, you cannot compute CE impact from updated data — write "Lowers CE — magnitude unknown" or "Direction unknown" in column H; do not skip or downgrade the finding because CE impact cannot be quantified.
>
> **Recommended Fix wording**: Lead every Recommended Fix (column G) with an imperative verb. When the fix is a formula change, include the complete replacement formula string — e.g., "Change to `=SUM(D4:D19)` (current formula excludes row 19)" rather than "Update the range to include the final year." The researcher should be able to copy-paste the fix directly from column G.
>
> **Researcher judgment needed threshold**: Mark `Researcher judgment needed ✓` only when (a) resolving the finding requires knowing the researcher's specific intent AND (b) the assumption is materially surprising — outside the typical range for this intervention type, inconsistent with stated sources, or contradicting the grant document's own data. Do not mark `Researcher judgment needed ✓` for parameters merely labeled "rough guess" that fall within expected ranges for this intervention. Reserve the flag for genuine ambiguities where the researcher's answer would change the finding's severity or routing. A vet where more than 25–30% of findings carry `Researcher judgment needed ✓` has set the threshold too low.
>
> **Never mark Researcher judgment needed for**: formula errors with a single unambiguous correct fix (e.g., replacing one cell reference with another — the fix is clear regardless of intent); missing source notes where the value itself is not in dispute; terminology renames; or documentation gaps where the recommended fix is simply "add a note." The test is whether the researcher's answer changes what you recommend — if the fix is identical regardless of their response, Researcher judgment needed is wrong.
>
> **Staging sheet — write all findings here**: Your session context specifies your staging sheet name. Write ALL findings to that staging tab using `modify_sheet_values`, prefixing the range with the tab name (e.g., for staging sheet `stg-arith-A`: write to `stg-arith-A!A2:J2`). Write your first finding to row 2, then row 3, and so on — appending sequentially. There is no row budget or overflow limit. Do not write to the Findings sheet or Publication Readiness sheet directly. For publication-readiness findings (Error Type: Sourcing, Box Link, or Legibility): write them to your staging sheet in the same 10-column format, with column D (Severity) left blank — the compaction agent routes them to Publication Readiness based on Error Type. The compaction agent (Wave 3) reads all staging sheets and merges findings into the final Findings and Publication Readiness sheets.
>
> **CE impact gate — mandatory before filing Medium or High**: Classify each finding by Nature and Materiality before assigning severity.
>
> **Nature**: **Defect** (formula error, confirmed wrong value, GW standard param violation with no note) | **Gap** (required element absent: missing source, missing adjustment) | **Judgment** (defensible choice you'd question)
>
> **Materiality — estimate using FORMULA mode before assigning**: Trace the affected cell through the CE formula chain and apply in order — stop at first match: (1) CE impact computable and ≥5% → **Material**; write `Raises CE — [estimate]` or `Lowers CE — [estimate]`. (2) CE impact computable and <5% → **Immaterial**; write `Raises CE — [estimate]` or `Lowers CE — [estimate]` (direction and magnitude are both known — do not write 'magnitude unknown' when magnitude is computable). Write `No CE impact` when confirmed zero. (3) Direction clear but magnitude not traceable → **unknown (round up)**; write `Raises CE — magnitude unknown` or `Lowers CE — magnitude unknown`. (4) Direction requires researcher input → **unknown (round up)**; write `Direction unknown`. (5) No CE chain connection → **Zero**.
>
> **Severity from Nature × Materiality**: High = any Defect/Gap that is Material, Decision-changing, or unknown materiality; any benchmark or moral weight deviation from key-parameters.md with no documented cell note rationale (discount rate deviations are always Medium/H per key-parameters.md, not High). Medium = Defect + Immaterial or Zero (Defect floor — formula errors never below Medium); Gap + Immaterial. Low = Gap + Zero; Judgment + Immaterial or Zero.
>
> **Do not file High without at least one of**: (a) CE impact computed ≥5%; (b) GW standard parameter violation with no documented cell note; (c) FORMULA-mode ≥2 hops confirming cell is in direct CE chain (unknown materiality → round-up rule applies). Filing High based on "this looks important" without computation or FORMULA-mode confirmation is the primary source of cross-run severity inconsistency — use Medium.
>
> **Column H — before writing any Estimated CE Impact value**: apply the `Direction unknown` decision tree from `reference/output-format.md` (5-step tree in the Estimated CE Impact section). This determines whether to write `Direction unknown` vs. a directional phrase. Use exact em-dash punctuation (` — `) with spaces — en-dash or hyphen variants cause sort failures in the compaction agent. All six valid phrases: `Raises CE — [estimate]` | `Lowers CE — [estimate]` | `Raises CE — magnitude unknown` | `Lowers CE — magnitude unknown` | `No CE impact` | `Direction unknown`.
>
> **AGENT_COMPLETE — COVERAGE_ROWS field**: When writing your AGENT_COMPLETE marker, include in column F: `COVERAGE_ROWS: [row ranges] | Staging sheet: [name]. Filed [K] findings in rows 2–[K+1].` where [row ranges] is comma-separated row spans you scanned on the source spreadsheet (e.g., `COVERAGE_ROWS: 1-49,76-150`). Use source spreadsheet row numbers. If your agent scans all rows, write `COVERAGE_ROWS: 1-[last_row]`. This field is machine-parsed by the reconcile agent to verify A and B instances covered complementary row ranges without gaps. A prose description ("Checked rows 1–50") is not machine-parseable.
>
> **Cell/Row column format**: Column C on Findings and Publication Readiness must contain cell references or row numbers only — e.g., `B14` or `C4, F7, H12` or `Row 14`. Do not include row labels, descriptions, or any other text after the reference. The cell or row identifier is the only content this column should contain.
>
> **Explanation — length and style**: Column F must be 1–2 sentences maximum. Apply GiveWell legibility principles: lead with the specific problem (not background); make a specific, falsifiable claim; include the actual value or formula fragment (e.g., "B14 = 0.87 but C22 = 0.79"); use plain language a non-expert can understand; do not hedge what you can confirm — write "B14 references the wrong row" not "B14 may be referencing the wrong row." No chain traces, no reasoning.
>
> **Recommended Fix — length and style**: Column G must be one sentence or formula only. Lead with an imperative verb (Change, Replace, Add, Delete). Be specific — include the exact replacement formula or value. No explanation of why — only the action.
>
> **Formula sub-type**: When column E is `Formula`, begin the Explanation with a bracketed sub-type indicating the nature of the error. Use one of: `[Copy-paste]` (value or formula copied from wrong cell), `[Wrong reference]` (references wrong row, column, or sheet), `[Year range]` (range boundary off by one or more rows/years), `[Sign error]` (positive/negative sign inverted), `[Wrong operator]` (wrong arithmetic operation), `[Off-by-one]` (range starts or ends at wrong boundary). Example: `[Wrong reference] B14 uses C22 (Nigeria rate) but should reference C23 (Kenya rate).`
>
> **Coverage declarations**: After completing each named check or scan section, write a coverage declaration in this exact format: `COVERAGE | [agent name] | [check name] | [rows/cells checked] | issues found: [N] | status: complete`. Use this format — do not use free-form prose coverage declarations.
>
> **Analysis order**: Process rows top-to-bottom within your assigned row scope. Do not reorganize, jump ahead to "interesting" sections, or skip early rows in order to reach later ones faster. Top-to-bottom order ensures that every row in your scope receives equivalent analytical attention regardless of context state when you reach it. If your scope is a bottom-half band (rows `split_row+1`–end), process those rows top-to-bottom within that band.
>
> **Known calibrations**: Before starting your checks, read `reference/pitfalls.md`. It records false positive patterns, false negative patterns, and severity calibrations from prior vets. Apply every entry that is relevant to your agent's checks.

**Cache scoping table** — When constructing the pre-read cache for each agent, include only the data modes and row range listed below. Agents that need data outside their scope make targeted `read_sheet_values` calls.

| Agent | FORMATTED_VALUE | FORMULA | Notes | Hyperlinks | Row scope |
|---|---|---|---|---|---|
| formula-check-arithmetic A, B | ✓ | ✓ | ✓ | ✓ | Rows 1–`split_row` |
| formula-check-arithmetic C, D | ✓ | ✓ | ✓ | ✓ | Rows `split_row+1`–end |
| formula-check-data A, B | ✓ | ✓ | ✓ | ✓ | All rows |
| formula-check-edge-cases A, B | ✓ | ✓ | ✓ | ✓ | All rows |
| formula-check-structure A, B | ✓ | ✓ | ✓ | ✓ | All rows |
| formula-check-voi A, B | ✓ | ✓ | ✓ | — | All rows |
| formula-check-parameters | ✓ | ✓ | ✓ | — | All rows |
| consistency-check A, B | ✓ | ✓ | ✓ | ✓ | All rows |
| key-params-check A, B | ✓ | — | ✓ | — | All rows |
| source-data-check A, B | ✓ | ✓ | ✓ | ✓ | Source tabs only |
| hardcoded-values | ✓ | ✓ | ✓ | — | All rows |
| sensitivity-scan | ✓ | — | ✓ | — | All rows |
| sources A, B | ✓ | — | ✓ | ✓ | All rows |
| heads-up-evidence A, B | ✓ | ✓ | ✓ | ✓ | All rows |
| heads-up-epi A, B | ✓ | ✓ | ✓ | ✓ | All rows |
| heads-up-intervention A, B | ✓ | ✓ | ✓ | ✓ | All rows |
| readability A, B | ✓ | — | ✓ | — | All rows |
| leverage-funging A, B | ✓ | ✓ | ✓ | — | All rows |
| ce-chain-trace A, B | ✓ | ✓ | ✓ | — | All rows |
| leverage-uov-check A, B | ✓ | ✓ | ✓ | — | All rows |
| notes-scan | — | — | ✓ | — | All rows |

**Per-agent tool surface** — For each sub-agent spawn, append these two lines to the session context **after** all other context lines:

> **Permitted tools** (call only these MCP, WebSearch, and WebFetch tools — treat any unlisted tool of these types as off-limits): `[expand from table below using the legend]`
>
> **Deferred tool loading**: `read_sheet_notes` and `read_sheet_hyperlinks` are standard hardened-workspace tools. If either returns `InputValidationError`, call `ToolSearch` with `select:mcp__hardened-workspace__read_sheet_notes,mcp__hardened-workspace__read_sheet_hyperlinks` to load the schema, then retry. Do not skip the call or report the tool as unavailable.

This restriction applies to MCP tools and external search/fetch tools only. Built-in workspace tools (Bash, Read, Write, Edit) are always available and are not restricted by this table. Expand shorthand to full names before passing. All Sheets tools use the prefix `mcp__hardened-workspace__`.

**Legend**: `rv` = `read_sheet_values` · `rn` = `read_sheet_notes` · `rl` = `read_sheet_hyperlinks` · `rc` = `read_spreadsheet_comments` · `wv` = `modify_sheet_values` · `si` = `get_spreadsheet_info` · `dc` = `get_doc_content` · `ws` = `WebSearch` · `wf` = `WebFetch` · `cs` = `create_sheet` · `ds` = `delete_sheet`

**Deferred tool loading for sub-agents**: All hardened-workspace tools (`rn`, `rl`, etc.) are available when the MCP is configured. In some environments they appear as deferred — listed by name but not yet callable. If a tool returns `InputValidationError` on first call, load its schema via `ToolSearch` (e.g., `select:mcp__hardened-workspace__read_sheet_notes,mcp__hardened-workspace__read_sheet_hyperlinks`) and retry. Do not skip or report the tool as unavailable.

| Agent | Permitted tools |
|---|---|
| formula-check-arithmetic | rv, rn, rl, rc, wv, ws |
| formula-check-data | rv, rn, rl, rc, wv, ws, wf |
| formula-check-edge-cases | rv, rn, rl, rc, wv |
| formula-check-structure | rv, rn, rl, rc, wv, ws |
| formula-check-voi | rv, rn, rc, wv, si, dc |
| consistency-check | rv, rn, rl, rc, wv, dc |
| key-params-check | rv, rn, rc, wv |
| formula-check-parameters | rv, rn, rc, wv, ws |
| source-data-check | rv, rn, rl, rc, wv, ws, wf |
| hardcoded-values | rv, rn, rl, rc, wv |
| sensitivity-scan | rv, rn, rc, wv |
| sources | rv, rn, rl, rc, wv, ws, wf |
| heads-up-evidence | rv, rn, rl, rc, wv, dc, ws, wf |
| heads-up-epi | rv, rn, rl, rc, wv, dc, ws, wf |
| heads-up-intervention | rv, rn, rl, rc, wv, dc, ws, wf |
| readability | rv, rn, rl, rc, wv, dc |
| leverage-funging | rv, rn, rc, wv, dc |
| ce-chain-trace | rv, rn, rc, wv |
| ce-chain-trace-ta | rv, rn, rc, wv, dc |
| leverage-uov-check | rv, rn, rc, wv |
| notes-scan | rv, rn, rc, wv |
| reconcile | rv, rn, wv, dc |
| final-review-compaction | rv, wv, si, cs |
| final-review-gap-fill | rv, rn, wv |
| final-review-validation | rv, rn, wv, si |
| final-review-dashboard | rv, wv, si, ds |
| source-citation-verify | rv, wv, dc, wf |

---

**Sub-agents are required for every vet, without exception — including small BOTECs and single-sheet optionality models.** There is no sheet-size threshold below which inline execution is acceptable. Inline execution causes anchoring: observations from Steps 0–2 contaminate later steps, and each subsequent "pass" becomes confirmation of what was already noticed rather than an independent exhaustive check. Every step must start with a clean context. If a sheet has only 10 rows, spawn sub-agents anyway — the exhaustiveness of the check matters more than the time saved by running inline.

**Each sub-agent must execute its full checklist exhaustively, on every row.** No check in any agent file is optional or skippable because the sheet is small or because a prior agent already noticed something nearby. The formula-check agent must audit every formula row against its label — not just rows that match a named pattern. The sources agent must complete the full column F text audit on every row. The readability agent must read every row label top-to-bottom. The consistency agent must compare against the VOI template structure row-by-row. A sub-agent that shortcuts because "this is a small BOTEC" will miss findings the same way inline execution does. **The named checks in each agent file are patterns to look for on top of the row-by-row baseline — they are not a substitute for it.**

Agents run in four phases (Wave 1, Wave 2, Wave 2.5, Wave 3) with Wave 1.5 as a conditional sub-phase between Waves 1 and 2. Progress announcements use Phase 1/4, 1.5/4, 2/4, 3/4, 4/4 accordingly. The Wave 1 progress announcement is emitted **after** all conditional skips and band-split evaluations are complete — see the "Spawn Wave 1 agents" section below for the announcement instruction with the computed count.

---

### Wave 1 — Formula check

**Wave 1 entry conditions** — confirm all before spawning any Wave 1 agent:
- [ ] Steps 0–2 complete and researcher confirmed the orientation summary.
- [ ] Output spreadsheet created; all staging tabs created and pre-expanded; staging tab log written to Dashboard A99.
- [ ] Vet metadata written to Dashboard A150–A153.
- [ ] Session context block assembled: spreadsheet ID, in-scope/out-of-scope sheets, all output sheet IDs, user email, program context, declared deviations, current date.

**Before spawning Wave 1 agents**, compute the following from the Step 2 structure review and `get_spreadsheet_info` results:

1. **`split_row`**: `ceil(populated_rows / 2)` for the primary vetted sheet. Formula-check A and B audit spreadsheet rows 1–`split_row`; C and D audit rows `split_row+1` through the last populated row. This halves the per-agent context load while keeping independent verification on each half. For workbooks with multiple vetted sheets, use the largest sheet's populated row count to compute `split_row`. Pass the row range in each agent's session context.

2. **Source data tabs list**: From the `get_spreadsheet_info` results already in hand, collect all tab names whose names contain (case-insensitive): `Coverage Data`, `WUENIC`, `DHS`, `IHME`, `IGME`, `GBD`, `MICS`, `EPI`, `SAE`, `WorldPop`, `Population`, `Mortality`, `Subnational Data`. Exclude section-divider tabs (names containing `-->`) and calculated/output tabs. Pass this list and the in-scope geographies to the source-data-check agent.

3. **Conditional skips** — evaluate before spawning; record each skip decision explicitly in session context:
   - **Source-data-check skip**: If the source data tabs list is empty, skip source-data-check A and B. Record: `source-data-check: SKIPPED (no source data tabs)`.
   - **Formula-check-arithmetic 2-instance mode**: If `populated_rows ≤ 80` on the primary vetted sheet, skip instances C and D. A and B each audit **all rows** (1 through `populated_rows`). In session context for A and B, set: "Sheet row scope: all rows 1 through {populated_rows}. No row-splitting applies." **Also override the cache scope**: pass FORMATTED_VALUE, FORMULA, notes, and hyperlinks for all rows 1 through `populated_rows` (not "Rows 1–split_row"). Record: `formula-check-arithmetic: 2-INSTANCE MODE (≤80 rows) — C and D skipped; A/B each cover all rows`. Their staging tabs (stg-arith-C and stg-arith-D) remain created but empty.
   - **Key-params-check 1-instance mode**: If `populated_rows ≤ 80`, skip key-params-check B. A runs only. Record: `key-params-check: 1-INSTANCE MODE (≤80 rows) — B skipped`. stg-kp-B remains created but empty.
   - **Formula-check-voi — always launch**: Do not skip formula-check-voi at spawn time, even if no VOI tab is detected by name. VOI content can appear within any CEA tab as an embedded section. The agent self-detects and exits cleanly (writing only an AGENT_COMPLETE marker) if no VOI content is found across any vetted sheet.

4. **Band-split protocol** — evaluate before spawning:

   **Band computation**:
   - `band_size = 150`
   - `band_count = max(1, ceil(populated_rows / band_size))`
   - Band k covers rows `(k−1)×band_size + 1` through `min(k×band_size, populated_rows)` for k = 1, 2, 3, 4
   - Cap at 4 bands. If `populated_rows > 600`, warn the researcher: "This sheet has [N] rows, which exceeds the 4-band cap (600 rows). Consider splitting the workbook before vetting for best coverage." Then proceed with 4 bands.
   - Instance pair naming: band 1 → A/B, band 2 → C/D, band 3 → E/F, band 4 → G/H

   When `band_count = 1` (≤150 rows): only A/B run, pre-read cache passed — no change from standard behavior.

   When `band_count > 1`: A/B are **restricted to band 1 rows only** (rows 1–`band_size`). C/D cover band 2, E/F cover band 3, G/H cover band 4 as applicable. Each band gets exactly 2 independent instances with fresh context. No instance covers more than `band_size` rows.

   **Announce when band_count > 1**: `⚠️ Band-split protocol: [N] rows → [band_count] bands of [band_size] rows each. Pairs: [A/B=band1, C/D=band2, ...]. Affected agents: [list].`

   **Which agents use banding** (applies to both Wave 1 and Wave 2 agents that scan rows sequentially):
   - Wave 1: `formula-check-data`, `formula-check-edge-cases`, `formula-check-structure`
   - Wave 2: `sources`, `heads-up-evidence`, `heads-up-intervention`, `readability`
   - **`heads-up-epi`** (special case): epi uses a complementary section split (A=Section A, B=Section B). For each additional band k, spawn two more instances: one for Section A on band k and one for Section B on band k. Name them sequentially: band 2 → C (Section A) and D (Section B); band 3 → E (Section A) and F (Section B); band 4 → G (Section A) and H (Section B). Apply the adversarial preamble to the Section B instance of each band (D, F, H).

   **Agents that do NOT use banding**: `ce-chain-trace` (traces backwards from CE output, not row-sequential), `leverage-funging` (concentrated in the adjustments section), `leverage-uov-check` (targeted structural check), `notes-scan` (runs once).

   **Pre-read cache per band**: Pass only the cache slice for that band's row range (FORMATTED_VALUE, FORMULA, notes, hyperlinks for rows `band_start`–`band_end`). Do not pass the full-sheet cache to any band instance when `band_count > 1`.

   **Band agent tracking**: Band instance entries were already written to the staging sheet log at Dashboard A99 during output setup (same batch as the main staging tabs — see the Band-split extra staging tabs section above). Do not write to A99 again here.

   **Wave 2.5 — one reconcile agent per band pair per agent type**: Each band pair (A/B, C/D, E/F, G/H) for each affected agent gets its own reconcile agent. Do not cross-reconcile between bands — if the same cell appears in both the A/B reconciled set and the C/D reconciled set, the Wave 3 compaction agent deduplicates it. Pass to each band reconcile agent: `"Band [k] of [band_count]: rows [start]–[end]. Compare only within this band's pair. Do not attempt to read or reconcile findings from other bands."`

   Add all band reconcile pairs after the standard Wave 2.5 pairs in the reconcile spawn batch. Announce: `Wave 2.5 reconciliation: [N] standard pairs + [M] band-split pairs ([band_count−1] extra bands × [affected agent count] agents).`

**After completing steps 1–4 above**, compute the actual Wave 1 agent count:
- Start with base count 21
- Subtract 2 if source-data-check is skipped
- Subtract 2 if formula-check-arithmetic is in 2-instance mode (C and D skipped)
- Subtract 1 if key-params-check is in 1-instance mode (B skipped)
- Add `(band_count − 1) × 2` for each banded agent with extra band pairs

Then announce: `[Phase 1/4] Wave 1 starting — [actual_count] agents ([list any skips or band additions]).`

#### Spawn Wave 1 agents simultaneously

Assign staging sheets before spawning:

| Step | Agent file | Instance | Sheet rows scope | Staging tab | Spawn condition |
|---|---|---|---|---|---|
| 3 | `agents/formula-check-arithmetic.md` | A | Rows 1–`split_row` (or all rows in 2-instance mode) | `stg-arith-A` | Always |
| 3 | `agents/formula-check-arithmetic.md` | B | Rows 1–`split_row` (or all rows in 2-instance mode) | `stg-arith-B` | Always |
| 3 | `agents/formula-check-arithmetic.md` | C | Rows `split_row+1`–end | `stg-arith-C` | **Skip when `populated_rows ≤ 80` (2-instance mode)** |
| 3 | `agents/formula-check-arithmetic.md` | D | Rows `split_row+1`–end | `stg-arith-D` | **Skip when `populated_rows ≤ 80` (2-instance mode)** |
| 3d | `agents/formula-check-data.md` | A | All rows | `stg-data-A` |
| 3d | `agents/formula-check-data.md` | B | All rows | `stg-data-B` |
| 4 | `agents/formula-check-edge-cases.md` | A | All rows | `stg-edge-A` |
| 4 | `agents/formula-check-edge-cases.md` | B | All rows | `stg-edge-B` |
| — | `agents/source-data-check.md` | A | Source tabs only | `stg-srcdt-A` | Skip if no source data tabs (per conditional skips above) |
| — | `agents/source-data-check.md` | B | Source tabs only | `stg-srcdt-B` | Skip if no source data tabs (per conditional skips above) |
| 3b | `agents/formula-check-structure.md` | A | All rows | `stg-struct-A` |
| 3b | `agents/formula-check-structure.md` | B | All rows | `stg-struct-B` |
| 4b | `agents/consistency-check.md` | A | All rows | `stg-consist-A` |
| 4b | `agents/consistency-check.md` | B | All rows | `stg-consist-B` |
| 3e | `agents/key-params-check.md` | A | All rows | `stg-kp-A` |
| 3e | `agents/key-params-check.md` | B | All rows | `stg-kp-B` |
| 3v | `agents/formula-check-voi.md` | A | All rows | `stg-voi-A` |
| 3v | `agents/formula-check-voi.md` | B | All rows | `stg-voi-B` |
| 3f | `agents/formula-check-parameters.md` | — | All rows | `stg-params` |
| 8 | `agents/sensitivity-scan.md` | — | All sheets | Confidentiality Flags sheet only |
| 9 | `agents/hardcoded-values.md` | — | All sheets | Hardcoded Values sheet only |

**Note (sensitivity-scan spawn message)**: Do not append the standard staging sheet session context to the sensitivity-scan spawn message. Instead append: "Write all findings to the Confidentiality Flags sheet (ID: [cf_sheet_id]). This agent has no staging tab. Standard staging tab instructions do not apply."

**AGENT_COMPLETE format for sensitivity-scan**: After writing all flags to the Confidentiality Flags sheet, the agent writes ONE final row as the AGENT_COMPLETE marker: column A = `AGENT_COMPLETE`, column B = `sensitivity-scan`, column D = `Sensitivity scan complete. Scanned [N] sheets. Found [K] confidentiality flags in rows 2–[K+1].` The pre-Wave-3 self-verification check reads the Confidentiality Flags sheet and looks for a row with `AGENT_COMPLETE` in any column. Do not create a staging tab for this agent.

**AGENT_COMPLETE format for hardcoded-values**: After writing all rows to the Hardcoded Values sheet, the agent writes ONE final row as the AGENT_COMPLETE marker: column B = `hardcoded-values`, column D = `AGENT_COMPLETE`, column F = completion summary text. The pre-Wave-3 self-verification check and the pre-Wave-1.5 guard both look for a row with `AGENT_COMPLETE` in column D of the Hardcoded Values sheet. Do not create a staging tab for this agent.

Append to each formula-check-arithmetic instance's session context:
> **Staging sheet**: `{stg-arith-A / stg-arith-B / stg-arith-C / stg-arith-D}`. Write all findings to this staging tab starting at row 2.
> **Sheet row scope**: Audit only spreadsheet rows `{scope_start}` to `{scope_end}`. Do not read or audit rows outside this range.
> **Pre-read cache scope**: FORMATTED_VALUE, FORMULA, notes, and hyperlinks for spreadsheet rows `{scope_start}` to `{scope_end}` only. For cells outside this range referenced in formulas (e.g., a formula in row 40 pointing to row 85), make targeted `read_sheet_values` calls to retrieve those values — do not assume the value from the cache.

Append to formula-check-data and formula-check-edge-cases session contexts (A/B share the same prompt — do not tell either instance that a second instance is running):
> **Staging sheet**: `{stg-data-A / stg-data-B / stg-edge-A / stg-edge-B}`. Write all findings to this staging tab starting at row 2.

Append to formula-check-voi A and B session contexts (A/B share the same prompt except the adversarial B preamble — do not tell either instance that a second instance is running):
> **Staging sheet**: `{stg-voi-A / stg-voi-B}`. Write all findings to this staging tab starting at row 2.
> **Sheet row scope**: All rows across all vetted sheets. Self-detect VOI content before running checks — if no VOI content is found, write your completion marker and stop.

Append to formula-check-parameters session context:
> **Staging sheet**: `stg-params`. Write all findings to this staging tab starting at row 2.
> **Sheet row scope**: All rows across all vetted sheets.

Append to source-data-check A and B session contexts (identical content except staging sheet name):
> **Staging sheet**: `{stg-srcdt-A / stg-srcdt-B}`. Write all findings to this staging tab starting at row 2.
> **Source data tabs**: `{comma-separated list from step above}`
> **In-scope geographies**: `{list of countries and states from program context}`

Do **not** tell A instances that B instances are running. For **B instances only** (formula-check-arithmetic B, formula-check-data B, formula-check-edge-cases B, source-data-check B, formula-check-structure B, consistency-check B, key-params-check B, formula-check-voi B), append the following adversarial preamble to the session context **before** the row allocation note:

> **Reviewer framing — B instance**: You are a skeptical second reviewer. A separate first reviewer has independently audited this same spreadsheet. Your job is to find what a thorough but reasonable reviewer would have rationalized away. Specifically: (a) assume the first reviewer accepted well-labeled rows as correct without verifying the referenced cells — challenge that instinct by reading the referenced cells themselves, not just their labels; (b) give extra attention to checks requiring you to read multiple tabs together, since cross-tab checks are harder and more likely to be shortcut; (c) when a formula looks correct at first glance, ask "am I pattern-matching on the label rather than actually reading the formula?" — then read the formula; (d) for every section where you find no issues, write one specific reason the section is clean before moving on; (e) **your scanning strategy is bottom-up** — begin at the last row of your assigned scope and work backward to the first, tracing each formula's inputs upstream before moving to the row above. This is the opposite of the A instance's top-down approach and ensures that input rows at the start of sections — which top-down reviewers reach last, after reading fatigue sets in — receive full attention. Do not read the Findings sheet. Do not tell the researcher you are a B instance.

Wait for all spawned Wave 1 agents to complete before proceeding.

**Consistency-check always runs — including for BOTECs**: Do not skip the consistency-check agent for simple BOTECs, single-sheet models, or workbooks with no declared deviations. Every model uses moral weights, and moral weight drift is one of the most common silent errors. Pass this note in the consistency-check session context: "For simple BOTECs and non-standard models that lack VOI content: skip the VOI structural completeness check and the cross-cutting CEA parameters check. Always run the moral weights numeric verification regardless of model type."

**Progress — Wave 1 complete**: Announce: `[Phase 1/4 done] Wave 1 complete.`

**Wave 1 exit conditions** — confirm all before proceeding to Wave 1.5 or Wave 2:
- [ ] All required Wave 1 staging tabs contain an AGENT_COMPLETE marker (confirmed by the silent failure check below).
- [ ] Hardcoded Values sheet contains an AGENT_COMPLETE marker row.
- [ ] Confidentiality Flags sheet contains an AGENT_COMPLETE marker row.
- [ ] Researcher checkpoint completed (presented or skipped if no flagged rows).

**Silent failure check — do this before the researcher checkpoint**: For each Wave 1 agent, read its staging sheet and check whether any non-header, non-AGENT_COMPLETE rows exist. An agent that has no AGENT_COMPLETE row and no finding rows in its staging sheet may have failed silently (auth timeout, context limit, API error) rather than genuinely found no issues. Read each staging tab with `read_sheet_values` on `{staging_tab_name}!A1:J500` to check for the AGENT_COMPLETE marker. Report any empty staging sheet in chat:

> ⚠️ Silent failure warning: [agent name] staging sheet `[staging_tab_name]` is empty (no AGENT_COMPLETE marker and no findings). This may indicate agent failure. Consider re-running this agent before proceeding to Wave 2.

**Per-agent thresholds for zero-finding results** — use these instead of general judgment:

| Agent | Is 0-findings a plausible clean pass? |
|---|---|
| formula-check-arithmetic (any instance) | **No** — every CEA has at least one formula worth noting. 0 findings from any instance is a failure signal regardless of sheet size. |
| formula-check-data | Yes — if no external data citations or GBD/IHME source tabs exist, 0 findings may be valid. Check for an AGENT_COMPLETE marker with a confirming clean declaration. |
| formula-check-edge-cases | Yes — on simple BOTECs with no INDIRECT, IFERROR, or SUMPRODUCT formulas, 0 findings is plausible. Check AGENT_COMPLETE. |
| formula-check-structure | **No** — every workbook has at least one structural observation. 0 findings is a failure signal. |
| consistency-check | **No** — moral weights are present in every CEA; 0 findings means moral weight check was skipped. |
| key-params-check | Yes — if the model uses no standard GiveWell parameters, 0 findings is valid. Check AGENT_COMPLETE. |
| sources | Yes — if pub-readiness scope was excluded, 0 findings is expected. |
| readability | Yes — if pub-readiness scope was excluded, 0 findings is expected. |
| heads-up-evidence | **No** — every CEA has at least one evidence or plausibility point worth flagging. |
| heads-up-epi | **No** — every CEA uses epidemiological parameters. |
| heads-up-intervention | Yes — all intervention-specific checks may pass on a well-calibrated model. Check AGENT_COMPLETE. |
| leverage-funging | Yes — if no Leverage/Funging tab exists, 0 findings is expected. |
| ce-chain-trace | **No** — every CEA has a CE chain that must be traced. 0 findings means the trace was not completed. |
| formula-check-voi | Yes — self-detecting; 0 findings is valid when no VOI content is found. Check AGENT_COMPLETE text. |
| ce-chain-trace-ta | Yes — self-detecting; 0 findings is valid when no TA signals are found. Check AGENT_COMPLETE text. |
| sensitivity-scan | **No** — every populated spreadsheet has at least one cell worth scanning for sensitive data. Check the Confidentiality Flags sheet: if it has only the header row (no data rows and no AGENT_COMPLETE), this is a failure signal. Read `'Confidentiality Flags'!A1:D5` to confirm. |
| hardcoded-values | **No** — every spreadsheet has at least one hardcoded input cell. Check the Hardcoded Values sheet: if it has only the header row (no data rows and no AGENT_COMPLETE), this is a failure signal. Read `'Hardcoded Values'!A1:H5` to confirm. |

**Researcher-confirm checkpoint**: After all Wave 1 agents complete and before spawning Wave 2, read all Wave 1 staging tabs (stg-arith-A through stg-params) and collect all rows with `✓` in the **Researcher judgment needed** column (column I). If **no such rows exist**, skip this checkpoint entirely and proceed immediately to Wave 2. If flagged rows exist, present them to the user as a numbered list: cell reference, finding type, and the specific question. Explain that subsequent agents will proceed on current assumptions unless they respond. Then immediately proceed to Wave 2 — do not wait for a response. If the researcher responds before Wave 2 agents complete, update the declared deviations list in session context at that point and note the change in chat. If they respond after Wave 2 is already running, note their answers in the declared deviations list and flag in the Wave 2.5 session context: "Researcher responded to checkpoint after Wave 2 launched — review any finding touching [confirmed cells] for whether the researcher's intent changes the severity or routing." This checkpoint exists so intent questions (e.g., "is this $0 intentional?") can be answered before plausibility and readability agents analyze the same cells. **For any checkpoint item that is High severity or tagged D**: add a sentence flagging that downstream agents will analyze this cell using the current (potentially wrong) value — if the researcher's answer changes the value, the plausibility findings for that section may need to be revisited.

**Declared-deviation update before spawning Wave 2**: If the researcher responds to the checkpoint and any answer (a) confirms that a parameter was set intentionally, (b) clarifies that a $0 or zero value is intentional, or (c) changes whether a finding should be treated as a declared deviation — update the **declared-intentional deviations** list in session context before spawning Wave 2 agents. Pass the updated list to all Wave 2 agents in the standard session context block. Do not pass the original (stale) list if the researcher has since clarified intent. If the researcher does not respond before proceeding, pass the original list unchanged and note in the Wave 2 session context: `Researcher checkpoint: no response received; Wave 2 proceeds on pre-checkpoint assumptions.`

---

### Wave 1.5 — Source citation verification

**Pre-Wave-1.5 guard — check hardcoded-values agent completed**: Before spawning the source-citation-verify agent, read the Hardcoded Values sheet's last non-empty row. If the row contains `AGENT_COMPLETE` in column D, the hardcoded-values agent completed normally. If no AGENT_COMPLETE row is found: announce `⚠️ hardcoded-values agent appears not to have completed — Hardcoded Values sheet may be incomplete or empty. Wave 1.5 source citation verification requires a populated Hardcoded Values sheet to run. Options: (1) re-run the hardcoded-values agent and then re-run Wave 1.5, or (2) skip Wave 1.5 by proceeding to Wave 2. Ask the researcher which to do before continuing.` Do not skip silently.

**Wave 1.5 skip conditions** — evaluate in order; skip on the first matching condition:

1. **Researcher declined at startup**: skip. Announce: `⏭️ Wave 1.5 skipped — source citation verification declined by researcher.` GiveWell parameter consistency (key-params-check, Wave 1) always runs regardless of this choice.
2. **Hardcoded Values sheet incomplete**: check per the pre-Wave-1.5 guard above. If no AGENT_COMPLETE is found, ask the researcher whether to (a) re-run hardcoded-values then re-run Wave 1.5, or (b) skip Wave 1.5.
3. **No verifiable rows**: if the Hardcoded Values sheet has no `Study-Derived` or `Org-Reported` rows that include a source URL in column F, skip. Announce: `⏭️ Wave 1.5 skipped — no Study-Derived or Org-Reported rows with source URLs found.`

If none of the above conditions match, run Wave 1.5.

**Progress announcement** (only when Wave 1.5 runs): `[Phase 1.5/4] Source citation verification starting — pre-filling Hardcoded Values sheet.`

Spawn one `source-citation-verify` agent. Pass: Hardcoded Values sheet ID and user email. This agent uses the Anthropic Citations API to pre-fill the **Verified?** (column G) and **Auto-check evidence** (column H) columns for every `Study-Derived` and `Org-Reported` row that cites an accessible source URL.

**The agent requires Bash and Write built-in tools** (to write and run the verification script) in addition to its MCP tools. Ensure these are available in its spawned context.

**Bash tool fallback**: If the Bash tool is unavailable in the spawned agent's context, the source-citation-verify agent should fall back to manual `WebFetch` verification for the top 5 `Study-Derived` parameters only (by CE impact proximity in the Hardcoded Values sheet), write its AGENT_COMPLETE marker noting `Bash unavailable — fell back to manual spot-check of top-5 Study-Derived parameters; full citation verification not completed. [N] spot-checked.`, and not attempt to write the verification script. After the agent completes, check its AGENT_COMPLETE column F for the phrase `Bash unavailable`. If present, announce: `⚠️ Wave 1.5 ran in manual fallback mode — Bash unavailable; only top-5 parameters spot-checked. Consider re-running with Bash access for full citation coverage.` and surface this alongside any Contradicted findings.

Wait for this agent to complete before announcing Wave 2. After it completes, if the coverage declaration lists any `Contradicted ✗` rows, surface them to the researcher before proceeding: "Source citation check found [N] contradicted value(s): [list]. Review column H for the verbatim sentence from the source. Wave 2 will proceed — plausibility agents will independently flag these if they are materially significant."

---

### Wave 2 — Parallel (doubled for independent verification)

**Wave 2 entry conditions** — confirm all before spawning any Wave 2 agent:
- [ ] Wave 1 exit conditions satisfied (all staging tabs have AGENT_COMPLETE markers, HV and CF sheets have AGENT_COMPLETE rows).
- [ ] Wave 1.5 complete or explicitly skipped (skip recorded in session context).
- [ ] Researcher checkpoint complete — declared deviations list is finalized or noted as "no response received."
- [ ] Declared-deviation update applied if researcher responded.

**Progress announcement** before spawning: compute the agent count at runtime from the staging tab table below, applying the applicable skips (leverage-uov-check skipped if no leverage tab; sources/readability/notes-scan skipped if formula-only scope; heads-up-epi C/D added only for TA BOTEC). Announce:

`[Phase 2/4] Wave 2 starting — [N] agents ([list the agent types being spawned, e.g., "sources A/B, heads-up A/B ×3, readability A/B, leverage A/B, CE chain A/B, CE chain TA A/B, leverage UoV A/B, notes-scan A/B"]; [list any skips, e.g., "leverage-uov-check skipped — no leverage tab"]).`

Do not use a hardcoded count. Count the rows in the staging tab table that will actually spawn (each row = one agent). **CE chain TA (ce-chain-trace-ta) always launches** — never skip at spawn time. The agent self-detects TA signals and exits cleanly if none are found.

Spawn agents simultaneously after the researcher checkpoint. Each of the eight core analysis agents (sources, heads-up-evidence, heads-up-epi, heads-up-intervention, readability, leverage-funging, ce-chain-trace, leverage-uov-check) runs as two independent instances (A and B) with separate context windows and no knowledge of each other. notes-scan now also runs as two independent instances (A and B) — both write to their dedicated staging sheets (stg-nscn-A and stg-nscn-B); the compaction agent routes their findings to Publication Readiness based on Error Type and deduplicates overlapping findings in its standard PR dedup pass. sensitivity-scan and hardcoded-values have moved to Wave 1 and do not run here.

**Leverage-uov-check skip condition**: Before spawning, check whether any leverage activity exists: (a) does a dedicated Leverage/Funging tab exist (names containing Leverage, Funging, or L/F)? OR (b) is there a leverage/funging section in the Main CEA tab (leverage-funging A or B filed leverage-related findings)? Skip leverage-uov-check only when both (a) and (b) are false. Announce: `⏭️ leverage-uov-check A and B: skipped — no Leverage/Funging tab found.` Their pre-allocated row ranges remain reserved but unused. leverage-funging A and B still run — they check leverage treatment in the Main CEA regardless of tab structure.

**If formula/heads-up only scope was selected**: skip sources-A, sources-B, readability-A, readability-B, and `agents/notes-scan.md` entirely — spawn 14 agents instead of 20. Their pre-allocated row ranges remain reserved but unused. Notes are still *read* in the initial batch (step 3) and remain available to all formula-check and heads-up agents as formula context — only the pub-readiness audit of notes documentation (missing "Calculation." entries, source annotations, style) is skipped. Pass to all spawned agents: "Pub readiness out of scope; value-correctness verification (GBD vizhub URLs, study extractions) is in scope." Also pass to all Wave 2 heads-up agents (heads-up-evidence, heads-up-epi, heads-up-intervention): "Pub readiness out of scope for this vet. Do not route any finding to Publication Readiness — route all issues including source quality and notation concerns to the Findings sheet as Parameter or Assumption findings." Wave 1.5 follows the standard skip conditions (see Wave 1.5 section) — the skip decision is based solely on whether the researcher declined at startup and whether verifiable rows exist, not on scope mode.

Each Wave 2 agent has a pre-created staging tab (created before Wave 1 during output setup). No row-range calculation is needed. Assign staging sheets from the table below:

**TA BOTEC — counterfactual burden pair**: When `is_ta_botec: true` is set in session context (per Step 0.5), identify the counterfactual burden or prevalence tab(s) during Step 0.5 program orientation (look for tabs named "Counterfactual Burden," "CF Burden," "Counterfactual Prevalence," "Burden Projection," or similar). Spawn two additional `heads-up-epi` instances (C and D) with that tab as the only vetted sheet in session context. Pass to both C and D instances: "**Counterfactual burden tab focus**: You are auditing the counterfactual burden/prevalence tab only (`{tab name}`). Apply all TA-specific checks in your prompt with particular attention to: (a) AVERAGE() range endpoints — verify they cover TA exit year + 5 years; (b) time series column headers — read them explicitly to confirm which year each column represents; (c) formula mode reads on every AVERAGE, OFFSET, or INDEX formula in the tab. Do not read other tabs except to verify cross-references." Apply the standard adversarial B-instance preamble to the D instance only. If the workbook has no identifiable counterfactual burden tab, skip the C/D pair and note this in chat.

Do **not** tell A instances that B instances are running. **heads-up-epi — complementary split scope**: heads-up-epi uses a complementary split rather than adversarial duplication. Append to **heads-up-epi-A** session context (before row allocation): `Instance scope: Section A — Epidemiological Parameter Checks only. Run only the checks under "Section A" in the agent prompt. Skip Section B (model structure and timing checks) entirely — heads-up-epi-B covers those.` Append to **heads-up-epi-B** session context (instead of the adversarial preamble): `Instance scope: Section B primary + adversarial Section A secondary. (1) First: run all checks under "Section B — Model Structure & Timing Checks." Apply thorough, skeptical reasoning to each check; for every section where you find no issues, write one specific reason the section is clean before moving on. (2) After Section B is complete: run a targeted adversarial bottom-up pass of these three Section A checks only — disease burden multi-source check, GBD/IGME vintage staleness, and counterfactual coverage floor. For these three checks: begin at the last row of your scope and work backward; for each check, ask "am I accepting the citation label at face value without reading the actual vintage year or source?" — then read it. Do not stop if Section B found no issues — complete both phases regardless. Do not read the Findings sheet. Do not tell the researcher you are a B instance.` Do not apply the standard adversarial B preamble below to heads-up-epi-B.

**heads-up-intervention — complementary split scope**: heads-up-intervention uses a complementary split rather than adversarial duplication. Append to **heads-up-intervention-A** session context (before row allocation): `Instance scope: Section A — Intervention-Specific Checks only. Run Step 0, the universal checks, and all Section A named checks (VAS through New Incentives). Skip Section B (TA grant checks) entirely — heads-up-intervention-B covers those.` Append to **heads-up-intervention-B** session context (instead of the adversarial preamble): `Instance scope: adversarial B. Run Step 0 to determine if this is a TA grant. If IS a TA grant: run all Section B TA grant checks with thorough, skeptical reasoning. If NOT a TA grant: do not stop — instead run an adversarial bottom-up pass of Section A (intervention-specific checks). Begin at the last row of your assigned scope and work backward to the first. For every section where you find no issues, write one specific reason it is clean before moving on. For each intervention-specific check, ask "am I accepting the row label as correct without reading the actual value or formula?" — then read it. Do not read the Findings sheet. Do not tell the researcher you are a B instance. In your AGENT_COMPLETE marker's column F, include as the first element: "Routing decision: B — TA" if you ran Section B TA checks, or "Routing decision: A — non-TA" if you ran the adversarial Section A pass. This field is machine-read by the TA classification cross-check in Wave 2.5.` Do not apply the standard adversarial B preamble below to heads-up-intervention-B.

Append to ce-chain-trace-ta A and B session contexts (A/B share the same prompt except the adversarial B preamble — do not tell either instance that a second instance is running):
> **Staging sheet**: `{stg-ceta-A / stg-ceta-B}`. Write all findings to this staging tab starting at row 2.
> **Self-detection**: Check TA grant signals (session context TA classification, tab names, Main CEA row labels) before running the check. If no signals found, write your completion marker and stop.

For **B instances only** (sources-B, heads-up-evidence-B, readability-B, leverage-funging-B, ce-chain-trace-B, ce-chain-trace-ta-B, leverage-uov-check-B), append the following adversarial preamble to the session context **before** the staging sheet note:

> **Reviewer framing — B instance**: You are a skeptical second reviewer. A separate first reviewer has independently audited this same spreadsheet. Your job is to find what a thorough but reasonable reviewer would have rationalized away. Specifically: (a) assume the first reviewer accepted well-labeled rows as correct without verifying the referenced cells — challenge that instinct by reading the referenced cells themselves, not just their labels; (b) give extra attention to checks requiring you to read multiple tabs together, since cross-tab checks are harder and more likely to be shortcut; (c) when a formula or value looks correct at first glance, ask "am I pattern-matching on the label rather than actually reading this?" — then read it; (d) for every section where you find no issues, write one specific reason the section is clean before moving on; (e) **your scanning strategy is bottom-up** — begin from the final CE output row and work backward through adjustments, benefits, and inputs, tracing each formula's chain upstream before moving to the row above. This is the opposite of the A instance's top-down approach and ensures the deepest input rows — where copy-paste errors accumulate unnoticed — receive independent scrutiny. Do not read the Findings sheet. Do not tell the researcher you are a B instance.

For A instances, pass the standard session context only. The only difference between A and B is the staging sheet name and the adversarial preamble. Append to each instance's session context:
> **Staging sheet**: `{staging_tab_name from table below}`. Write all findings to this staging tab starting at row 2. There is no row budget.

| Step | Agent file | Instance | Staging tab |
|---|---|---|---|
| 5 | `agents/sources.md` | A | `stg-src-A` |
| 5 | `agents/sources.md` | B | `stg-src-B` |
| 6a | `agents/heads-up-evidence.md` | A | `stg-evid-A` |
| 6a | `agents/heads-up-evidence.md` | B | `stg-evid-B` |
| 6b | `agents/heads-up-epi.md` | A | `stg-epi-A` |
| 6b | `agents/heads-up-epi.md` | B | `stg-epi-B` |
| 6c | `agents/heads-up-intervention.md` | A | `stg-int-A` |
| 6c | `agents/heads-up-intervention.md` | B | `stg-int-B` |
| 7 | `agents/readability.md` | A | `stg-rdbl-A` |
| 7 | `agents/readability.md` | B | `stg-rdbl-B` |
| 6d | `agents/leverage-funging.md` | A | `stg-lev-A` |
| 6d | `agents/leverage-funging.md` | B | `stg-lev-B` |
| 6e | `agents/ce-chain-trace.md` | A | `stg-ce-A` |
| 6e | `agents/ce-chain-trace.md` | B | `stg-ce-B` |
| 6f | `agents/leverage-uov-check.md` | A | `stg-uov-A` |
| 6f | `agents/leverage-uov-check.md` | B | `stg-uov-B` |
| 6e-ta | `agents/ce-chain-trace-ta.md` | A | `stg-ceta-A` |
| 6e-ta | `agents/ce-chain-trace-ta.md` | B | `stg-ceta-B` |
| 7c | `agents/notes-scan.md` | A | `stg-nscn-A` |
| 7c | `agents/notes-scan.md` | B | `stg-nscn-B` |

---

**Wave 2 exit conditions** — confirm all before proceeding to Wave 2.5:
- [ ] All spawned Wave 2 agents have completed (staging tabs contain AGENT_COMPLETE markers or were pre-approved as legitimate skips).
- [ ] Wave 2 silent failure check complete — any empty staging tabs flagged.

**Silent failure check — Wave 2 agents (run before spawning Wave 2.5)**: For each Wave 2 staging tab in the table above, read the first 5 rows using `read_sheet_values` on `{tab}!A1:J5` and check for an AGENT_COMPLETE row. An agent whose staging tab contains only the header row and no AGENT_COMPLETE marker may have failed silently. Apply the same per-agent zero-findings thresholds from the Wave 1 thresholds table above:

- For agents where 0-findings is **not** plausible (heads-up-evidence, heads-up-epi, ce-chain-trace), an empty staging tab with no AGENT_COMPLETE is a failure signal regardless.
- For agents where 0-findings is plausible (readability when formula-only scope, leverage-uov-check when no leverage tab exists, sources when formula-only scope): verify the AGENT_COMPLETE text explicitly declares the check clean or the skip was pre-approved.

Report any failed agent:

> ⚠️ Wave 2 silent failure warning: [agent name] staging tab `[staging_tab]` is empty (no AGENT_COMPLETE and no findings). Consider re-running this agent before spawning Wave 2.5 reconciliation.

---

### Wave 2.5 — Reconciliation (after all Wave 2 agents complete)

**Wave 2.5 entry conditions** — confirm all before spawning any reconcile agent:
- [ ] Wave 2 exit conditions satisfied (all spawned agents complete, silent failure check run).
- [ ] Staging tab names available in session context or recovered from Dashboard A99.
- [ ] Pre-flight empty pair check complete — perform the check described below (under "Pre-flight empty pair check") before confirming this item. Empty pairs identified and recorded.

Announce before spawning: `[Phase 2/4 done → Phase 3/4] Wave 2 complete — starting reconciliation ([computed_count] agents: [list active pairs]; [list skipped pairs if any] skipped in pre-flight check).` Compute the count before announcing: start with 17 standard pairs (or 18 if a TA BOTEC adds the ce-chain-trace-ta pair), subtract skipped pairs (arith C/D if 2-instance mode; source-data-check if no source tabs), add any additional band-split pairs if banding is active.

**Staging sheet name recovery — do this first if names are not in context**: If the staging sheet names are not available in the current session context (e.g., context was compacted between Wave 2 and Wave 2.5), read Dashboard cells A99 onward of the output spreadsheet to recover the full staging sheet log written during output setup.

**Pre-flight empty pair check**: Before spawning, fire a parallel batch of `read_sheet_values` calls — one per pair — reading `{tab}!A1:J500` for each staging-A and staging-B tab (AGENT_COMPLETE may be at any row after all findings) to check whether they contain an AGENT_COMPLETE marker or any finding rows. For any pair where **both** staging-A and staging-B tabs contain only the header row (no AGENT_COMPLETE, no findings): skip spawning that reconcile agent and announce: `⏭️ Skipping [pair name] reconcile — both A and B wrote zero findings.` Only skip when both tabs are confirmed empty; if either tab has any non-header row, spawn the reconcile agent as normal. Update the agent count in your announcement accordingly.

For the combined consistency-check + key-params-check agent, evaluate the two pairs independently. Skip the combined agent only if BOTH the consistency pair (stg-consist-A and stg-consist-B both empty) AND the key-params pair (stg-kp-A and stg-kp-B both empty) are confirmed empty. If either pair has any non-header row, spawn the combined agent as normal.

Spawn reconciliation agents simultaneously (up to 17 standard agents, or 18 if a TA BOTEC is present; consistency-check and key-params-check share one combined agent; fewer if empty pairs are skipped), using `agents/reconcile.md`. Each agent receives the standard session context plus its specific pair assignment. Do not tell any reconcile agent about the other pairs being processed.

For each instance, append to session context:
> **Pair to reconcile**: [pair name]
> **Staging sheet A**: `[stg-agent-A]` — read all rows from this tab
> **Staging sheet B**: `[stg-agent-B]` — read all rows from this tab
> **Reconcile staging sheet**: `[stg-rec-pair]` — write net-new findings discovered during reconciliation here, starting at row 2

**Combined consistency-check + key-params-check agent**: For this pair only, pass the following session context instead of the standard single-pair format:
> **Pairs to reconcile**: consistency-check AND key-params-check. Process sequentially in this order: (1) reconcile consistency-check A/B first — staging sheet A: `stg-consist-A`, staging sheet B: `stg-consist-B`; write any net-new findings to reconcile staging sheet `stg-rec-con`. (2) Then reconcile key-params-check A/B — staging sheet A: `stg-kp-A`, staging sheet B: `stg-kp-B`; write any net-new findings to reconcile staging sheet `stg-rec-kp`. Complete consistency-check reconciliation fully before beginning key-params-check reconciliation. Write a coverage declaration after each pair.

If key-params-check ran in 1-instance mode (populated_rows ≤ 80), also append: `Note: key-params-check ran in 1-instance mode — stg-kp-B was intentionally not written to and will contain only the header row. This is not a silent failure. Treat stg-kp-A as the complete finding set for key-params-check; the B-instance absent marker does not require investigation or flagging.`

**heads-up-epi reconcile agent**: Append to this agent's session context: `Note: heads-up-epi A and B used a complementary section split. A covered Section A checks only (epidemiological parameters). B covered Section B checks (model structure, timing) plus an adversarial pass of three specific Section A checks. B-only findings whose Error Type or Explanation references model structure or timing checks are expected; treat them as Retain without escalating to Needs researcher input unless the cell read reveals a genuine error.`

**heads-up-intervention reconcile agent** (TA grants only — when is_ta_botec is true): Append to this agent's session context: `Note: heads-up-intervention A covered Section A (intervention-specific) checks only; B covered Section B TA grant checks. The sections are complementary and non-overlapping on TA grants. B-only findings whose context clearly relates to TA grant structure are expected; treat as Retain unless the cell read reveals an error.`

| Pair | Staging sheet A | Staging sheet B | Reconcile staging sheet |
|---|---|---|---|
| formula-check-arithmetic (A/B pair — rows 1–split_row, or all rows in 2-instance mode) | `stg-arith-A` | `stg-arith-B` | `stg-rec-arith1` |
| formula-check-arithmetic (C/D pair — rows split_row+1–end in 4-instance mode, or band-2 rows when banding is active; skip if 2-instance mode) | `stg-arith-C` | `stg-arith-D` | `stg-rec-arith2` |
| formula-check-data | `stg-data-A` | `stg-data-B` | `stg-rec-data` |
| formula-check-edge-cases | `stg-edge-A` | `stg-edge-B` | `stg-rec-edge` |
| source-data-check | `stg-srcdt-A` | `stg-srcdt-B` | `stg-rec-srcdt` |
| formula-check-structure | `stg-struct-A` | `stg-struct-B` | `stg-rec-struct` |
| consistency-check + key-params-check *(combined)* | `stg-consist-A`, `stg-kp-A` | `stg-consist-B`, `stg-kp-B` | `stg-rec-con` (consistency), `stg-rec-kp` (key-params) |
| formula-check-voi | `stg-voi-A` | `stg-voi-B` | `stg-rec-voi` |
| sources | `stg-src-A` | `stg-src-B` | `stg-rec-src` |
| heads-up-evidence | `stg-evid-A` | `stg-evid-B` | `stg-rec-evid` |
| heads-up-epi | `stg-epi-A` | `stg-epi-B` | `stg-rec-epi` |
| heads-up-intervention | `stg-int-A` | `stg-int-B` | `stg-rec-int` |
| readability | `stg-rdbl-A` | `stg-rdbl-B` | `stg-rec-rdbl` |
| leverage-funging | `stg-lev-A` | `stg-lev-B` | `stg-rec-lev` |
| ce-chain-trace | `stg-ce-A` | `stg-ce-B` | `stg-rec-ce` |
| leverage-uov-check | `stg-uov-A` | `stg-uov-B` | `stg-rec-uov` |
| **heads-up-epi (TA counterfactual burden)** *(TA BOTEC only)* | `stg-epi-C` | `stg-epi-D` | `stg-rec-epi-ta` |
| ce-chain-trace-ta *(self-detecting TA check)* | `stg-ceta-A` | `stg-ceta-B` | `stg-rec-ceta` |

Note: notes-scan (Step 7c) has no reconciliation pair — it runs as A/B, each writing to its own staging tab (`stg-nscn-A`, `stg-nscn-B`); the Wave 3 compaction agent deduplicates their overlapping findings in its standard Step 3 dedup pass. No reconcile agent is needed. formula-check-parameters (Step 3f) also has no reconciliation pair — it runs as a single instance writing to `stg-params`. The final-review compaction step reads both alongside all other staging tabs. The heads-up-epi TA counterfactual burden pair has no reconciliation agent for non-TA models — skip that row entirely when program context is not a TA BOTEC.

**Silent failure check after Wave 2.5 — do this before Wave 3**: After all reconciliation agents complete, check each reconcile staging sheet (stg-rec-*) and check whether each reconcile agent wrote its coverage declaration to chat. (Pairs confirmed empty in the pre-flight check are exempt — their skipped status was already logged.) A reconcile agent is a silent failure risk if its reconcile staging sheet contains only the header row (no AGENT_COMPLETE, no findings) OR if no coverage declaration for this pair appears in the current session context. Report any pair where either condition holds:

> ⚠️ Reconciliation failure warning: [pair name] reconcile agent produced no coverage declaration and its reconcile staging sheet (`stg-rec-[pair]`) contains no net-new findings. Its A/B divergences may be unreconciled. Consider re-running this reconcile agent before proceeding to Wave 3.

Exception: pairs where both A and B agents wrote zero findings (confirmed empty) produce no divergences to reconcile and zero net-new findings legitimately — verify this by reading the pair's staging-A and staging-B tabs before flagging.

**notes-scan completion check**: After all Wave 2.5 reconciliation agents complete, read staging sheets `stg-nscn-A` and `stg-nscn-B` separately. For each tab, check for an AGENT_COMPLETE marker independently:

If `stg-nscn-A` lacks an AGENT_COMPLETE marker:
> ⚠️ notes-scan-A silent failure suspected: no AGENT_COMPLETE in `stg-nscn-A`. notes-scan has no reconciliation pair, so this gap will not be caught by any reconcile agent. Consider re-running notes-scan-A before proceeding to Wave 3.

If `stg-nscn-B` lacks an AGENT_COMPLETE marker:
> ⚠️ notes-scan-B silent failure suspected: no AGENT_COMPLETE in `stg-nscn-B`. notes-scan has no reconciliation pair, so this gap will not be caught by any reconcile agent. Consider re-running notes-scan-B before proceeding to Wave 3.

Issue each warning independently — a clean `stg-nscn-A` does not suppress a `stg-nscn-B` warning.

**TA misclassification cross-check**: After all Wave 2.5 reconciliation agents complete and before starting Wave 3, verify that heads-up-intervention-B and ce-chain-trace-ta reached consistent TA/non-TA classifications. Run this check unconditionally — the dangerous case is a TA grant classified as non-TA (not the reverse), so gating on `is_ta_botec` would miss exactly the failures this check is designed to catch.

1. Read the AGENT_COMPLETE marker row from staging sheet `stg-int-B`. Extract the `Routing decision:` field from column F. **The `Routing decision:` field must appear as the first element in column F** — parse it as a prefix match: the field is present if column F starts with `Routing decision:`. If column F does not start with this prefix, treat the routing decision as missing and announce: `⚠️ TA cross-check: stg-int-B AGENT_COMPLETE row has no Routing decision prefix in column F — cannot determine TA classification for heads-up-intervention-B. Skipping mismatch check.`
2. Read the AGENT_COMPLETE marker row from staging sheet `stg-ceta-A`. First check whether an AGENT_COMPLETE row exists at all — if no AGENT_COMPLETE row is found, announce: `⚠️ TA cross-check: stg-ceta-A has no AGENT_COMPLETE marker — ce-chain-trace-ta-A may have failed silently. Skipping TA mismatch check; consider re-running ce-chain-trace-ta before Wave 3.` Then proceed to Step 4 (silent agree). Do not evaluate Steps 3a or 3b when stg-ceta-A has no AGENT_COMPLETE. If an AGENT_COMPLETE row is found, check whether column F contains `No TA grant signals found` (non-TA) or `TA grant signals confirmed:` (TA-positive canonical phrase).
3a. If heads-up-intervention-B declared `Routing decision: A — non-TA` but ce-chain-trace-ta-A column F contains `TA grant signals confirmed:` (its AGENT_COMPLETE does **not** contain `No TA grant signals found`), announce:

> ⚠️ TA classification mismatch: heads-up-intervention-B identified this as non-TA (ran Section A intervention checks only) but ce-chain-trace-ta found TA signals. If this is a TA grant, Section B TA grant checks were skipped by heads-up-intervention-B. Consider re-running heads-up-intervention with `is_ta_botec = true` in session context before Wave 3.

3b. If heads-up-intervention-B declared `Routing decision: B — TA` but ce-chain-trace-ta-A column F contains `No TA grant signals found` (not `TA grant signals confirmed:`), announce:

> ⚠️ TA classification mismatch: heads-up-intervention-B ran TA grant checks but ce-chain-trace-ta found no TA signals. Confirm with the researcher whether this is a TA grant — if not, the Section B TA checks may not apply and can be disregarded.

4. If both agree (both non-TA or both found TA signals), proceed silently.

**Wave 2.5 exit conditions** — confirm all before proceeding to Wave 3:
- [ ] All reconcile stg-rec-* sheets contain an AGENT_COMPLETE row (or confirmed empty pairs).
- [ ] Wave 2.5 silent failure check run — any unreconciled pairs flagged.
- [ ] notes-scan completion check run — both stg-nscn-A and stg-nscn-B checked independently.
- [ ] TA misclassification cross-check run (unconditionally — even for non-TA models).

---

### Wave 3 — Sequential (after Wave 2.5)

**Wave 3 entry conditions** — confirm all before running the self-verification pre-pass:
- [ ] Wave 2.5 exit conditions satisfied (all reconcile agents complete, TA cross-check run).
- [ ] Session context has output spreadsheet ID, source spreadsheet ID, staging tab list (from context or Dashboard A99).

**Progress announcement** before starting: `[Phase 3/4 done → Phase 4/4] Reconciliation complete — starting final review (4 sequential steps). If this session is interrupted before Wave 3 completes, run /givewell-vetting:vetting-finalize (plugin) or /vetting-finalize (standalone) with the output and source spreadsheet URLs to resume.`

**Self-verification pre-pass — required before spawning any Wave 3 agent**: Before compaction begins, verify that all required agents ran. For each agent in the table below, check that its staging tab contains an AGENT_COMPLETE row. Read each tab with `read_sheet_values` on `{tab}!A1:J100` (use a full range — AGENT_COMPLETE may not be in row 2 if the agent filed many findings) — an AGENT_COMPLETE row confirms completion. For standard staging-tab agents, AGENT_COMPLETE is in **column D**. For hardcoded-values and sensitivity-scan, check for AGENT_COMPLETE in any column — see the table notes at lines ending 'check for AGENT_COMPLETE row in any column' below.

| Required agent | Staging tab | Is 0-findings a plausible clean pass? |
|---|---|---|
| formula-check-arithmetic A | `stg-arith-A` | No |
| formula-check-arithmetic B | `stg-arith-B` | No |
| formula-check-data A | `stg-data-A` | Yes (check AGENT_COMPLETE text) |
| formula-check-data B | `stg-data-B` | Yes (check AGENT_COMPLETE text) |
| formula-check-edge-cases A | `stg-edge-A` | Yes |
| formula-check-edge-cases B | `stg-edge-B` | Yes |
| formula-check-structure A | `stg-struct-A` | No |
| formula-check-structure B | `stg-struct-B` | No |
| consistency-check A | `stg-consist-A` | No |
| consistency-check B | `stg-consist-B` | No |
| key-params-check A | `stg-kp-A` | Yes |
| key-params-check B | `stg-kp-B` | Yes |
| formula-check-voi A | `stg-voi-A` | Yes (self-detecting) |
| formula-check-voi B | `stg-voi-B` | Yes (self-detecting) |
| formula-check-parameters | `stg-params` | Yes |
| hardcoded-values | `'Hardcoded Values'!A:H` | No — check for AGENT_COMPLETE row in any column |
| sensitivity-scan | `'Confidentiality Flags'!A:D` | No — check for AGENT_COMPLETE row in any column |
| source-data-check A | `stg-srcdt-A` | Yes (skip if no source data tabs) |
| source-data-check B | `stg-srcdt-B` | Yes (skip if no source data tabs) |
| ce-chain-trace A | `stg-ce-A` | No |
| ce-chain-trace B | `stg-ce-B` | No |
| heads-up-evidence A | `stg-evid-A` | No |
| heads-up-evidence B | `stg-evid-B` | No |
| heads-up-epi A | `stg-epi-A` | No |
| heads-up-epi B | `stg-epi-B` | No |
| heads-up-intervention A | `stg-int-A` | Yes (check AGENT_COMPLETE text) |
| heads-up-intervention B | `stg-int-B` | Yes (check AGENT_COMPLETE text) |
| readability A | `stg-rdbl-A` | Yes (if pub readiness out of scope) |
| readability B | `stg-rdbl-B` | Yes (if pub readiness out of scope) |
| leverage-funging A | `stg-lev-A` | Yes (if no leverage tab) |
| leverage-funging B | `stg-lev-B` | Yes (if no leverage tab) |
| leverage-uov-check A | `stg-uov-A` | Yes (if no Leverage/Funging tab) |
| leverage-uov-check B | `stg-uov-B` | Yes (if no Leverage/Funging tab) |
| notes-scan A | `stg-nscn-A` | Yes (if pub readiness out of scope) |
| notes-scan B | `stg-nscn-B` | Yes (if pub readiness out of scope) |
| ce-chain-trace-ta A | `stg-ceta-A` | Yes (self-detecting — check AGENT_COMPLETE text) |
| ce-chain-trace-ta B | `stg-ceta-B` | Yes (self-detecting — check AGENT_COMPLETE text) |

**Checking hardcoded-values and sensitivity-scan**: These agents write directly to their output sheets, not to staging tabs. Read the last non-empty row of `'Hardcoded Values'!A:H` and `'Confidentiality Flags'!A:D` — look for a row where any column contains `AGENT_COMPLETE`. If absent and 0-findings is not plausible, treat as a silent failure.

**Checking skipped agents**: For any agent that was explicitly skipped (source-data-check when no source tabs exist, leverage-uov-check when no leverage tab exists, notes-scan when formula-only scope, readability when formula-only scope): confirm the skip was recorded in session context before the tab was created. If the tab is empty but the skip was NOT recorded, treat as a potential silent failure rather than a legitimate skip.

For any required agent whose staging tab is empty and where 0-findings is **not** a plausible clean pass: announce `⚠️ Pre-Wave-3 self-verification failed: [agent] staging tab [tab] is empty. Consider re-running this agent before compaction.` Proceed only after either re-running the missing agent or obtaining explicit researcher approval to proceed with incomplete coverage.

**Wave 3 session context** — pass to each Wave 3 agent:

> `Output spreadsheet ID: <id>` | `Source spreadsheet ID: <id>` | `Source spreadsheet URL: <url>` | `Vet scope: <full or formula-only>` | `CE baseline: <geography = cell = value, one per geography>` | `All staging tabs: [read from Dashboard A99 if not in context]` | `User email: <email>` | `Current date: <today>`
>
> **Staging tab recovery**: If the full staging tab list is not in current context (context may have been compacted since Wave 1), read Dashboard cells A99 onward of the output spreadsheet to recover the complete list before proceeding.

Run the four steps in order — each must complete before the next begins. Announce each step as it starts:
- Before 10a: `[Wave 3 — Step 1/4] Running compaction.`
- Before 10b: `[Wave 3 — Step 2/4] Running gap-fill.`
- Before 10c: `[Wave 3 — Step 3/4] Running validation.`
- Before 10d: `[Wave 3 — Step 4/4] Running dashboard.`

| Step | Agent file | Covers |
|---|---|---|
| 10a | `agents/final-review-compaction.md` | Route misrouted rows, deduplicate, sort, assign Finding IDs |
| 10b | `agents/final-review-gap-fill.md` | Formula cascade check, coverage gap scan, Won't Fix verification — if band-split was used, append `band1_end: {last_row_of_band_1}` to this agent's session context so it can run the cross-band root cause trace (Check 2.5). The gap-fill agent can also recover `band1_end` from Dashboard A154 if session context was compacted. **Cascade finding definition** (pass in session context): "A cascade finding is a new finding that identifies a cell that will remain wrong *after* a confirmed High/Formula finding is corrected — not the error itself, but a downstream cell whose formula assumed the old wrong value. File as Medium/Formula, at most 2 hops downstream." |
| 10c | `agents/final-review-validation.md` | Fix-validation, confidence intervals check, placeholder scan, CE impact completeness |
| 10d | `agents/final-review-dashboard.md` | Dashboard content, Key Findings summary in chat |

**Wave 3 exit conditions** — confirm all before proceeding to Final Summary:
- [ ] Compaction (10a) complete: all staging tabs read, findings sorted, Finding IDs assigned, misrouted rows corrected.
- [ ] Gap-fill (10b) complete: cascade check, coverage gap scan, Won't Fix verification, category coverage declaration all written.
- [ ] Validation (10c) complete: fix-validation, CI check, placeholder scan, CE impact completeness checked.
- [ ] Dashboard (10d) complete: Dashboard written, Key Findings summary presented in chat.

---

## Final Summary

After all agents complete, announce `[Vet complete — Phase 4/4 done]`, then:

**Step 1 — Present results to the user**:

**Findings Sheet (Google Sheet):** [link]

One-line count: e.g., "13 findings: 2 High, 6 Medium, 5 Low — 4 require researcher input"

**Step 2 — Collect pilot feedback**

Ask the researcher the following six questions. Present them as a labelled block so they are easy to copy and answer:

```
Vetting skill feedback — 6 quick questions (answers go into a shared log to improve the skill):

1. False positives — Were any findings things Claude flagged that were not real issues? If so, which Finding IDs and briefly why they were wrong.
2. Missed findings — Did Claude miss anything significant you had to catch yourself? Briefly describe.
3. Most useful — Which part of the output was most useful to you?
4. Calibration suggestion — Is there one thing you'd like Claude to do differently next time?
5. Confidentiality flags — Did Claude miss any cells or sections that should have been flagged as potentially confidential? If so, briefly describe.
6. Box links — Did Claude miss any Box links in the spreadsheet that should have been flagged?

(You can skip any question — just reply with the numbers you want to answer.)
```

**Local mode**: If running in local mode (MCP unavailable), follow the feedback instructions in the "No-MCP / Local output mode" section (Step 8 — Feedback collection in local mode). Do not attempt to write to the Google Sheet or send a Slack DM. Skip steps a–d below entirely.

**Standard mode**: After the researcher responds, record their answers in the shared pilot feedback log:

**a. Use the canonical feedback sheet**

The feedback sheet is always: `https://docs.google.com/spreadsheets/d/1Ees1qo3N5SSTzo6MDDrCpvJEVrgANCTqRET6ak3glWM/`

Use spreadsheet ID `1Ees1qo3N5SSTzo6MDDrCpvJEVrgANCTqRET6ak3glWM` for all writes. Do not search for or create a new sheet.

**b. Append the feedback row**

Find the first empty row in column A (read `A:A` and count non-empty cells; first empty = that count + 1 — the header row is included in the non-empty count, so count already accounts for row 1). Write one row at that position:
- A: today's date (ISO format: YYYY-MM-DD)
- B: researcher email (from session context)
- C: source spreadsheet name (from `get_spreadsheet_info` results)
- D: false positives answer (truncated to 500 characters if longer)
- E: missed findings answer
- F: most useful answer
- G: calibration suggestion
- H: confidentiality flags missed answer
- I: Box links missed answer

**c. Notify the skill maintainer via Slack DM**

After writing the feedback row, send a direct Slack message to Meghna Ray (`meghna.ray@givewell.org`) to notify her of the new submission:

1. Use `mcp__claude_ai_Slack__slack_search_users` with query `meghna.ray@givewell.org` to get her Slack user ID.
2. Use `mcp__claude_ai_Slack__slack_send_message` to send a DM to that user ID with the following content:

```
New vetting skill feedback submitted

Researcher: [researcher email]
Spreadsheet: [source spreadsheet name]
False positives: [answer or "none / skipped"]
Missed findings: [answer or "none / skipped"]
Calibration suggestion: [answer or "skipped"]
Confidentiality flags missed: [answer or "none / skipped"]
Box links missed: [answer or "none / skipped"]
Feedback sheet: [link]
```

If `mcp__claude_ai_Slack__slack_search_users` returns no result for that email, skip the Slack notification silently — do not surface an error to the researcher.

**d. Share the link**

Tell the researcher: "Feedback recorded — thank you. [feedback sheet link]"

If the researcher skips all six questions, record a blank row for the date and spreadsheet name only, and do not prompt again.
