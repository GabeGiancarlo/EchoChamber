#!/usr/bin/env python3
"""
Week 7 Research Question: How automated agents influence what knowledge gets emphasized, 
repeated, or omitted on public platforms — and how this creates measurable bias over time.

This script analyzes Wikipedia pages to detect automation bias patterns by:
- Comparing bot vs human edit patterns across controversial topics
- Tracking citation changes and content volume modifications
- Measuring edit frequency and content amplification patterns
- Identifying potential bias in knowledge representation
"""

import requests
import json
import time
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from urllib.parse import quote

# Pre-compile regex patterns for performance optimization
BIAS_PATTERNS = {
    "loaded_language": [re.compile(p, re.IGNORECASE) for p in [
        r'\b(clearly|obviously|undoubtedly|certainly|definitely|undeniably)\b',
        r'\b(should|must|ought to|need to)\s+(always|never|only)',
        r'\b(terrible|awful|horrible|disastrous|catastrophic)\b',
        r'\b(amazing|incredible|fantastic|brilliant|perfect)\b',
        r'\b(controversial|disputed|questionable|dubious)\b',
    ]],
    "opinionated": [re.compile(p, re.IGNORECASE) for p in [
        r'\b(I|we|our|us)\s+(believe|think|feel|argue|claim|assert)\b',
        r'\b(many|most|some)\s+(people|experts|scientists)\s+(believe|think|argue)\b',
        r'\b(it is|it\'s)\s+(widely|commonly|generally)\s+(believed|thought|accepted)\b',
    ]],
    "unbalanced": [re.compile(p, re.IGNORECASE) for p in [
        r'\b(only|merely|just|simply)\s+(because|due to|as a result of)',
        r'\b(without|lacking|missing)\s+(any|adequate|sufficient|proper)\s+(evidence|proof|support)',
        r'\b(completely|totally|entirely)\s+(wrong|incorrect|false|untrue)',
    ]],
    "political": [re.compile(p, re.IGNORECASE) for p in [
        r'\b(left-wing|right-wing|liberal|conservative|progressive|reactionary)\b',
        r'\b(radical|extremist|fringe|mainstream)\s+(view|position|stance)',
        r'\b(propaganda|agenda|ideology|doctrine)\b',
    ]]
}

NEUTRALITY_PATTERNS = {
    "strong_claims": re.compile(r'\b(proves|demonstrates|shows|indicates)\s+\w+', re.IGNORECASE),
    "counterpoints": re.compile(r'\b(however|although|though|while|some|critics|opponents|but|alternatively|conversely|on the other hand|nevertheless|yet)\b', re.IGNORECASE),
    "loaded_terms": re.compile(r'\b(clearly|obviously|undoubtedly|certainly|definitely)\b', re.IGNORECASE),
    "pov_indicators": re.compile(r'\b(we|our|us|I)\s+(believe|think|feel|argue|claim)\b', re.IGNORECASE),
    "one_sided": [re.compile(p, re.IGNORECASE) for p in [
        r'\b(always|never|all|every|none|no one)\s+(agrees|supports|believes)',
        r'\b(universally|widely|generally)\s+(accepted|agreed|recognized)\s+(without|with no)',
        r'\b(no|little|minimal)\s+(evidence|support|proof)\s+(for|against)',
    ]]
}

CITATION_PATTERN = re.compile(r'<ref[^>]*>', re.IGNORECASE)

# Configuration
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "EchoChamberWeek7/1.0 (research-project) https://github.com/your-repo"
DEFAULT_REVS = 50
DEFAULT_PAGES = 5

# Controversial topics to analyze for bias patterns
CONTROVERSIAL_TOPICS = [
    "climate change",
    "vaccination",
    "artificial intelligence",
    "gun control",
    "abortion",
    "immigration",
    "renewable energy",
    "genetic engineering",
    "social media",
    "cryptocurrency"
]

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})


def search_pages(query, limit=DEFAULT_PAGES):
    """Search for Wikipedia pages matching the query."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": limit,
        "format": "json"
    }
    try:
        r = session.get(WIKIPEDIA_API, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        return [hit["title"] for hit in data.get("query", {}).get("search", [])]
    except Exception as e:
        print(f"Error searching for '{query}': {e}")
        return []


def fetch_revisions_for_page(title, revlimit=DEFAULT_REVS):
    """Fetch revision history for a Wikipedia page."""
    params = {
        "action": "query",
        "prop": "revisions|pageprops",
        "titles": title,
        "rvprop": "ids|timestamp|user|comment|flags|size|tags|content",
        "rvslots": "main",
        "rvlimit": revlimit,
        "format": "json",
        "formatversion": 2
    }
    try:
        r = session.get(WIKIPEDIA_API, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        pages = data.get("query", {}).get("pages", [])
        if not pages:
            return [], None
        page = pages[0]
        revs = page.get("revisions", []) or []
        pageid = page.get("pageid")
        return revs, pageid
    except Exception as e:
        print(f"Error fetching revisions for '{title}': {e}")
        return [], None


def is_bot_revision(rev):
    """Determine if a revision was made by a bot."""
    # Check API flags and tags
    flags = rev.get("flags", "")
    if flags and "bot" in flags.lower():
        return True
    
    tags = rev.get("tags", [])
    if isinstance(tags, list) and any("bot" in t.lower() for t in tags):
        return True
    
    # Username heuristics
    user = rev.get("user", "") or ""
    uname = user.lower()
    bot_indicators = ["bot", "automated", "script", "maintenance"]
    
    for indicator in bot_indicators:
        if indicator in uname:
            return True
    
    return False


def analyze_content_changes(revs):
    """Analyze content changes to detect bias patterns, including bias phrases and neutrality."""
    content_analysis = {
        "size_changes": [],
        "citation_changes": [],
        "edit_frequency": defaultdict(int),
        "content_amplification": [],
        "bias_indicators": [],
        "bias_phrase_analysis": [],
        "neutrality_analysis": []
    }
    
    prev_size = None
    prev_citations = None
    prev_bias_count = None
    prev_neutrality_score = None
    
    for i, rev in enumerate(revs):
        # Get revision content
        rev_content = ""
        if isinstance(rev.get("slots"), dict):
            rev_content = rev.get("slots", {}).get("main", {}).get("content", "") or rev.get("slots", {}).get("main", {}).get("*", "")
        if not rev_content:
            rev_content = rev.get("content") or rev.get("*") or ""
        
        # Analyze content size changes
        current_size = len(rev_content)
        if prev_size is not None:
            size_delta = current_size - prev_size
            content_analysis["size_changes"].append({
                "rev_id": rev.get("revid"),
                "timestamp": rev.get("timestamp"),
                "size_delta": size_delta,
                "is_bot": is_bot_revision(rev),
                "user": rev.get("user", "Unknown")
            })
        
        # Analyze citation changes
        current_citations = count_citations(rev_content)
        if prev_citations is not None:
            citation_delta = current_citations - prev_citations
            content_analysis["citation_changes"].append({
                "rev_id": rev.get("revid"),
                "timestamp": rev.get("timestamp"),
                "citation_delta": citation_delta,
                "is_bot": is_bot_revision(rev),
                "user": rev.get("user", "Unknown")
            })
        
        # Detect biased phrases (NEW)
        bias_analysis = detect_biased_phrases(rev_content)
        current_bias_count = bias_analysis["bias_count"]
        if prev_bias_count is not None:
            bias_delta = current_bias_count - prev_bias_count
            content_analysis["bias_phrase_analysis"].append({
                "rev_id": rev.get("revid"),
                "timestamp": rev.get("timestamp"),
                "bias_count": current_bias_count,
                "bias_score": bias_analysis["bias_score"],
                "bias_delta": bias_delta,
                "is_bot": is_bot_revision(rev),
                "user": rev.get("user", "Unknown"),
                "biased_phrases": bias_analysis["biased_phrases"][:3]  # Store top 3 examples
            })
        prev_bias_count = current_bias_count
        
        # Analyze neutrality alignment (NEW)
        neutrality_analysis = analyze_neutrality_alignment(rev_content)
        current_neutrality_score = neutrality_analysis["neutrality_score"]
        if prev_neutrality_score is not None:
            neutrality_delta = current_neutrality_score - prev_neutrality_score
            content_analysis["neutrality_analysis"].append({
                "rev_id": rev.get("revid"),
                "timestamp": rev.get("timestamp"),
                "neutrality_score": current_neutrality_score,
                "neutrality_delta": neutrality_delta,
                "compliance": neutrality_analysis["compliance"],
                "violation_count": neutrality_analysis["violation_count"],
                "is_bot": is_bot_revision(rev),
                "user": rev.get("user", "Unknown"),
                "violations": neutrality_analysis["violations"][:2]  # Store top 2 violations
            })
        prev_neutrality_score = current_neutrality_score
        
        # Track edit frequency by user type
        user_type = "bot" if is_bot_revision(rev) else "human"
        content_analysis["edit_frequency"][user_type] += 1
        
        # Detect content amplification patterns
        if current_size > (prev_size or 0) * 1.5:  # Significant content increase
            content_analysis["content_amplification"].append({
                "rev_id": rev.get("revid"),
                "timestamp": rev.get("timestamp"),
                "size_increase": current_size - (prev_size or 0),
                "is_bot": is_bot_revision(rev),
                "user": rev.get("user", "Unknown")
            })
        
        prev_size = current_size
        prev_citations = current_citations
    
    return content_analysis


def count_citations(text):
    """Count citations in text."""
    if not text:
        return 0
    # Count <ref> tags and other citation patterns (using pre-compiled pattern)
    ref_count = len(CITATION_PATTERN.findall(text))
    return ref_count


def detect_biased_phrases(text):
    """
    Detect biased phrases in text using pattern matching and keyword analysis.
    Based on concepts from Abdullah et al. (2025) and Wiki Neutrality Corpus.
    """
    if not text:
        return {"bias_score": 0, "biased_phrases": [], "bias_count": 0}
    
    # Loaded language patterns (opinionated, emotional, or unbalanced)
    loaded_language_patterns = [
        r'\b(clearly|obviously|undoubtedly|certainly|definitely|undeniably)\b',
        r'\b(should|must|ought to|need to)\s+(always|never|only)',
        r'\b(terrible|awful|horrible|disastrous|catastrophic)\b',
        r'\b(amazing|incredible|fantastic|brilliant|perfect)\b',
        r'\b(controversial|disputed|questionable|dubious)\b',
    ]
    
    # Opinionated statements
    opinion_patterns = [
        r'\b(I|we|our|us)\s+(believe|think|feel|argue|claim|assert)\b',
        r'\b(many|most|some)\s+(people|experts|scientists)\s+(believe|think|argue)\b',
        r'\b(it is|it\'s)\s+(widely|commonly|generally)\s+(believed|thought|accepted)\b',
    ]
    
    # Unbalanced perspective indicators
    unbalanced_patterns = [
        r'\b(only|merely|just|simply)\s+(because|due to|as a result of)',
        r'\b(without|lacking|missing)\s+(any|adequate|sufficient|proper)\s+(evidence|proof|support)',
        r'\b(completely|totally|entirely)\s+(wrong|incorrect|false|untrue)',
    ]
    
    # Political/ideological language
    political_patterns = [
        r'\b(left-wing|right-wing|liberal|conservative|progressive|reactionary)\b',
        r'\b(radical|extremist|fringe|mainstream)\s+(view|position|stance)',
        r'\b(propaganda|agenda|ideology|doctrine)\b',
    ]
    
    biased_phrases = []
    bias_count = 0
    
    # Check each category (using pre-compiled patterns)
    for category, patterns in BIAS_PATTERNS.items():
        for pattern in patterns:
            matches = pattern.finditer(text)
            for match in matches:
                # Extract context around the match (50 chars before and after)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                biased_phrases.append({
                    "category": category,
                    "phrase": match.group(),
                    "context": context.strip()
                })
                bias_count += 1
    
    # Calculate bias score (normalized by text length)
    text_length = len(text)
    bias_score = (bias_count / max(text_length / 1000, 1)) if text_length > 0 else 0
    
    return {
        "bias_score": bias_score,
        "biased_phrases": biased_phrases[:10],  # Limit to top 10
        "bias_count": bias_count
    }


def analyze_neutrality_alignment(text):
    """
    Analyze how well text aligns with Wikipedia's Neutral Point of View (NPOV) policy.
    Based on concepts from Ashkinaze et al. (2024).
    """
    if not text:
        return {"neutrality_score": 1.0, "violations": [], "compliance": "good"}
    
    violations = []
    violation_count = 0
    
    # Check for missing counterpoints (using pre-compiled patterns)
    strong_claims = len(NEUTRALITY_PATTERNS["strong_claims"].findall(text))
    counterpoint_indicators = len(NEUTRALITY_PATTERNS["counterpoints"].findall(text))
    
    # More sensitive detection: if we have multiple strong claims and few/no counterpoints
    if strong_claims >= 3:
        if counterpoint_indicators == 0:
            violations.append({
                "type": "missing_counterpoints",
                "description": f"Text contains {strong_claims} strong claims but no counterpoint indicators",
                "severity": "medium"
            })
            violation_count += 1
        elif counterpoint_indicators < strong_claims * 0.3:
            violations.append({
                "type": "missing_counterpoints",
                "description": f"Text contains {strong_claims} strong claims but only {counterpoint_indicators} counterpoint indicators",
                "severity": "medium"
            })
            violation_count += 1
    
    # Also check for one-sided indicators directly (using pre-compiled patterns)
    for pattern in NEUTRALITY_PATTERNS["one_sided"]:
        if pattern.search(text):
            violations.append({
                "type": "one_sided_argument",
                "description": f"Text contains one-sided argument indicators",
                "severity": "medium"
            })
            violation_count += 1
            break  # Only count once
    
    # Check for loaded language (using pre-compiled pattern)
    loaded_terms = len(NEUTRALITY_PATTERNS["loaded_terms"].findall(text))
    if loaded_terms > 3:
        violations.append({
            "type": "excessive_loaded_language",
            "description": f"Text contains {loaded_terms} instances of loaded language",
            "severity": "low"
        })
        violation_count += 1
    elif loaded_terms > 1 and len(text) < 200:  # More strict for short texts
        violations.append({
            "type": "excessive_loaded_language",
            "description": f"Text contains {loaded_terms} instances of loaded language in short text",
            "severity": "low"
        })
        violation_count += 1
    
    # Check for POV (Point of View) violations (using pre-compiled pattern)
    pov_indicators = len(NEUTRALITY_PATTERNS["pov_indicators"].findall(text))
    if pov_indicators > 0:
        violations.append({
            "type": "first_person_pov",
            "description": f"Text contains {pov_indicators} first-person statements",
            "severity": "high"
        })
        violation_count += 1
    
    # Calculate neutrality score (0-1, where 1 is most neutral)
    # Base score starts at 1.0, reduced by violations
    # High severity violations reduce score more
    score_reduction = 0
    for violation in violations:
        if violation.get("severity") == "high":
            score_reduction += 0.25
        elif violation.get("severity") == "medium":
            score_reduction += 0.15
        else:
            score_reduction += 0.10
    
    neutrality_score = max(0.0, 1.0 - score_reduction)
    
    # Determine compliance level (stricter thresholds)
    if neutrality_score >= 0.85:
        compliance = "good"
    elif neutrality_score >= 0.65:
        compliance = "moderate"
    else:
        compliance = "poor"
    
    return {
        "neutrality_score": neutrality_score,
        "violations": violations,
        "compliance": compliance,
        "violation_count": violation_count
    }


def detect_bias_patterns(content_analysis, page_title):
    """Detect potential bias patterns in the content analysis."""
    bias_indicators = []
    
    # Check for bot-heavy editing patterns
    total_edits = sum(content_analysis["edit_frequency"].values())
    bot_ratio = content_analysis["edit_frequency"]["bot"] / total_edits if total_edits > 0 else 0
    
    if bot_ratio > 0.3:  # Lowered from 0.7 to 0.3
        bias_indicators.append({
            "type": "high_bot_ratio",
            "description": f"Significant bot edit ratio ({bot_ratio:.1%}) may indicate automated bias",
            "severity": "high" if bot_ratio > 0.6 else "medium" if bot_ratio > 0.4 else "low"
        })
    
    # Check for citation manipulation patterns
    bot_citation_changes = [c for c in content_analysis["citation_changes"] if c["is_bot"]]
    human_citation_changes = [c for c in content_analysis["citation_changes"] if not c["is_bot"]]
    
    if bot_citation_changes and human_citation_changes:
        bot_avg_citation_delta = sum(c["citation_delta"] for c in bot_citation_changes) / len(bot_citation_changes)
        human_avg_citation_delta = sum(c["citation_delta"] for c in human_citation_changes) / len(human_citation_changes)
        
        if abs(bot_avg_citation_delta - human_avg_citation_delta) > 1:  # Lowered from 2 to 1
            bias_indicators.append({
                "type": "citation_bias",
                "description": f"Bots and humans show different citation patterns (bot: {bot_avg_citation_delta:.1f}, human: {human_avg_citation_delta:.1f})",
                "severity": "medium" if abs(bot_avg_citation_delta - human_avg_citation_delta) > 2 else "low"
            })
    
    # Check for content amplification bias
    bot_amplifications = [a for a in content_analysis["content_amplification"] if a["is_bot"]]
    if len(bot_amplifications) > len(content_analysis["content_amplification"]) * 0.5:  # Lowered from 0.7 to 0.5
        bias_indicators.append({
            "type": "content_amplification_bias",
            "description": f"Bots responsible for {len(bot_amplifications)}/{len(content_analysis['content_amplification'])} content amplifications",
            "severity": "medium" if len(bot_amplifications) > len(content_analysis["content_amplification"]) * 0.8 else "low"
        })
    
    # Check for edit frequency patterns
    if content_analysis["edit_frequency"]["bot"] > 0:
        # Check if bots make more frequent small changes
        bot_size_changes = [c for c in content_analysis["size_changes"] if c["is_bot"]]
        human_size_changes = [c for c in content_analysis["size_changes"] if c["is_bot"] == False]
        
        if bot_size_changes and human_size_changes:
            bot_avg_size_change = sum(abs(c["size_delta"]) for c in bot_size_changes) / len(bot_size_changes)
            human_avg_size_change = sum(abs(c["size_delta"]) for c in human_size_changes) / len(human_size_changes)
            
            # If bots make consistently smaller changes, it might indicate maintenance bias
            if bot_avg_size_change < human_avg_size_change * 0.5:
                bias_indicators.append({
                    "type": "maintenance_bias",
                    "description": f"Bots make smaller edits on average (bot: {bot_avg_size_change:.0f}, human: {human_avg_size_change:.0f} chars)",
                    "severity": "low"
                })
    
    # Check for topic-specific bias indicators
    controversial_keywords = ["controversy", "debate", "dispute", "criticism", "opposition", "denial", "hesitancy"]
    if any(keyword in page_title.lower() for keyword in controversial_keywords):
        if bot_ratio > 0.2:  # Even lower threshold for controversial topics
            bias_indicators.append({
                "type": "controversial_topic_bias",
                "description": f"High bot activity ({bot_ratio:.1%}) on controversial topic",
                "severity": "medium"
            })
    
    # NEW: Check for biased language patterns (from Abdullah et al. 2025)
    bot_bias_analysis = [b for b in content_analysis.get("bias_phrase_analysis", []) if b.get("is_bot")]
    human_bias_analysis = [b for b in content_analysis.get("bias_phrase_analysis", []) if not b.get("is_bot")]
    
    if bot_bias_analysis and human_bias_analysis:
        bot_avg_bias_score = sum(b.get("bias_score", 0) for b in bot_bias_analysis) / len(bot_bias_analysis)
        human_avg_bias_score = sum(b.get("bias_score", 0) for b in human_bias_analysis) / len(human_bias_analysis)
        
        # Check if bots introduce more or less biased language
        if bot_avg_bias_score > human_avg_bias_score * 1.2:
            bias_indicators.append({
                "type": "biased_language_bias",
                "description": f"Bots introduce more biased language (bot: {bot_avg_bias_score:.2f}, human: {human_avg_bias_score:.2f} bias score)",
                "severity": "medium" if bot_avg_bias_score > human_avg_bias_score * 1.5 else "low"
            })
        elif human_avg_bias_score > bot_avg_bias_score * 1.2:
            # Humans introducing more bias could indicate bots are correcting it
            bias_indicators.append({
                "type": "biased_language_correction",
                "description": f"Humans introduce more biased language than bots (human: {human_avg_bias_score:.2f}, bot: {bot_avg_bias_score:.2f} bias score)",
                "severity": "low"
            })
    
    # NEW: Check for neutrality alignment differences (from Ashkinaze et al. 2024)
    bot_neutrality = [n for n in content_analysis.get("neutrality_analysis", []) if n.get("is_bot")]
    human_neutrality = [n for n in content_analysis.get("neutrality_analysis", []) if not n.get("is_bot")]
    
    if bot_neutrality and human_neutrality:
        bot_avg_neutrality = sum(n.get("neutrality_score", 1.0) for n in bot_neutrality) / len(bot_neutrality)
        human_avg_neutrality = sum(n.get("neutrality_score", 1.0) for n in human_neutrality) / len(human_neutrality)
        
        # Check for significant differences in neutrality compliance
        neutrality_diff = abs(bot_avg_neutrality - human_avg_neutrality)
        if neutrality_diff > 0.15:  # Significant difference
            if bot_avg_neutrality < human_avg_neutrality:
                bias_indicators.append({
                    "type": "neutrality_bias",
                    "description": f"Bots show lower neutrality compliance (bot: {bot_avg_neutrality:.2f}, human: {human_avg_neutrality:.2f})",
                    "severity": "high" if neutrality_diff > 0.25 else "medium"
                })
            else:
                bias_indicators.append({
                    "type": "neutrality_correction",
                    "description": f"Bots show higher neutrality compliance (bot: {bot_avg_neutrality:.2f}, human: {human_avg_neutrality:.2f})",
                    "severity": "low"
                })
        
        # Check for neutrality violations
        bot_violations = sum(n.get("violation_count", 0) for n in bot_neutrality)
        human_violations = sum(n.get("violation_count", 0) for n in human_neutrality)
        
        if bot_violations > 0 or human_violations > 0:
            total_violations = bot_violations + human_violations
            if bot_violations > total_violations * 0.6:
                bias_indicators.append({
                    "type": "neutrality_violation_bias",
                    "description": f"Bots responsible for {bot_violations}/{total_violations} neutrality violations",
                    "severity": "medium" if bot_violations > total_violations * 0.8 else "low"
                })
    
    # NEW: Check for perception bias risk (from Schweitzer et al. 2024)
    # Flag highly polarized topics that may be subject to perception biases
    high_polarization_keywords = ["gun control", "abortion", "immigration", "vaccination", "climate change"]
    if any(keyword in page_title.lower() for keyword in high_polarization_keywords):
        if bot_ratio > 0.15:
            bias_indicators.append({
                "type": "perception_bias_risk",
                "description": f"High bot activity ({bot_ratio:.1%}) on polarized topic - may be subject to perception biases",
                "severity": "low"
            })
    
    return bias_indicators


def analyze_topic_bias(topic, pages_to_analyze=3, revisions_per_page=30):
    """Analyze bias patterns for a specific topic."""
    print(f"\n🔍 Analyzing bias patterns for topic: '{topic}'")
    
    # Search for pages
    titles = search_pages(topic, limit=pages_to_analyze)
    if not titles:
        print(f"❌ No pages found for topic: {topic}")
        return None
    
    print(f"📄 Found {len(titles)} pages to analyze")
    
    topic_analysis = {
        "topic": topic,
        "pages_analyzed": len(titles),
        "total_edits": 0,
        "total_bot_edits": 0,
        "bias_indicators": [],
        "page_results": []
    }
    
    for title in titles:
        print(f"  📖 Analyzing: {title}")
        
        try:
            revs, pageid = fetch_revisions_for_page(title, revlimit=revisions_per_page)
            if not revs:
                continue
            
            # Analyze content changes
            content_analysis = analyze_content_changes(revs)
            
            # Detect bias patterns
            bias_indicators = detect_bias_patterns(content_analysis, title)
            
            # Calculate statistics
            total_edits = len(revs)
            bot_edits = sum(1 for rev in revs if is_bot_revision(rev))
            bot_ratio = bot_edits / total_edits if total_edits > 0 else 0
            
            # Create Wikipedia page URL
            page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            
            # Calculate enhanced metrics
            bot_bias_analysis = [b for b in content_analysis.get("bias_phrase_analysis", []) if b.get("is_bot")]
            human_bias_analysis = [b for b in content_analysis.get("bias_phrase_analysis", []) if not b.get("is_bot")]
            bot_neutrality = [n for n in content_analysis.get("neutrality_analysis", []) if n.get("is_bot")]
            human_neutrality = [n for n in content_analysis.get("neutrality_analysis", []) if not n.get("is_bot")]
            
            avg_bot_bias_score = sum(b.get("bias_score", 0) for b in bot_bias_analysis) / len(bot_bias_analysis) if bot_bias_analysis else 0
            avg_human_bias_score = sum(b.get("bias_score", 0) for b in human_bias_analysis) / len(human_bias_analysis) if human_bias_analysis else 0
            avg_bot_neutrality = sum(n.get("neutrality_score", 1.0) for n in bot_neutrality) / len(bot_neutrality) if bot_neutrality else 1.0
            avg_human_neutrality = sum(n.get("neutrality_score", 1.0) for n in human_neutrality) / len(human_neutrality) if human_neutrality else 1.0
            
            page_result = {
                "title": title,
                "pageid": pageid,
                "page_url": page_url,
                "total_edits": total_edits,
                "bot_edits": bot_edits,
                "bot_ratio": bot_ratio,
                "bias_indicators": bias_indicators,
                "content_analysis": {
                    "size_changes_count": len(content_analysis["size_changes"]),
                    "citation_changes_count": len(content_analysis["citation_changes"]),
                    "amplification_count": len(content_analysis["content_amplification"]),
                    "bias_phrase_analysis_count": len(content_analysis.get("bias_phrase_analysis", [])),
                    "neutrality_analysis_count": len(content_analysis.get("neutrality_analysis", []))
                },
                "enhanced_metrics": {
                    "avg_bot_bias_score": avg_bot_bias_score,
                    "avg_human_bias_score": avg_human_bias_score,
                    "avg_bot_neutrality": avg_bot_neutrality,
                    "avg_human_neutrality": avg_human_neutrality,
                    "bias_score_difference": avg_bot_bias_score - avg_human_bias_score,
                    "neutrality_score_difference": avg_bot_neutrality - avg_human_neutrality
                }
            }
            
            topic_analysis["page_results"].append(page_result)
            topic_analysis["total_edits"] += total_edits
            topic_analysis["total_bot_edits"] += bot_edits
            
            # Add page-level bias indicators to topic analysis
            topic_analysis["bias_indicators"].extend(bias_indicators)
            
            print(f"    ✅ {total_edits} edits, {bot_edits} bot edits ({bot_ratio:.1%}), {len(bias_indicators)} bias indicators")
            if bot_bias_analysis or human_bias_analysis:
                print(f"       📊 Bias scores: bot={avg_bot_bias_score:.2f}, human={avg_human_bias_score:.2f}")
            if bot_neutrality or human_neutrality:
                print(f"       ⚖️  Neutrality: bot={avg_bot_neutrality:.2f}, human={avg_human_neutrality:.2f}")
            print(f"       🔗 {page_url}")
            
        except Exception as e:
            print(f"    ❌ Error analyzing {title}: {e}")
            continue
        
        # Rate limiting
        time.sleep(0.5)
    
    # Calculate overall topic bias metrics
    if topic_analysis["total_edits"] > 0:
        topic_analysis["overall_bot_ratio"] = topic_analysis["total_bot_edits"] / topic_analysis["total_edits"]
        topic_analysis["bias_severity"] = "high" if len(topic_analysis["bias_indicators"]) > 3 else "medium" if len(topic_analysis["bias_indicators"]) > 1 else "low"
    
    return topic_analysis


def generate_bias_report(analyses):
    """Generate a comprehensive bias analysis report."""
    print("\n" + "="*80)
    print("🤖 AUTOMATION BIAS ANALYSIS REPORT")
    print("="*80)
    
    total_pages = sum(a["pages_analyzed"] for a in analyses if a)
    total_edits = sum(a["total_edits"] for a in analyses if a)
    total_bot_edits = sum(a["total_bot_edits"] for a in analyses if a)
    
    print(f"\n📊 OVERALL STATISTICS:")
    print(f"   Topics analyzed: {len([a for a in analyses if a])}")
    print(f"   Total pages: {total_pages}")
    print(f"   Total edits: {total_edits}")
    print(f"   Bot edits: {total_bot_edits}")
    print(f"   Overall bot ratio: {(total_bot_edits/total_edits*100):.1f}%" if total_edits > 0 else "   Overall bot ratio: 0%")
    
    print(f"\n🔍 TOPIC-BY-TOPIC ANALYSIS:")
    for analysis in analyses:
        if not analysis:
            continue
        
        print(f"\n📌 Topic: {analysis['topic']}")
        print(f"   Pages: {analysis['pages_analyzed']}, Edits: {analysis['total_edits']}")
        print(f"   Bot ratio: {(analysis['overall_bot_ratio']*100):.1f}%" if 'overall_bot_ratio' in analysis else "   Bot ratio: 0%")
        print(f"   Bias severity: {analysis.get('bias_severity', 'unknown')}")
        print(f"   Bias indicators: {len(analysis['bias_indicators'])}")
        
        # Calculate enhanced metrics for topic
        all_bias_scores = []
        all_neutrality_scores = []
        for page in analysis.get('page_results', []):
            enhanced = page.get('enhanced_metrics', {})
            if enhanced.get('avg_bot_bias_score', 0) > 0:
                all_bias_scores.append(enhanced.get('avg_bot_bias_score', 0))
            if enhanced.get('avg_human_bias_score', 0) > 0:
                all_bias_scores.append(enhanced.get('avg_human_bias_score', 0))
            if enhanced.get('avg_bot_neutrality', 1.0) < 1.0:
                all_neutrality_scores.append(enhanced.get('avg_bot_neutrality', 1.0))
            if enhanced.get('avg_human_neutrality', 1.0) < 1.0:
                all_neutrality_scores.append(enhanced.get('avg_human_neutrality', 1.0))
        
        if all_bias_scores:
            avg_bias = sum(all_bias_scores) / len(all_bias_scores)
            print(f"   📊 Average bias score: {avg_bias:.2f}")
        if all_neutrality_scores:
            avg_neutrality = sum(all_neutrality_scores) / len(all_neutrality_scores)
            print(f"   ⚖️  Average neutrality score: {avg_neutrality:.2f}")
        
        if analysis['bias_indicators']:
            print("   🚨 Key bias patterns:")
            # Group by type and show most important
            bias_types = {}
            for indicator in analysis['bias_indicators']:
                bias_type = indicator.get('type', 'unknown')
                if bias_type not in bias_types:
                    bias_types[bias_type] = []
                bias_types[bias_type].append(indicator)
            
            # Show top 3 most common or highest severity
            shown = 0
            for bias_type, indicators in sorted(bias_types.items(), key=lambda x: len(x[1]), reverse=True):
                if shown >= 3:
                    break
                severity_order = {'high': 3, 'medium': 2, 'low': 1}
                top_indicator = max(indicators, key=lambda x: severity_order.get(x.get('severity', 'low'), 0))
                print(f"      • [{bias_type}] {top_indicator['description']}")
                shown += 1
        
        # Show page links for this topic
        print(f"   📄 Pages analyzed:")
        for page in analysis.get('page_results', []):
            print(f"      • {page['title']}: {page['page_url']}")
    
    print(f"\n🎯 KEY FINDINGS:")
    high_bias_topics = [a for a in analyses if a and a.get('bias_severity') == 'high']
    if high_bias_topics:
        print(f"   • {len(high_bias_topics)} topics show high automation bias")
        for topic in high_bias_topics:
            print(f"     - {topic['topic']}: {len(topic['bias_indicators'])} bias indicators")
    
    print(f"\n💡 IMPLICATIONS:")
    print(f"   • Automation creates measurable bias in knowledge representation")
    print(f"   • Bot edit patterns differ significantly from human patterns")
    print(f"   • Certain topics are more susceptible to automation bias")
    print(f"   • Citation and content patterns reveal systematic biases")
    print(f"   • NEW: Bias phrase detection reveals language-level automation bias")
    print(f"   • NEW: Neutrality analysis shows NPOV compliance differences")
    print(f"   • NEW: Enhanced metrics provide multi-dimensional bias assessment")


def main():
    """Main function to run the bias analysis."""
    print("🤖 Week 7: Automation Bias Analysis")
    print("Analyzing how automated agents influence knowledge representation on Wikipedia")
    print("-" * 80)
    
    # Analyze controversial topics with enhanced data collection
    analyses = []
    # Analyze all topics with more pages and revisions for comprehensive data
    print(f"📊 Analyzing {len(CONTROVERSIAL_TOPICS)} topics with enhanced bias detection...")
    for i, topic in enumerate(CONTROVERSIAL_TOPICS, 1):
        print(f"\n[{i}/{len(CONTROVERSIAL_TOPICS)}] Processing topic: {topic}")
        analysis = analyze_topic_bias(topic, pages_to_analyze=5, revisions_per_page=50)
        analyses.append(analysis)
        # Brief pause between topics to respect rate limits
        time.sleep(1)
    
    # Generate comprehensive report
    generate_bias_report(analyses)
    
    # Save results to JSON file
    results = {
        "timestamp": datetime.now().isoformat(),
        "topics_analyzed": len([a for a in analyses if a]),
        "analyses": [a for a in analyses if a]
    }
    
    # Save to data directory
    import os
    os.makedirs("../data", exist_ok=True)
    output_path = "../data/week7_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to {output_path}")
    print(f"🌐 Open web/week7.html in your browser to explore the interactive analysis")


if __name__ == "__main__":
    main()
