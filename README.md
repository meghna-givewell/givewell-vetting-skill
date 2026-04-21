# GiveWell Vetting Skill

A Claude Code skill that runs a full audit of GiveWell cost-effectiveness spreadsheets. Checks formulas, parameters, sources, readability, and hardcoded values across multi-wave parallel agents. Outputs a structured Findings sheet with severity-classified findings and Finding IDs.

## Install

Clone this repo into your Claude Code skills directory:

```bash
git clone https://github.com/meghna-givewell/givewell-vetting-skill.git ~/.claude/skills/vetting
```

## Prerequisites

**Hardened Google Workspace MCP** must be installed and authenticated. Follow setup instructions at [github.com/c0webster/hardened-google-workspace-mcp](https://github.com/c0webster/hardened-google-workspace-mcp).

## Permissions

Copy `.claude/settings.json` from this repository into your project's `.claude/` directory to pre-approve all required MCP tool calls and avoid per-call permission prompts during a vet:

```bash
cp ~/.claude/skills/vetting/.claude/settings.json <your-project>/.claude/settings.json
```

If your project already has a `.claude/settings.json`, merge the `allow` array entries from the skill's file into yours.

## Keeping the skill up to date

The agent prompts are updated after each completed vet based on post-vet analysis. Pull the latest version before running a vet to ensure you have current judgment-call calibrations and agent logic:

```bash
git -C ~/.claude/skills/vetting pull --rebase origin main
```

## Invoke

```
/vetting <Google Sheets URL or local file path>
```

The skill will ask for your Google Workspace email address, authenticate, list the workbook's sheets, and ask which to vet and at what scope (full publication check or formula/heads-up only) before proceeding.

## What it checks

- **Wave 1** — Formula errors (arithmetic, structure, data verification, edge cases), cross-parameter consistency, source data tab audit
- **Wave 2** — Data sources and citations, CE sanity and evidence quality, epidemiological plausibility, intervention-specific checks, leverage/funging, CE chain trace, readability, confidentiality flags, hardcoded values, leverage UoV references, notes quality
- **Wave 2.5** — Reconciliation across parallel agent instances
- **Wave 3** — Compaction (route, deduplicate, sort, assign Finding IDs), gap-fill, validation, dashboard

## Output

A Google Spreadsheet with five tabs:
- **Findings** — model-integrity issues (formula errors, stale parameters, structural bugs) sorted High → Medium → Low with Finding IDs (F-001…)
- **Publication Readiness** — pub-only issues (permission flags, broken links, citation format, terminology) with IDs (PR-001…)
- **Hardcoded Values** — inventory of standalone hardcoded cells for researcher verification
- **Confidentiality Flags** — named individuals, donor info, PII
- **Dashboard** — summary counts by sheet, CE direction estimate, unvetted tab list

## File structure

```
vetting/
  SKILL.md                       # Main orchestrator: session setup, Steps 0–2, agent dispatch
  README.md                      # This file
  extract.py                     # Local Excel extraction (use for .xlsx files before vetting)
  agents/
    formula-check-arithmetic.md  # Wave 1: arithmetic, cell references, scalar multipliers (4 parallel instances)
    formula-check-structure.md   # Wave 1: structural completeness, cross-column value checks
    formula-check-data.md        # Wave 1: external data verification — GBD, trial papers, cross-model values
    formula-check-edge-cases.md  # Wave 1: zero denominators, blank refs, silenced errors, aggregation gaps
    consistency-check.md         # Wave 1: cross-cutting parameter consistency, moral weights
    source-data-check.md         # Wave 1: source data tab audit (coverage, WUENIC, DHS, GBD, population)
    sources.md                   # Wave 2 Step 5: data source audit, citation completeness
    heads-up-evidence.md         # Wave 2 Step 6a: CE sanity check, top-5 interrogation, evidence quality
    heads-up-epi.md              # Wave 2 Step 6b: epidemiological parameters, disease burden
    heads-up-intervention.md     # Wave 2 Step 6c: intervention-specific plausibility checks
    leverage-funging.md          # Wave 2 Step 6d: leverage/funging sign, direction, double-count checks
    leverage-uov-check.md        # Wave 2: leverage section UoV rate reference audit
    ce-chain-trace.md            # Wave 2 Step 6e: full CE chain trace from output to source inputs
    readability.md               # Wave 2 Step 7: labels, section ordering, legibility
    notes-scan.md                # Wave 2 Step 7c: missing Calculation entries, boilerplate, raw URLs
    sensitivity-scan.md          # Wave 2 Step 8: confidentiality flags — named individuals, donor info, PII
    hardcoded-values.md          # Wave 2 Step 9: hardcoded values inventory
    reconcile.md                 # Wave 2.5: reconciles divergences across parallel A/B agent instances
    final-review-compaction.md   # Wave 3 Step 10a: route misrouted rows, deduplicate, sort, assign IDs
    final-review-gap-fill.md     # Wave 3 Step 10b: fill blank CE impact cells, add missing severity labels
    final-review-validation.md   # Wave 3 Step 10c: fix-validation, confidence intervals, placeholder scan
    final-review-dashboard.md    # Wave 3 Step 10d: dashboard content, Key Findings summary in chat
  reference/
    key-parameters.md            # Authoritative GiveWell parameter values (benchmark, moral weights, etc.)
    output-format.md             # Findings and Publication Readiness column definitions and severity rules
    output-setup.md              # Output spreadsheet creation: tabs, headers, formatting, dashboard cells
    column-reference.md          # Canonical column specification referenced by all agents
```
