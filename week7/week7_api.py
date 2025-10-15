#!/usr/bin/env python3
"""
Flask API server for Week 7 automation bias analysis
Provides real Wikipedia data to the HTML interface
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import time
import re
from collections import defaultdict

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "EchoChamberWeek7/1.0 (research-project)"
DEFAULT_REVS = 30
DEFAULT_PAGES = 3

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
        "prop": "revisions",
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
    flags = rev.get("flags", "")
    if flags and "bot" in flags.lower():
        return True
    
    tags = rev.get("tags", [])
    if isinstance(tags, list) and any("bot" in t.lower() for t in tags):
        return True
    
    user = rev.get("user", "") or ""
    uname = user.lower()
    bot_indicators = ["bot", "automated", "script", "maintenance"]
    
    for indicator in bot_indicators:
        if indicator in uname:
            return True
    
    return False

def count_citations(text):
    """Count citations in text."""
    if not text:
        return 0
    return len(re.findall(r'<ref[^>]*>', text, re.IGNORECASE))

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
        rev_content = ""
        if isinstance(rev.get("slots"), dict):
            rev_content = rev.get("slots", {}).get("main", {}).get("content", "") or rev.get("slots", {}).get("main", {}).get("*", "")
        if not rev_content:
            rev_content = rev.get("content") or rev.get("*") or ""
        
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
        
        user_type = "bot" if is_bot_revision(rev) else "human"
        content_analysis["edit_frequency"][user_type] += 1
        
        if current_size > (prev_size or 0) * 1.5:
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

def detect_bias_patterns(content_analysis, page_title):
    """Detect potential bias patterns in the content analysis."""
    bias_indicators = []
    
    total_edits = sum(content_analysis["edit_frequency"].values())
    bot_ratio = content_analysis["edit_frequency"]["bot"] / total_edits if total_edits > 0 else 0
    
    if bot_ratio > 0.3:
        bias_indicators.append({
            "type": "high_bot_ratio",
            "description": f"Significant bot edit ratio ({bot_ratio:.1%}) may indicate automated bias",
            "severity": "high" if bot_ratio > 0.6 else "medium" if bot_ratio > 0.4 else "low"
        })
    
    bot_citation_changes = [c for c in content_analysis["citation_changes"] if c["is_bot"]]
    human_citation_changes = [c for c in content_analysis["citation_changes"] if not c["is_bot"]]
    
    if bot_citation_changes and human_citation_changes:
        bot_avg_citation_delta = sum(c["citation_delta"] for c in bot_citation_changes) / len(bot_citation_changes)
        human_avg_citation_delta = sum(c["citation_delta"] for c in human_citation_changes) / len(human_citation_changes)
        
        if abs(bot_avg_citation_delta - human_avg_citation_delta) > 1:
            bias_indicators.append({
                "type": "citation_bias",
                "description": f"Bots and humans show different citation patterns (bot: {bot_avg_citation_delta:.1f}, human: {human_avg_citation_delta:.1f})",
                "severity": "medium" if abs(bot_avg_citation_delta - human_avg_citation_delta) > 2 else "low"
            })
    
    bot_amplifications = [a for a in content_analysis["content_amplification"] if a["is_bot"]]
    if len(bot_amplifications) > len(content_analysis["content_amplification"]) * 0.5:
        bias_indicators.append({
            "type": "content_amplification_bias",
            "description": f"Bots responsible for {len(bot_amplifications)}/{len(content_analysis['content_amplification'])} content amplifications",
            "severity": "medium" if len(bot_amplifications) > len(content_analysis["content_amplification"]) * 0.8 else "low"
        })
    
    if content_analysis["edit_frequency"]["bot"] > 0:
        bot_size_changes = [c for c in content_analysis["size_changes"] if c["is_bot"]]
        human_size_changes = [c for c in content_analysis["size_changes"] if c["is_bot"] == False]
        
        if bot_size_changes and human_size_changes:
            bot_avg_size_change = sum(abs(c["size_delta"]) for c in bot_size_changes) / len(bot_size_changes)
            human_avg_size_change = sum(abs(c["size_delta"]) for c in human_size_changes) / len(human_size_changes)
            
            if bot_avg_size_change < human_avg_size_change * 0.5:
                bias_indicators.append({
                    "type": "maintenance_bias",
                    "description": f"Bots make smaller edits on average (bot: {bot_avg_size_change:.0f}, human: {human_avg_size_change:.0f} chars)",
                    "severity": "low"
                })
    
    controversial_keywords = ["controversy", "debate", "dispute", "criticism", "opposition", "denial", "hesitancy"]
    if any(keyword in page_title.lower() for keyword in controversial_keywords):
        if bot_ratio > 0.2:
            bias_indicators.append({
                "type": "controversial_topic_bias",
                "description": f"High bot activity ({bot_ratio:.1%}) on controversial topic",
                "severity": "medium"
            })
    
    return bias_indicators

@app.route("/api/analyze")
def analyze_topic():
    """API endpoint to analyze a topic for automation bias"""
    topic = request.args.get("topic", "climate change")
    pages = int(request.args.get("pages", 3))
    revisions = int(request.args.get("revisions", 30))
    
    print(f"Analyzing topic: {topic}")
    
    # Search for pages
    titles = search_pages(topic, limit=pages)
    if not titles:
        return jsonify({"error": f"No pages found for topic: {topic}"})
    
    results = []
    total_edits = 0
    total_bot_edits = 0
    all_bias_indicators = []
    
    for title in titles:
        try:
            revs, pageid = fetch_revisions_for_page(title, revlimit=revisions)
            if not revs:
                continue
            
            content_analysis = analyze_content_changes(revs)
            bias_indicators = detect_bias_patterns(content_analysis, title)
            
            total_page_edits = len(revs)
            bot_edits = sum(1 for rev in revs if is_bot_revision(rev))
            bot_ratio = bot_edits / total_page_edits if total_page_edits > 0 else 0
            
            page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            
            page_result = {
                "title": title,
                "pageid": pageid,
                "page_url": page_url,
                "total_edits": total_page_edits,
                "bot_edits": bot_edits,
                "bot_ratio": bot_ratio,
                "bias_indicators": bias_indicators,
                "content_analysis": {
                    "size_changes_count": len(content_analysis["size_changes"]),
                    "citation_changes_count": len(content_analysis["citation_changes"]),
                    "amplification_count": len(content_analysis["content_amplification"])
                }
            }
            
            results.append(page_result)
            total_edits += total_page_edits
            total_bot_edits += bot_edits
            all_bias_indicators.extend(bias_indicators)
            
        except Exception as e:
            print(f"Error analyzing {title}: {e}")
            continue
        
        time.sleep(0.5)  # Rate limiting
    
    overall_bot_ratio = total_bot_edits / total_edits if total_edits > 0 else 0
    bias_severity = "high" if len(all_bias_indicators) > 3 else "medium" if len(all_bias_indicators) > 1 else "low"
    
    return jsonify({
        "topic": topic,
        "pages_analyzed": len(results),
        "total_edits": total_edits,
        "total_bot_edits": total_bot_edits,
        "overall_bot_ratio": overall_bot_ratio,
        "bias_severity": bias_severity,
        "bias_indicators": all_bias_indicators,
        "page_results": results
    })

@app.route("/")
def index():
    return """
    <html>
    <head><title>Week 7 API</title></head>
    <body>
        <h1>Week 7 Automation Bias Analysis API</h1>
        <p>Use /api/analyze?topic=climate%20change&pages=3&revisions=30</p>
        <p>Example: <a href="/api/analyze?topic=climate%20change&pages=3&revisions=30">Analyze Climate Change</a></p>
    </body>
    </html>
    """

if __name__ == "__main__":
    print("Starting Week 7 API server at http://127.0.0.1:5002")
    app.run(debug=True, host="0.0.0.0", port=5002)
