#!/usr/bin/env python3
"""
Reddit 精选资讯 - GitHub Actions 版本
生成 JSON Feed 供本地 QClaw 读取
"""

import json
import os
import subprocess
import time
import urllib.parse
from datetime import datetime
from pathlib import Path

# 配置
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
CONFIG_PATH = REPO_ROOT / "config.json"
STATE_FILE = REPO_ROOT / "state-reddit.json"
OUTPUT_FILE = REPO_ROOT / "feed-reddit.json"

def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 无法读取 config.json: {e}")
        # 使用默认配置
        return {
            "reddit": {
                "subreddits": [
                    "AI_Agents", "ArtificialInteligence", "artificial", "ChatGPT",
                    "Entrepreneur", "GoogleGemini", "OpenAI", "productivity",
                    "TrueReddit", "advertising", "AskReddit", "marketing",
                    "remotework", "smallbusiness", "startups"
                ]
            }
        }

def load_state():
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"seenPosts": {}}

def save_state(state):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ 无法保存状态: {e}")

def translate_google(text):
    """使用 Google Translate 网页翻译"""
    if not text or len(text.strip()) < 3:
        return text
    
    # 检查是否已是中文
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    if chinese_chars / max(len(text), 1) > 0.3:
        return text
    
    try:
        encoded = urllib.parse.quote(text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q={encoded}"
        
        result = subprocess.run([
            "curl", "-s", "-A", "Mozilla/5.0",
            url
        ], capture_output=True, text=True, timeout=10)
        
        if result.stdout and result.stdout.startswith('['):
            data = json.loads(result.stdout)
            if data[0]:
                translated = ''.join([item[0] for item in data[0] if item[0]])
                return translated
    except Exception as e:
        print(f"  翻译错误: {e}")
    
    return text

def fetch_hot_posts(config):
    """抓取所有热门帖子"""
    all_posts = []
    for subreddit in config['reddit']['subreddits']:
        print(f"  🔍 r/{subreddit}...", end=" ", flush=True)
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
        try:
            r = subprocess.run(
                ["curl", "-s", "-H", "User-Agent: QClaw/1.0", url],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(r.stdout)
            count = 0
            for item in data.get('data', {}).get('children', []):
                post = item.get('data', {})
                all_posts.append({
                    'id': post.get('id', ''),
                    'title': post.get('title', ''),
                    'url': f"https://reddit.com{post.get('permalink', '')}",
                    'subreddit': post.get('subreddit', subreddit),
                    'score': post.get('score', 0),
                    'num_comments': post.get('num_comments', 0),
                    'selftext': post.get('selftext', '')[:500],
                    'hot_score': post.get('score', 0) * 0.6 + post.get('num_comments', 0) * 0.4
                })
                count += 1
            print(f"✓ {count}")
        except Exception as e:
            print(f"✗ ({e})")
        time.sleep(0.2)
    
    # 去重
    seen = set()
    unique = []
    for p in all_posts:
        if p['id'] not in seen:
            seen.add(p['id'])
            unique.append(p)
    return sorted(unique, key=lambda x: x['hot_score'], reverse=True)

def main():
    print("🚀 开始抓取 Reddit 资讯...")

config = load_config()
    state = load_state()
    
    all_posts = fetch_hot_posts(config)
    
    if not all_posts:
        print("⚠️ 未获取到帖子")
        return
    
    print(f"
✅ 获取 {len(all_posts)} 条帖子")
    
    # 过滤已见过的帖子
    unseen_posts = [p for p in all_posts if p['id'] not in state.get('seenPosts', {})]
    print(f"📋 新帖子: {len(unseen_posts)} 条")
    
    # 取 Top 28
    top_posts = unseen_posts[:28] if unseen_posts else all_posts[:28]
    
    # 翻译标题
    print("
🌐 翻译标题...")
    translations = {}
    for post in top_posts:
        if post['title'] not in translations:
            translations[post['title']] = translate_google(post['title'])
            time.sleep(0.3)
    
    # 标记为已见
    for post in top_posts[:7]:
        state.setdefault('seenPosts', {})[post['id']] = datetime.now().isoformat()
    
    # 保存状态
    save_state(state)
    print("✅ 状态已保存")
    
    # 生成 JSON Feed
    feed = {
        "generated_at": datetime.now().isoformat(),
        "count": len(top_posts),
        "starred": [],
        "regular": []
    }
    
    # 星级精选 Top 7
    for i, post in enumerate(top_posts[:7]):
        feed["starred"].append({
            "rank": i + 1,
            "subreddit": post['subreddit'],
            "title_cn": translations.get(post['title'], post['title']),
            "title_en": post['title'],
            "score": post['score'],
            "num_comments": post['num_comments'],
            "url": post['url'],
            "selftext": post['selftext'][:200] if post['selftext'] else ""
        })
    
    # 普通精选 21 条
    for i, post in enumerate(top_posts[7:28], 8):
        feed["regular"].append({
            "rank": i,
            "subreddit": post['subreddit'],
            "title_cn": translations.get(post['title'], post['title']),
            "title_en": post['title'],
            "score": post['score'],
            "num_comments": post['num_comments'],
            "url": post['url']
        })
    
    # 保存 Feed
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(feed, f, ensure_ascii=False, indent=2)
        
        print(f"
✅ Feed 已保存: {OUTPUT_FILE}")
        print(f"   - 星级精选: {len(feed['starred'])} 条")
        print(f"   - 普通精选: {len(feed['regular'])} 条")
    except Exception as e:
        print(f"❌ 保存 Feed 失败: {e}")
if __name__ == "__main__":
    main()
