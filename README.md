# Vetting Skill — Setup Guide

Invoke with:

```
/vetting <Google Sheets URL or local file path>
```

## One-Time Setup

Add the following to the `permissions.allow` array in `~/.claude/settings.json` to avoid per-call permission prompts:

```json
"mcp__hardened-workspace__start_google_auth",
"mcp__hardened-workspace__get_spreadsheet_info",
"mcp__hardened-workspace__read_sheet_values",
"mcp__hardened-workspace__read_sheet_notes",
"mcp__hardened-workspace__read_sheet_hyperlinks",
"mcp__hardened-workspace__read_spreadsheet_comments",
"mcp__hardened-workspace__modify_sheet_values",
"mcp__hardened-workspace__format_sheet_range",
"mcp__hardened-workspace__add_conditional_formatting",
"mcp__hardened-workspace__update_conditional_formatting",
"mcp__hardened-workspace__delete_conditional_formatting",
"mcp__hardened-workspace__create_spreadsheet",
"mcp__hardened-workspace__create_sheet",
"mcp__hardened-workspace__list_spreadsheets",
"mcp__hardened-workspace__get_doc_content",
"mcp__hardened-workspace__create_doc",
"mcp__hardened-workspace__batch_update_doc",
"mcp__hardened-workspace__insert_doc_elements",
"mcp__hardened-workspace__inspect_doc_structure",
"mcp__hardened-workspace__modify_doc_text",
"mcp__hardened-workspace__find_and_replace_doc",
"mcp__hardened-workspace__list_docs_in_folder",
"mcp__hardened-workspace__search_docs",
"mcp__hardened-workspace__read_document_comments",
"mcp__hardened-workspace__create_document_comment",
"mcp__hardened-workspace__reply_to_document_comment",
"mcp__hardened-workspace__resolve_document_comment",
"mcp__hardened-workspace__list_drive_items",
"mcp__hardened-workspace__search_drive_files",
"mcp__hardened-workspace__get_drive_shareable_link",
"mcp__hardened-workspace__get_drive_file_content",
"mcp__hardened-workspace__check_drive_file_public_access"
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
