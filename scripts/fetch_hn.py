#!/usr/bin/env python3
"""
Hacker News 热点抓取脚本
使用 Firebase HN API (国内可访问)
"""

import json
import requests
import sys
from datetime import datetime
from typing import List, Dict

AI_KEYWORDS = [
    "AI", "artificial intelligence", "LLM", "GPT", "Claude", "OpenAI",
    "machine learning", "neural network", "transformer",
    "stable diffusion", "Midjourney", "ChatGPT", "Gemini", "Anthropic",
    "deep learning", "LLaMA", "Mistral", "Copilot"
]

def fetch_hn_frontpage(limit: int = 50) -> List[Dict]:
    """获取 HN 首页热门"""
    try:
        resp = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=15
        )
        resp.raise_for_status()
        top_ids = resp.json()[:limit]
        
        stories = []
        for story_id in top_ids:
            try:
                story_resp = requests.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                    timeout=5
                )
                story = story_resp.json()
                if story and not story.get("deleted") and not story.get("dead"):
                    stories.append({
                        "objectID": str(story_id),
                        "title": story.get("title", ""),
                        "url": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                        "points": story.get("score", 0),
                        "num_comments": story.get("descendants", 0),
                        "author": story.get("by", "")
                    })
            except Exception as e:
                print(f"Fetch story {story_id} error: {e}", file=sys.stderr)
                continue
        return stories
    except Exception as e:
        print(f"Frontpage fetch error: {e}", file=sys.stderr)
        return []

def score_story(story: Dict) -> float:
    """计算故事得分"""
    points = story.get("points", 0)
    comments = story.get("num_comments", 0)
    title = story.get("title", "").lower()
    
    ai_bonus = 0
    for kw in AI_KEYWORDS:
        if kw.lower() in title:
            ai_bonus = 25
            break
    
    return points + comments * 1.5 + ai_bonus

def main():
    print("🚀 开始抓取 Hacker News...")
    
    stories = fetch_hn_frontpage(60)
    
    if not stories:
        print("❌ 未获取到数据", file=sys.stderr)
        sys.exit(1)
    
    # 按得分排序
    stories.sort(key=score_story, reverse=True)
    
    # 取前30
    top_stories = stories[:30]
    
    # 分级
    starred = top_stories[:7]
    regular = top_stories[7:30]
    
    output = {
        "generated_at": datetime.now().isoformat(),
        "source": "Hacker News",
        "total_stories": len(top_stories),
        "starred_count": len(starred),
        "regular_count": len(regular),
        "starred": starred,
        "regular": regular
    }
    
    with open("feed-hn.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 抓取完成: {len(starred)} 条星级 + {len(regular)} 条普通")

if __name__ == "__main__":
    main()
