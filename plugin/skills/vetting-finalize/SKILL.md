# Vetting Finalize — Wave 3 (Final Review)

Run this skill to execute Wave 3 of a GiveWell spreadsheet vet after Waves 1–2.5 have already completed in a prior session. Use it for:

- **Recovery**: the main vet session timed out or was interrupted before Wave 3 ran
- **Re-run**: findings were edited manually and Wave 3 needs to run again

Wave 3 is purely output-side work (compaction, gap-fill, validation, dashboard). It does not re-read or re-analyze the source spreadsheet beyond targeted cell lookups. Accuracy is not affected by splitting here — all findings are already in the Findings sheet.

---

## Step 1 — Gather inputs

Ask the user:

> 1. What is the URL of the **Vetting Findings output spreadsheet** (the one created during the main vet)?
> 2. What is the URL of the **source spreadsheet** that was vetted?
> 3. What is your Google Workspace email address?

Parse both spreadsheet IDs from the provided URLs. The source spreadsheet ID is the long alphanumeric string in the Google Sheets URL between `/d/` and `/edit`.

---

## Step 2 — Read vet metadata from Dashboard

Call `read_sheet_values` (FORMATTED_VALUE) on the **Dashboard** tab of the output spreadsheet, range `A150:B153`. Extract:

| Cell | Contains |
|---|---|
| B151 | Fully vetted tabs (comma-separated) |
| B152 | Lite-pass tabs (comma-separated, or "none") |
| B153 | Vet scope (`full` or `formula-only`) |

Call `read_sheet_values` (FORMATTED_VALUE) on the **CE Baseline** tab, range `A1:B20`. This tab contains the pre-vet baseline CE values — one row per geography/scenario — written by the orchestrator during the main vet.

**If Dashboard rows 150–153 are blank** (vet was run before metadata persistence was added), ask:

> "The vet metadata block was not found in the Dashboard. Please provide: (1) which tabs were fully vetted, (2) which tabs were lite-passed (or 'none'), and (3) was this a full vet or formula/heads-up only?"

---

## Step 3 — Check if Wave 3 already ran

Read Dashboard cell B22 (CE estimate direction). If it is not blank, Wave 3 has already completed. Confirm with the user before re-running:

> "Wave 3 appears to have already completed (CE direction is populated in the Dashboard). Re-running will overwrite compaction, gap-fill, validation, and dashboard output. Continue?"

Proceed only if the user confirms.

---

## Step 4 — Reconstruct session context

Call `get_spreadsheet_info` on the source spreadsheet to obtain the full tab list and numeric GIDs. Compute:
- **In-scope sheets**: vetted tabs + lite-pass tabs
- **Out-of-scope sheets**: all other tabs

Build the session context block that each Wave 3 sub-agent will receive:

```
Spreadsheet ID: <source_spreadsheet_id>
Sheets to vet: <vetted_tabs>
In-scope sheets: <vetted_tabs and lite_pass_tabs>
Out-of-scope sheets: <remaining tabs>
Findings sheet ID: <output_spreadsheet_id> (tab: Findings)
Publication Readiness sheet ID: <output_spreadsheet_id> (tab: Publication Readiness)
User email: <email>
Pre-vet baseline CE: <from CE Baseline tab, e.g., "Nigeria = B48 (7.8x), Kenya = C48 (6.2x)">
Scope: <full or formula-only>
Lite-pass tabs: <lite_pass_tabs>
Current date: <today's date>
```

---

## Step 5 — Run Wave 3

Announce: `[Wave 3 — Finalize starting]`

Run the four steps in order — each must complete before the next begins. Announce each step:
- Before 10a: `[Wave 3 — Step 1/4] Running compaction.`
- Before 10b: `[Wave 3 — Step 2/4] Running gap-fill.`
- Before 10c: `[Wave 3 — Step 3/4] Running validation.`
- Before 10d: `[Wave 3 — Step 4/4] Running dashboard.`

For each step: use the Agent tool to spawn a sub-agent. Read the agent file listed below and pass its full content as the agent prompt, appending the session context from Step 4 plus any agent-specific notes.

| Step | Agent file (relative to this skill) | Notes |
|---|---|---|
| 10a | `../vetting/agents/final-review-compaction.md` | Pass: output spreadsheet ID only (no source spreadsheet needed) |
| 10b | `../vetting/agents/final-review-gap-fill.md` | Pass: source + output spreadsheet IDs, pre-vet baseline CE |
| 10c | `../vetting/agents/final-review-validation.md` | Pass: source + output spreadsheet IDs, pre-vet baseline CE |
| 10d | `../vetting/agents/final-review-dashboard.md` | Pass: source + output spreadsheet IDs, scope declaration |

After all four steps complete, announce `[Wave 3 complete]` and share the output spreadsheet link in chat.

---

## Standalone install note

If you installed this skill via git clone rather than plugin, agent files are at `~/.claude/skills/vetting/agents/`. Update the paths in Step 5 accordingly, or create a symlink:

```bash
ln -s ~/.claude/skills/vetting ~/.claude/skills/vetting-finalize
```

Then invoke as `/vetting-finalize`.
