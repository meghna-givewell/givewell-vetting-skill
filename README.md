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
  SKILL.md              # Main skill: session setup, Steps 0–2, agent orchestration
  README.md             # This file
  agents/
    formula-check.md    # Steps 3–4: formula errors, parameter consistency
    plausibility.md     # Step 5: assumption plausibility, cross-column review
    sources.md          # Step 6: data source audit
    readability.md      # Step 7: readability, labels, cross-sheet consistency
    sensitivity.md      # Steps 8–9: sensitive data, hardcoded values, final review
  reference/
    key-parameters.md   # Authoritative GiveWell parameter values
    output-format.md    # Findings sheet column definitions and severity rules
```
