# Collaboration Log

This file tracks contributions and activities by group members working on the EchoChamber project.

---

## 2025-11-11 — Literature Review Session

**Contributor:** Gabriel Giancarlo  
**Duration:** 2 hours  
**Activity:** Comprehensive review of 4 newly identified peer-reviewed papers on Wikipedia bots and bias

### Papers Reviewed

1. **Reeves & Simperl (2025)** — "Machines in the Margins: A Systematic Review of Automated Content Generation for Wikipedia"
2. **Ashkinaze et al. (2024)** — "Seeing Like an AI: How LLMs Apply (and Misapply) Wikipedia Neutrality Norms"
3. **Abdullah et al. (2025)** — "Detection of Biased Phrases in the Wiki Neutrality Corpus for Fairer Digital Content Management Using Artificial Intelligence"
4. **Schweitzer et al. (2024)** — "Political Bot Bias in the Perception of Online Discourse"

### Summary of Findings

#### Key Insights from Reeves & Simperl (2025)
- Systematic review reveals diverse automated content generation techniques but highlights gaps in evaluation methodologies
- Need for comprehensive evaluation frameworks that assess both effectiveness and bias in automated systems
- Different models and techniques show varying levels of alignment with Wikipedia's editorial standards
- Source content quality significantly impacts generated content quality

#### Key Insights from Ashkinaze et al. (2024)
- Large language models struggle to consistently apply Wikipedia's Neutral Point of View (NPOV) policy
- AI systems show systematic misapplications of neutrality standards, often over-correcting or under-correcting bias
- Challenges in aligning AI outputs with community norms reveal the complexity of automated bias detection
- LLMs may introduce new forms of bias while attempting to correct existing ones

#### Key Insights from Abdullah et al. (2025)
- AI-based methods can effectively detect biased phrases using the Wiki Neutrality Corpus
- Automated bias detection shows promise for enhancing digital content management at scale
- The Wiki Neutrality Corpus provides a valuable resource for training and evaluating bias detection systems
- Integration of bias detection into content moderation workflows can improve neutrality

#### Key Insights from Schweitzer et al. (2024)
- Political partisans exhibit bias in attributing counter-ideological content to bots rather than humans
- Perception of bot activity is influenced by political alignment, not just objective bot indicators
- This attribution bias may affect how users evaluate and trust Wikipedia content
- Understanding perception biases is crucial for interpreting user feedback and edit patterns

### Comprehensive Plan for Applying Insights

#### 1. Enhanced Bias Detection in Data Collection

**From Abdullah et al. (2025) and Ashkinaze et al. (2024):**
- **Action:** Integrate AI-based bias phrase detection into `week7.py` and `week7_api.py`
- **Implementation:**
  - Add a function to detect biased phrases using pattern matching and keyword analysis
  - Incorporate the Wiki Neutrality Corpus concepts (if accessible) or similar bias indicators
  - Track bias indicators per revision, not just citation and size changes
  - Flag revisions that contain potentially biased language patterns

- **Specific Modifications:**
  - Extend `analyze_content_changes()` to include bias phrase detection
  - Add new bias indicators: "biased_language_detected", "neutrality_violation", "political_language"
  - Create a `detect_biased_phrases()` function that scans revision content for known bias patterns
  - Track bias phrase frequency changes over time (similar to citation tracking)

#### 2. Neutrality Norm Analysis

**From Ashkinaze et al. (2024):**
- **Action:** Add analysis of how bot edits align with Wikipedia's Neutral Point of View policy
- **Implementation:**
  - Compare bot vs. human edits for neutrality violations
  - Track instances where bots may be over-correcting or under-correcting bias
  - Measure alignment with NPOV standards using heuristics (e.g., balanced perspective indicators, loaded language detection)

- **Specific Modifications:**
  - Add `analyze_neutrality_alignment()` function to assess NPOV compliance
  - Extend `detect_bias_patterns()` to include neutrality violation detection
  - Track neutrality scores per revision and compare bot vs. human averages
  - Add new bias indicator type: "neutrality_alignment_bias"

#### 3. Evaluation Framework Enhancement

**From Reeves & Simperl (2025):**
- **Action:** Implement more comprehensive evaluation metrics for automated content analysis
- **Implementation:**
  - Add quality metrics beyond size and citation counts
  - Track source content quality indicators (when available)
  - Implement multi-dimensional bias assessment (not just binary bot/human)

- **Specific Modifications:**
  - Extend `generate_bias_report()` to include evaluation framework metrics
  - Add quality scoring system for revisions
  - Track content quality trends over time
  - Compare evaluation metrics across different controversial topics

#### 4. Perception Bias Analysis

**From Schweitzer et al. (2024):**
- **Action:** Account for potential perception biases in data interpretation
- **Implementation:**
  - Document how political or ideological factors might influence edit patterns
  - Add context about controversial topics that may trigger attribution biases
  - Consider user feedback patterns (if available) in bias assessment

- **Specific Modifications:**
  - Enhance controversial topic categorization with political/ideological context
  - Add warnings in reports about potential perception biases
  - Document how topic selection might influence findings
  - Consider adding a "perception_bias_risk" indicator for highly polarized topics

### Script Modification Plan

#### Priority 1: Bias Phrase Detection (High Impact)
**File:** `src/week7.py` and `src/week7_api.py`

**Changes:**
1. Add `detect_biased_phrases(text)` function that:
   - Scans for loaded language, opinionated statements, unbalanced perspectives
   - Uses regex patterns and keyword lists for common bias indicators
   - Returns bias score and detected phrases

2. Modify `analyze_content_changes()` to:
   - Call `detect_biased_phrases()` for each revision
   - Track bias phrase counts and changes over time
   - Store bias detection results in content_analysis dictionary

3. Extend `detect_bias_patterns()` to:
   - Compare bot vs. human bias phrase usage
   - Flag pages with increasing bias phrase frequency
   - Add "biased_language_bias" indicator type

#### Priority 2: Neutrality Analysis (Medium Impact)
**File:** `src/week7.py` and `src/week7_api.py`

**Changes:**
1. Add `analyze_neutrality_alignment(text)` function that:
   - Checks for balanced perspective indicators
   - Detects one-sided arguments or missing counterpoints
   - Assesses compliance with NPOV principles using heuristics

2. Modify `detect_bias_patterns()` to:
   - Compare bot vs. human neutrality scores
   - Flag systematic neutrality violations
   - Add "neutrality_bias" indicator type

#### Priority 3: Enhanced Evaluation Metrics (Medium Impact)
**File:** `src/week7.py`

**Changes:**
1. Extend `generate_bias_report()` to:
   - Include bias phrase statistics
   - Show neutrality alignment scores
   - Provide multi-dimensional bias assessment

2. Add quality metrics tracking:
   - Content quality scores per revision
   - Source diversity indicators (when available)
   - Comprehensive bias severity assessment

#### Priority 4: Perception Bias Documentation (Low Impact, High Value)
**File:** `src/week7.py`

**Changes:**
1. Add documentation and warnings about:
   - Potential perception biases in controversial topics
   - How political alignment might affect edit patterns
   - Limitations of automated bias detection

2. Enhance controversial topic categorization:
   - Add political/ideological context metadata
   - Flag high-risk topics for perception bias

### Expected Outcomes

After implementing these modifications:
1. **More Comprehensive Bias Detection:** Scripts will identify bias at the phrase level, not just citation and size patterns
2. **Neutrality Assessment:** Ability to evaluate how well bot edits align with Wikipedia's NPOV policy
3. **Better Evaluation:** Multi-dimensional assessment of bias with quality metrics
4. **Improved Interpretation:** Context about perception biases helps avoid misinterpretation of results

### Next Steps

- Implement Priority 1 modifications (bias phrase detection)
- Test new detection methods on existing data
- Validate findings against known bias patterns
- Integrate improved data and conclusions into main paper

---

