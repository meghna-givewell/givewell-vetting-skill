# GiveWell Vetting Skill

A Claude Code skill that runs a full audit of GiveWell cost-effectiveness spreadsheets. Checks formulas, parameters, sources, readability, and hardcoded values across multi-wave parallel agents. Outputs a structured Findings sheet with severity-classified findings and Finding IDs.

## Install

This repo ships the vetting skill two ways. Pick one.

### Option A — Install as a plugin (recommended, works in cowork / Claude.ai)

The repo is also a Claude Code plugin marketplace, so you can install it from GitHub without cloning. In Claude Code (CLI, desktop, or cowork on the web):

```
/plugin marketplace add meghna-givewell/givewell-vetting-skill
/plugin install givewell-vetting@givewell-skills
```

Invoke it as `/givewell-vetting:vetting <Google Sheets URL or local file path>`. The marketplace has `autoUpdate` enabled — Claude Code refreshes to the latest version on startup automatically. To pull an update immediately: `/plugin marketplace update givewell-skills`.

### Option B — Install as a standalone skill (clone)

Clone this repo into your Claude Code skills directory:

```bash
git clone https://github.com/meghna-givewell/givewell-vetting-skill.git ~/.claude/skills/vetting
```

Invoke the main vet as `/vetting <Google Sheets URL or local file path>`. The repo-root `SKILL.md`, `agents/`, `reference/`, and `extract.py` are symlinks into `plugin/skills/vetting/`, so the clone resolves the skill at `~/.claude/skills/vetting/SKILL.md` automatically.

To also install the Wave 3 recovery skill:

```bash
ln -s ~/.claude/skills/vetting ~/.claude/skills/vetting-finalize
```

This symlinks the same directory so `/vetting-finalize` resolves to the same agents and reference files via the `../vetting/agents/` relative paths in `vetting-finalize/SKILL.md`.

## Prerequisites

**Hardened Google Workspace MCP** must be installed and authenticated. Follow setup instructions at [github.com/c0webster/hardened-google-workspace-mcp](https://github.com/c0webster/hardened-google-workspace-mcp).

## Permissions

Copy `.claude/settings.json` from this repository into your project's `.claude/` directory to pre-approve all required MCP tool calls and avoid per-call permission prompts during a vet:

```bash
cp ~/.claude/skills/vetting/.claude/settings.json <your-project>/.claude/settings.json
```

If your project already has a `.claude/settings.json`, merge the `allow` array entries from the skill's file into yours.

## Keeping the skill up to date

The agent prompts are updated after each completed vet based on post-vet analysis and pilot feedback. Update before running a vet to ensure you have current judgment-call calibrations and agent logic:

- **Plugin install**: auto-updates on startup. To pull immediately: `/plugin marketplace update givewell-skills`
- **Standalone install**: `git -C ~/.claude/skills/vetting pull --rebase origin main`

## Invoke

```
/vetting <Google Sheets URL or local file path>                  # standalone install
/givewell-vetting:vetting <Google Sheets URL or local file path> # plugin install
```

If the main vet session is interrupted before Wave 3 (final review) completes, resume it with:

```
/vetting-finalize                        # standalone install
/givewell-vetting:vetting-finalize       # plugin install
```

The finalize skill asks for the output spreadsheet URL and source spreadsheet URL, reads the vet scope from the Dashboard, and runs the 4 Wave 3 steps (compaction → gap-fill → validation → dashboard) in a fresh session.

At the start of each vet, Claude will ask:
1. Your Google Workspace email address
2. Which sheets to vet and at what scope (full publication check or formula/heads-up only)
3. Program context questions (grant doc, prior CEA, declared intentional deviations)
4. Whether to run source citation verification for Study-Derived and Org-Reported hardcoded values (GiveWell parameter consistency is always checked regardless)

## What it checks

- **Wave 1** — Formula errors (arithmetic, structure, data verification, edge cases), parameter value accuracy (SUMIFS staleness, stale vintages, country mismatches), cross-parameter consistency, source data tab audit, key-parameter values, VOI checks, confidentiality flags, hardcoded values inventory
- **Wave 1.5** *(optional, if researcher opts in)* — Source citation verification: fetches each cited source and uses the Anthropic Citations API to check whether Study-Derived and Org-Reported hardcoded values are supported by their sources. Pre-fills `Verified?` and `Auto-check evidence` columns in the Hardcoded Values sheet.
- **Wave 2** — Data sources and citations, CE sanity and evidence quality, epidemiological plausibility, intervention-specific checks, leverage/funging, CE chain trace, readability, leverage UoV references, notes quality
- **Wave 2.5** — Reconciliation across parallel agent instances
- **Wave 3** — Compaction (route, deduplicate, sort, assign Finding IDs), gap-fill, validation, dashboard

## Reconciliation criteria

Wave 2.5 reconciliation runs only when two agent instances received the **same sheet data and the same check instructions** (i.e., truly independent coverage of the same scope). Agents that divide work by row range or check type are not a reconciliation pair — they are complementary coverage and their outputs are combined, not reconciled. Specifically:

- `formula-check-arithmetic` A and B cover rows 1–split_row independently → **reconcile pair**
- `formula-check-arithmetic` C and D cover split_row+1 through end independently → **reconcile pair**
- A/B vs. C/D are complementary (different row scopes) → **not a reconcile pair**; combine outputs directly
- Any two agents with different instructions (e.g., one scoped to a counterfactual burden tab, one to Main CEA) → **not a reconcile pair**

## Output

A Google Spreadsheet with six tabs:
- **Findings** — model-integrity issues (formula errors, stale parameters, structural bugs) sorted High → Medium → Low with Finding IDs (F-001…)
- **Publication Readiness** — pub-only issues (permission flags, broken links, citation format, terminology) with IDs (PR-001…)
- **Hardcoded Values** — inventory of standalone hardcoded cells for researcher verification; columns G (`Verified?`) and H (`Auto-check evidence`) pre-filled by Wave 1.5 when source citation verification is enabled
- **Confidentiality Flags** — named individuals, donor info, PII
- **CE Baseline** — pre-vet cost-effectiveness figures by geography/scenario; used as the reference for all CE impact direction estimates in the Findings sheet
- **Dashboard** — summary counts by sheet, CE direction estimate, unvetted tab list

## Pilot feedback

At the end of each vet, Claude asks five short feedback questions (accuracy rating, false positives, missed findings, most useful part, calibration suggestions). Answers are recorded in a shared Google Sheet (`Vetting Skill Pilot Feedback`) and a Slack DM is sent to the skill maintainer. This powers the `reference/pitfalls.md` calibration file, which every agent reads before starting its checks.

## File structure

The repo doubles as a Claude Code **plugin** (in `plugin/`) and a single-plugin **marketplace** (`.claude-plugin/marketplace.json`). The canonical skill files live once in `plugin/skills/vetting/`; the repo-root `SKILL.md`, `agents/`, `reference/`, and `extract.py` are symlinks into that folder so the standalone clone-install keeps working. **Edit the real files under `plugin/skills/vetting/`, never the root symlinks.**

```
givewell-vetting-skill/
  .claude-plugin/
    marketplace.json             # Marketplace catalog: lists givewell-vetting plugin; autoUpdate: true
  plugin/
    .claude-plugin/
      plugin.json                # Plugin manifest (name, version, author)
    skills/
      vetting/                     # Main vet skill (canonical files — edit here, never the root symlinks)
        SKILL.md                   # Orchestrator: startup questions, Steps 0–2, wave dispatch
        extract.py                 # Local Excel extraction (use for .xlsx files before vetting)
        agents/
          formula-check-arithmetic.md  # Wave 1: arithmetic, cell references, scalar multipliers (4 instances)
          formula-check-parameters.md  # Wave 1: parameter accuracy — SUMIFS staleness, stale vintages, country mismatches
          formula-check-structure.md   # Wave 1: structural completeness, cross-column value checks
          formula-check-data.md        # Wave 1: external data verification — GBD, trial papers, cross-model values
          formula-check-edge-cases.md  # Wave 1: zero denominators, blank refs, silenced errors, aggregation gaps
          formula-check-voi.md         # Wave 1: VOI/option-value model checks
          consistency-check.md         # Wave 1: cross-cutting parameter consistency, moral weights
          source-data-check.md         # Wave 1: source data tab audit (coverage, WUENIC, DHS, GBD, population)
          key-params-check.md          # Wave 1: GiveWell standard parameter values (benchmark, moral weights)
          sensitivity-scan.md          # Wave 1: confidentiality flags — named individuals, donor info, PII
          hardcoded-values.md          # Wave 1: hardcoded values inventory
          source-citation-verify.md    # Wave 1.5 (optional): Citations API source verification for hardcoded values
          sources.md                   # Wave 2 Step 5: data source audit, citation completeness
          heads-up-evidence.md         # Wave 2 Step 6a: CE sanity check, top-5 interrogation, evidence quality
          heads-up-epi.md              # Wave 2 Step 6b: epidemiological parameters, disease burden
          heads-up-intervention.md     # Wave 2 Step 6c: intervention-specific plausibility checks
          leverage-funging.md          # Wave 2 Step 6d: leverage/funging sign, direction, double-count checks
          leverage-uov-check.md        # Wave 2: leverage section UoV rate reference audit
          ce-chain-trace.md            # Wave 2 Step 6e: full CE chain trace from output to source inputs
          ce-chain-trace-ta.md         # Wave 2: TA BOTEC denominator and counterfactual burden checks
          readability.md               # Wave 2 Step 7: labels, section ordering, legibility
          notes-scan.md                # Wave 2 Step 7c: missing Calculation entries, boilerplate, raw URLs
          reconcile.md                 # Wave 2.5: reconciles divergences across parallel A/B agent instances
          final-review-compaction.md   # Wave 3 Step 10a: route misrouted rows, deduplicate, sort, assign IDs
          final-review-gap-fill.md     # Wave 3 Step 10b: cascade check, coverage gap scan, Won't Fix verification
          final-review-validation.md   # Wave 3 Step 10c: fix-validation, confidence intervals, placeholder scan
          final-review-dashboard.md    # Wave 3 Step 10d: dashboard content, Key Findings summary in chat
        reference/
          key-parameters.md        # Authoritative GiveWell parameter values (benchmark, moral weights, etc.)
          output-format.md         # Findings and Publication Readiness column definitions and severity rules
          output-setup.md          # Output spreadsheet creation: tabs, headers, formatting, dashboard cells
          column-reference.md      # Canonical column specification referenced by all agents
          pitfalls.md              # Known calibrations: false positive and false negative patterns from prior vets
      vetting-finalize/            # Wave 3 recovery skill (invoked separately if main session is interrupted)
        SKILL.md                   # Reads vet metadata from Dashboard, runs 4 Wave 3 steps in a fresh session
  SKILL.md   agents/   reference/   extract.py   # symlinks → plugin/skills/vetting/ (standalone clone compat)
  README.md  CLAUDE.md  CONTRIBUTING.md  LICENSE
  .github/CODEOWNERS             # Auto-requests review from the owner on PRs
  .claude/commands/done.md       # /done — commit, push, open/update PR at session end
```

## Shared repo

This is a multi-contributor repo. For collaboration and git workflow rules — pull, branch, commit, `/done`, PR, squash-merge-delete, conflicts, and what not to commit — see [CONTRIBUTING.md](CONTRIBUTING.md). Read it at the start of every session.
