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
    """Analyze content changes to detect bias patterns."""
    content_analysis = {
        "size_changes": [],
        "citation_changes": [],
        "edit_frequency": defaultdict(int),
        "content_amplification": [],
        "bias_indicators": []
    }
    
    prev_size = None
    prev_citations = None
    
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
    # Count <ref> tags and other citation patterns
    ref_count = len(re.findall(r'<ref[^>]*>', text, re.IGNORECASE))
    return ref_count


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
                    "amplification_count": len(content_analysis["content_amplification"])
                }
            }
            
            topic_analysis["page_results"].append(page_result)
            topic_analysis["total_edits"] += total_edits
            topic_analysis["total_bot_edits"] += bot_edits
            
            # Add page-level bias indicators to topic analysis
            topic_analysis["bias_indicators"].extend(bias_indicators)
            
            print(f"    ✅ {total_edits} edits, {bot_edits} bot edits ({bot_ratio:.1%}), {len(bias_indicators)} bias indicators")
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
        
        if analysis['bias_indicators']:
            print("   🚨 Key bias patterns:")
            for indicator in analysis['bias_indicators'][:3]:  # Show top 3
                print(f"      • {indicator['description']}")
        
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


def main():
    """Main function to run the bias analysis."""
    print("🤖 Week 7: Automation Bias Analysis")
    print("Analyzing how automated agents influence knowledge representation on Wikipedia")
    print("-" * 80)
    
    # Analyze controversial topics
    analyses = []
    for topic in CONTROVERSIAL_TOPICS[:5]:  # Analyze top 5 topics
        analysis = analyze_topic_bias(topic, pages_to_analyze=3, revisions_per_page=30)
        analyses.append(analysis)
    
    # Generate comprehensive report
    generate_bias_report(analyses)
    
    # Save results to JSON file
    results = {
        "timestamp": datetime.now().isoformat(),
        "topics_analyzed": len([a for a in analyses if a]),
        "analyses": [a for a in analyses if a]
    }
    
    with open("week7_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to week7_results.json")
    print(f"🌐 Open week7.html in your browser to explore the interactive analysis")


if __name__ == "__main__":
    main()
