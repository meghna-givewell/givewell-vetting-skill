# Contributing

This file is the canonical guide for collaborating in this repo — for both humans driving git through Claude and for Claude itself. Claude reads it at session start and follows the rules; humans can use it as a cheat sheet for what to ask Claude to do.

## Maintainer

- **Owner**: GiveWell (@meghna-givewell) — approves merges to the default branch

Slack the owner with questions; open a GitHub issue for proposed changes.

## Editing the skill

The canonical skill files live once in `plugin/skills/vetting/` (`SKILL.md` orchestrator, `agents/` per-wave agent prompts, `reference/` parameter values and output-format specs, `extract.py`). The matching entries at the repo root are **symlinks** into that folder, kept so the standalone clone-into-`~/.claude/skills/vetting` install keeps working. Always edit the real files under `plugin/skills/vetting/` — never the root symlinks. The agent prompts are refined after each completed vet based on post-vet analysis — keep changes scoped and explain the calibration in the commit message. After changing the skill, bump `version` in both `plugin/.claude-plugin/plugin.json` and the plugin entry in `.claude-plugin/marketplace.json` so plugin users receive the update.

## Workflow

### Start of session

Pull the latest from the default branch (`git pull --rebase`). For non-trivial work, create a branch named after the task (`add-data-source`, `fix-rendering-bug`), not the contributor.

### During the work

Commit at natural checkpoints with imperative messages ("Add data source"). Push the branch early (`git push -u origin <branch>`) so collaborators can see WIP.

### End of session

Run `/done`. It commits WIP, pushes the branch, and opens or updates a PR. Don't leave work abandoned in a closed Claude window.

### Reviewing

Open a PR against the default branch with what changed, why, and how to verify. PRs auto-request review from CODEOWNERS. Ask Claude to summarize the diff in plain English if you didn't author the work.

### Merging (owner only)

**Squash and merge**, then **delete the branch.** Keeps the default branch clean and prevents stale-branch sprawl. If you're not the owner, tag the owner for review instead of self-merging.

Exception: a long-lived branch with several genuinely distinct logical changes can be merged non-squashed. Default is squash.

### Conflicts

If `git pull --rebase` or merging produces conflicts, stop. Explain the conflicting hunks in plain English; let the maintainer decide. Don't auto-resolve.

## Cheat sheet (what to tell your Claude)

| Stage | Say to Claude |
|---|---|
| Starting | "Pull the latest and start a branch for [what I'm doing]." |
| Mid-work | "Commit my changes." |
| Done for the session | "Run `/done`." (Or: "Push the branch and open a PR.") |
| Reviewing | "Summarize the changes in this PR in plain English." |
| Merging (owner only) | "Squash, merge, and delete the branch." (Otherwise: "Tag the owner for review.") |

## Coordinate before big work

For schema changes, new features, or anything that touches a shared interface — open a GitHub issue (or message the owner) before starting. Saves you from doing work that gets rejected at PR time.

## Don't

- Commit secrets (API keys, tokens, `.env` contents). If one's already in history, flag for rotation.
- Commit large data files or generated outputs. Add patterns to `.gitignore`.
- Commit spreadsheet data, vetting outputs, or reference docs pulled from Google Workspace — these belong in the gitignored `spreadsheets/`, `output/`, and `reference_docs/` folders.
- *Edit* Excel/Word/PowerPoint in the repo — git can't merge them, so one person's changes disappear. Reference-only copies are fine; collaborative editing is not. Use markdown/CSV/YAML for live work.
- Force-push (`--force`, `--force-with-lease`) unless the maintainer explicitly requests it.
- Skip hooks (`--no-verify`) unless the maintainer explicitly requests it.
- Commit directly to the default branch.
- Merge your own PR if you're not the owner.

## If something looks weird

Ask Claude to explain before doing anything destructive. Or ping the owner.
