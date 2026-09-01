import json
from duckduckgo_search import DDGS

queries = [
    'site:linkedin.com/in/ "owner" "dental clinic"',
    'site:linkedin.com/in/ "founder" "dental clinic"',
    '"Hi, I\'m Dr." "dental clinic"',
    'site:twitter.com dentist clinic owner website',
    '"My clinic" "dental practice" owner',
]

results = []
with DDGS() as ddgs:
    for q in queries:
        print(f"Searching: {q}")
        try:
            for r in ddgs.text(q, max_results=10):
                results.append({"query": q, "title": r.get('title'), "href": r.get('href'), "body": r.get('body')})
        except Exception as e:
            print(f"Error for {q}: {e}")

with open('search_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)
print(f"Saved {len(results)} results")
