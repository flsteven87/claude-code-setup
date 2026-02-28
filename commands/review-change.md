---
description: 全面深入審查程式碼改動
---

## Scope 規則

1. 執行 `git diff --name-only` 取得本次變更的檔案清單
2. **只 review 和修改這些檔案**，不碰其他檔案
3. 發現其他檔案的問題→告知用戶，不要自己動手
4. 除非用戶明確說「review 全部」，嚴格限定 scope

## Review 維度

逐檔讀取變更內容，依以下 8 個維度檢查：

### 1. 架構一致性
- 層級職責是否正確（API → Service → Repository）
- 是否違反 CLAUDE.md 的 Absolute Prohibitions

### 2. DRY 與模組化
- 重要邏輯是否有合適的抽取（不 over-engineer）
- 是否有可消除的重複

### 3. 命名與慣例
- 檔案、變數、函數命名是否符合 CLAUDE.md 規範
- 是否混用了不同命名風格

### 4. 程式碼品質
- 是否精準優雅簡潔
- 沒有冗雜判斷、過度防禦性、不必要的 fallback
- 沒有 over-defensive null checks（信任型別系統和內部 code）

### 5. 安全性
- 有無 IDOR、未驗證 input、secrets exposure
- RLS policies 是否正確

### 6. 效能
- 有無 N+1 查詢、sequential await（應用 gather/Promise.all）
- 前端：不必要的 re-render、缺少 cleanup 的 useEffect

### 7. 型別安全
- 有無 `any` leak 到 critical paths
- error handling 型別是否明確

### 8. Legacy 清理
- 是否有該淘汰的舊 code 殘留
- 未使用的 imports、變數、函數

## 行動原則

- **能直接修的就修**：lint error、命名不一致、unused imports、明顯的品質問題
- **需要討論的告知用戶**：架構決策疑慮、潛在的 breaking change、效能 trade-off、不確定是否該改的地方
- 不需要輸出完整 review report，但重要發現和疑慮必須讓用戶知道

## 驗證

完成 review 和修復後，執行：

```bash
# Backend (如有改動)
cd backend && uv run ruff check .

# Frontend (如有改動)
cd frontend && npm run lint && npx tsc --noEmit

# 受影響的測試 (如有)
cd backend && uv run pytest tests/unit/ -x --tb=short -q
```
