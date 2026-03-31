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
CONFIG_PATH = Path(__file__).parent.parent / "config.json"
SCRIPT_DIR = Path(__file__).parent
STATE_FILE = SCRIPT_DIR.parent / "state-reddit.json"
OUTPUT_FILE = SCRIPT_DIR.parent / "feed-reddit.json"

# 飞书配置（仅用于翻译）
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"seenPosts": {}}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

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
        r = subprocess.run(
            ["curl", "-s", "-H", "User-Agent: QClaw/1.0", url],
            capture_output=True, text=True, timeout=15
        )
        try:
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
        except:
            print("✗")
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
    config = load_config()
    state = load_state()
    today = datetime.now().strftime("%Y-%m-%d")
    
    print("🚀 开始抓取 Reddit 资讯...")
    all_posts = fetch_hot_posts(config)
    
    if not all_posts:
        print("⚠️ 未获取到帖子")
        return
    
    print(f"\n✅ 获取 {len(all_posts)} 条帖子")
    
    # 过滤已见过的帖子
    unseen_posts = [p for p in all_posts if p['id'] not in state.get('seenPosts', {})]
    print(f"📋 新帖子: {len(unseen_posts)} 条")
    
    # 取 Top 28
    top_posts = unseen_posts[:28]
    
    # 翻译标题
    print("\n🌐 翻译标题...")
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
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Feed 已保存: {OUTPUT_FILE}")
    print(f"   - 星级精选: {len(feed['starred'])} 条")
    print(f"   - 普通精选: {len(feed['regular'])} 条")

if __name__ == "__main__":
    main()