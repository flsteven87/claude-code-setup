---
name: github-workflow
description: GitHub repository 和 workflow 操作。當用戶需要：(1) 建立新 GitHub repository 並 clone 到本地 (2) 初始化新專案 (3) 建立 PR、issue、release (4) 管理 branch 和 merge (5) 查詢 repo 狀態、PR 列表、issue 時觸發此 skill。使用 GitHub CLI (gh) 執行所有操作。
status: active
tags: [core, github, workflow]
updated: 2026-02-07
---

# GitHub Workflow

使用 GitHub CLI (`gh`) 執行 GitHub 操作。

## 前置檢查

執行任何操作前，先確認 gh CLI 狀態：
```bash
gh auth status
```

若未登入，引導用戶執行 `gh auth login`。

## 主要工作流程

### 建立新 Repository

1. **建立並 Clone**
   ```bash
   gh repo create <name> --public --clone --description "<description>"
   cd <name>
   ```
   - `--public` 或 `--private` 控制可見性
   - `--clone` 自動 clone 到當前目錄

2. **初始化專案（依需求選擇）**
   - **Next.js**: `npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir`
   - **Python**: `uv init && uv add <packages>`
   - **空專案**: 直接開始編輯

3. **首次提交**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push -u origin main
   ```

### 從現有 Repository 開始

```bash
gh repo clone <owner>/<repo>
cd <repo>
```

### 建立 Pull Request

```bash
# 建立並推送 branch
git checkout -b feature/<name>
git add .
git commit -m "<type>(<scope>): <description>"
git push -u origin feature/<name>

# 建立 PR
gh pr create --title "<title>" --body "<description>"
```

### 建立 Issue

```bash
gh issue create --title "<title>" --body "<description>" --label "<label>"
```

### 查詢操作

| 需求 | 指令 |
|------|------|
| 列出 PR | `gh pr list` |
| 查看 PR 詳情 | `gh pr view <number>` |
| 列出 Issues | `gh issue list` |
| Repo 資訊 | `gh repo view` |
| 搜尋 Repo | `gh search repos <query>` |

## 常用參數

### gh repo create
- `--public` / `--private` - 可見性
- `--clone` - 建立後 clone
- `--description` - 描述
- `--license` - 授權（mit, apache-2.0, gpl-3.0）
- `--gitignore` - .gitignore 模板（node, python, go）

### gh pr create
- `--draft` - 建立草稿 PR
- `--reviewer` - 指定 reviewer
- `--assignee` - 指定 assignee
- `--label` - 加標籤
- `--base` - 目標 branch（預設 main）

## 注意事項

1. **Commit 訊息**：遵循 Conventional Commits
2. **Branch 命名**：使用 `feature/`、`fix/`、`docs/` 前綴
3. **不自動 commit**：除非用戶明確要求
