#!/usr/bin/env python3
"""
Reddit 精选资讯 - 本地推送脚本
从 GitHub 仓库读取 feed-reddit.json 并推送到飞书
"""

import json
import os
import subprocess
from datetime import datetime

# 飞书配置
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "cli_a94a1f9fd17b5bd3")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "coUNvdJ5LfyqsJksUM3kDgbnxaOGV4gH")
USER_ID = os.getenv("FEISHU_USER_ID", "ou_250a5418c3b3dc01342906ced15621e6")
FOLDER_TOKEN = os.getenv("FEISHU_FOLDER_TOKEN", "HEXmfT4Czl4bC6dYdMecrec3nPP")

# GitHub 配置
GITHUB_OWNER = os.getenv("GITHUB_OWNER", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# 本地路径
FEED_PATH = os.getenv("FEED_PATH", "/Users/yangdan/.openclaw/workspace/skills/reddit-digest/feed-reddit.json")

def get_feishu_token():
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET})
    ], capture_output=True, text=True)
    return json.loads(result.stdout)["tenant_access_token"]

def fetch_github_feed():
    """从 GitHub 获取 feed"""
    if GITHUB_OWNER and GITHUB_REPO:
        url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/feed-reddit.json?ref={GITHUB_BRANCH}"
        headers = {"Accept": "application/vnd.github.v3+json"}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
        
        result = subprocess.run([
            "curl", "-s", "-H", f"Authorization: token {GITHUB_TOKEN}" if GITHUB_TOKEN else "",
            "-H", "Accept: application/vnd.github.v3+json",
            url
        ], capture_output=True, text=True)
        
        data = json.loads(result.stdout)
        import base64
        content = base64.b64decode(data["content"]).decode("utf-8")
        return json.loads(content)
    else:
        # 读取本地文件
        with open(FEED_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

def generate_markdown(feed):
    """生成 Markdown 报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        f"# 📮 Reddit 精选资讯 | {today}",
        "",
        "---",
        "",
        "## ⭐ 今日星级推荐 Top 7",
        "",
        "---",
        ""
    ]
    
    rank_emojis = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]
    
    for i, post in enumerate(feed.get('starred', [])):
        lines.append(f"### {rank_emojis[i]} 第{i+1}名 | r/{post['subreddit']}")
        lines.append(f"# {post.get('title_cn', post.get('title_en', ''))}")
        lines.append("")
        lines.append(f"> **原文标题：** {post.get('title_en', '')}")
        lines.append("")
        if post.get('selftext'):
            lines.append(f"**📝 内容：** {post['selftext'][:200]}")
            lines.append("")
        lines.append(f"**🔗 链接：** {post['url']}")
        lines.append(f"👍 {post['score']:,} 赞同 · 💬 {post['num_comments']:,} 评论")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    lines.append("## 📋 精选列表（21条）")
    lines.append("")
    
    for post in feed.get('regular', []):
        lines.append(f"**#{post['rank']}** 🔹 {post.get('title_cn', post.get('title_en', ''))}")
        lines.append(f"👍 {post['score']:,} 赞同 · 💬 {post['num_comments']:,} 评论")
        lines.append(f"🔗 {post['url']}")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append("*🤖 由 QClaw Reddit精选资讯技能自动生成*")
    
    return "\n".join(lines)

def upload_to_feishu_drive(file_path, file_name):
    """上传文件到飞书云盘"""
    token = get_feishu_token()
    file_size = os.path.getsize(file_path)
    
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "https://open.feishu.cn/open-apis/drive/v1/files/upload_all",
        "-H", f"Authorization: Bearer {token}",
        "-F", f"file_name={file_name}",
        "-F", "parent_type=explorer",
        "-F", f"parent_node={FOLDER_TOKEN}",
        "-F", f"size={file_size}",
        "-F", f"file=@{file_path};type=text/markdown"
    ], capture_output=True, text=True, timeout=30)
    
    resp = json.loads(result.stdout)
    if resp.get("code") == 0:
        return resp["data"]["file_token"]
    return None

def send_feishu_message(message):
    """发送飞书消息"""
    token = get_feishu_token()
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "receive_id": USER_ID,
            "msg_type": "text",
            "content": json.dumps({"text": message})
        })
    ], capture_output=True, text=True)
    return json.loads(result.stdout).get("code") == 0

def main():
    print("🚀 开始推送 Reddit 资讯...")
    
    # 获取 Feed
    print("📥 获取 Feed...")
    feed = fetch_github_feed()
    print(f"   - 星级精选: {len(feed.get('starred', []))} 条")
    print(f"   - 普通精选: {len(feed.get('regular', []))} 条")
    
    # 生成 Markdown
    print("📄 生成报告...")
    markdown = generate_markdown(feed)
    
    # 保存到本地
    today = datetime.now().strftime("%Y-%m-%d")
    file_name = f"Reddit_精选_{today}.md"
    file_path = f"/tmp/{file_name}"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    print(f"   - 已保存: {file_path}")
    
    # 上传到飞书云盘
    print("☁️ 上传到飞书云盘...")
    file_token = upload_to_feishu_drive(file_path, file_name)
    
    if file_token:
        file_url = f"https://da3bozc5a32.feishu.cn/drive/file/{file_token}"
        print(f"   - 上传成功: {file_url}")
        
        # 发送飞书通知
        message = f"✅ 完整报告已上传！\n\n📮 Reddit 精选资讯 | {today}\n包含：⭐ {len(feed.get('starred', []))}个星级精选 + 📋 {len(feed.get('regular', []))}个普通精选\n\n🔗 {file_url}"
        send_feishu_message(message)
        print("✅ 飞书通知已发送")
    else:
        print("❌ 上传失败")

if __name__ == "__main__":
    main()