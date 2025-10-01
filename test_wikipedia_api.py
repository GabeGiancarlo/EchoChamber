# test_wikipedia_api.py
"""
Flask demo for homework:
- Query the MediaWiki Action API for pages matching a query
- For each top page, fetch recent revisions and mark bot vs human edits
- Compute citation changes (counts of '<ref')
- Serve JSON at /api/summary and a static index.html UI
"""
from flask import Flask, request, jsonify, send_from_directory
import requests
import html
import time

app = Flask(__name__, static_folder="static", static_url_path="/static")

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
DEFAULT_REVS = 30
DEFAULT_PAGES = 3
USER_AGENT = "EchoChamberDemo/0.1 (student-demo) https://github.com/your-repo"

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})


def search_pages(query, limit=DEFAULT_PAGES):
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": limit,
        "format": "json"
    }
    r = session.get(WIKIPEDIA_API, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    return [hit["title"] for hit in data.get("query", {}).get("search", [])]


def fetch_revisions_for_page(title, revlimit=DEFAULT_REVS):
    # Get revisions with content and flags (flags/tags may appear in response)
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


def is_bot_revision(rev):
    # Check flags/tags, user name heuristics
    # API may provide 'bot' flag in rev.get('flags') or rev.get('tags')
    flags = rev.get("flags", "")
    if flags and "bot" in flags:
        return True
    tags = rev.get("tags", [])
    if isinstance(tags, list) and any("bot" in t.lower() for t in tags):
        return True
    user = rev.get("user", "") or ""
    uname = user.lower()
    # heuristic: usernames that end with 'bot' or contain 'bot' might indicate bot accounts
    if uname.endswith("bot") or uname.endswith("-bot") or uname.endswith("_bot") or uname.startswith("bot"):
        return True
    return False


def count_refs_in_text(text):
    if not text:
        return 0
    # simple heuristic: count occurrences of "<ref"
    return text.lower().count("<ref")


@app.route("/api/summary")
def api_summary():
    query = request.args.get("query", "Artificial intelligence in Wikipedia")
    pages_n = int(request.args.get("pages", DEFAULT_PAGES))
    revs_n = int(request.args.get("revs", DEFAULT_REVS))

    titles = search_pages(query, limit=pages_n)
    results = []

    for title in titles:
        try:
            revs, pageid = fetch_revisions_for_page(title, revlimit=revs_n)
        except Exception as e:
            results.append({"title": title, "error": str(e)})
            continue

        total = len(revs)
        bot_count = 0
        anon_count = 0
        citation_deltas = []
        prev_ref_count = None
        
        # Create Wikipedia page URL
        page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        
        # process in reverse chronological order (API returns newest first typically)
        for i, rev in enumerate(revs):
            rev_content = ""
            # In formatversion=2, revision content is in rev['slots']['main']['*'] sometimes:
            if isinstance(rev.get("slots"), dict):
                rev_content = rev.get("slots", {}).get("main", {}).get("content", "") or rev.get("slots", {}).get("main", {}).get("*", "")
            # fallback to 'content' if present
            if not rev_content:
                rev_content = rev.get("content") or rev.get("*") or ""

            ref_count = count_refs_in_text(rev_content)
            if prev_ref_count is None:
                # first (newest) revision — we don't compute delta to later revisions, but store for next loop
                prev_ref_count = ref_count
            else:
                delta = ref_count - prev_ref_count
                if delta != 0:
                    # Create revision URL
                    rev_url = f"https://en.wikipedia.org/w/index.php?title={title.replace(' ', '_')}&oldid={rev.get('revid')}"
                    citation_deltas.append({
                        "rev_id": rev.get("revid") or rev.get("revid", None),
                        "timestamp": rev.get("timestamp"),
                        "citation_delta": delta,
                        "ref_count": ref_count,
                        "rev_url": rev_url,
                        "user": rev.get("user", "Unknown"),
                        "comment": rev.get("comment", "")
                    })
                prev_ref_count = ref_count

            if is_bot_revision(rev):
                bot_count += 1
            # anonymous editor heuristic
            if rev.get("user") and rev.get("user").startswith("10.") is False and "Anonymous" in rev.get("user", ""):
                anon_count += 1

        results.append({
            "title": title,
            "pageid": pageid,
            "page_url": page_url,
            "total_revisions_analyzed": total,
            "bot_edits_count": bot_count,
            "bot_edit_percent": (bot_count / total * 100) if total else 0,
            "anonymous_edits_count": anon_count,
            "citation_deltas": citation_deltas
        })
        # small delay so we don't hammer API
        time.sleep(0.2)

    return jsonify({
        "query": query,
        "pages_requested": pages_n,
        "revs_requested": revs_n,
        "results": results
    })


@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/debug")
def api_debug():
    """Debug endpoint to show what parameters are being received"""
    return jsonify({
        "query": request.args.get("query", "Not provided"),
        "pages": request.args.get("pages", "Not provided"),
        "revs": request.args.get("revs", "Not provided"),
        "all_args": dict(request.args)
    })


if __name__ == "__main__":
    print("Starting EchoChamber demo at http://127.0.0.1:5001")
    app.run(debug=True, host="0.0.0.0", port=5001)
