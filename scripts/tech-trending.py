#!/usr/bin/env python3
"""Tech News Digest - GitHub Actions 端抓取脚本
抓取 GitHub Trending + Hacker News，生成结构化 JSON 上传 GitHub
"""
import json, requests, re
from datetime import datetime

def translate(text):
    """MyMemory 免费翻译 API"""
    if not text or len(text) < 3:
        return text
    try:
        text_clean = re.sub(r"https?://\S+", "", text).strip()
        if len(text_clean) < 3:
            return text
        url = f"https://api.mymemory.translated.net/get?q={requests.utils.quote(text_clean)}&langpair=en|zh"
        r = requests.get(url, timeout=5).json()
        trans = r.get("responseData", {}).get("translatedText", "")
        if trans and "MYMEMORY" not in trans and trans != text:
            return trans
    except:
        pass
    return text

def fetch_hackernews():
    """抓取 Hacker News"""
    print("📡 抓取 Hacker News...")
    try:
        ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=8).json()[:30]
        stories = []
        for sid in ids:
            try:
                s = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=4).json()
                if s and not s.get("deleted"):
                    title = s.get("title", "")
                    title_zh = translate(title)
                    score = s.get("score", 0) + s.get("descendants", 0) * 1.5
                    # AI 加权
                    ai_kw = ["AI", "LLM", "GPT", "Claude", "OpenAI", "machine learning", "agent", "model"]
                    if any(k.lower() in title.lower() for k in ai_kw):
                        score += 30
                    stories.append({
                        "objectID": str(sid),
                        "title": title,
                        "title_zh": title_zh,
                        "url": s.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                        "points": s.get("score", 0),
                        "num_comments": s.get("descendants", 0),
                        "author": s.get("by", ""),
                        "source": "hackernews",
                        "score": score
                    })
            except:
                pass
        stories.sort(key=lambda x: x["score"], reverse=True)
        return stories
    except Exception as e:
        print(f"  HN 失败: {e}")
        return []

def fetch_github_trending():
    """抓取 GitHub Trending"""
    print("📡 抓取 GitHub Trending...")
    try:
        repos = []
        for lang in ["", "python", "typescript", "rust", "go"]:
            url = "https://api.github.com/search/repositories"
            params = {"q": "created:>2026-04-10", "sort": "stars", "order": "desc", "per_page": 10}
            if lang:
                params["q"] += f" language:{lang}"
            r = requests.get(url, params=params, timeout=8, headers={"Accept": "application/vnd.github.v3+json"})
            if r.status_code == 200:
                for item in r.json().get("items", [])[:10]:
                    repos.append({
                        "name": item["full_name"],
                        "description": item.get("description", ""),
                        "description_zh": translate(item.get("description", "") or ""),
                        "stars": item.get("stargazers_count", 0),
                        "language": item.get("language", ""),
                        "url": item["html_url"],
                        "source": "github_trending"
                    })
        repos.sort(key=lambda x: x["stars"], reverse=True)
        return repos[:20]
    except Exception as e:
        print(f"  GitHub Trending 失败: {e}")
        return []

def main():
    print(f"🔍 Tech News Digest - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    hn = fetch_hackernews()
    gh = fetch_github_trending()
    
    data = {
        "generated_at": datetime.now().isoformat(),
        "hackernews": {
            "top": hn[:10],
            "starred": hn[:5],
            "regular": hn[5:15]
        },
        "github_trending": gh[:15]
    }
    
    with open("feed-tech.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 完成: HN {len(hn)} 条 | GitHub {len(gh)} 条")
    print(f"📁 输出: feed-tech.json")

if __name__ == "__main__":
    main()
