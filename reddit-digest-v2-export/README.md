# Reddit 精选资讯

自动抓取 Reddit 热门帖子并生成 JSON Feed。

## 文件结构

```
reddit-digest/
├── .github/workflows/
│   └── generate-feed.yml    # GitHub Actions 定时任务
├── scripts/
│   ├── reddit_digest_github.py  # GitHub Actions 抓取脚本
│   └── deliver.py               # 本地 QClaw 推送脚本
├── config.json                 # 配置文件
├── feed-reddit.json           # 生成的 Feed（自动生成）
└── state-reddit.json          # 状态文件（自动生成）
```

## 配置

### 1. 配置 GitHub Secrets（可选）

如需推送到私有仓库，添加：
- `GH_TOKEN`: GitHub Personal Access Token

### 2. 配置 GitHub Actions

仓库设置 → Actions → 启用 Actions

## 本地配置

编辑 `scripts/deliver.py`，修改飞书配置：

```python
FEISHU_APP_ID = "你的 App ID"
FEISHU_APP_SECRET = "你的 App Secret"
USER_ID = "你的 open_id"
FOLDER_TOKEN = "云盘文件夹 Token"
```

## 手动测试

### 1. 本地测试抓取（GitHub Actions）
```bash
cd scripts
python3 reddit_digest_github.py
```

### 2. 本地测试推送
```bash
python3 deliver.py
```

## 定时任务

- **GitHub Actions**: 每天 10:00 UTC 自动抓取并推送 feed-reddit.json
- **本地 QClaw**: 每天 10:00 AM 读取 GitHub JSON 并推送到飞书
