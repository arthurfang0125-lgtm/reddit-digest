#!/usr/bin/env python3
"""Tech News Digest - 简化版"""
import json, urllib.request
from datetime import datetime

def fetch_hackernews():
    print("📡 抓取 Hacker News...")
    try:
        req = urllib.request.Request(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            ids = json.loads(resp.read().decode())[:30]
        
        stories = []
        for sid in ids:
            try:
                req2 = urllib.request.Request(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req2, timeout=5) as resp2:
                    s = json.loads(resp2.read().decode())
                if s and not s.get("deleted"):
                    score = s.get("score", 0) + s.get("descendants", 0) * 1.5
                    stories.append({
                        "id": sid,
                        "title": s.get("title", ""),
                        "url": s.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                        "points": s.get("score", 0),
                        "comments": s.get("descendants", 0),
                        "score": score
                    })
            except Exception as e:
                print(f"  跳过 {sid}: {e}")
        stories.sort(key=lambda x: x["score"], reverse=True)
        return stories
    except Exception as e:
        print(f"HN 失败: {e}")
        return []

def fetch_github():
    print("📡 抓取 GitHub Trending...")
    try:
        req = urllib.request.Request(
            "https://api.github.com/search/repositories?q=created:>2026-04-10&sort=stars&order=desc&per_page=20",
            headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        repos = []
        for item in data.get("items", [])[:15]:
            repos.append({
                "name": item["full_name"],
                "description": item.get("description", "") or "",
                "stars": item.get("stargazers_count", 0),
                "language": item.get("language", ""),
                "url": item["html_url"]
            })
        return repos
    except Exception as e:
        print(f"GitHub 失败: {e}")
        return []

def main():
    print(f"🔍 Tech News Digest - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    hn = fetch_hackernews()
    gh = fetch_github()
    
    data = {
        "generated_at": datetime.now().isoformat(),
        "hackernews": {"top": hn[:10], "all": hn},
        "github_trending": gh
    }
    
    with open("feed-tech.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 完成: HN {len(hn)} 条 | GitHub {len(gh)} 条")

if __name__ == "__main__":
    main()
