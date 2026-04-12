#!/usr/bin/env python3
import json, requests, re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

AI_KEYWORDS = ["AI", "LLM", "GPT", "Claude", "OpenAI", "machine learning", 
               "ChatGPT", "Gemini", "Anthropic", "neural network"]

def translate(text):
    """使用 MyMemory API 翻译"""
    if not text or len(text) < 3:
        return text
    try:
        # 清理文本
        text = re.sub(r"https?://\S+", "", text).strip()
        if len(text) < 3:
            return text
        
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text)}&langpair=en|zh"
        r = requests.get(url, timeout=5).json()
        trans = r.get("responseData", {}).get("translatedText", "")
        # 如果翻译结果和原文一样或包含错误信息，返回原文
        if trans and "MYMEMORY" not in trans and trans != text:
            return trans
    except:
        pass
    return text

def fetch_story(sid):
    try:
        s = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", 
                        timeout=3).json()
        if s and not s.get("deleted"):
            title = s.get("title", "")
            # 翻译标题
            title_zh = translate(title)
            return {
                "objectID": str(sid),
                "title": title,
                "title_zh": title_zh,
                "url": s.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                "points": s.get("score", 0),
                "num_comments": s.get("descendants", 0),
                "author": s.get("by", "")
            }
    except: pass
    return None

def main():
    print("🚀 抓取 Hacker News...")
    
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
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "starred": top[:7],
            "regular": top[7:30]
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 完成: {len(top)} 条 (含中文翻译)")

if __name__ == "__main__":
    import urllib.parse
    main()
