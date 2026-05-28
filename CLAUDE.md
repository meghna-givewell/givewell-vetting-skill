# GiveWell Vetting Skill

This repo packages the GiveWell spreadsheet **vetting** skill — a Claude Code skill that runs a
full audit of a cost-effectiveness spreadsheet (formulas, parameters, sources, readability, and
hardcoded values) across multiple waves of parallel agents, and writes a structured Findings
sheet.

The skill ships two ways from this one repo:

- **Standalone skill** — clone into `~/.claude/skills/vetting` and invoke `/vetting`.
- **Claude Code / cowork plugin** — install from the `givewell-skills` marketplace and invoke
  `/givewell-vetting:vetting`.

The canonical skill files live once in `plugin/skills/vetting/` (`SKILL.md` orchestrator, `agents/`
per-wave agent prompts, `reference/` parameter values and output-format specs, `extract.py` local
`.xlsx` extraction). The repo-root `SKILL.md`, `agents/`, `reference/`, and `extract.py` are
symlinks into that folder so the standalone clone-install keeps working — edit the real files under
`plugin/skills/vetting/`, never the symlinks. See [README.md](README.md) for install and usage.

## Shared repo

This is a multi-contributor repo. For collaboration and git workflow rules — pull, branch,
commit, `/done`, PR, squash-merge-delete, conflicts, and what not to commit — see
[CONTRIBUTING.md](CONTRIBUTING.md). Read it at the start of every session.
