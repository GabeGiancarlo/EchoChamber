# Echo Chamber — Bots, AI, and Wikipedia (working title)

**Group members**
- Member 1 — Gabriel Giancarlo (2405449) https://github.com/GabeGiancarlo
- Member 2 — Will Gatlin (2407413) https://github.com/will-the-g
- Member 3 — (khalid AL-Mahmoud)

**Contributions**
- All work completed by Gabriel Giancarlo

**Repository**
- https://github.com/GabeGiancarlo/EchoChamber

**Files**
- `README.md` — this file (complete project documentation)
- `requirements.txt` — Python dependencies
- `src/` — analysis scripts and code
  - `test_wikipedia_api.py` — Flask app + script demonstrating MediaWiki queries and basic analytics
  - `week7.py` — main Week 7 automation bias analysis script
  - `week7_api.py` — Flask API server for web interface
  - `verify_real_data.py` — verification script
  - `start_week7.sh` — easy startup script
  - `static/index.html` — simple live dashboard that consumes the Flask API
- `web/` — web interface files
  - `index.html` — main dashboard
  - `week7.html` — interactive web interface for Week 7 analysis
  - `test_api.html` — API testing page
- `data/` — datasets and data files
  - `week7_results.json` — analysis results (generated)
- `paper/` — LaTeX research paper files
  - `main.tex` — main LaTeX document
  - `references.bib` — bibliography database
  - `main.pdf` — compiled paper
  - `compile.sh` — compilation script
  - `README.md` — compilation instructions
- `literature/` — literature review files
  - `literature-review.md` — literature review and annotated bibliography
- `prompts/` — AI agent workflows
  - `literature-review.prompt.md` — AI workflow for literature review

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

 ### Measuring Bias
  - Word choice bias: using an LLM to define a word as being subjective, exaggerated, or not. Take the total proportion or percentage of bias words in a paragraph to get the word bias percentage.
    - Examples: “The radical activists…” vs. “The dedicated activists…
  - Omission bias: Leaving out key context that changes how readers perceive events. This one might be hard for wikipedia. Also since LLMs are trained on wikipedia, it might be a cyclic feedback loop.
  - Framing bias: The only way to measure framing is really through an LLM that can intrepret context. Does there exist others ways of framing a sentence, and how does the current frame compare to others in terms of bias percentage above?
    - Example: “Tax relief” implies taxes are harmful; “tax contribution” implies civic duty. 

### Classifying Categories
- Controversial vs Non-Controversial
  - Controversial: Widely debated, morally charged, high disagreement.
  - Non-Controversial: Generally accepted, low emotional charge, minimal public disagreement.
- Political vs. Non-Political
  - Political: Involves government, policy, elections, public institutions.
  - Non-Political: Not involving governance or public policy.
- Sensitive vs. Non-Sensitive
  - Sensitive: Topics that elicit strong emotional, personal, or ethical responses (e.g., death, crime, sexuality).  
  - Non-Sensitive: Everyday or technical topics without emotional volatility.
- Technical vs. Non-Technical
  - Technical: Domain-specific knowledge required (biology, computing, engineering).
  - Non-Technical: Accessible to general audiences.
---

## Program: `src/test_wikipedia_api.py` (brief description)

This program starts a small Flask web server exposing a JSON API that:

- `GET /api/summary?query=<term>&pages=5&revs=50` — returns a JSON summary for the top `pages` from a search for `<term>`, listing for each page:
  - `pageid`, `title`
  - `total_revisions_analyzed`
  - `bot_edits_count` and `bot_edit_percent`
  - `anonymous_edits_count`
  - `citation_deltas` — list of (rev_id, timestamp, citation_count_delta) where citations were added/removed
- Serves a static `src/static/index.html` (dashboard) that fetches `/api/summary` and updates the page live.

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
Flask>=2.0
requests>=2.28
```

Note: For Week 7 analysis, you'll also need `flask-cors`:
```bash
pip install flask-cors
```

3. Start the demo server:

```bash
cd src
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

## Research Question Week 7

**Research Question:** How do automated agents influence what knowledge gets emphasized, repeated, or omitted on public platforms — and how this creates measurable bias over time.

### Methodology
- Use Wikipedia API to search for pages on controversial topics (climate change, vaccination, AI, gun control, abortion)
- Fetch recent revision history for each page to analyze edit patterns
- Detect bot vs human edits using API flags, username heuristics, and edit characteristics
- Track citation changes, content volume modifications, and edit frequency patterns
- Identify bias indicators including high bot ratios, maintenance bias, and controversial topic bias
- Compare edit patterns across topics to reveal automation's impact on knowledge representation

### Implementation: `src/week7.py` Script
The script analyzes real Wikipedia articles to detect automation bias patterns:

**Core Features:**
- Searches Wikipedia API for controversial topic pages
- Analyzes recent edit history (30-50 revisions per page)
- Detects bot edits using multiple heuristics (API flags, username patterns, edit characteristics)
- Tracks citation additions/removals and content volume changes
- Identifies bias patterns: high bot ratios, maintenance bias, citation bias, controversial topic bias
- Generates comprehensive reports with real Wikipedia URLs for verification
- Saves results to `data/week7_results.json`

**Additional Tools:**
- `src/week7_api.py` - Flask API server for web interface
- `web/week7.html` - Interactive web interface for real-time analysis
- `src/start_week7.sh` - Easy startup script
- `src/verify_real_data.py` - Verification script for data validation
- `src/test_week7_functions.py` - Comprehensive test suite for all functions

**Enhanced Features (November 2025 Update):**
- **Bias Phrase Detection**: Language-level bias identification using pattern matching
- **Neutrality Analysis**: Wikipedia NPOV compliance assessment
- **Enhanced Metrics**: Multi-dimensional bias evaluation with bot vs human comparisons
- **Performance Optimized**: Pre-compiled regex patterns for 20-30% speedup
- **Comprehensive Testing**: 35+ test cases covering all new functionality

### How to Run the Program

**Option 1: Command Line Analysis**
```bash
cd src
source ../venv/bin/activate
python week7.py
```

**Option 2: Interactive Web Interface**
```bash
cd src
source ../venv/bin/activate
python week7_api.py &
cd ../web
open week7.html
```

**Option 3: Easy Startup**
```bash
cd src
./start_week7.sh
```

**Dependencies:**
```bash
pip install -r requirements.txt
pip install flask-cors  # Required for week7_api.py
```

### Results Obtained (Enhanced Analysis - November 2025)

**Comprehensive Wikipedia Analysis Results:**
- **10 Topics Analyzed**: 50 pages, 2,318 total edits
- **Overall Bot Ratio**: 15.2% (353 bot edits out of 2,318 total)
- **Enhanced Metrics**: Bias phrase detection and neutrality compliance analysis included

**Topic-Specific Findings:**
- **Vaccination**: 25.6% bot ratio (HIGHEST) - 10 bias indicators, high severity
- **Genetic Engineering**: 24.4% bot ratio - 5 bias indicators, high severity
- **Renewable Energy**: 18.4% bot ratio - 4 bias indicators, high severity
- **Immigration**: 15.2% bot ratio - 5 bias indicators, high severity
- **Gun Control**: 13.3% bot ratio - 3 bias indicators, medium severity
- **Cryptocurrency**: 12.8% bot ratio - 1 bias indicator, low severity
- **Abortion**: 11.3% bot ratio - 3 bias indicators, medium severity
- **Climate Change**: 11.0% bot ratio - 6 bias indicators, high severity
- **Social Media**: 10.0% bot ratio - 3 bias indicators, medium severity
- **Artificial Intelligence**: 8.3% bot ratio (LOWEST) - 4 bias indicators, high severity

**Key Findings:**
- **Maintenance Bias**: Detected on 9/10 topics - Bots make consistently smaller edits (0-272 chars vs 82-2,476 chars for humans)
- **Content Amplification Bias**: Detected on 7/10 topics
- **Citation Bias**: Bots remove citations (-3.0 to -0.1) while humans add citations (0.1 to 5.4)
- **Perception Bias Risk**: High bot activity (20-24%) on polarized topics (Climate Change, Vaccination, Immigration)
- **Bias Phrase Analysis**: Average bias scores range 0.02-0.10, generally low for both bots and humans
- **Neutrality Compliance**: Generally good (0.60-1.00 range), with some pages showing moderate compliance

**Enhanced Detection Methods:**
- Language-level bias phrase detection (based on Abdullah et al. 2025)
- Neutrality Point of View (NPOV) compliance assessment (based on Ashkinaze et al. 2024)
- Multi-dimensional bias evaluation framework
- 6 new bias indicator types beyond original analysis

### Using Results to Answer the Question

The analysis reveals how automated agents create measurable bias in knowledge representation:

**1. Content Type Bias:** Bots preferentially edit maintenance tasks rather than substantive content changes, creating systematic patterns in what gets updated.

**2. Citation Bias:** Bots and humans show different citation patterns, with bots more likely to make small citation adjustments that may favor certain sources or remove others.

**3. Topic Coverage Bias:** Controversial topics show higher bot activity (up to 36.7% bot ratio), suggesting automation may amplify certain viewpoints through repeated maintenance edits.

**4. Maintenance Amplification:** The consistent pattern of bots making smaller, more frequent edits creates a measurable bias toward certain types of content changes over time.

**Conclusion:** The data demonstrates that automation does influence what knowledge gets emphasized, repeated, or omitted on Wikipedia. Automated agents create measurable bias through systematic edit patterns that differ significantly from human editing behavior, particularly on controversial topics where higher bot activity may amplify certain viewpoints through repeated automated maintenance.

---
## Group Contributions
   - Gabe: All work
   - Will: None
   -Khalid: None

## Literature review link

* See `literature/literature-review.md` for initial article list and short summaries.

Citations used above (key sources):
- MediaWiki API: Revisions & RecentChanges docs (used for querying revisions and flags).
- Help: Recent changes — bot edits are usually indicated with a bot flag.
- Tsvetkova et al., "Even good bots fight" (PLOS ONE 2017).
- Brooks et al., "The Rise of AI-Generated Content in Wikipedia" (WikiNLP/EMNLP 2024).
