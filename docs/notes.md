# Research Notes & Ideas

This is a scratch-pad for detailed notes, ideas, and working thoughts on the EchoChamber project.

---

## Next Working Session Tasks

**Date:** 2025-11-11  
**Status:** Planned for next session

### Script Modifications

I will perform the following modifications based on the literature review findings:

1. **Implement bias phrase detection** in `week7.py` and `week7_api.py`
   - Add `detect_biased_phrases()` function
   - Integrate into content analysis pipeline
   - Track bias phrase frequency changes

2. **Add neutrality alignment analysis**
   - Implement `analyze_neutrality_alignment()` function
   - Compare bot vs. human NPOV compliance
   - Add neutrality metrics to bias indicators

3. **Enhance evaluation framework**
   - Extend reporting with new metrics
   - Add quality scoring system
   - Improve multi-dimensional bias assessment

4. **Update data collection**
   - Run improved scripts on existing topics
   - Collect new data with enhanced bias detection
   - Validate findings against literature review insights

### Paper Integration

After completing script modifications and data collection:

- Integrate improved data and conclusions into `paper/main.tex`
- Update methodology section with new bias detection approaches
- Add discussion of neutrality alignment findings
- Incorporate insights from reviewed papers into related work section
- Update results section with enhanced bias metrics

---

## Research Ideas & Future Directions

### Potential Enhancements

- **Temporal Analysis:** Track how bias patterns evolve over time, not just current state
- **Cross-Language Comparison:** Compare bias patterns across different language Wikipedias
- **Bot Type Categorization:** Distinguish between different types of bots (maintenance, content generation, etc.)
- **Human-Bot Collaboration Patterns:** Analyze how human editors respond to bot edits

### Open Questions

- How do different bot types contribute differently to bias?
- What is the relationship between bot edit frequency and bias severity?
- How do controversial topics differ in their susceptibility to automation bias?
- Can we predict bias patterns based on topic characteristics?

---

## Technical Notes

### Current Script Limitations

- Bot detection relies on heuristics (username patterns, flags, tags) — may miss some bots
- Citation counting is simple (ref tag counting) — doesn't assess citation quality
- Bias detection is primarily quantitative (size, frequency) — lacks qualitative analysis
- No temporal trend analysis — only snapshot comparisons

### Potential Improvements

- Use MediaWiki API's bot flag more reliably
- Implement citation quality assessment (source diversity, reliability)
- Add natural language processing for qualitative bias detection
- Implement time-series analysis for trend detection

---

