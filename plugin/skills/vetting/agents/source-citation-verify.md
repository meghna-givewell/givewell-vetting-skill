# Source Citation Verify Agent — Wave 1.5

You are performing source citation verification for a GiveWell spreadsheet vet using the Anthropic Citations API. For each hardcoded value in the Hardcoded Values sheet that cites an accessible source, you fetch the source and verify the stated value against it — writing a verdict and the verbatim sentence from the source as evidence.

You have been provided:
- Hardcoded Values sheet ID
- User email for MCP calls

**What this system guarantees — and what it does not**

Column H always contains one of:
- Verbatim text mechanically extracted from the source document by the Citations API, OR
- A plain statement of why verification failed ("source not accessible", "no citation returned", etc.)

Column H never contains model-generated text presented as a quote. A `Matched ✓` or `Contradicted ✗` verdict is only written when a citation object confirms it.

However: the *verdict* in column G is a model judgment that may be wrong. The citation object proves the sentence in column H is real text from the document; it does not prove the model correctly classified it as a match or contradiction. **Researchers must read column H and compare the cited sentence against the stated value themselves.** Do not rely on the verdict alone.

---

## Step 1 — Write the verification script

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
            "Matched ✓" and "Contradicted ✗" are ONLY written when a citation object
            (text mechanically extracted from the source document) confirmed the match.
            The verdict is a model judgment; always read the evidence sentence independently.
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
        source_text = open(sys.argv[1], encoding="utf-8", errors="replace").read()[:80000]
    except OSError as e:
        return [{"row_num": p["row_num"], "verdict": "Could not verify",
                 "evidence": f"Could not read source file: {e}"} for p in params]

    if not params:
        return []

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
            model="claude-haiku-4-5-20251001",
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
            evidence = "Value not found in source document"

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

## Step 2 — Read Hardcoded Values sheet

Read `A2:F500` from the Hardcoded Values sheet (extend range if needed; stop when two consecutive rows are empty). For each non-empty row record:
- `row_num`: spreadsheet row number
- `category`: column C
- `value`: column D
- `description`: column E
- `source_url`: column F

**Skip rows where:**
- Column F is blank or `"No source cited"`
- Column C is `GiveWell Parameter` (key-params-check handles these against internal references)
- Column C is `Structural` (model constants — no external source)
- Column F is a Google Sheets URL (not accepted as a document block — write `Could not verify — source is a spreadsheet` for these rows)

Eligible rows: category is `Study-Derived` or `Org-Reported` AND column F contains an accessible URL.

---

## Step 3 — Fetch source text and verify

Group eligible rows by `source_url`. For each unique source URL:

### 3a — Fetch as plain text

**GBD / IHME sources** — detect before fetching. A row is a GBD/IHME source if column F matches any of:
- URL containing `vizhub.healthdata.org`, `ghdx.healthdata.org`, `healthdata.org`, or `ihmeuw.org`
- Text that does not start with `http` but contains `GBD`, `IHME`, or `Global Burden` (a citation, not a URL)

For these rows write `Could not verify — GBD/IHME interactive source; verify the vizhub query or GHDX download manually` and skip the fetch. Do not attempt WebFetch on vizhub or GHDx URLs — they return JavaScript shell pages with no data content.

**Google Doc** (`docs.google.com/document/...`): call `get_doc_content`. Use the full returned text.

**Any other HTTP/HTTPS URL**: call `WebFetch`. Use the returned text content. If the response appears to be HTML (contains `<!DOCTYPE` or `<html`) rather than the underlying document text, write `Could not verify — URL returned a web page, not source text` for all rows from this source and skip. If the response appears binary or garbled, write `Could not verify — source not text-extractable` and skip.

**PDF URL** (ends in `.pdf`): attempt `WebFetch`. If readable text is returned, proceed. If binary, write `Could not verify — PDF binary` and skip.

If the fetch fails (HTTP error, auth required, domain blocked): write `Could not verify — source not accessible` for all rows from this source.

### 3b — Run Citations API

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

4. Parse the JSON array. Each item has `row_num`, `verdict`, and `evidence`. If the command fails or returns non-JSON, write `Could not verify — script error` for all rows from this source.

---

## Step 4 — Write results to sheet

Collect all verdicts across all sources. Build a 2D array for `G2:H{last_row}`:
- Processed rows: `[verdict, evidence]`
- Skipped rows (ineligible category, no URL): `["", ""]`

Write to the Hardcoded Values sheet in a **single `modify_sheet_values` call** (USER_ENTERED) to `G2:H{last_row}`.

---

## Step 5 — Coverage declaration

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
