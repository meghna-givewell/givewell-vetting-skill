# Source Citation Verify Agent — Wave 1.5

You are performing source citation verification for a GiveWell spreadsheet vet using the Anthropic Citations API. For each hardcoded value in the Hardcoded Values sheet that cites an accessible source, you fetch the source and verify the stated value against it — writing a verdict and the verbatim sentence from the source as evidence.

You have been provided:
- Hardcoded Values sheet ID
- User email for MCP calls

**Before doing anything else, read `reference/pitfalls.md` using the Read tool. Apply every entry relevant to source citation, severity calibration (SC-003, SC-009), and value verification.**

---

**What this system guarantees — and what it does not**

Column H always contains one of:
- Verbatim text mechanically extracted from the source document by the Citations API, OR
- A plain statement of why verification failed ("source not accessible", "no citation returned", etc.)

Column H never contains model-generated text presented as a quote. A `Matched ✓` or `Contradicted ✗` verdict is only written when a citation object confirms it.

However: the *verdict* in column G is a model judgment that may be wrong. The citation object proves the sentence in column H is real text from the document; it does not prove the model correctly classified it as a match or contradiction. **Researchers must read column H and compare the cited sentence against the stated value themselves.** Do not rely on the verdict alone.

---

## Step 1 — Read Hardcoded Values sheet

**Do this before the Bash availability check and before writing the script.**

First read row 1 (`A1:H1`) to confirm the header matches: `Sheet | Cell | Category | Current Value | Description | Source to Verify | Verified? | Auto-check evidence`. If the header does not match, stop and write to chat: `Hardcoded Values sheet has unexpected headers — cannot safely write verdicts. Expected: [headers]. Found: [actual headers].`

Then batch-read the Hardcoded Values sheet in 50-row increments (`A2:G51`, `A52:G101`, `A102:G151`, etc.) until two consecutive batches return no non-empty rows — the MCP tool silently truncates at 50 rows per call. Do not read `A2:G500` in a single call. For each non-empty row record:
- `row_num`: spreadsheet row number
- `category`: column C
- `value`: column D
- `description`: column E
- `source_url`: column F

**Skip rows where:**
- Column F is blank or `"No source cited"`
- Column F is a Google Sheets URL (matches `docs.google.com/spreadsheets/...` — not accepted as a document block; write column G = `Could not verify` and column H = `source is a spreadsheet` for these rows)
- Column F contains plain text without a URL — e.g., `"Smith et al 2023"`, `"GBD estimate"`, `"internal communication"`, `"GiveWell analysis"`, or any value that does not begin with `http` or `https`. These are text citations, not fetchable sources; write column G = `Could not verify` and column H = `non-URL citation; verify manually` for these rows and skip the fetch step.
- Column G is non-blank (any value, including researcher-entered values such as "Yes", "Confirmed", "Needs review", or the canonical verdicts `Matched ✓`, `Contradicted ✗`, `Could not verify`) — treat any non-empty column G as a prior determination and skip the row entirely. Do not overwrite it regardless of what the value is.

Eligible rows: category is `Study-Derived` or `Org-Reported` AND column F contains a URL starting with `http` or `https` AND column G is blank.

**If eligible rows = 0:** write the Step 6 coverage declaration with all-zero counts and a note explaining why (e.g., `All rows have non-URL citations or no source cited — no rows eligible for automated citation verification`), then write the Step 7 AGENT_COMPLETE marker, and stop. Do not proceed to Steps 2–3.

---

## Step 2 — Bash availability check (do this after Step 1, before Step 3)

After reading the sheet and confirming eligible rows exist, confirm the Bash tool is available by attempting a trivial command (e.g., `echo "bash_available"`). If Bash is unavailable:

1. Fall back to manual `WebFetch` verification for the top 5 eligible parameters (Study-Derived or Org-Reported with a URL in column F — select by CE impact proximity, prioritising rows whose Description mentions mortality rate, coverage, or unit cost take precedence).
2. For each of the 5 parameters: call `WebFetch` on the Source to Verify URL, then compare the stated value against the fetched content.
3. Write verdicts (`Matched ✓`, `Contradicted ✗`, or `Could not verify`) and evidence to columns G and H of those 5 rows.
4. Write a single row to the Hardcoded Values sheet immediately after the last filled row: column B = `source-citation-verify`, column D = `AGENT_COMPLETE`, column F = `Bash unavailable — fell back to manual spot-check of top-5 eligible parameters; full citation verification not completed. [N] spot-checked. [K] Matched ✓, [M] Contradicted ✗, [P] Could not verify.`, all other columns blank.
5. Stop — do not proceed to Steps 3–7 below (the AGENT_COMPLETE marker was already written in fallback bullet 4 above).

The orchestrator (SKILL.md) checks the AGENT_COMPLETE text for `Bash unavailable` and will surface a warning to the researcher.

---

## Step 3 — Write the verification script

Write the following Python script to `/tmp/citation_verify.py` using the Write tool:

```python
#!/usr/bin/env python3
"""
Batch-verify hardcoded values against a source using the Anthropic Citations API.

Usage: python3 citation_verify.py /tmp/citation_source.txt < /tmp/citation_params.json

  /tmp/citation_source.txt  — plain text of the source document (read directly, no JSON encoding)
  stdin                     — JSON [{"row_num": int, "description": str, "value": str}, ...]

Output (stdout): JSON [{"row_num": int, "verdict": str, "evidence": str}]
  verdict:  "Matched ✓" | "Contradicted ✗" | "Could not verify"
  evidence: verbatim sentence from a citation object, or reason verification failed.
"""
import sys, json, os, re

try:
    import anthropic
except ImportError:
    params = json.loads(sys.stdin.read())
    print(json.dumps([
        {"row_num": p["row_num"], "verdict": "Could not verify",
         "evidence": "anthropic package not found — run: pip install anthropic"}
        for p in params
    ]))
    sys.exit(0)


def find_citation_for_quote(model_quote, available_citations):
    """Return the cited_text of the first citation whose text overlaps with model_quote,
    and remove that citation from available_citations so it cannot be reused.

    citation.cited_text is verbatim text extracted from the source document by the API.
    citation.start_char_index is a position in the SOURCE DOCUMENT — not the response —
    so it cannot be used to locate citations within the response text.
    Substring overlap is the correct coordinate-independent matching strategy.
    """
    if not model_quote:
        return None
    q = model_quote.lower()[:60]
    for idx, c in enumerate(available_citations):
        ct = c.cited_text.lower()
        if q in ct or ct[:60] in model_quote.lower():
            return available_citations.pop(idx).cited_text
    return None


def run():
    # Read stdin first so every error-return path has per-parameter row numbers.
    # If run() called print() AND returned a value, __main__ would emit a second JSON
    # object — the parse would fail. Reading stdin first and always returning avoids that.
    try:
        params = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        return [{"row_num": 0, "verdict": "Could not verify",
                 "evidence": f"Invalid parameters JSON: {e}"}]

    if len(sys.argv) < 2:
        return [{"row_num": p["row_num"], "verdict": "Could not verify",
                 "evidence": "Script invocation error: source file path not provided"}
                for p in params]

    try:
        full_text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
        truncated = len(full_text) > 80000
        source_text = full_text[:80000]
    except OSError as e:
        return [{"row_num": p["row_num"], "verdict": "Could not verify",
                 "evidence": f"Could not read source file: {e}"} for p in params]

    if not params:
        return []

    truncation_note = " [Source text truncated at 80,000 chars — value may appear beyond truncation point; verify manually]" if truncated else ""

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    items = "\n".join(
        f'{i+1}. "{p["description"]}": stated value = {p["value"]}'
        for i, p in enumerate(params)
    )

    # Prose format so the API attaches citation objects to inline quoted text.
    # Each citation object carries cited_text extracted verbatim from the source document.
    prompt = (
        "For each numbered item, check whether the attached document explicitly states that value.\n"
        "Respond with exactly one line per item:\n"
        "  If found:        N. MATCHED — \"exact verbatim sentence from document\"\n"
        "  If contradicted: N. CONTRADICTED — \"exact verbatim sentence stating the different value\"\n"
        "  If not found:    N. NOT_FOUND\n\n"
        f"Items:\n{items}"
    )

    try:
        # Citations is GA as of June 2025 — use standard messages.create (no betas parameter).
        # The document block with citations.enabled causes the API to attach citation objects
        # (text extracted verbatim from the source) to model output drawn from the document.
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=4096,
            messages=[{"role": "user", "content": [
                {
                    "type": "document",
                    "source": {"type": "text", "media_type": "text/plain", "data": source_text},
                    "citations": {"enabled": True}
                },
                {"type": "text", "text": prompt}
            ]}]
        )
    except Exception as e:
        return [{"row_num": p["row_num"], "verdict": "Could not verify",
                 "evidence": f"API error: {str(e)[:120]}"} for p in params]

    # Collect citation objects. These are our ONLY trusted evidence source —
    # the API extracted them verbatim from source_text, not generated by the model.
    # Use (... or []) to guard against the attribute existing but being set to None.
    available_citations = []
    for block in response.content:
        for c in (getattr(block, "citations", None) or []):
            if hasattr(c, "cited_text") and c.cited_text:
                available_citations.append(c)

    response_text = "".join(b.text for b in response.content if hasattr(b, "text"))

    # Map item number -> response line text.
    line_map = {}
    for line in response_text.split("\n"):
        m = re.match(r"^(\d+)\.", line.strip())
        if m:
            n = int(m.group(1))
            if 1 <= n <= len(params):
                line_map[n] = line.strip()

    results = []
    for i, param in enumerate(params):
        n = i + 1
        line_text = line_map.get(n, "")

        vm = re.search(r"\b(MATCHED|CONTRADICTED|NOT_FOUND)\b", line_text, re.IGNORECASE)
        if not vm:
            results.append({"row_num": param["row_num"], "verdict": "Could not verify",
                             "evidence": "No result line found in API response"})
            continue

        verdict_raw = vm.group(1).upper()

        if verdict_raw in ("MATCHED", "CONTRADICTED"):
            q_match = re.search(r'"([^"]{10,})"', line_text)
            model_quote = q_match.group(1) if q_match else ""

            # Only accept confirmed citation objects as evidence.
            # If no citation object matches, do not surface the model's own text —
            # we cannot distinguish accurate quoting from hallucination without the citation.
            confirmed = find_citation_for_quote(model_quote, available_citations)
            if confirmed:
                verdict = "Matched ✓" if verdict_raw == "MATCHED" else "Contradicted ✗"
                evidence = confirmed[:300]
            else:
                verdict = "Could not verify"
                evidence = "Match reported by model but no citation object returned — manual check required"
        else:
            verdict = "Could not verify"
            evidence = "Value not found in source document" + truncation_note

        results.append({"row_num": param["row_num"], "verdict": verdict, "evidence": evidence})

    # Ensure every param has a result.
    returned = {r["row_num"] for r in results}
    for p in params:
        if p["row_num"] not in returned:
            results.append({"row_num": p["row_num"], "verdict": "Could not verify",
                             "evidence": "No result returned for this item"})
    return results


if __name__ == "__main__":
    print(json.dumps(run()))
```

---

## Step 4 — Fetch source text and verify

Group eligible rows by `source_url`. For each unique source URL:

### 4a — Fetch as plain text

**GBD / IHME sources** — detect before fetching. A row is a GBD/IHME source if column F contains a URL with `vizhub.healthdata.org`, `ghdx.healthdata.org`, `healthdata.org`, or `ihmeuw.org`.

For these rows write `Could not verify — GBD/IHME interactive source; verify the vizhub query or GHDX download manually` and skip the fetch. Do not attempt WebFetch on vizhub or GHDx URLs — they return JavaScript shell pages with no data content.

**Box.com URLs** — detect before fetching. A URL is a Box.com URL if column F contains `box.com` or `givewell.box.com`. For these rows write `Could not verify — Box.com link requires authenticated access and cannot be verified automatically. Replace with a public link before publication.` Do not attempt WebFetch on Box URLs.

**Google Doc** (`docs.google.com/document/...`): call `get_doc_content`. Use the full returned text.

**PDF sources** — A URL is likely a PDF source if it ends in `.pdf`, or if WebFetch returns a `Content-Type` header of `application/pdf`, or if the returned content begins with `%PDF`. Attempt `WebFetch`. If readable text is returned, proceed. If binary or not text-extractable, write `Could not verify — PDF binary` and skip. If a DOI URL (e.g., `https://doi.org/10.xxxx`) returns an HTML landing page rather than document text, write `Could not verify — DOI resolved to HTML landing page, not source text; verify by fetching the PDF link from the journal landing page.`

**Any other HTTP/HTTPS URL**: call `WebFetch`. Use the returned text content. If the response appears to be HTML (contains `<!DOCTYPE` or `<html`) rather than the underlying document text, write `Could not verify — URL returned a web page, not source text` for all rows from this source and skip. If the response appears binary or garbled, write `Could not verify — source not text-extractable` and skip.

If the fetch fails (HTTP error, auth required, domain blocked): write `Could not verify — source not accessible` for all rows from this source.

### 4b — Run Citations API

For each source with successfully fetched text:

1. **Write source text to `/tmp/citation_source.txt`** using the Write tool. Write the raw text directly — do not embed it in JSON. This avoids JSON-encoding issues with quotes, backslashes, or special characters in source documents.

2. **Write parameters JSON to `/tmp/citation_params.json`** using the Write tool:
```json
[
  {"row_num": <N>, "description": "<col E>", "value": "<col D>"},
  ...
]
```
Parameters are short strings and safe to embed in JSON directly.

3. **Run**:
```bash
python3 /tmp/citation_verify.py /tmp/citation_source.txt < /tmp/citation_params.json
```

   Before running the script for each new source, confirm the `/tmp/citation_params.json` write in step 3b-2 completed without error. If the Write tool call for `/tmp/citation_params.json` returned an error, write `Could not verify — script parameter write failed` for all rows from this source and skip the Bash run.

4. Parse the JSON array. Each item has `row_num`, `verdict`, and `evidence`. If the command fails or returns non-JSON, write `Could not verify — script error` for all rows from this source.

---

## Step 5 — Write results to sheet

For each eligible row processed in Steps 4a/4b: write the resulting `[verdict, evidence]` to columns G and H. **Do not write to any row whose column G was already non-empty in Step 1** — those rows were already verified and must not be overwritten.

Do NOT write `["", ""]` for rows whose verdict was already written directly by the skip-rule handling in Step 1 or Step 4a (e.g., rows with non-URL citations, Google Sheets URLs, or GBD/IHME sources). Those rows already have column G populated. Only write `["", ""]` for rows where column F is blank — i.e. rows where no verdict was written at all.

Because already-verified rows may be interspersed with new rows, write results **row by row** using individual `modify_sheet_values` calls (one call per eligible row) rather than a single contiguous `G2:H{last_row}` array. A single array write would overwrite already-verified cells in the gaps with blank values.

If a single-row write fails (MCP error), retry once. If retry also fails, record the row number in your reasoning and continue. After all writes, read back column G for all eligible rows in 50-row batches (same batching pattern as Step 1) and compare against intended verdicts — any discrepancy indicates a silent write failure. Include failed row numbers in AGENT_COMPLETE column F.

---

## Step 6 — Coverage declaration

Write to chat:

```
Source citation verification complete.
Total rows: [N] | Eligible (Study-Derived / Org-Reported with URL): [N] | Skipped: [N]
Unique sources fetched: [N]
Verdicts — Matched ✓: [N] | Contradicted ✗: [N] | Could not verify: [N]
  (of Could not verify: [N] match reported but uncited, [N] GBD/IHME interactive source, [N] source not accessible, [N] not found in doc, [N] other)
Note: column G verdict is a model judgment — researchers should read column H and verify independently.
```

If any `Contradicted ✗` rows exist:
```
⚠️ Contradicted values (researcher attention required):
• Row [N] — [description]: model states [value] | source sentence: "[cited text]"
```

---

## Step 7 — Write completion marker

This agent writes directly to the Hardcoded Values sheet, not a staging tab. The orchestrator should not apply the standard staging-tab AGENT_COMPLETE parser to this agent's output.

After writing all results to columns G and H (and writing the coverage declaration in Step 6), write ONE final row to the Hardcoded Values sheet immediately after the last data row: column B = `source-citation-verify`, column D = `AGENT_COMPLETE`, column F = `COVERAGE_ROWS: [row range checked, e.g., 2-85] | Output sheet: Hardcoded Values. [N] rows eligible. [K] Matched ✓, [M] Contradicted ✗, [P] Could not verify. [Q] skipped — breakdown: [n1] no URL or blank F, [n2] non-URL citation, [n3] Google Sheets URL, [n4] GBD/IHME interactive, [n5] column G already non-blank (prior determination — not overwritten).`, all other columns blank. Use a single `modify_sheet_values` call. This is the absolute last action.
