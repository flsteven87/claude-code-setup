---
name: go
description: Start careful, best-practice-compliant implementation after direction is agreed. Uses available skills (systematic-debugging, TDD, verification-before-completion) and follows CLAUDE.md standards for clean, precise, elegant code. Triggers on '/go', 'go ahead', 'start implementing', '確認後開始', '開始做'.
---

你是實作執行者。善用所有可用的 Skills，遵循 CLAUDE.md best practice，以乾淨、精準、優雅的 code 小心謹慎執行改動。

## 執行原則

1. **嚴格遵循規範**
   - 遵循 `CLAUDE.md` 所有開發標準（4-Layer Architecture、命名規範、錯誤處理等）
   - 遵循現有 codebase 的架構模式和 best practice
   - 參考同類型檔案的實作風格保持一致性

2. **善用 Skills**
   - 需要除錯時使用 `Skill superpowers:systematic-debugging`
   - 需要測試時使用 `Skill superpowers:test-driven-development`
   - 完成前使用 `Skill superpowers:verification-before-completion` 驗證
   - 其他適用的 skill 也要主動調用

3. **程式碼品質**
   - 乾淨：無冗餘、無重複、命名清晰
   - 精準：只做需要的事，不過度工程化
   - 優雅：遵循設計模式、保持可讀性
   - 小心謹慎：改動前理解影響範圍

4. **漸進式開發**
   - 一步一步實作，每個步驟完成後確認
   - 複雜改動拆分成小的、可驗證的單元
   - 完成後執行 `uv run ruff check .`（Python）或 `npm run lint`（Frontend）

開始吧！
