# GiveWell Vetting Skill

This repo packages the GiveWell spreadsheet **vetting** skill — a Claude Code skill that runs a
full audit of a cost-effectiveness spreadsheet (formulas, parameters, sources, readability, and
hardcoded values) across multiple waves of parallel agents, and writes a structured Findings
sheet.

The skill files live at the repo root: `SKILL.md` is the orchestrator, `agents/` holds the
per-wave agent prompts, `reference/` holds authoritative parameter values and output-format
specs, and `extract.py` handles local `.xlsx` extraction. It installs by cloning into
`~/.claude/skills/vetting` and is invoked with `/vetting`. See [README.md](README.md) for install
and usage.

## Shared repo

This is a multi-contributor repo. For collaboration and git workflow rules — pull, branch,
commit, `/done`, PR, squash-merge-delete, conflicts, and what not to commit — see
[CONTRIBUTING.md](CONTRIBUTING.md). Read it at the start of every session.
