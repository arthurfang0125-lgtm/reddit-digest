# Reddit 精选资讯技能 - 最终配置

## 技能概览

**功能**：自动抓取 Reddit 热门帖子，全文翻译为中文，生成精选报告，上传到飞书云盘并发送通知。

**定时推送**：每天 10:00 AM（Asia/Shanghai）

---

## 核心脚本

**主脚本**：`reddit_digest_full.py`

```bash
cd ~/.openclaw/workspace/skills/reddit-digest/scripts
python3 reddit_digest_full.py
```

**功能流程**：
1. 抓取 15 个 Reddit 社区的热门帖子（150 条）
2. 提取 Top 7 的完整内容和精华评论
3. 使用 Google Translate 翻译所有内容为中文
4. 生成 Markdown 报告
5. 上传到飞书云盘
6. 发送飞书通知 + 文件链接

---

## 报告内容

### 星级精选（Top 7）
- 完整标题（中文翻译）
- 原文标题
- 完整内容（中文翻译）
- 精华评论 2 条（中文翻译）+ 点赞数
- 原链接

### 普通精选（21 条）
- 中文翻译标题
- 点赞数 + 评论数
- 原链接

---

## 关注的社区（15 个）

| 分类 | 社区 |
|------|------|
| 🤖 AI 与科技 | r/AI_Agents, r/ArtificialInteligence, r/artificial, r/ChatGPT, r/GoogleGemini, r/OpenAI |
| 💼 创业与商业 | r/Entrepreneur, r/advertising, r/marketing, r/productivity, r/remotework, r/smallbusiness, r/startups |
| 🌍 社区讨论 | r/AskReddit, r/TrueReddit |

---

## 配置文件

**路径**：`~/.openclaw/workspace/skills/reddit-digest/config.json`

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
    "user_id": "ou_250a5418c3b3dc01342906ced15621e6"
  }
}
```

---

## 翻译方案

**使用**：Google Translate 网页翻译

**优势**：
- 无 API 频率限制
- 翻译质量稳定
- 无需额外权限配置

**实现**：
```python
url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q={encoded_text}"
```

---

## 飞书集成

**权限**：
- `drive:file:upload` - 上传文件到云盘
- `im:message` - 发送消息

**云盘位置**：
- Folder Token: `HEXmfT4Czl4bC6dYdMecrec3nPP`
- 文件格式：Markdown

**通知格式**：
```
✅ 完整报告已上传！

📮 Reddit 精选资讯 | 2026-03-31
包含：⭐ 7个星级精选（中文翻译）+ 📋 21个普通精选（全中文）

🔗 https://da3bozc5a32.feishu.cn/drive/file/xxx
```

---

## 定时任务

**方式**：OpenClaw cron

**配置**：
- 时间：`0 10 * * *`（每天 10:00 AM）
- 时区：`Asia/Shanghai`
- 推送：飞书消息 + 文件链接

**日志**：`/tmp/reddit_cron.log`

---

## 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 翻译为空 | Google Translate 不可用 | 检查网络连接 |
| 上传失败 | 云盘权限不足 | 检查 `drive:file:upload` 权限 |
| 消息未发送 | 飞书 API 错误 | 检查 App ID/Secret |
| 定时未执行 | Cron 配置错误 | 检查 openclaw cron list |

---

## 更新日志

| 日期 | 版本 | 更新 |
|------|------|------|
| 2026-03-31 | v1.0 | 初始版本 |
| 2026-03-31 | v1.1 | 优化翻译批处理 |
| 2026-03-31 | v1.2 | 改用 Google Translate |
| 2026-03-31 | v1.3 | 固定定时任务 |

---

**技能已就绪，明天 10 点开始自动推送！** ✨
