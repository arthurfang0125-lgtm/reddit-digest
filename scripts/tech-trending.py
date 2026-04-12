#!/usr/bin/env python3
"""Tech News Digest - GitHub Actions 测试版"""
import json, urllib.request
from datetime import datetime

def fetch_github():
    print("📡 抓取 GitHub Trending...")
    req = urllib.request.Request(
        "https://api.github.com/search/repositories?q=created:>2026-04-11&sort=stars&order=desc&per_page=20",
        headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
    repos = []
    for item in data.get("items", [])[:15]:
        repos.append({
            "name": item["full_name"],
            "description": item.get("description", "") or "",
            "stars": item.get("stargazers_count", 0),
            "language": item.get("language", "") or "",
            "url": item["html_url"]
        })
    return repos

def fetch_hn():
    print("📡 抓取 Hacker News (Algolia)...")
    query = json.dumps({"numericFilters": "points>10", "hitsPerPage": 20}).encode()
    req = urllib.request.Request(
        "https://hn.algolia.com/api/v1/search",
        data=query if False else None,
        headers={"User-Agent": "Mozilla/5.0 (compatible; TechDigest/1.0)"},
        method="GET"
    )
    req = urllib.request.Request(
        "https://hn.algolia.com/api/v1/search_by_date?tags=front_page&hitsPerPage=20",
        headers={"User-Agent": "Mozilla/5.0 (compatible; TechDigest/1.0)"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
    stories = []
    for hit in data.get("hits", [])[:15]:
        if hit.get("url"):
            stories.append({
                "title": hit.get("title", ""),
                "url": hit.get("url", ""),
                "points": hit.get("points", 0),
                "comments": hit.get("num_comments", 0)
            })
    return stories

def main():
    print(f"🔍 Tech News Digest - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    gh = fetch_github()
    hn = fetch_hn()
    data = {
        "generated_at": datetime.now().isoformat(),
        "github_trending": gh,
        "hackernews": hn
    }
    with open("feed-tech.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 完成: GitHub {len(gh)} 条 | HN {len(hn)} 条")

if __name__ == "__main__":
    main()
