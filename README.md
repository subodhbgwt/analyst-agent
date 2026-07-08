# analyst-agent

An agentic workflow that turns a company name into an investment one-pager.

Type `/company-profile Getinge` in [Claude Code](https://claude.com/claude-code)
and the agent:

1. resolves the ticker and pulls real financials from Yahoo Finance
2. computes growth, margins and a screening DCF (`src/analysis.py`)
3. researches the business on the web and writes a specific, sourced thesis
4. renders a formatted PPTX one-pager (`src/render.py`)

The design splits the work deliberately: **scripts do the deterministic
parts** (data fetching, arithmetic, rendering) so the numbers are exactly
reproducible, and **the agent does the judgment parts** (ticker resolution,
qualitative research, thesis writing, QA). The skill definition in
[`.claude/skills/company-profile/SKILL.md`](.claude/skills/company-profile/SKILL.md)
is the contract between the two.

## Example output

See [`examples/`](examples/) for a generated profile of Getinge AB
(Nordic medtech, SEK 34bn revenue).

## Running without the agent

Each stage is a plain script and works standalone:

```bash
pip install -r requirements.txt
python src/fetch.py GETI-B.ST runs/geti/company.json
python src/analysis.py runs/geti/company.json runs/geti/analysis.json
# write runs/geti/thesis.json by hand (see SKILL.md for the schema)
python src/render.py runs/geti/
```

## Honest limitations

- Yahoo Finance data quality varies; the fetch script normalizes but does
  not audit it.
- The DCF is a screening heuristic (single-stage FCF fade), not a model
  you would bid off. It exists to flag "cheap vs expensive at first
  glance", nothing more.
- Thesis quality is the agent's responsibility; the skill enforces
  specificity rules but a human should read the output before it goes
  anywhere that matters.
