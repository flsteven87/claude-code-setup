---
description: 輕量收尾審查並提交 commit
---

> 前提：深度 review 已由 `/review-change` 完成。此指令只做最後一哩收尾。

## Scope 規則

1. 執行 `git diff --name-only` 取得本次變更的檔案清單
2. **只檢查和清理這些檔案**，不碰其他檔案
3. 發現其他檔案的問題→告知用戶，不要自己動手

## 收尾檢查

快速掃描變更檔案，清理 debug artifacts：

- [ ] 移除 `console.log`、`print()` 等調試輸出
- [ ] 移除被註解掉的 code blocks
- [ ] 移除 `// TODO`、`// HACK`、`// FIXME` 等開發註解
- [ ] 移除未使用的 imports 和變數
- [ ] 確認沒有 `.env`、credentials 等敏感檔案被加入

如果發現重要問題（不只是 debug 殘留），告知用戶，建議先跑 `/review-change`。

## 驗證 & Commit

```bash
# 確保 type check + lint 通過
cd backend && uv run ruff check .
cd frontend && npx tsc -b && pnpm lint

# Commit
git add <相關檔案>
git commit -m "<conventional commit message>"
```

- 用簡潔英文撰寫 commit message，遵循 conventional commits
- 不要提到 AI 或 Claude Code

## 推送規則

- **如果在 `main` branch → 自動 `git push origin main`**
- 如果在 feature branch → 只 commit，不推送（除非用戶要求）

## Memory 更新

Commit 後，檢查本次工作是否產生了對未來 session 有價值的資訊，更新 project memory：

**該更新的：**
- 新發現的 trap / gotcha（會讓下次踩坑的）
- 架構決策或 pattern 變更（影響未來開發方向的）
- 新增的重要檔案路徑或 hook
- Backlog 項目的狀態變更（完成的標 ✅、新發現的加入）

**該清理的：**
- 已修復的 trap（不再會踩的坑）
- 已完成的 backlog items（別讓 memory 堆積過時資訊）
- 與 codebase 不再 sync 的描述（檔案已改名、邏輯已重構）

**不該更新的：**
- 本次 session 的臨時 context（任務細節、debug 過程）
- 尚未驗證的推測
- CLAUDE.md 已涵蓋的規則（不要重複）

保持 MEMORY.md 精簡、準確、與 codebase 同步。
