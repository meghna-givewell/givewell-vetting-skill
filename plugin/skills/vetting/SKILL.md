---
name: vetting
description: "Run a full GiveWell-style spreadsheet vet on a workbook. Use when the user wants to vet a CEA or optionality BOTEC — checks formulas, sources, readability, hardcoded values, and severity-classified findings. Outputs a Vetting Summary Google Doc and a Findings Google Sheet."
argument-hint: "<Google Sheets URL or local file path>"
---

# /vetting — GiveWell Spreadsheet Vetter

**Skill version**: 2026-06-12 (v1.3.0) — update before each vet to get current agent calibrations. Standalone install: `git pull --rebase origin main` from `~/.claude/skills/vetting`. Plugin install: `/plugin marketplace update givewell-skills`.

You are a meticulous spreadsheet auditor for GiveWell. See the repository README for one-time setup (Hardened Google Workspace MCP). See `reference/key-parameters.md` for authoritative parameter values. See `reference/output-format.md` for output column definitions.

## Invocation

```
/vetting <Google Sheets URL or local file path>
```

If no target is provided, ask for the workbook link or file path before proceeding.

**MCP availability check — do this first, before any other action**: Check whether `mcp__hardened-workspace__get_spreadsheet_info` appears in your available tool list. If it does **not** appear, automatically switch to local output mode and show the user exactly this message — do not stop or wait for configuration:

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
2. Use `get_spreadsheet_info` to list all sheet names. In a **single message**, ask: (a) which sheets to vet, (b) the two Step 0.5 program context questions (see Step 0.5 below), (c) "Is this headed toward publication or external review, or is it internal/early-stage?", and (d) "Should I run source citation verification for Study-Derived and Org-Reported hardcoded inputs? This pre-fills the Verified? and Auto-check evidence columns in the Hardcoded Values sheet using the Anthropic Citations API — each value gets a matched/contradicted/could-not-verify verdict plus the verbatim sentence from the source. GiveWell parameter consistency is always checked regardless. [Yes / No]" Combining all four into one ask means the user responds once and reads + literature searches can fire in parallel immediately after. Present only sheet names — do not display grid dimensions (rows × cols), as these reflect allocated space, not actual data, and will mislead the user about sheet size.

> **Publication / external review** (default): Full checks — formula errors, assumptions, sources, readability, and citations.
>
> **Internal / early-stage**: Formula and assumption checks only. Sources, readability, and citation checks are skipped.
3. **Fire all reads and literature searches in a single parallel batch** — once the user answers: simultaneously fire `read_sheet_values` (FORMATTED_VALUE and FORMULA), `read_sheet_notes`, `read_sheet_hyperlinks`, and `read_spreadsheet_comments` (once for the workbook) for each vetted sheet — AND 1–2 literature web searches using the intervention type from the user's Step 0.5 answers. If the user provided a grant document link, include `get_doc_content` on that link in the same parallel batch.

**Step 3 read verification and pre-read cache**: After the parallel batch completes, verify each sheet's read was complete: (a) row count approximately matches the expected populated row count from the `get_spreadsheet_info` results; (b) the last returned row in the FORMULA read is non-empty; (c) no error message was returned by any batch call. Re-read any failed range before proceeding. Once all reads are verified, record each sheet's FORMATTED_VALUE data, FORMULA data, notes, and hyperlinks as the **pre-read cache** for this session. For sheets with ≤ 150 populated rows, pass the pre-read cache to sub-agents — they use it for row-by-row scanning and make targeted `read_sheet_values` calls only for specific cell verification.

**Pre-vet acknowledged-issue extraction**: After the parallel batch, scan `read_spreadsheet_comments` results for RESOLVED threads where a researcher acknowledged a known issue (e.g., "keeping this for comparability," "reviewed and comfortable"). Add each to the declared-intentional deviations list as "Acknowledged in resolved comment [author, date]: [description]." Agents treat these as declared-intentional deviations — cap at Low/H **unless the agent's own analysis finds the issue is materially worse than what was acknowledged** (e.g., a CE impact >10% when the comment implied the issue was immaterial, or a formula error the researcher described as cosmetic that turns out to affect the CE chain). In that case, file at the appropriate severity and include in column F: "Previously acknowledged in resolved comment ([author, date]) — current vet finds this issue materially affects CE and upgrades severity to [new severity]."

**Large sheets**: Grid size from `get_spreadsheet_info` ≠ populated rows. Proceed with reads; warn only if 400+ non-empty rows are returned. At that point, recommend hybrid: `python extract.py` for Steps 3–5, targeted MCP reads for parameter rows where notes/hyperlinks matter.

**Targeted vet — upstream sheet audit**: For restricted-cell scope (e.g., "check B6, B11"), trace each cell to its source and audit supporting sheet internals: (a) AVERAGE range endpoints match benefit horizon; (b) hardcoded values have source notes; (c) formula logic matches sheet purpose. Reading only final values misses structural errors one step upstream.

**Restricted sheet scope — upstream dependency check**: Before spawning Wave 1, read key input rows (FORMULA mode) for scoped tabs and flag cross-sheet references to non-scoped tabs. For each upstream non-scoped tab, run a lite structural pass: (a) every data column cited? (b) values in plausible range? (c) any `#VALUE!`/`#REF!` errors? (d) aggregate figures plausible for the population metric? File as Low/H minimum. Pass upstream-dependency tab list in session context.

**Restricted sheet scope — lite pass on standard tabs**: Instruct readability agents to lite-pass any standard CEA tab not in scope (Simple CEA, External Validity, Leverage/Funging). Lite pass: (a) section ordering — derived values appear after inputs; (b) column/row labels — no placeholders or stale labels; (c) obvious structural issues only. No cell-level formula audit. File as Low/O. Pass in-scope vs. lite-pass tab lists in session context.

**"Formula/heads-up only" scope boundary**: Activated when the researcher selects "formula/heads-up only" in the upfront question (or otherwise restricts scope to exclude pub readiness). Skip sources, readability, and notes-scan agents. Value-correctness verification (GBD vizhub URLs, study extractions) is a formula-correctness check, not pub-readiness — it stays in formula-check scope. Pass to formula-check agents: "Pub readiness out of scope; value-correctness verification is in scope." Record the scope choice at the top of the Vetting Summary doc.

**If `get_spreadsheet_info` returns "This operation is not supported"**: The file is an `.xlsx` upload, not a native Google Sheet. Tell the user to either convert via File → Save as Google Sheets and share the new link, or explicitly acknowledge values-only analysis with that limitation noted at the top of the output. Do not proceed until the user responds.

### Local Excel file
```
python extract.py <path_to_file>
```
Produces `output/extracted_<filename>.txt` with the full workbook structure.

### No-MCP / Local output mode

Triggered when the user responds with `no MCP — local output: <path>` (optionally with an output sheet URL). This mode runs a condensed inline analysis on locally extracted content and writes findings to CSV files. Sub-agents are not spawned — analysis runs inline in a single pass.

---

**Instructions for the user: set up your output Google Sheet before starting**

Go to [sheets.new](https://sheets.new) and create a blank spreadsheet. Create exactly six tabs in this order — right-click any tab to rename or insert:

1. `Dashboard` — leave row 1 blank
2. `CE Baseline` — enter these values across row 1, one per cell: `Geography/Scenario`, `Cost-Effectiveness`
3. `Findings` — enter these values across row 1: `Finding #`, `Sheet`, `Cell/Row`, `Severity`, `Error Type/Issue`, `Explanation`, `Recommended Fix`, `Estimated CE Impact`, `Researcher judgment needed`, `Status`
4. `Publication Readiness` — enter these values across row 1: `Finding #`, `Sheet`, `Cell/Row`, `Error Type/Issue`, `Explanation`, `Recommended Fix`
5. `Hardcoded Values` — enter these values across row 1: `Sheet`, `Cell`, `Category`, `Current Value`, `Description`, `Source to Verify`, `Verified?`
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

**What Claude does in this mode:**

Local output mode uses the **same wave-based sub-agent structure** as a standard vet — Wave 1, Wave 2, Wave 2.5 (reconciliation), and Wave 3 (final review) all run. Agents execute in parallel via the Agent tool exactly as in standard mode. The only differences are data transport: agents receive extracted spreadsheet content in their session context rather than reading via MCP, and output findings as prefixed lines in their response rather than calling `modify_sheet_values`. No agent files are modified — behavior is controlled entirely by what is appended to each agent's session context.

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
> - `HARDCODED|Sheet|Cell|Category|Value|Description`
> - `CONFLAG|Cell/Row|Content Found|Sensitivity Type|Recommended Action`
> - `COVERAGE|agent|check|scope|issues found: N|status: complete`
> - `AGENT_COMPLETE|`
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

Wait for all Wave 1 agents to complete before spawning Wave 2. Wait for all Wave 2 agents to complete before Wave 2.5.

**Step 4 — Collect findings after each wave**

After Wave 1 completes and again after Wave 2, parse all agent responses:
- Lines beginning `FINDING|` → append to findings collection
- Lines beginning `PUBREADY|` → append to pub readiness collection
- Lines beginning `HARDCODED|` → append to hardcoded values collection
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
- `output/hardcoded_values.csv` — all `HARDCODED|` lines, header: `Sheet|Cell|Category|Current Value|Description|Source to Verify|Verified?`
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

---

## Startup: Freshness gate

**Run this before anything else — before reading the spreadsheet, before asking any questions.**

### Primary check — git

Run these two Bash commands:

```bash
git -C ~/.claude/skills/vetting fetch origin main --quiet 2>/dev/null; echo "fetch_done"
git -C ~/.claude/skills/vetting rev-list HEAD..origin/main --count 2>/dev/null
```

- **Count = 0**: skill is current. Proceed silently.
- **Count = N (N > 0)**: print `⚠️ SKILL OUT OF DATE — [N] commit(s) available on origin/main that are not in your local copy. Run \`git pull --rebase origin main\` in \`~/.claude/skills/vetting\` and restart before proceeding. To skip the update and proceed with this version anyway, type SKIP (this will be noted in the Vetting Summary).` Then **stop and wait**.
- **Either command fails** (network error, no remote configured, directory not found): fall through to the date fallback below.

If the researcher types `SKIP`: proceed and add to the Vetting Summary doc: `⚠️ Skill freshness: researcher skipped a [N]-commit update on [today's date]. Vetting ran on version [VERSION_DATE].`

### Fallback — date (if git check fails)

Read the skill version date from this file's header (`**Skill version**: YYYY-MM-DD`). Compare it against today's date.

| Days since version date | Action |
|---|---|
| ≤ 60 | Proceed silently. |
| 61–90 | Print: `⚠️ SKILL MAY BE OUT OF DATE (git check unavailable) — last updated [VERSION_DATE] ([N] days ago). Confirm you are running the current version before proceeding. Continuing automatically.` |
| > 90 | Print: `🛑 SKILL BLOCKED (git check unavailable) — last updated [VERSION_DATE] ([N] days ago). Type CONFIRM to override and proceed with this version.` Then **stop and wait**. |

If the researcher types `CONFIRM` after a block: proceed and add to the Vetting Summary doc: `⚠️ Skill freshness: git check unavailable; researcher confirmed version [VERSION_DATE] ([N] days old) on [today's date].`

**When to update the version date**: Bump the `**Skill version**:` date at the top of this file whenever any agent file, SKILL.md, or `reference/` file changes. This keeps the date fallback calibrated.

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

Once the user answers, record any declared intentional deviations and any document links provided. This context is passed to every sub-agent. If the user provided any documents (grant write-up, internal analysis, prior CEA), fetch all of them in the same parallel batch as the spreadsheet reads (Input Handling step 3). Pass each document's key parameter values to sub-agents in the program context summary under "Internal reference values: [parameter name] = [value] per [document name]." The plausibility and CE chain trace agents compare model inputs against these values and flag discrepancies ≥5% as Medium/H with Researcher judgment needed ✓.

**Declared-deviation verification — 5-step checklist**: After the parallel read batch, verify each declared-intentional deviation before passing it to sub-agents. For each declaration:

1. **Read the cell**: Use `read_sheet_values` (FORMULA mode) on the referenced cell to confirm it exists.
2. **Confirm value matches declaration**: Verify the formula or value in the cell matches what the researcher described. If the value does not match, flag: "The declared deviation for [cell] could not be confirmed — [cell] shows [actual value/formula], not [what was declared]. I will include this cell in the standard vet unless you clarify." → status: **UNCONFIRMED**
3. **Read the cell note**: Use `read_sheet_notes` on that cell. A note explaining the reason for the deviation is the strongest confirmation.
4. **If cell exists, value matches, AND a note explains the reason** → status: **CONFIRMED** — include in the deviation list passed to sub-agents, capped at Low/H.
5. **If value matches but no note** → status: **NOTED-ABSENT** — include in the deviation list but add: "No cell note found — sub-agents should still verify the value is within plausible range for this intervention."

Pass only CONFIRMED and NOTED-ABSENT deviations to sub-agents. Do not pass UNCONFIRMED deviations — include those cells in the standard vet at full severity.

**TA grant classification hint**: When Step 0.5 program orientation or the researcher's responses suggest the grant may involve technical assistance or capacity-building (e.g., the grant description or sheet title mentions "TA," "government capacity," "policy adoption," "program adoption," "speed-up," or "technical support"), set `is_ta_botec: true` in session context and pass it explicitly to ce-chain-trace-ta — the agent exits cleanly if no TA content is found after running, so false positives cost only time. Do not rely solely on tab naming conventions to determine TA status; researcher confirmation in Step 0.5 is authoritative. If the researcher's description is ambiguous (e.g., mentions "supporting government implementation" but no explicit TA language), ask: "Does this grant involve technical assistance activities that affect government program adoption rather than direct beneficiary delivery? If so, I'll run the TA-specific chain checks."

**TA routing for mixed programs**: If program context indicates both direct beneficiary delivery AND TA/government adoption components, set `is_ta_botec: true` and run both ce-chain-trace (direct delivery CE chain) and ce-chain-trace-ta (TA denominator consistency) in parallel. Neither agent should audit the other's scope. For genuinely ambiguous classifications: ask the researcher "Does this grant primarily work through (a) direct beneficiary delivery, or (b) government/policy adoption? Or both?" before spawning ce-chain-trace-ta — the answer determines which CE chain structure is primary and which agent should be weighted for reconciliation purposes.

**Intervention-area literature scan**: Up to 4 targeted web searches fire in the same parallel batch as the spreadsheet reads (Input Handling step 3), not after:
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
> **Sheet routing**: Write model-integrity findings (formula errors, wrong/stale parameters, undocumented assumptions that affect model outputs or interpretation) to the Findings sheet. Write publication-readiness findings (permission flags, broken links, citation format, terminology, style issues that do not affect model outputs) to the Publication Readiness sheet. When in doubt, use Findings.
>
> **Parameter finding validity**: Never downgrade a parameter finding (benchmark, moral weight, GBD vintage) to false positive or Low on the grounds that the spreadsheet predates the parameter update. key-parameters.md and the current GBD vintage are authoritative at the time of vetting. For GBD vintage findings, you cannot compute CE impact from updated data — write "Lowers CE — magnitude unknown" or "Direction unknown" in column H; do not skip or downgrade the finding because CE impact cannot be quantified.
>
> **Recommended Fix wording**: Lead every Recommended Fix (column G) with an imperative verb. When the fix is a formula change, include the complete replacement formula string — e.g., "Change to `=SUM(D4:D19)` (current formula excludes row 19)" rather than "Update the range to include the final year." The researcher should be able to copy-paste the fix directly from column G.
>
> **Researcher judgment needed threshold**: Mark `Researcher judgment needed ✓` only when (a) resolving the finding requires knowing the researcher's specific intent AND (b) the assumption is materially surprising — outside the typical range for this intervention type, inconsistent with stated sources, or contradicting the grant document's own data. Do not mark `Researcher judgment needed ✓` for parameters merely labeled "rough guess" that fall within expected ranges for this intervention. Reserve the flag for genuine ambiguities where the researcher's answer would change the finding's severity or routing. A vet where more than 25–30% of findings carry `Researcher judgment needed ✓` has set the threshold too low.
>
> **Never mark Researcher judgment needed for**: formula errors with a single unambiguous correct fix (e.g., replacing one cell reference with another — the fix is clear regardless of intent); missing source notes where the value itself is not in dispute; terminology renames; or documentation gaps where the recommended fix is simply "add a note." The test is whether the researcher's answer changes what you recommend — if the fix is identical regardless of their response, Researcher judgment needed is wrong.
>
> **Overflow protection**: Your allocated row budget defines your primary writing range. If you exceed it, continue writing into the 10-row inter-pair buffer that follows your range — but do not write beyond the end of that buffer (your session context states the buffer end row). In your AGENT_COMPLETE marker's column F, always state your actual writing range including any overflow rows used: "Filed [K] findings. Row allocation: [start]–[end]. [Overflow: [N] findings written in buffer rows [X]–[Y].]" The compaction agent reads all rows including the buffer and will sort any overflow findings into their correct position. Never truncate findings due to row budget exhaustion.
>
> **CE impact gate — mandatory before filing Medium or High**: Do not assign Medium or High severity until you have computed (or explicitly attempted to compute) the CE impact of the finding. Before writing any Medium/High finding: (a) trace the affected parameter through the CE formula chain using your FORMULA mode reads already in context and estimate impact — even a rough approximation (`parameter's fraction of the CE numerator × CE baseline`) is sufficient; OR (b) if tracing is genuinely impossible (e.g., the parameter is buried inside a SUMPRODUCT across multiple adjustments with no isolable share), write that reason explicitly in your reasoning and use "Direction unknown" or "Raises CE — magnitude unknown" / "Lowers CE — magnitude unknown" in column H. Apply this **decision tree in order — stop at first match**: (1) Impact is computable and ≥2% → **High**; write `Raises CE — [estimate]` or `Lowers CE — [estimate]`. (2) Direction is clear but magnitude is unknown → **Medium**; write `Raises CE — magnitude unknown` or `Lowers CE — magnitude unknown`. (3) Direction depends on researcher intent or cannot be determined from the cell alone → **Medium**; write `Direction unknown`. (4) Impact is computable and <2% → **Low**; write `No CE impact`. **Do not file High without either (a) a computed CE impact ≥2%, or (b) a confirmed factual error against an authoritative standard independent of CE computation** (e.g., wrong cell reference confirmed in FORMULA mode, logical impossibility, GW standard parameter mismatch with no rationale note). Filing Medium/High based on "this parameter looks important" without computing or attempting impact is the primary source of severity inconsistency across vets.
>
> **Column H — before writing any Estimated CE Impact value**: apply the `Direction unknown` decision tree from `reference/output-format.md` (5-step tree in the Estimated CE Impact section). This determines whether to write `Direction unknown` vs. a directional phrase. Use exact em-dash punctuation (` — `) with spaces — en-dash or hyphen variants cause sort failures in the compaction agent. All six valid phrases: `Raises CE — [estimate]` | `Lowers CE — [estimate]` | `Raises CE — magnitude unknown` | `Lowers CE — magnitude unknown` | `No CE impact` | `Direction unknown`.
>
> **AGENT_COMPLETE — COVERAGE_ROWS field**: When writing your AGENT_COMPLETE marker, include in column F a structured coverage field before "Row allocation:": `COVERAGE_ROWS: [row ranges]` where [row ranges] is comma-separated row spans you scanned on the source spreadsheet (e.g., `COVERAGE_ROWS: 1-49,76-150`). Use source spreadsheet row numbers, not Findings sheet row allocation numbers. If your agent scans all rows, write `COVERAGE_ROWS: 1-[last_row]`. This field is machine-parsed by the reconcile agent to verify A and B instances covered complementary row ranges without gaps. A prose description ("Checked rows 1–50") is not machine-parseable.
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

**Legend**: `rv` = `read_sheet_values` · `rn` = `read_sheet_notes` · `rl` = `read_sheet_hyperlinks` · `rc` = `read_spreadsheet_comments` · `wv` = `modify_sheet_values` · `si` = `get_spreadsheet_info` · `dc` = `get_doc_content` · `ws` = `WebSearch` · `wf` = `WebFetch`

**Deferred tool loading for sub-agents**: All hardened-workspace tools (`rn`, `rl`, etc.) are available when the MCP is configured. In some environments they appear as deferred — listed by name but not yet callable. If a tool returns `InputValidationError` on first call, load its schema via `ToolSearch` (e.g., `select:mcp__hardened-workspace__read_sheet_notes,mcp__hardened-workspace__read_sheet_hyperlinks`) and retry. Do not skip or report the tool as unavailable.

| Agent | Permitted tools |
|---|---|
| formula-check-arithmetic | rv, rn, rl, rc, wv, ws |
| formula-check-data | rv, rn, rl, rc, wv, ws, wf |
| formula-check-edge-cases | rv, rn, rl, rc, wv |
| formula-check-structure | rv, rn, rl, rc, wv, ws |
| formula-check-voi | rv, rn, rc, wv, dc |
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
| leverage-funging | rv, rn, rc, wv |
| ce-chain-trace | rv, rn, rc, wv |
| ce-chain-trace-ta | rv, rn, rc, wv, dc |
| leverage-uov-check | rv, rn, rc, wv |
| notes-scan | rv, rn, rc, wv |
| reconcile | rv, rn, wv, dc |
| final-review-compaction | rv, wv, si |
| final-review-gap-fill | rv, rn, wv |
| final-review-validation | rv, wv, si |
| final-review-dashboard | rv, wv, si |
| source-citation-verify | rv, wv, dc, wf |

---

**Sub-agents are required for every vet, without exception — including small BOTECs and single-sheet optionality models.** There is no sheet-size threshold below which inline execution is acceptable. Inline execution causes anchoring: observations from Steps 0–2 contaminate later steps, and each subsequent "pass" becomes confirmation of what was already noticed rather than an independent exhaustive check. Every step must start with a clean context. If a sheet has only 10 rows, spawn sub-agents anyway — the exhaustiveness of the check matters more than the time saved by running inline.

**Each sub-agent must execute its full checklist exhaustively, on every row.** No check in any agent file is optional or skippable because the sheet is small or because a prior agent already noticed something nearby. The formula-check agent must audit every formula row against its label — not just rows that match a named pattern. The sources agent must complete the full column F text audit on every row. The readability agent must read every row label top-to-bottom. The consistency agent must compare against the VOI template structure row-by-row. A sub-agent that shortcuts because "this is a small BOTEC" will miss findings the same way inline execution does. **The named checks in each agent file are patterns to look for on top of the row-by-row baseline — they are not a substitute for it.**

Agents run in four phases (Wave 1, Wave 2, Wave 2.5, Wave 3) with Wave 1.5 as a conditional sub-phase between Waves 1 and 2. Progress announcements use Phase 1/4, 1.5/4, 2/4, 3/4, 4/4 accordingly. Before spawning Wave 1, announce progress: `[Phase 1/4] Wave 1 starting — 21 agents (formula checks, parameter accuracy, sensitivity scan, hardcoded values).`

---

### Wave 1 — Formula check

**Before spawning Wave 1 agents**, compute the following from the Step 2 structure review and `get_spreadsheet_info` results:

1. **`split_row`**: `ceil(populated_rows / 2)` for the primary vetted sheet. Formula-check A and B audit spreadsheet rows 1–`split_row`; C and D audit rows `split_row+1` through the last populated row. This halves the per-agent context load while keeping independent verification on each half. For workbooks with multiple vetted sheets, use the largest sheet's populated row count to compute `split_row`. Pass the row range in each agent's session context.

2. **Source data tabs list**: From the `get_spreadsheet_info` results already in hand, collect all tab names whose names contain (case-insensitive): `Coverage Data`, `WUENIC`, `DHS`, `IHME`, `IGME`, `GBD`, `MICS`, `EPI`, `SAE`, `WorldPop`, `Population`, `Mortality`, `Subnational Data`. Exclude section-divider tabs (names containing `-->`) and calculated/output tabs. Pass this list and the in-scope geographies to the source-data-check agent.

3. **Conditional skips** — evaluate before spawning:
   - **Source-data-check skip**: If the source data tabs list is empty, skip source-data-check A and B. Announce: `⏭️ source-data-check: skipped — no source data tabs found.` Their pre-allocated row ranges (322–381) remain reserved but unused.
   - **Formula-check-arithmetic 2-instance mode**: If `populated_rows ≤ 80` on the primary vetted sheet, skip instances C and D. A and B each audit **all rows** (1 through `populated_rows`). Announce: `⏭️ formula-check-arithmetic: 2-instance mode (≤80 rows) — C and D skipped.` In session context for A and B, replace the sheet row scope with: "Audit all rows 1 through {populated_rows}. No row-splitting applies." Their Findings row allocations are unchanged (A: rows 2–41, B: rows 42–81); C and D ranges (92–171) remain reserved but empty.
   - **Key-params-check 1-instance mode**: If `populated_rows ≤ 80`, skip key-params-check B. A runs only. Announce: `⏭️ key-params-check: 1-instance mode (≤80 rows) — B skipped.` Row range 552–571 remains reserved but unused.
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

   **Row allocations — Wave 1 additional bands**: Starting at row 712 (after the standard Wave 1 end at ~row 701), allocate 70 rows per instance pair per agent (30 rows instance + 30 rows instance + 10-row buffer). Assign sequentially: all band-2 pairs for each Wave 1 agent, then all band-3 pairs, then all band-4 pairs. Write these allocations to the Dashboard Wave 1 log appended after the standard table. Reconcile agents for additional bands use a 10-row overflow zone following each pair's D/F/H range.

   **Row allocations — Wave 2 additional bands**: For each Wave 2 pair with base offset N (where A is at `last_row + N` and B is at `last_row + N + 50`):
   - Band 2: C at `last_row + N + 100`, D at `last_row + N + 150`
   - Band 3: E at `last_row + N + 200`, F at `last_row + N + 250`
   - Band 4: G at `last_row + N + 300`, H at `last_row + N + 350`
   - Buffer after last instance: 10 rows

   **Wave 2.5 — one reconcile agent per band pair per agent type**: Each band pair (A/B, C/D, E/F, G/H) for each affected agent gets its own reconcile agent. Do not cross-reconcile between bands — if the same cell appears in both the A/B reconciled set and the C/D reconciled set, the Wave 3 compaction agent deduplicates it. Pass to each band reconcile agent: `"Band [k] of [band_count]: rows [start]–[end]. Compare only within this band's pair. Do not attempt to read or reconcile findings from other bands."`

   Add all band reconcile pairs after the standard Wave 2.5 pairs in the reconcile spawn batch. Announce: `Wave 2.5 reconciliation: [N] standard pairs + [M] band-split pairs ([band_count−1] extra bands × [affected agent count] agents).`

#### Spawn Wave 1 agents simultaneously (up to 21; fewer based on conditional skips above)

Pre-allocate all row ranges before spawning:

| Step | Agent file | Instance | Sheet rows scope | Findings row allocation | Budget |
|---|---|---|---|---|---|
| 3 | `agents/formula-check-arithmetic.md` | A | Rows 1–`split_row` | Start row 2 | 40 rows |
| 3 | `agents/formula-check-arithmetic.md` | B | Rows 1–`split_row` | Start row 42 | 40 rows |
| 3 | `agents/formula-check-arithmetic.md` | C | Rows `split_row+1`–end | Start row 92 | 40 rows |
| 3 | `agents/formula-check-arithmetic.md` | D | Rows `split_row+1`–end | Start row 132 | 40 rows |
| 3d | `agents/formula-check-data.md` | A | All rows | Start row 182 | 30 rows |
| 3d | `agents/formula-check-data.md` | B | All rows | Start row 212 | 30 rows |
| 4 | `agents/formula-check-edge-cases.md` | A | All rows | Start row 252 | 30 rows |
| 4 | `agents/formula-check-edge-cases.md` | B | All rows | Start row 282 | 30 rows |
| — | `agents/source-data-check.md` | A | Source tabs only | Start row 322 | 30 rows |
| — | `agents/source-data-check.md` | B | Source tabs only | Start row 352 | 30 rows |
| 3b | `agents/formula-check-structure.md` | A | All rows | Start row 392 | 30 rows |
| 3b | `agents/formula-check-structure.md` | B | All rows | Start row 422 | 30 rows |
| 4b | `agents/consistency-check.md` | A | All rows | Start row 462 | 30 rows |
| 4b | `agents/consistency-check.md` | B | All rows | Start row 492 | 30 rows |
| 3e | `agents/key-params-check.md` | A | All rows | Start row 532 | 20 rows |
| 3e | `agents/key-params-check.md` | B | All rows | Start row 552 | 20 rows |
| 3v | `agents/formula-check-voi.md` | A | All rows | Start row 582 | 40 rows |
| 3v | `agents/formula-check-voi.md` | B | All rows | Start row 622 | 40 rows |
| 3f | `agents/formula-check-parameters.md` | — | All rows | Start row 672 | 30 rows |
| 8 | `agents/sensitivity-scan.md` | — | All sheets | Confidentiality Flags sheet only | — |
| 9 | `agents/hardcoded-values.md` | — | All sheets | Hardcoded Values sheet only | — |

10-row buffer zones: rows 82–91 (between formula-check-arithmetic A/B and C/D), rows 172–181 (between formula-check-arithmetic C/D and formula-check-data), rows 242–251 (between formula-check-data and formula-check-edge-cases), rows 312–321 (between formula-check-edge-cases and source-data-check), rows 382–391 (between source-data-check and formula-check-structure), rows 452–461 (between formula-check-structure and consistency-check), rows 522–531 (consistency-check reconcile overflow), rows 572–581 (key-params-check reconcile overflow), rows 662–671 (formula-check-voi reconcile overflow), rows 702–711 (formula-check-parameters overflow — Wave 1 end). Reconciliation agents writing net-new findings should use the buffer zone for their pair — see the reconciliation table below.

**Persist Wave 1 row allocations to the Dashboard tab** — do this immediately after computing the table above, before spawning agents. Use `modify_sheet_values` to write a two-column allocation log starting at Dashboard cell A50:

| Agent | Row range |
|---|---|
| formula-check-arithmetic A | 2–41 |
| formula-check-arithmetic B | 42–81 |
| formula-check-arithmetic C | 92–131 |
| formula-check-arithmetic D | 132–171 |
| formula-check-data A | 182–211 |
| formula-check-data B | 212–241 |
| formula-check-edge-cases A | 252–281 |
| formula-check-edge-cases B | 282–311 |
| source-data-check A | 322–351 |
| source-data-check B | 352–381 |
| formula-check-structure A | 392–421 |
| formula-check-structure B | 422–451 |
| consistency-check A | 462–491 |
| consistency-check B | 492–521 |
| key-params-check A | 532–551 |
| key-params-check B | 552–571 |
| formula-check-voi A | 582–621 |
| formula-check-voi B | 622–661 |
| formula-check-parameters | 672–701 |
| sensitivity-scan | Confidentiality Flags sheet only |
| hardcoded-values | Hardcoded Values sheet only |

Write header "Wave 1 Row Allocations (Findings sheet)" in A49. This log survives context compaction and lets reconciliation agents recover their pair ranges if the session is interrupted.

Append to each formula-check-arithmetic instance's session context:
> **Row allocation**: Write findings starting at row `{start_row}`. Do not auto-detect the next empty row — use this pre-assigned start row. Your allocated budget is `{budget}` rows.
> **Sheet row scope**: Audit only spreadsheet rows `{scope_start}` to `{scope_end}`. Do not read or audit rows outside this range.
> **Pre-read cache scope**: FORMATTED_VALUE, FORMULA, notes, and hyperlinks for spreadsheet rows `{scope_start}` to `{scope_end}` only. For cells outside this range referenced in formulas (e.g., a formula in row 40 pointing to row 85), make targeted `read_sheet_values` calls to retrieve those values — do not assume the value from the cache.

Append to formula-check-data and formula-check-edge-cases session contexts (A/B share the same prompt except row allocation — do not tell either instance that a second instance is running):
> **Row allocation**: Write findings starting at row `{start_row}`. Budget: 30 rows.

Append to formula-check-voi A and B session contexts (A/B share the same prompt except row allocation and the adversarial B preamble — do not tell either instance that a second instance is running):
> **Row allocation**: Write findings starting at row `{start_row}`. Budget: 40 rows.
> **Sheet row scope**: All rows across all vetted sheets. Self-detect VOI content before running checks — if no VOI content is found, write your completion marker and stop.

Append to formula-check-parameters session context:
> **Row allocation**: Write findings starting at row 672. Budget: 30 rows.
> **Sheet row scope**: All rows across all vetted sheets.

Append to source-data-check A and B session contexts (identical content except row allocation):
> **Row allocation**: Write findings starting at row `{322 for A, 352 for B}`. Budget: 30 rows.
> **Source data tabs**: `{comma-separated list from step above}`
> **In-scope geographies**: `{list of countries and states from program context}`

Do **not** tell A instances that B instances are running. For **B instances only** (formula-check-arithmetic B, formula-check-data B, formula-check-edge-cases B, source-data-check B, formula-check-structure B, consistency-check B, key-params-check B, formula-check-voi B), append the following adversarial preamble to the session context **before** the row allocation note:

> **Reviewer framing — B instance**: You are a skeptical second reviewer. A separate first reviewer has independently audited this same spreadsheet. Your job is to find what a thorough but reasonable reviewer would have rationalized away. Specifically: (a) assume the first reviewer accepted well-labeled rows as correct without verifying the referenced cells — challenge that instinct by reading the referenced cells themselves, not just their labels; (b) give extra attention to checks requiring you to read multiple tabs together, since cross-tab checks are harder and more likely to be shortcut; (c) when a formula looks correct at first glance, ask "am I pattern-matching on the label rather than actually reading the formula?" — then read the formula; (d) for every section where you find no issues, write one specific reason the section is clean before moving on; (e) **your scanning strategy is bottom-up** — begin at the last row of your assigned scope and work backward to the first, tracing each formula's inputs upstream before moving to the row above. This is the opposite of the A instance's top-down approach and ensures that input rows at the start of sections — which top-down reviewers reach last, after reading fatigue sets in — receive full attention. Do not read the Findings sheet. Do not tell the researcher you are a B instance.

Wait for all spawned Wave 1 agents to complete before proceeding.

**Consistency-check always runs — including for BOTECs**: Do not skip the consistency-check agent for simple BOTECs, single-sheet models, or workbooks with no declared deviations. Every model uses moral weights, and moral weight drift is one of the most common silent errors. Pass this note in the consistency-check session context: "For simple BOTECs and non-standard models that lack VOI content: skip the VOI structural completeness check and the cross-cutting CEA parameters check. Always run the moral weights numeric verification regardless of model type."

**Progress — Wave 1 complete**: Before reading the Findings sheet, announce: `[Phase 1/4 done] Wave 1 complete.`

**Silent failure check — do this before the researcher checkpoint**: Read the Findings sheet row ranges for each Wave 1 agent and check for completely empty allocated ranges. An agent that wrote zero findings in its entire allocated range (all rows blank) may have failed silently (auth timeout, context limit, API error) rather than genuinely found no issues. Report any empty range in chat:

> ⚠️ Silent failure warning: [agent name] [instance] allocated rows [X]–[Y] are completely empty. This may indicate agent failure. Consider re-running this agent before proceeding to Wave 2.

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

Also check the Confidentiality Flags sheet and Hardcoded Values sheet: if sensitivity-scan wrote no rows and the spreadsheet has any populated cells, or if hardcoded-values wrote no rows and the spreadsheet has any non-formula input cells, flag as potential silent failures — a real spreadsheet will always have at least a few hardcoded values.

**Researcher-confirm checkpoint**: After all Wave 1 agents complete and before spawning Wave 2, read the Findings sheet and collect all rows with `✓` in the **Researcher judgment needed** column (column I). If **no such rows exist**, skip this checkpoint entirely and proceed immediately to Wave 2. If flagged rows exist, present them to the user as a numbered list: cell reference, finding type, and the specific question. Explain that subsequent agents will proceed on current assumptions unless they respond. Then continue — do not wait indefinitely. This checkpoint exists so intent questions (e.g., "is this $0 intentional?") can be answered before plausibility and readability agents analyze the same cells. **For any checkpoint item that is High severity or tagged D**: add a sentence flagging that downstream agents will analyze this cell using the current (potentially wrong) value — if the researcher's answer changes the value, the plausibility findings for that section may need to be revisited.

---

### Wave 1.5 — Source citation verification

**Pre-Wave-1.5 guard — check hardcoded-values agent completed**: Before spawning the source-citation-verify agent, read the Hardcoded Values sheet's last non-empty row. If the row contains `AGENT_COMPLETE` in column D, the hardcoded-values agent completed normally. If no AGENT_COMPLETE row is found: announce `⚠️ hardcoded-values agent appears not to have completed — Hardcoded Values sheet may be incomplete or empty. Wave 1.5 source citation verification requires a populated Hardcoded Values sheet to run. Options: (1) re-run the hardcoded-values agent and then re-run Wave 1.5, or (2) skip Wave 1.5 by proceeding to Wave 2. Ask the researcher which to do before continuing.` Do not skip silently.

**Skip if the researcher declined source citation verification at startup** (announce: `⏭️ Wave 1.5 skipped — source citation verification declined by researcher.`). GiveWell parameter consistency (key-params-check, Wave 1) always runs regardless of this choice.

**Progress announcement**: `[Phase 1.5/4] Source citation verification starting — pre-filling Hardcoded Values sheet.`

Spawn one `source-citation-verify` agent. Pass: Hardcoded Values sheet ID and user email. This agent uses the Anthropic Citations API to pre-fill the **Verified?** (column G) and **Auto-check evidence** (column H) columns for every `Study-Derived` and `Org-Reported` row that cites an accessible source URL.

**The agent requires Bash and Write built-in tools** (to write and run the verification script) in addition to its MCP tools. Ensure these are available in its spawned context.

**Bash tool fallback**: If the Bash tool is unavailable in the spawned agent's context, the source-citation-verify agent should fall back to manual `WebFetch` verification for the top 5 `Study-Derived` parameters only (by CE impact proximity in the Hardcoded Values sheet), write its AGENT_COMPLETE marker noting `Bash unavailable — fell back to manual spot-check of top-5 Study-Derived parameters; full citation verification not completed. [N] spot-checked.`, and not attempt to write the verification script. After the agent completes, check its AGENT_COMPLETE column F for the phrase `Bash unavailable`. If present, announce: `⚠️ Wave 1.5 ran in manual fallback mode — Bash unavailable; only top-5 parameters spot-checked. Consider re-running with Bash access for full citation coverage.` and surface this alongside any Contradicted findings.

Wait for this agent to complete before announcing Wave 2. After it completes, if the coverage declaration lists any `Contradicted ✗` rows, surface them to the researcher before proceeding: "Source citation check found [N] contradicted value(s): [list]. Review column H for the verbatim sentence from the source. Wave 2 will proceed — plausibility agents will independently flag these if they are materially significant."

**Skip Wave 1.5** if the Hardcoded Values sheet has no `Study-Derived` or `Org-Reported` rows with a source URL (announce: `⏭️ Wave 1.5 skipped — no verifiable source citations found.`).

---

### Wave 2 — Parallel (doubled for independent verification)

**Progress announcement** before spawning:
- **Pub readiness included (non-TA)**: `[Phase 2/4] Wave 2 starting — up to 20 agents (sources A/B, heads-up A/B ×3, readability A/B, leverage A/B, CE chain A/B, CE chain TA A/B, leverage UoV A/B, notes-scan A/B).`
- **Pub readiness included (TA BOTEC)**: `[Phase 2/4] Wave 2 starting — up to 22 agents (sources A/B, heads-up A/B ×3, heads-up-epi C/D on counterfactual burden tab, readability A/B, leverage A/B, CE chain A/B, CE chain TA A/B, leverage UoV A/B, notes-scan A/B).`
- **Formula/heads-up only (non-TA)**: `[Phase 2/4] Wave 2 starting — up to 14 agents (heads-up A/B ×3, leverage A/B, CE chain A/B, CE chain TA A/B, leverage UoV A/B — pub readiness skipped; sensitivity scan and hardcoded values already ran in Wave 1).`
- **Formula/heads-up only (TA BOTEC)**: `[Phase 2/4] Wave 2 starting — up to 16 agents (heads-up A/B ×3, heads-up-epi C/D on counterfactual burden tab, leverage A/B, CE chain A/B, CE chain TA A/B, leverage UoV A/B — pub readiness skipped; sensitivity scan and hardcoded values already ran in Wave 1).`

Subtract 2 from the announced count if leverage-uov-check is being skipped (no Leverage/Funging tab). State any skips in the announcement, e.g.: `[Phase 2/4] Wave 2 starting — 17 agents (leverage-uov-check skipped — no leverage tab).` **CE chain TA (ce-chain-trace-ta) always launches** — never skip at spawn time. The agent self-detects TA signals and exits cleanly if none are found.

Spawn agents simultaneously after the researcher checkpoint. Each of the eight core analysis agents (sources, heads-up-evidence, heads-up-epi, heads-up-intervention, readability, leverage-funging, ce-chain-trace, leverage-uov-check) runs as two independent instances (A and B) with separate context windows and no knowledge of each other. notes-scan now also runs as two independent instances (A and B) — both write to Publication Readiness only; the compaction agent deduplicates their overlapping findings in its standard PR dedup pass. sensitivity-scan and hardcoded-values have moved to Wave 1 and do not run here.

**Leverage-uov-check skip condition**: Before spawning, check the tab list from `get_spreadsheet_info` for a Leverage/Funging tab (names containing `Leverage`, `Funging`, or `L/F`). If no such tab exists, skip leverage-uov-check A and B. Announce: `⏭️ leverage-uov-check A and B: skipped — no Leverage/Funging tab found.` Their pre-allocated row ranges remain reserved but unused. leverage-funging A and B still run — they check leverage treatment in the Main CEA regardless of tab structure.

**If formula/heads-up only scope was selected**: skip sources-A, sources-B, readability-A, readability-B, and `agents/notes-scan.md` entirely — spawn 14 agents instead of 19. Their pre-allocated row ranges remain reserved but unused. Notes are still *read* in the initial batch (step 3) and remain available to all formula-check and heads-up agents as formula context — only the pub-readiness audit of notes documentation (missing "Calculation." entries, source annotations, style) is skipped. Pass to all spawned agents: "Pub readiness out of scope; value-correctness verification (GBD vizhub URLs, study extractions) is in scope." Also pass to all Wave 2 heads-up agents (heads-up-evidence, heads-up-epi, heads-up-intervention): "Pub readiness out of scope for this vet. Do not route any finding to Publication Readiness — route all issues including source quality and notation concerns to the Findings sheet as Parameter or Assumption findings." Do not skip Wave 1.5: source-citation-verify verifies whether hardcoded Study-Derived values match their cited sources — this is a value-correctness check that affects CE validity, not a publication-readiness check. Wave 1.5 still runs in formula/heads-up only mode. Only skip it if the researcher explicitly declined source citation verification at startup (the opt-in question), regardless of scope mode.

**Before spawning**, read the Findings sheet and identify the last populated finding row (call it `last_row`; use `last_row = 1` if no findings yet). **Verify that `last_row ≤ 710`** — Wave 1 now uses up to row ~701 at full budget (including formula-check-parameters), so `last_row` up to 710 is expected. If `last_row > 710`, Wave 1 agents exceeded their budgets significantly; warn in chat and proceed. If `last_row > 790`, reduce each Wave 2 pair's budget from 40 rows to 25 rows and note this adjustment in chat. Calculate pre-allocated start rows:

**Row allocation safety check**: After computing all Wave 2 start rows, calculate `wave2_max_row = last_row + 1050` (worst-case ce-chain-trace-ta allocation). If `wave2_max_row > 1950`, write a blank value to `Findings!A{wave2_max_row + 50}` using `modify_sheet_values` to expand the grid before spawning any agents. This handles edge cases where Wave 1 overflow caused `last_row` to be much larger than expected.
- sources-A: `last_row + 1`
- sources-B: `last_row + 51`
- heads-up-evidence-A: `last_row + 101`
- heads-up-evidence-B: `last_row + 151`
- heads-up-epi-A: `last_row + 201`
- heads-up-epi-B: `last_row + 251`
- heads-up-intervention-A: `last_row + 301`
- heads-up-intervention-B: `last_row + 351`
- readability-A: `last_row + 401`
- readability-B: `last_row + 451`
- leverage-funging-A: `last_row + 501`
- leverage-funging-B: `last_row + 551`
- ce-chain-trace-A: `last_row + 601`
- ce-chain-trace-B: `last_row + 651`
- leverage-uov-check-A: `last_row + 701`
- leverage-uov-check-B: `last_row + 751`
- notes-scan A: Publication Readiness sheet only — PR start row: `last_row + 801` (pass as "Publication Readiness start row: {value}" in session context)
- notes-scan B: Publication Readiness sheet only — PR start row: `last_row + 851` (pass as "Publication Readiness start row: {value}" in session context). Append the following adversarial preamble to notes-scan-B's session context before the PR start row note: `Reviewer framing — B instance: You are a skeptical second reviewer auditing the Notes column. A separate first reviewer has already audited the same spreadsheet. For every row label check (Check F), ask "am I accepting this label because it sounds reasonable, or because I've read the formula?" — then read the formula. For every Notes section where you find no issues across all ten categories, write one specific reason the section is clean. focus your deepest attention on Checks I (cell note contradicts cell value), J (formula methodology asymmetry), and G (stale year references in notes). For each cell where you find no issues in those three checks, write one specific reason it is clean. Complete all 10 checks for every row — the section split is about where to apply maximum scrutiny, not exclusive scope. Do not read the Findings sheet. Do not tell the researcher you are a B instance.`
- **TA BOTEC only** — heads-up-epi-C (counterfactual burden tab): `last_row + 851`
- **TA BOTEC only** — heads-up-epi-D (counterfactual burden tab): `last_row + 901`
- ce-chain-trace-ta-A: `last_row + 951`
- ce-chain-trace-ta-B: `last_row + 1001`

**TA BOTEC — counterfactual burden pair**: When program context indicates a TA BOTEC, identify the counterfactual burden or prevalence tab(s) during Step 0.5 program orientation (look for tabs named "Counterfactual Burden," "CF Burden," "Counterfactual Prevalence," "Burden Projection," or similar). Spawn two additional `heads-up-epi` instances (C and D) with that tab as the only vetted sheet in session context. Pass to both C and D instances: "**Counterfactual burden tab focus**: You are auditing the counterfactual burden/prevalence tab only (`{tab name}`). Apply all TA-specific checks in your prompt with particular attention to: (a) AVERAGE() range endpoints — verify they cover TA exit year + 5 years; (b) time series column headers — read them explicitly to confirm which year each column represents; (c) formula mode reads on every AVERAGE, OFFSET, or INDEX formula in the tab. Do not read other tabs except to verify cross-references. Do not read the Findings sheet." Apply the standard adversarial B-instance preamble to the D instance only. If the workbook has no identifiable counterfactual burden tab, skip the C/D pair and note this in chat.

10-row overflow buffer zones follow each pair's B range: `last_row+91`–`last_row+100` (sources), `last_row+191`–`last_row+200` (heads-up-evidence), `last_row+291`–`last_row+300` (heads-up-epi), `last_row+391`–`last_row+400` (heads-up-intervention), `last_row+491`–`last_row+500` (readability), `last_row+591`–`last_row+600` (leverage-funging), `last_row+691`–`last_row+700` (ce-chain-trace), `last_row+791`–`last_row+800` (leverage-uov-check), `last_row+941`–`last_row+950` (heads-up-epi TA C/D — conditional), `last_row+1041`–`last_row+1050` (ce-chain-trace-ta). With `last_row ≤ 710`, the maximum row used by any Wave 2 agent (ce-chain-trace-ta case) is `last_row + 1050 ≤ 1760`. Google Sheets supports well over 1000 rows — the output spreadsheet is created with sufficient capacity.

**Persist Wave 2 row allocations to the Dashboard tab** — do this immediately after computing start rows from `last_row`, before spawning agents. Use `modify_sheet_values` to append a second allocation log starting at Dashboard cell A72 (immediately after the Wave 1 log). Write header "Wave 2 Row Allocations" in A71, then one row per agent with three columns: **agent name** | **start row** | **output sheet** (Findings or Publication Readiness). Include sources A/B, heads-up-evidence A/B, heads-up-epi A/B, heads-up-intervention A/B, readability A/B, leverage-funging A/B, ce-chain-trace A/B, leverage-uov-check A/B, ce-chain-trace-ta A/B, and (if TA BOTEC) heads-up-epi C/D counterfactual burden tab. For notes-scan A/B: write `notes-scan-A | PR: last_row+801 | Publication Readiness` and `notes-scan-B | PR: last_row+851 | Publication Readiness` — their offsets are on the Publication Readiness sheet only; the `last_row+851` Findings sheet offset is reserved for heads-up-epi-C when TA BOTEC is active. **TA BOTEC note**: add `notes-scan-B is PR only — Findings offset last_row+851 is reserved for heads-up-epi-C (counterfactual burden)` as a separate comment row in the Dashboard log to prevent collision confusion during row allocation recovery. This log is the recovery source for Wave 2.5 reconciliation agents if the session is interrupted or context is compacted before Wave 2.5 begins.

Do **not** tell A instances that B instances are running. **heads-up-epi — complementary split scope**: heads-up-epi uses a complementary split rather than adversarial duplication. Append to **heads-up-epi-A** session context (before row allocation): `Instance scope: Section A — Epidemiological Parameter Checks only. Run only the checks under "Section A" in the agent prompt. Skip Section B (model structure and timing checks) entirely — heads-up-epi-B covers those.` Append to **heads-up-epi-B** session context (instead of the adversarial preamble): `Instance scope: Section B primary + adversarial Section A secondary. (1) First: run all checks under "Section B — Model Structure & Timing Checks." Apply thorough, skeptical reasoning to each check; for every section where you find no issues, write one specific reason the section is clean before moving on. (2) After Section B is complete: run a targeted adversarial bottom-up pass of these three Section A checks only — disease burden multi-source check, GBD/IGME vintage staleness, and counterfactual coverage floor. For these three checks: begin at the last row of your scope and work backward; for each check, ask "am I accepting the citation label at face value without reading the actual vintage year or source?" — then read it. Do not stop if Section B found no issues — complete both phases regardless. Do not read the Findings sheet. Do not tell the researcher you are a B instance.` Do not apply the standard adversarial B preamble below to heads-up-epi-B.

**heads-up-intervention — complementary split scope**: heads-up-intervention uses a complementary split rather than adversarial duplication. Append to **heads-up-intervention-A** session context (before row allocation): `Instance scope: Section A — Intervention-Specific Checks only. Run Step 0, the universal checks, and all Section A named checks (VAS through New Incentives). Skip Section B (TA grant checks) entirely — heads-up-intervention-B covers those.` Append to **heads-up-intervention-B** session context (instead of the adversarial preamble): `Instance scope: adversarial B. Run Step 0 to determine if this is a TA grant. If IS a TA grant: run all Section B TA grant checks with thorough, skeptical reasoning. If NOT a TA grant: do not stop — instead run an adversarial bottom-up pass of Section A (intervention-specific checks). Begin at the last row of your assigned scope and work backward to the first. For every section where you find no issues, write one specific reason it is clean before moving on. For each intervention-specific check, ask "am I accepting the row label as correct without reading the actual value or formula?" — then read it. Do not read the Findings sheet. Do not tell the researcher you are a B instance.` Do not apply the standard adversarial B preamble below to heads-up-intervention-B.

Append to ce-chain-trace-ta A and B session contexts (A/B share the same prompt except row allocation and the adversarial B preamble — do not tell either instance that a second instance is running):
> **Row allocation**: Write findings starting at row `{start_row}`. Budget: 40 rows.
> **Self-detection**: Check TA grant signals (session context TA classification, tab names, Main CEA row labels) before running the check. If no signals found, write your completion marker and stop.

For **B instances only** (sources-B, heads-up-evidence-B, readability-B, leverage-funging-B, ce-chain-trace-B, ce-chain-trace-ta-B, leverage-uov-check-B), append the following adversarial preamble to the session context **before** the row allocation note:

> **Reviewer framing — B instance**: You are a skeptical second reviewer. A separate first reviewer has independently audited this same spreadsheet. Your job is to find what a thorough but reasonable reviewer would have rationalized away. Specifically: (a) assume the first reviewer accepted well-labeled rows as correct without verifying the referenced cells — challenge that instinct by reading the referenced cells themselves, not just their labels; (b) give extra attention to checks requiring you to read multiple tabs together, since cross-tab checks are harder and more likely to be shortcut; (c) when a formula or value looks correct at first glance, ask "am I pattern-matching on the label rather than actually reading this?" — then read it; (d) for every section where you find no issues, write one specific reason the section is clean before moving on; (e) **your scanning strategy is bottom-up** — begin from the final CE output row and work backward through adjustments, benefits, and inputs, tracing each formula's chain upstream before moving to the row above. This is the opposite of the A instance's top-down approach and ensures the deepest input rows — where copy-paste errors accumulate unnoticed — receive independent scrutiny. Do not read the Findings sheet. Do not tell the researcher you are a B instance.

For A instances, pass the standard session context only. The only difference between A and B is the row allocation and the adversarial preamble. Append to each instance's session context:
> **Row allocation**: Write findings starting at row `{start_row}`. Do not auto-detect the next empty row — use this pre-assigned start row. Your allocated budget is 40 rows (rows `{start_row}` to `{start_row+39}`). A 10-row inter-pair buffer follows. If you produce more than 40 findings, continue into the buffer rows — but do not write beyond row `{start_row+49}`.

| Step | Agent file | Instance | Row allocation |
|---|---|---|---|
| 5 | `agents/sources.md` | A | `last_row + 1` |
| 5 | `agents/sources.md` | B | `last_row + 51` |
| 6a | `agents/heads-up-evidence.md` | A | `last_row + 101` |
| 6a | `agents/heads-up-evidence.md` | B | `last_row + 151` |
| 6b | `agents/heads-up-epi.md` | A | `last_row + 201` |
| 6b | `agents/heads-up-epi.md` | B | `last_row + 251` |
| 6c | `agents/heads-up-intervention.md` | A | `last_row + 301` |
| 6c | `agents/heads-up-intervention.md` | B | `last_row + 351` |
| 7 | `agents/readability.md` | A | `last_row + 401` |
| 7 | `agents/readability.md` | B | `last_row + 451` |
| 6d | `agents/leverage-funging.md` | A | `last_row + 501` |
| 6d | `agents/leverage-funging.md` | B | `last_row + 551` |
| 6e | `agents/ce-chain-trace.md` | A | `last_row + 601` |
| 6e | `agents/ce-chain-trace.md` | B | `last_row + 651` |
| 6f | `agents/leverage-uov-check.md` | A | `last_row + 701` |
| 6f | `agents/leverage-uov-check.md` | B | `last_row + 751` |
| 6e-ta | `agents/ce-chain-trace-ta.md` | A | `last_row + 951` |
| 6e-ta | `agents/ce-chain-trace-ta.md` | B | `last_row + 1001` |
| 7c | `agents/notes-scan.md` | A | Publication Readiness only (PR start row: `last_row + 801`) |
| 7c | `agents/notes-scan.md` | B | Publication Readiness only (PR start row: `last_row + 851`) |

---

### Wave 2.5 — Reconciliation (after all Wave 2 agents complete)

Announce before spawning: `[Phase 2/4 done → Phase 3/4] Wave 2 complete — starting reconciliation (up to 17 agents, or 18 if TA BOTEC; fewer if empty pairs skipped in pre-flight check).`

**Row allocation recovery — do this first if allocations are not in context**: If Wave 2 row allocations are not available in the current session context (e.g., context was compacted between Wave 2 and Wave 2.5), read Dashboard cells A49:B90 of the output spreadsheet to recover the full Wave 1 and Wave 2 allocation tables before computing the reconciliation ranges below. Do not skip Wave 2.5 due to missing row allocations — always recover from the Dashboard log.

**Pre-flight empty pair check**: Before spawning, fire a parallel batch of `read_sheet_values` calls — one per pair — to check whether each pair's A and B ranges contain any non-empty rows. For any pair where **both** the A range and B range are confirmed completely empty: skip spawning that reconcile agent and announce: `⏭️ Skipping [pair name] reconcile — both A and B wrote zero findings.` Only skip when both ranges are confirmed empty; if either range has any non-empty row, spawn the reconcile agent as normal. Update the agent count in your announcement accordingly.

Spawn **up to 17 reconciliation agents simultaneously** (consistency-check and key-params-check share one combined agent; fewer if empty pairs are skipped), using `agents/reconcile.md`. Each agent receives the standard session context plus its specific pair assignment. Do not tell any reconcile agent about the other pairs being processed.

For each instance, append to session context:
> **Pair to reconcile**: [pair name]
> **A row range**: rows [start]–[end] on the Findings sheet (also check Publication Readiness sheet for sources and readability pairs)
> **B row range**: rows [start]–[end] on the Findings sheet (same note)
> **Overflow zone**: rows [start]–[end] — write net-new findings discovered during reconciliation investigation here, not beyond this range

**Combined consistency-check + key-params-check agent**: For this pair only, pass the following session context instead of the standard single-pair format:
> **Pairs to reconcile**: consistency-check AND key-params-check. Process sequentially in this order: (1) reconcile consistency-check A/B first — A range rows 462–491, B range rows 492–521, overflow zone rows 522–531; write any net-new findings to rows 522–531. (2) Then reconcile key-params-check A/B — A range rows 532–551, B range rows 552–571, overflow zone rows 572–581; write any net-new findings to rows 572–581. Complete consistency-check reconciliation fully before beginning key-params-check reconciliation. Write a coverage declaration after each pair.

| Pair | A row range | B row range | Overflow zone |
|---|---|---|---|
| formula-check-arithmetic (first half) | rows 2–41 | rows 42–81 | rows 82–91 |
| formula-check-arithmetic (second half) | rows 92–131 | rows 132–171 | rows 172–181 |
| formula-check-data | rows 182–211 | rows 212–241 | rows 242–251 |
| formula-check-edge-cases | rows 252–281 | rows 282–311 | rows 312–321 |
| source-data-check | rows 322–351 | rows 352–381 | rows 382–391 |
| formula-check-structure | rows 392–421 | rows 422–451 | rows 452–461 |
| consistency-check + key-params-check *(combined)* | consistency-check A: 462–491, B: 492–521; key-params-check A: 532–551, B: 552–571 | rows 522–531 (consistency overflow); rows 572–581 (key-params overflow) |
| formula-check-voi | rows 582–621 | rows 622–661 | rows 662–671 |
| sources | rows `last_row+1` to `last_row+50` | rows `last_row+51` to `last_row+90` | rows `last_row+91` to `last_row+100` |
| heads-up-evidence | rows `last_row+101` to `last_row+150` | rows `last_row+151` to `last_row+190` | rows `last_row+191` to `last_row+200` |
| heads-up-epi | rows `last_row+201` to `last_row+250` | rows `last_row+251` to `last_row+290` | rows `last_row+291` to `last_row+300` |
| heads-up-intervention | rows `last_row+301` to `last_row+350` | rows `last_row+351` to `last_row+390` | rows `last_row+391` to `last_row+400` |
| readability | rows `last_row+401` to `last_row+450` | rows `last_row+451` to `last_row+490` | rows `last_row+491` to `last_row+500` |
| leverage-funging | rows `last_row+501` to `last_row+550` | rows `last_row+551` to `last_row+590` | rows `last_row+591` to `last_row+600` |
| ce-chain-trace | rows `last_row+601` to `last_row+650` | rows `last_row+651` to `last_row+690` | rows `last_row+691` to `last_row+700` |
| leverage-uov-check | rows `last_row+701` to `last_row+750` | rows `last_row+751` to `last_row+790` | rows `last_row+791` to `last_row+800` |
| **heads-up-epi (TA counterfactual burden)** *(TA BOTEC only)* | rows `last_row+851` to `last_row+900` | rows `last_row+901` to `last_row+940` | rows `last_row+941` to `last_row+950` |
| ce-chain-trace-ta *(self-detecting TA check)* | rows `last_row+951` to `last_row+1000` | rows `last_row+1001` to `last_row+1040` | rows `last_row+1041` to `last_row+1050` |

Note: notes-scan (Step 7c) has no reconciliation pair — it runs as A/B but both write only to Publication Readiness; the Wave 3 compaction agent deduplicates their overlapping PR findings in its standard Step 3 dedup pass. No reconcile agent is needed. formula-check-parameters (Step 3f) also has no reconciliation pair — it runs as a single instance; its overflow zone (rows 702–711) is for any findings that exceed its 30-row budget, not for a second instance. The final-review compaction step handles both alongside all other Wave 1 findings. The heads-up-epi TA counterfactual burden pair also has no reconciliation pair for non-TA models — skip that row entirely when program context is not a TA BOTEC.

**Silent failure check after Wave 2.5 — do this before Wave 3**: After all reconciliation agents complete, read the Findings sheet to verify each reconciliation pair's overflow zone for net-new findings, then check whether each reconcile agent wrote its coverage declaration to chat. (Pairs confirmed empty in the pre-flight check are exempt — their skipped status was already logged.) A reconcile agent that wrote no coverage declaration and produced zero reconciled findings is a silent failure risk. Report any pair where:

> ⚠️ Reconciliation failure warning: [pair name] reconcile agent produced no coverage declaration and no net-new findings. Its A/B divergences may be unreconciled. Consider re-running this reconcile agent before proceeding to Wave 3.

Exception: pairs where both A and B agents wrote zero findings (confirmed empty) produce no divergences to reconcile and zero net-new findings legitimately — verify this by reading the pair's A and B ranges before flagging.

**notes-scan completion check**: After all Wave 2.5 reconciliation agents complete, read the Publication Readiness sheet at rows `last_row+801` through `last_row+900` (the combined A/B range for notes-scan). If both sub-ranges (`last_row+801`–`last_row+850` and `last_row+851`–`last_row+900`) are completely empty — no AGENT_COMPLETE row and no finding rows — surface a silent failure warning:

> ⚠️ notes-scan silent failure suspected: Publication Readiness rows `last_row+801`–`last_row+900` are entirely empty. notes-scan has no reconciliation pair, so this gap will not be caught by any reconcile agent. Consider re-running notes-scan A and B before proceeding to Wave 3.

If either sub-range contains any rows, notes-scan is presumed to have run. This check is necessary because notes-scan writes only to the Publication Readiness sheet and is excluded from all Findings-sheet-based silent failure checks.

**TA misclassification cross-check**: After all Wave 2.5 reconciliation agents complete and before starting Wave 3, verify that heads-up-intervention-B and ce-chain-trace-ta reached consistent TA/non-TA classifications. Run this check unconditionally — the dangerous case is a TA grant classified as non-TA (not the reverse), so gating on `is_ta_botec` would miss exactly the failures this check is designed to catch.

1. Read the AGENT_COMPLETE marker row for heads-up-intervention-B from its allocated row range (rows `last_row + 351` to `last_row + 390` on the Findings sheet). Extract the `Routing decision:` field from column F.
2. Read the AGENT_COMPLETE marker row for ce-chain-trace-ta-A from its allocated row range (rows `last_row + 951` to `last_row + 1000`). Check whether column F contains `No TA grant signals found` (non-TA self-detection) or describes TA-specific check results.
3a. If heads-up-intervention-B declared `Routing decision: A — non-TA` but ce-chain-trace-ta-A produced TA-specific findings (its AGENT_COMPLETE does **not** contain `No TA grant signals found`), announce:

> ⚠️ TA classification mismatch: heads-up-intervention-B identified this as non-TA (ran Section A intervention checks only) but ce-chain-trace-ta found TA signals. If this is a TA grant, Section B TA grant checks were skipped by heads-up-intervention-B. Consider re-running heads-up-intervention with `is_ta_botec = true` in session context before Wave 3.

3b. If heads-up-intervention-B declared `Routing decision: B — TA` but ce-chain-trace-ta-A contains `No TA grant signals found`, announce:

> ⚠️ TA classification mismatch: heads-up-intervention-B ran TA grant checks but ce-chain-trace-ta found no TA signals. Confirm with the researcher whether this is a TA grant — if not, the Section B TA checks may not apply and can be disregarded.

4. If both agree (both non-TA or both found TA signals), proceed silently.

---

### Wave 3 — Sequential (after Wave 2.5)

**Progress announcement** before starting: `[Phase 3/4 done → Phase 4/4] Reconciliation complete — starting final review (4 sequential steps). If this session is interrupted before Wave 3 completes, run /givewell-vetting:vetting-finalize (plugin) or /vetting-finalize (standalone) with the output and source spreadsheet URLs to resume.`

Run the four steps in order — each must complete before the next begins. Announce each step as it starts:
- Before 10a: `[Wave 3 — Step 1/4] Running compaction.`
- Before 10b: `[Wave 3 — Step 2/4] Running gap-fill.`
- Before 10c: `[Wave 3 — Step 3/4] Running validation.`
- Before 10d: `[Wave 3 — Step 4/4] Running dashboard.`

| Step | Agent file | Covers |
|---|---|---|
| 10a | `agents/final-review-compaction.md` | Route misrouted rows, deduplicate, sort, assign Finding IDs |
| 10b | `agents/final-review-gap-fill.md` | Formula cascade check, coverage gap scan, Won't Fix verification — if band-split was used, append `band1_end: {last_row_of_band_1}` to this agent's session context so it can run the cross-band root cause trace (Check 2.5). **Cascade finding definition** (pass in session context): "A cascade finding is a new finding that identifies a cell that will remain wrong *after* a confirmed High/Formula finding is corrected — not the error itself, but a downstream cell whose formula assumed the old wrong value. File as Medium/Formula, at most 2 hops downstream." |
| 10c | `agents/final-review-validation.md` | Fix-validation, confidence intervals check, placeholder scan, CE impact completeness |
| 10d | `agents/final-review-dashboard.md` | Dashboard content, Key Findings summary in chat |

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

After the researcher responds, record their answers in the shared pilot feedback log:

**a. Use the canonical feedback sheet**

The feedback sheet is always: `https://docs.google.com/spreadsheets/d/1Ees1qo3N5SSTzo6MDDrCpvJEVrgANCTqRET6ak3glWM/`

Use spreadsheet ID `1Ees1qo3N5SSTzo6MDDrCpvJEVrgANCTqRET6ak3glWM` for all writes. Do not search for or create a new sheet.

**b. Append the feedback row**

Find the first empty row in column A (read `A:A` and count non-empty cells; first empty = that count + 2, accounting for the header). Write one row at that position:
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
