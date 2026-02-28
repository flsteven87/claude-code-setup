---
name: commit-message
description: 當用戶要求生成 commit message、寫 git commit、提交代碼時觸發此 skill
status: active
tags: [core, git]
updated: 2026-02-07
---

# Commit Message Skill

遵循 Conventional Commits 規範生成清晰、有意義的 commit message。

## Commit Message 格式

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

## Type 類型

| Type | 使用時機 |
|------|----------|
| `feat` | 新增功能 |
| `fix` | 修復 bug |
| `docs` | 文檔變更 |
| `style` | 格式調整（不影響代碼邏輯） |
| `refactor` | 重構（不是新功能也不是 bug 修復） |
| `perf` | 效能優化 |
| `test` | 測試相關 |
| `build` | 構建系統或外部依賴變更 |
| `ci` | CI 配置變更 |
| `chore` | 其他不修改 src 或 test 的變更 |
| `revert` | 撤銷之前的 commit |

## 撰寫規則

### Subject（標題）
- 使用祈使句（"add" 而非 "added" 或 "adds"）
- 首字母小寫
- 結尾不加句號
- 限制在 50 字元內
- 清楚描述「做了什麼」

### Body（內容）- 可選
- 解釋「為什麼」做這個變更
- 與標題空一行
- 每行限制 72 字元
- 可使用 bullet points

### Footer（頁尾）- 可選
- Breaking changes 以 `BREAKING CHANGE:` 開頭
- 關閉 issue 使用 `Closes #123`

## 範例

### 簡單變更
```
feat(auth): add Google OAuth login support
```

### 含詳細說明
```
fix(cart): resolve race condition in quantity update

The cart quantity was not updating correctly when users
rapidly clicked the increment button. Added debounce
mechanism to prevent concurrent API calls.

Closes #234
```

### Breaking Change
```
refactor(api)!: migrate to v2 endpoint structure

BREAKING CHANGE: All API endpoints now require /v2/ prefix.
Previous /api/users becomes /api/v2/users.

Migration guide available at docs/migration.md
```

## 執行步驟

1. 分析變更的文件和內容
2. 確定最適合的 type
3. 識別受影響的 scope（模組/功能區塊）
4. 用簡潔的語言描述變更
5. 如有必要，補充說明原因和影響
