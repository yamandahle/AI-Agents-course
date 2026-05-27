from duckduckgo_search import DDGS

def web_search(query: str, max_results: int = 3) -> str:
    """
    Performs a web search using DuckDuckGo and returns a summary of results.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if not results:
                return "No results found."
            
            summary = ""
            for i, r in enumerate(results, 1):
                summary += f"[{i}] {r['title']}\nSource: {r['href']}\nSnippet: {r['body']}\n\n"
            return summary
    except Exception as e:
        return f"Search failed: {str(e)}"
