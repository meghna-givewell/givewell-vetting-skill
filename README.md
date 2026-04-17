# Vetting Skill — Setup Guide

Invoke with:

```
/vetting <Google Sheets URL or local file path>
```

## One-Time Setup

Add the following to the `permissions.allow` array in your project's `.claude/settings.local.json` (or `~/.claude/settings.json` for global) to avoid per-call permission prompts:

```json
"Agent",
"WebSearch",
"WebFetch",
"mcp__hardened-workspace__*"
```

## File Structure

```
skills/vetting/
  SKILL.md                       # Main skill: session setup, Steps 0–2, agent orchestration
  README.md                      # This file
  agents/
    formula-check-arithmetic.md  # Step 3 (Wave 1): arithmetic, cell references, scalar multipliers — 4 instances (A/B rows 1→½, C/D rows ½→end)
    formula-check-structure.md   # Step 3b (Wave 1): structural completeness, cross-column value checks, parallel scenario symmetry
    formula-check-data.md        # Step 3d (Wave 1): external data verification — GBD, trial papers, cross-model values
    formula-check-edge-cases.md  # Step 4 (Wave 1): zero denominators, blank refs, silenced errors, aggregation gaps
    consistency-check.md         # Step 4b (Wave 1): cross-cutting parameter consistency, moral weights, study-derived parameter rows
    source-data-check.md         # Wave 1: source data tab audit (coverage data, WUENIC, DHS, GBD, population tabs)
    sources.md                   # Step 5 (Wave 2): data source audit, citation completeness, cost input row coverage
    heads-up-evidence.md         # Step 6a (Wave 2): CE sanity check, top-5 interrogation, hyperlink audit, benefit streams, evidence quality
    heads-up-epi.md              # Step 6b (Wave 2): epidemiological parameters, disease burden, model structure, leverage UoV references
    heads-up-intervention.md     # Step 6c (Wave 2): intervention-specific plausibility checks
    leverage-funging.md          # Step 6d (Wave 2): leverage/funging sign, direction, and double-count checks
    ce-chain-trace.md            # Step 6e (Wave 2): full CE chain trace from output to source inputs, scenario UoV references
    readability.md               # Step 7 (Wave 2): labels, section ordering, legibility
    sensitivity-scan.md          # Step 8 (Wave 2): confidentiality flags — named individuals, donor info, PII
    hardcoded-values.md          # Step 9 (Wave 2): hardcoded values inventory for researcher verification
    notes-scan.md                # Step 7c (Wave 2): missing Calculation entries, boilerplate, raw URLs
    reconcile.md                 # Wave 2.5: reconciles A/B instance divergences per agent pair
    final-review-compaction.md   # Step 10a (Wave 3): route misrouted rows, deduplicate, sort, assign Finding IDs
    final-review-validation.md   # Step 10b (Wave 3): fix-validation, confidence intervals, placeholder scan, CE impact
    final-review-dashboard.md    # Step 10c (Wave 3): dashboard content, Key Findings summary in chat
  reference/
    key-parameters.md            # Authoritative GiveWell parameter values
    output-format.md             # Findings sheet column definitions and severity rules
    output-setup.md              # Output spreadsheet creation: tabs, headers, formatting batch, dashboard cells
```
