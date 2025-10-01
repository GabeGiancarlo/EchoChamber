# Echo Chamber — Bots, AI, and Wikipedia (working title)

**Group members**
- Member 1 — Gabriel Giancarlo (2405449) https://github.com/GabeGiancarlo
- Member 2 — (replace)
- Member 3 — (replace)

**Repository**
- (Post the repo link on Discord when ready)

**Files**
- `README.md` — this file
- `literature-review.md` — literature review and annotated bibliography (local file)
- `test_wikipedia_api.py` — Flask app + script demonstrating MediaWiki queries and basic analytics
- `requirements.txt` — Python dependencies
- `static/index.html` — simple live dashboard that consumes the Flask API

**Citations / background**
- MediaWiki provides an Action API for queries and revisions; the API exposes revision metadata and revision flags that can indicate bot-marked edits.
- Bots are widely used for maintenance and content tasks on Wikipedia and have measurable interactions with each other and with humans. See Tsvetkova et al. (2017) and Zheng et al. (2019).
- Recent work documents a rise in AI-generated content and concerns about quality and bias amplification.

---

## Abstract

Wikipedia relies on a mixed ecosystem of human editors and automated tools (bots). As bots and generative-AI authored content increase, their role raises questions about neutrality, reliability, and bias: automated enforcement of citation rules or automated textual generation may introduce systematic patterns that look like "objective" fixes but in fact encode biases. This project seeks to measure how bot and AI-influenced edits are distributed across pages related to politically/socially charged topics, and to prototype tooling that surfaces bot activity and citation changes for human reviewers.

---

## Research questions

1. **RQ1 — What proportion of recent edits on topic X are made by accounts flagged as bots vs human editors?**  
   Discussion: We will measure per-article and per-topic bot / human edit proportions across a moving window (last N revisions or last M days). We will use MediaWiki revision flags and username heuristics (e.g., accounts ending in "bot") and compare results across topics.

2. **RQ2 — How often do edits (bot or human) add or remove citations, and are bot edits more/less likely to change reference counts?**  
   Discussion: We will count `<ref` occurrences in revision content or diffs and mark where citation counts increase/decrease, and link that to whether the edit was bot-flagged (or automated).

3. **RQ3 — Could automated enforcement (or AI-generated text) unintentionally reinforce systemic bias, e.g., by preferentially adding certain kinds of sources or producing stylistic patterns that correlate with bias detectors?**  
   Discussion: We'll combine edit metadata with simple content metrics (source domains added, adjectives/phrasing signals) and then qualitatively inspect examples flagged as automated.

---

## Methodology (plan)

- Data source: live queries to the MediaWiki Action API (en.wikipedia.org/w/api.php) to fetch search results, page IDs, and revision histories. We will rely on revision metadata fields and revision-level flags to determine bot-labeled edits.
- Processing:
  - Search pages for topic keywords → list page IDs.
  - For each page, fetch the last N revisions (e.g., 50) with metadata and content.
  - Mark revisions as bot-like if they include a bot flag (API flags/tags) or the username looks like a bot (heuristic fallback).
  - For citation analysis, count occurrences of `"<ref"` (case-insensitive) in revision content and compute differences between successive revisions.
- Prototype: a small Flask-based local API + one-page dashboard that requests live data and displays per-page summary (total edits, bot edits, bot %; recent citation additions/removals).
- Ethics: all data are public; we will not attempt to deanonymize editors beyond publicly visible usernames; the project will follow Wikimedia terms of use and community norms.

---

## Program: `test_wikipedia_api.py` (brief description)

This program starts a small Flask web server exposing a JSON API that:

- `GET /api/summary?query=<term>&pages=5&revs=50` — returns a JSON summary for the top `pages` from a search for `<term>`, listing for each page:
  - `pageid`, `title`
  - `total_revisions_analyzed`
  - `bot_edits_count` and `bot_edit_percent`
  - `anonymous_edits_count`
  - `citation_deltas` — list of (rev_id, timestamp, citation_count_delta) where citations were added/removed
- Serves a static `index.html` (dashboard) that fetches `/api/summary` and updates the page live.

How it relates to the research question: the program surfaces who (bot vs human) is editing target pages and whether edits are changing citation counts — a starting point for evaluating whether automation changes citation enforcement or introduces suspect content.

---

## How to run / demo instructions (for the next lecture)

1. Clone the repo and `cd` into it.
2. Create a virtual env (recommended) and install:

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

`requirements.txt` includes:

```
Flask
requests
```

3. Start the demo server:

```bash
python test_wikipedia_api.py
```

4. In your browser open `http://localhost:5000` and try queries like:

* `AI-generated content Wikipedia`
* `Climate change`
* `Vaccination`

or run a quick curl to see JSON:

```bash
curl 'http://localhost:5000/api/summary?query=AI-generated+content+Wikipedia&pages=3&revs=30'
```

**Demo tip**: have one group member run and explain the code while another shares the browser to show live updates.

---

## Next steps (what we'll refine in class)

* Expand heuristics for detecting AI-generated text (integrate available detectors).
* Add domain analysis for added references (which domains are being cited by bots vs humans).
* Scale: run the collector as a scheduled job and store revision data to analyze trends over time.

---

## Literature review link

* See `literature-review.md` for initial article list and short summaries.

Citations used above (key sources):
- MediaWiki API: Revisions & RecentChanges docs (used for querying revisions and flags).
- Help: Recent changes — bot edits are usually indicated with a bot flag.
- Tsvetkova et al., "Even good bots fight" (PLOS ONE 2017).
- Brooks et al., "The Rise of AI-Generated Content in Wikipedia" (WikiNLP/EMNLP 2024).
