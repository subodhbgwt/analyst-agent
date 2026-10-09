---
name: company-profile
description: Generate a one-page investment profile deck for a public company. Fetches real financials, runs a screening valuation, researches the business and renders a PPTX one-pager. Use when asked to profile a company, e.g. "/company-profile Getinge" or "make a one-pager on Elekta".
---

# Company profile agent

Turn a company name into an investment one-pager. The scripts handle the
deterministic work (data, math, rendering); you handle the judgment
(resolving the ticker, researching the business, writing the thesis).

## Steps

1. **Resolve the ticker.** If the user gave a name, not a ticker, find the
   Yahoo Finance ticker (e.g. Getinge → `GETI-B.ST`). Nordic listings need
   the exchange suffix (`.ST`, `.CO`, `.OL`, `.HE`). Confirm with the user
   only if genuinely ambiguous.

2. **Create a working directory** `runs/<ticker>/` inside the repo.

3. **Fetch financials:**
   ```
   python src/fetch.py <TICKER> runs/<ticker>/company.json
   ```
   Sanity-check the output: does the company name match what the user asked
   for? Are there at least 3 years of revenue? If data is thin, say so
   rather than papering over it.

4. **Run the analysis:**
   ```
   python src/analysis.py runs/<ticker>/company.json runs/<ticker>/analysis.json
   ```
   Defaults: 8.5% WACC, 2% terminal growth. If the user gave
   different assumptions, edit the call in `analysis.py`'s `analyze()`
   signature or pass them through.

5. **Research and write the thesis.** This is your part, not a script.
   Use web search for: what the company actually does, recent news
   (last 6 months), competitive position, and anything that would worry
   an investor. Then write `runs/<ticker>/thesis.json`:
   ```json
   {
     "overview": ["3-5 bullets: what it does, segments, geography, market position"],
     "angle": ["2-4 bullets: why this could be interesting to an investor"],
     "risks": ["2-3 bullets: real risks and open questions, not boilerplate"]
   }
   ```
   Rules: every bullet must be specific to this company (if a bullet could
   apply to any company, cut it). Cite numbers from company.json rather
   than from memory. Keep bullets under 20 words.

6. **Render the deck:**
   ```
   python src/render.py runs/<ticker>/
   ```

7. **QA before handing over.** Open questions to check: chart years match
   the table, valuation bullets present, no "None" strings visible. Report
   the output path and the 3 headline numbers (revenue, EBITDA margin,
   DCF vs market).

## Honesty rules

- The DCF is a screening heuristic. Never present it as a price target.
- If fetch returns partial data (missing EBITDA, no FCF), state what is
  missing in your summary. Do not invent numbers.
- Thesis bullets must be traceable to a source you actually read.
