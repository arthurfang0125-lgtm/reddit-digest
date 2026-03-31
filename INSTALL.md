# Reddit 精选资讯技能 - 安装说明书

> 一次性安装指南，适用于 QClaw / Workbuddy 等 OpenClaw 环境

---

## 快速安装（3步完成）

### 第1步：复制技能目录

将整个 `reddit-digest` 文件夹复制到目标机器的技能目录：

```bash
cp -r reddit-digest ~/.openclaw/workspace/skills/
```

### 第2步：修改配置文件

编辑 `~/.openclaw/workspace/skills/reddit-digest/config.json`，填入你的飞书信息：

```json
{
  "reddit": {
    "subreddits": [
      "AI_Agents", "ArtificialInteligence", "artificial", "ChatGPT",
      "Entrepreneur", "GoogleGemini", "OpenAI", "productivity",
      "TrueReddit", "advertising", "AskReddit", "marketing",
      "remotework", "smallbusiness", "startups"
    ]
  },
  "push": {
    "count": 28,
    "starred_count": 7,
    "starred_comments_count": 2
  },
  "feishu": {
    "user_id": "你的飞书 open_id"
  }
}
```

### 第3步：修改脚本中的飞书凭证

编辑 `scripts/reddit_digest_full.py`，修改文件顶部的配置：

```python
FEISHU_APP_ID = "你的飞书 App ID"
FEISHU_APP_SECRET = "你的飞书 App Secret"
FOLDER_TOKEN = "你的飞书云盘文件夹 Token"
USER_ID = "你的飞书 open_id"
```

---

## 飞书 Bot 配置

### 创建飞书应用

1. 打开 https://open.feishu.cn/app
2. 点击「创建企业自建应用」
3. 填写应用名称（如：Reddit精选资讯）
4. 记录 **App ID** 和 **App Secret**

### 开通必要权限

在应用管理页面 → 权限管理，开通以下权限：

| 权限 | 用途 |
|------|------|
| `im:message:send_as_bot` | 发送飞书消息 |
| `drive:file:upload` | 上传文件到云盘 |
| `translation:text` | 翻译文本（备用） |

### 获取飞书 open_id

在飞书开放平台 → 用户信息，或通过以下方式获取：

```bash
# 替换 YOUR_TOKEN 为 tenant_access_token
curl -X GET "https://open.feishu.cn/open-apis/contact/v3/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 获取云盘文件夹 Token

1. 打开飞书云盘，进入目标文件夹
2. 复制 URL 中的 folder token，例如：
   `https://xxx.feishu.cn/drive/folder/HEXmfT4Czl4bC6dYdMecrec3nPP`
   → Token 为 `HEXmfT4Czl4bC6dYdMecrec3nPP`

---

## 手动测试

安装完成后，手动运行一次验证：

```bash
cd ~/.openclaw/workspace/skills/reddit-digest/scripts
python3 reddit_digest_full.py
```

**预期输出：**
```
🚀 开始抓取 Reddit 资讯...
  🔍 r/AI_Agents... ✓ 10
  ...
✅ 获取 150 条帖子
📥 抓取 Top 7 详情和评论...
🌐 翻译内容...
✅ 翻译完成: 47 条
📄 生成报告...
☁️ 上传到飞书云盘...
✅ 上传成功: https://xxx.feishu.cn/drive/file/xxx
✅ 飞书通知已发送
```

---

## 设置定时任务（每天 10 点推送）

### 方式一：OpenClaw cron（推荐）

在 OpenClaw 对话框中发送：

```
帮我设置一个定时任务，每天 10 点运行：
cd ~/.openclaw/workspace/skills/reddit-digest/scripts && python3 reddit_digest_full.py
推送到飞书，我的 open_id 是 [你的 open_id]
```

### 方式二：系统 crontab

```bash
# 编辑 crontab
crontab -e

# 添加以下内容（每天 10:00 AM）
0 10 * * * cd ~/.openclaw/workspace/skills/reddit-digest/scripts && /usr/local/bin/python3 reddit_digest_full.py >> /tmp/reddit_cron.log 2>&1
```

---

## 技能文件说明

```
reddit-digest/
├── INSTALL.md              # 本安装说明书
├── FINAL_CONFIG.md         # 完整配置文档
├── README.md               # 技能说明书
├── config.json             # 配置文件（需修改）
└── scripts/
    └── reddit_digest_full.py   # 主脚本（需修改凭证）
```

---

## 输出示例

**飞书通知消息：**
```
✅ 完整报告已上传！

📮 Reddit 精选资讯 | 2026-03-31
包含：⭐ 7个星级精选（中文翻译）+ 📋 21个普通精选（全中文）

🔗 https://xxx.feishu.cn/drive/file/xxx
```

**Markdown 报告结构：**
```
# 📮 Reddit 精选资讯 | 2026-03-31

## ⭐ 今日星级推荐 Top 7

### 🥇 第1名 | r/AskReddit
# 中文翻译标题

> 原文标题：...
📝 内容：中文翻译内容
🔗 链接：...
💬 精华评论：
> "中文翻译评论" 👍 1,234

## 📋 精选列表（21条）
#8 🔹 中文翻译标题
👍 1,000 赞同 · 💬 200 评论
🔗 链接
```

---

## 常见问题

**Q: 翻译失败怎么办？**
A: 脚本使用 Google Translate 网页翻译，确保网络可以访问 `translate.googleapis.com`

**Q: 上传云盘失败？**
A: 检查飞书 App 是否开通了 `drive:file:upload` 权限

**Q: 消息发送失败？**
A: 检查 App ID / App Secret 是否正确，以及 `im:message:send_as_bot` 权限

**Q: 如何修改关注的社区？**
A: 编辑 `config.json` 中的 `subreddits` 列表

**Q: 如何修改推送时间？**
A: 修改定时任务的 cron 表达式，`0 10 * * *` 表示每天 10 点

---

## 依赖

- Python 3.x（系统自带）
- curl（系统自带）
- 无需安装额外 Python 包

---

*技能版本：v1.3 | 最后更新：2026-03-31*
