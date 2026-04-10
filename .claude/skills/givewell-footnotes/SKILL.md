# GiveWell-Style Footnotes

Convert a research document's factual claims into verified footnotes with direct source quotes.

## When This Skill Applies

You have a markdown document (QEA, research update, memo) that contains factual claims — some with inline citations, some without — and you want every claim backed by a footnote containing a hyperlinked source and a direct quote from that source.

## Inputs

- **File path**: Path to the markdown document to annotate
- **Scope** (optional): "full" (default) processes the entire document; "section" processes only a named section; "summary-only" processes only the summary

## What a GiveWell-Style Footnote Looks Like

Each footnote has three parts:

```markdown
[^N]: [Author Year](URL): "Exact quote from the source supporting the claim." Any verification notes.
```

1. **Hyperlinked source** — author, year, and a working URL (DOI, PMC, or direct link)
2. **Direct quote** — the actual sentence or passage from the source that contains the data point or finding. Not a paraphrase.
3. **Verification notes** — corrections, caveats, or flags for manual follow-up

Example:
```markdown
Neonatal mortality in SSA is ~27/1,000 live births.[^4]

[^4]: [WHO Newborn Mortality Fact Sheet](https://www.who.int/news-room/fact-sheets/detail/newborn-mortality): "Sub-Saharan Africa had a neonatal mortality rate of 27 deaths per 1,000 live births in 2022, the highest in the world." Source: UN IGME 2024.
```

## Method

### Step 1: Extract claims
Scan the document and build a numbered list of every factual claim needing a source. For each claim, record: the claim text, the existing citation (if any), whether it is cited or uncited, and the section it appears in. Present the full claim list to the user before proceeding.

### Step 2: Check for local full text
Before fetching from the internet, check the repository for PDFs or notes already containing the source text. If a relevant PDF exists locally, use the `/split-pdf` skill to read it.

### Step 3: Attempt to retrieve full text for sources not already local
Use the project's PDF retriever, chaining: Semantic Scholar → Unpaywall → PubMed Central → CORE. If a PDF is downloaded, use `/split-pdf` to read it.

### Step 4: Fall back to abstracts and web sources
Fetch PubMed abstracts, WHO fact sheets, UNICEF data pages, or use WebSearch as a last resort. **If you cannot find the exact quote, do not fabricate one.** Flag for manual verification instead.

### Step 5: Verify each claim against the source
For each claim: if source confirms exactly → write footnote with direct quote; if approximately → note discrepancy; if contradicts → correct the claim and note the correction; if inaccessible → flag "Manual verification needed"; if uncited and no source found → flag "Needs citation."

### Step 6: Convert to footnotes
Replace inline citations with footnote markers `[^N]`, add markers to newly-sourced uncited claims, write footnote definitions at end of document, and deduplicate thoughtfully (same paper may appear in multiple footnotes with different quotes for different claims).

### Step 7: Validation
Run a consistency check script to confirm every `[^N]` reference has a matching `[^N]:` definition and vice versa. Report results to the user.

## Parallelization
Group claims by source and use parallel agents — each handles 1–3 sources, fetching and reading that source once. A typical document needs 5–10 agents.

## What NOT to Do
- Do not fabricate quotes.
- Do not paraphrase and present as a quote — verbatim only.
- Do not skip uncited claims.
- Do not rely on memory of what a paper says — always fetch.
- Do not read full PDFs directly — always use the split-pdf workflow.
- Do not silently correct claims — note every correction in the footnote.

## Output
The skill modifies the input file in place and prints a verification summary: claims verified with direct quotes, verified from abstracts only, flagged for manual verification, factual corrections made, and uncited claims still needing sources.
