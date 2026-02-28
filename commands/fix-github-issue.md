---
description: 分析並修復 GitHub issue
---

請分析並修復 GitHub issue: $ARGUMENTS

## 步驟

1. **取得 Issue 詳情**
   ```bash
   gh issue view $ARGUMENTS
   ```

2. **理解問題**
   - 分析 issue 描述的問題
   - 確認重現步驟和預期行為

3. **搜尋相關程式碼**
   - 在 codebase 中找到相關檔案
   - 理解現有實作

4. **實作修復**
   - 實作必要的更改
   - 遵循 CLAUDE.md 規範

5. **驗證**
   - 撰寫並執行測試確認修復
   - 確保通過 linting 和 type checking

6. **提交與 PR**
   - 撰寫描述性的 commit message
   - Push 並建立 PR

使用 GitHub CLI (`gh`) 執行所有 GitHub 相關操作。
