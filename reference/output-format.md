# Output Format Reference

## Sheet routing rule

- **Findings** — model-integrity issues: formula errors, stale/wrong parameters, structural bugs, undocumented assumptions that affect CE or model interpretation.
- **Publication Readiness** — issues that don't affect the model: missing sources, permission flags, broken links, citation format, terminology, style, labeling, personal names in notes, internal-only references.
- **Missing Source always goes to Publication Readiness** — a missing citation does not by itself mean the value is wrong. If the value itself is suspect (e.g., labeled "guess," outside the plausible range, or inconsistent with other sources), file it as `Outdated Parameter` or `Edge Case` in Findings instead.
- When in doubt between Findings and Publication Readiness, use Findings.

---

## Findings Sheet — Sheet 1 (model integrity)

Columns (A–L): Finding # | Sheet | Cell/Row | Severity | Error Type / Issue | Current Formula/Value | Recommended Fix | Explanation | Changes CE? | Estimated CE Impact | Researcher judgment needed | Status

- **Finding #** (A): Sequential ID assigned by the final-review compaction step (e.g., `F-001`, `F-002` on the Findings sheet; `PR-001`, `PR-002` on Publication Readiness). Left blank by all analysis agents — do not write to this column.
- **Sheet** (B): The sheet name the finding applies to (e.g., `Main CEA`, `Leverage/Funging`, `Inputs`). Use `Multiple` if a finding spans more than one sheet.
- **Cell/Row** (C): Exact location (e.g., `B14`). For grouped findings, list all affected cells (e.g., `B14, B18, B22`).
- **Severity** (D): `High`, `Medium`, or `Low`. Color-coded — see Severity Rules below.
- **Error Type / Issue** (E): `Formula Error`, `Missing Source`, `Readability`, `Confidential Info`, `Adjustment Scope`, `Edge Case`, `Outdated Parameter`, `Template Language`, `Internal Reference`, `Intentional`
- **Current Formula/Value** (F): The formula or hardcoded value from the problematic cell as it currently reads — e.g., `=SUM(D4:D18)` for a formula-range error, or `0.73` for a wrong hardcoded parameter. For grouped findings covering multiple cells, write the most representative one. Leave blank for style or readability findings where the cell content itself is not the core issue.
- **Recommended Fix** (G): Specific corrective action. Lead with an imperative verb. When the fix is a formula change, include the complete replacement formula string — e.g., "Change to `=SUM(D4:D19)` (current formula excludes row 19)" so the researcher can copy-paste directly.
- **Explanation** (H): Why this is an error or concern.
- **Changes CE?** (I): Mark `✓` if correcting this finding would change the bottom-line CE multiple. Leave blank if it affects interpretation or documentation only without moving the calculated number. For formula errors in the CE calculation chain, this is almost always ✓. For missing sources where the value may be correct, leave blank unless there is reason to believe the value is wrong.
- **Estimated CE Impact** (J): For High findings, quantify directional effect on bottom-line CE (e.g., "raises weighted CE from 8.7x to ~10.2x"). For Medium/Low with negligible or unknown impact: "None / not quantified".
- **Researcher judgment needed** (K): Mark `✓` if the finding cannot be resolved without researcher input — e.g., an intent question ("is this $0 intentional?") or a verification that requires the researcher to check a source. Leave blank if the fix is unambiguous.
- **Status** (L): Left blank by Claude. The researcher fills this in: `Open` / `Fixed` / `Won't Fix` / `Needs Discussion`. Do not write to this column.

### Severity Rules
- **High**: Materially affects bottom-line CE — formula errors, structural omissions, adjustments calculated but not applied. Ask: does correcting this change the number a decision-maker sees? If yes, it's High.
- **Medium**: Affects interpretation, methodology, or parameter accuracy but does not directly change the calculated CE — stale parameters, missing sources, undocumented assumptions.
- **Low**: Cosmetic or labeling issues with no calculation impact.

### Grouping and Sorting
Sort by sheet (column B), then row number. Where the same issue applies to multiple cells, **group into a single finding** listing all affected cells (e.g., "B14, B18, B22"). Only create separate rows when the issue, explanation, or recommended fix differs meaningfully. Aim for ~15–25 grouped findings rather than 50+ individual entries.

**Newly-added geography column — missing source batch finding**: When a column represents a newly-added geography and multiple parameters in that column lack cell notes or source citations, file a single grouped Medium finding listing all affected cells rather than one finding per cell. Example wording: "CIV column (J) has N parameters with no source note — newly-added geographies commonly have documentation gaps across the board. Cells: [J16, J34, J92, J135, J146, ...]. Recommend adding a source note or cell note for each before publication." This prevents alert fatigue from 8+ identical Low/H findings that all have the same fix.

Write findings starting at row 2.

---

---

## Publication Readiness Sheet — Sheet 2 (pub-only issues)

7-column format (A–G) — streamlined for pub-readiness work. No Severity, Decision Relevance, Estimated CE Impact, or Current Formula/Value. Contains only issues that do not affect model outputs: permission flags, broken links, GBD/IHME citation completeness (text-only citations), personal names in notes, internal-only references, Box links, terminology (x cash → x benchmark), label/note style issues. Researchers working on model correctness can ignore this sheet entirely until the pre-publication checklist.

Columns (A–G): Finding # | Sheet | Cell/Row | Error Type / Issue | Recommended Fix | Explanation | Status

- **Finding #** (A): Sequential ID assigned by final-review (e.g., `PR-001`, `PR-002`). Left blank by agents.
- **Sheet** (B): Sheet name the finding applies to.
- **Cell/Row** (C): Exact cell or row reference.
- **Error Type / Issue** (D): Same vocabulary as Findings sheet — `Missing Source`, `Readability`, `Internal Reference`, etc.
- **Recommended Fix** (E): Specific corrective action, leading with an imperative verb.
- **Explanation** (F): Why this is an issue.
- **Status** (G): Left blank by Claude. The researcher fills this in: `Open` / `Fixed` / `Won't Fix` / `Needs Discussion`.

---

## Hardcoded Values Sheet — Sheet 3

Columns: Cell/Row | Current Value | Description | Source to Verify | Verified?

- **Verified?** (E): Left blank by Claude. The researcher fills this in (Yes / No / In Progress) after checking each entry against its source.

---

## Confidentiality Flags Sheet — Sheet 5

Columns: Cell/Row | Content Found | Sensitivity Type | Recommended Action

- **Sensitivity Type**: `PII`, `Donor Info`, `Salary/Compensation`, `Unpublished Strategy`, `Contact Info`, `Other`
- **Recommended Action**: Specific instruction (e.g., "Remove name — replace with role title", "Delete row before publication")

Confidentiality Flags findings go on this sheet only — do not duplicate in the Findings sheet.
