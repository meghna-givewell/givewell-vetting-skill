# Spreadsheet Vetter — GiveWell

This folder is used for GiveWell spreadsheet vetting sessions. The full vetting workflow lives in the `/vetting` skill (`~/.claude/skills/vetting/SKILL.md`) — that file is the single source of truth. This CLAUDE.md covers only folder layout and data handling rules.

Invoke the skill with `/vetting <Google Sheets URL or file path>`.

---

## Project Layout

```
spreadsheet-vetter/
  reference_docs/     # LINKS.md (legacy — doc IDs now live in the skill)
  spreadsheets/       # Spreadsheets to be vetted (place inputs here)
  output/             # Vetting outputs: summary doc + findings sheet
  CLAUDE.md           # This file
```

---

## Data Sensitivity Rules

- Do not write sensitive data (donor names, PII, financial records) to any output file or commit.
- If sensitive data is detected in the spreadsheet being vetted, pause and flag it before continuing.
- Follow GiveWell's data classification policy as defined in the global CLAUDE.md.
