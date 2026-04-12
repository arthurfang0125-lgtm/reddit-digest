#!/usr/bin/env python3
import json, requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

AI_KEYWORDS = ["AI", "LLM", "GPT", "Claude", "OpenAI", "machine learning", 
               "ChatGPT", "Gemini", "Anthropic", "neural network"]

def fetch_story(sid):
    try:
        s = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", 
                        timeout=3).json()
        if s and not s.get("deleted"):
            return {"objectID": str(sid), "title": s.get("title", ""),
                    "url": s.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                    "points": s.get("score", 0), "num_comments": s.get("descendants", 0),
                    "author": s.get("by", "")}
    except: pass
    return None

def main():
    ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", 
                       timeout=10).json()[:50]
    stories = []
    with ThreadPoolExecutor(10) as ex:
        for r in ex.map(fetch_story, ids):
            if r: stories.append(r)
    
    def score(s):
        pts = s["points"] + s["num_comments"] * 1.5
        if any(k.lower() in s["title"].lower() for k in AI_KEYWORDS):
            pts += 25
        return pts
    
    stories.sort(key=score, reverse=True)
    top = stories[:30]
    
    with open("feed-hn.json", "w") as f:
        json.dump({"generated_at": datetime.now().isoformat(), 
                   "starred": top[:7], "regular": top[7:30]}, f, indent=2)
    print(f"Saved {len(top)} stories")

if __name__ == "__main__":
    main()
