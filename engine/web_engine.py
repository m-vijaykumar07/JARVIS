"""
JARVIS Web Engine & In-App Intelligence Layer
Executes in-app search, article text extraction, page summarization,
and factual grounding without redirecting every query to an external browser.
"""
import urllib.request
import urllib.parse
import json
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

class WebEngine:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }

    def search_in_app(self, query: str, max_results: int = 4) -> List[Dict[str, Any]]:
        """
        Performs web search and returns structured cards: title, url, snippet, source.
        Does NOT launch Chrome.
        """
        results = []
        if not query or not query.strip():
            return results

        clean_query = query.strip()

        # 1. Primary: DuckDuckGo Search API
        if DDGS:
            try:
                with DDGS() as ddgs:
                    raw_items = ddgs.text(clean_query, max_results=max_results)
                    if raw_items:
                        for item in raw_items:
                            results.append({
                                "title": item.get("title", "No Title"),
                                "url": item.get("href", ""),
                                "snippet": item.get("body", ""),
                                "source": urllib.parse.urlparse(item.get("href", "")).netloc or "Web"
                            })
                        if results:
                            return results
            except Exception as e:
                print(f"[WebEngine] DDGS search failed: {e}")

        # 2. Fallback: Wikipedia Summary API if single topic
        try:
            wiki_encoded = urllib.parse.quote(clean_query)
            wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_encoded}"
            req = urllib.request.Request(wiki_url, headers={'User-Agent': 'JarvisAssistant/2.0'})
            with urllib.request.urlopen(req, timeout=4) as res:
                data = json.loads(res.read().decode('utf-8'))
                if "extract" in data:
                    results.append({
                        "title": data.get("title", clean_query),
                        "url": data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{wiki_encoded}"),
                        "snippet": data.get("extract", "")[:350],
                        "source": "Wikipedia"
                    })
        except Exception:
            pass

        return results

    def extract_page_text(self, url: str, max_chars: int = 3000) -> str:
        """
        Fetches web page HTML and extracts clean readable article text.
        """
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=6) as response:
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type and 'application/xhtml' not in content_type:
                    return "The requested resource is not an HTML document."
                
                html = response.read().decode('utf-8', errors='ignore')
                soup = BeautifulSoup(html, 'html.parser')

                # Strip scripts, styles, forms, navigation
                for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'svg']):
                    element.decompose()

                # Collect paragraph text
                paragraphs = []
                for p in soup.find_all(['p', 'article']):
                    txt = p.get_text().strip()
                    if len(txt) > 30 and not any(skip in txt.lower() for skip in ['cookie', 'subscribe', 'terms of service']):
                        paragraphs.append(txt)

                full_text = " ".join(paragraphs)
                # Normalize spaces
                clean_text = re.sub(r'\s+', ' ', full_text).strip()
                return clean_text[:max_chars] if clean_text else "Unable to parse text from page."
        except Exception as e:
            return f"Failed to retrieve page: {e}"

    def summarize_content(self, text: str, max_sentences: int = 3) -> str:
        """
        Heuristic extractive summarizer (used when offline or local fallback).
        """
        if not text or len(text.strip()) < 50:
            return text

        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        meaningful = [s for s in sentences if len(s.strip()) > 20 and not s.startswith("http")]
        return " ".join(meaningful[:max_sentences])

# Global instance
web_engine = WebEngine()
