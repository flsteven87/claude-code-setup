---
name: codebase-audit
description: 全面審查專案 codebase 的技術與商業架構
status: active
tags: [core, audit]
updated: 2026-02-07
---

# 深度 Codebase 審查

作為獨立的專業審查員，對整個 codebase 進行全面性的技術與商業面審查。此專案經過多個 session 迭代開發，需要識別跨 session 常見的問題。

## 審查範疇

### 1. 架構設計審查

**檢查項目：**
- 整體架構是否符合 best practice design patterns
- 前後端分離是否清晰，職責是否明確
- 資料流向是否合理（API → Service → Repository → Database）
- 是否存在循環依賴或不當的模組耦合
- 微服務架構（如適用）的邊界是否清晰

**產出：**
- 架構圖的問題點標註
- 不符合 best practice 的設計決策清單

### 2. 程式碼品質分析

**檢查項目：**
- 重複程式碼（DRY principle violations）
- 過度複雜的函數或類別（Cyclomatic Complexity）
- Magic numbers 和 hardcoded values
- 不一致的命名規範
- 缺少或過多的註解
- Error handling 是否完善且一致
- 防禦性程式碼是否過度或不足

**使用工具：**
```bash
# Python 專案
uv run ruff check .
uv run mypy .

# JavaScript/TypeScript 專案
npm run lint
npx tsc --noEmit
npm run build

# 檢查重複程式碼
npx jscpd . --min-lines 10 --min-tokens 50
```

### 3. Legacy Code 與技術債務

**檢查項目：**
- 被註解但未刪除的程式碼
- 未使用的 imports、functions、variables、components
- 過時的 dependencies
- Deprecated API 的使用
- TODO/FIXME 註解的數量與嚴重性
- 臨時性的 workaround 是否已固化

**掃描指令：**
```bash
# 找出所有 TODO/FIXME
grep -rn "TODO\|FIXME\|HACK\|XXX" --include="*.ts" --include="*.tsx" --include="*.py" --include="*.js" .

# 找出被註解的程式碼區塊
grep -rn "^[[:space:]]*//.*{" --include="*.ts" --include="*.tsx" --include="*.js" .

# 檢查未使用的 dependencies
npx depcheck  # For Node.js projects
```

### 4. Pipeline 與整合問題

**檢查項目：**
- CI/CD pipeline 是否完整且正常運作
- 測試覆蓋率是否足夠
- 部署流程是否自動化
- 環境變數管理是否安全
- Database migration 策略是否清晰
- API 版本控制是否適當
- 監控與日誌系統是否齊全

**驗證：**
```bash
# 檢查 CI/CD 配置
cat .github/workflows/*.yml
cat .gitlab-ci.yml
cat Dockerfile*

# 執行測試
npm test -- --coverage
uv run pytest --cov

# 檢查環境變數
cat .env.example
```

### 5. 安全性審查

**檢查項目：**
- 敏感資訊是否有外洩風險（API keys, passwords）
- Input validation 是否完善
- SQL Injection / XSS 風險
- CORS 配置是否適當
- Authentication / Authorization 實作是否安全
- Dependencies 是否有已知漏洞

**安全掃描：**
```bash
# Node.js 專案
npm audit
npm audit fix

# Python 專案
uv run pip-audit

# 檢查敏感資訊
git secrets --scan-history
```

### 6. 效能與可擴展性

**檢查項目：**
- N+1 查詢問題
- 不必要的資料庫查詢
- 缺少適當的快取策略
- 未優化的演算法
- Memory leaks 風險
- Bundle size 是否過大

**效能分析：**
```bash
# Frontend bundle 分析
npm run build -- --stats
npx webpack-bundle-analyzer

# 檢查 bundle size
npm run build && du -sh dist/
```

### 7. 商業邏輯一致性

**檢查項目：**
- 商業規則是否正確實作
- Edge cases 是否有處理
- 資料驗證是否完整
- 交易完整性是否保證
- 錯誤處理是否符合業務需求
- 使用者體驗流程是否合理

### 8. 文件與可維護性

**檢查項目：**
- README 是否完整且最新
- API 文件是否齊全
- 架構決策文件（ADR）是否存在
- 程式碼註解是否適當
- 設定檔是否有說明
- Onboarding 文件是否足夠

## 審查流程

1. **初步掃描**：使用自動化工具快速識別明顯問題
2. **深度閱讀**：仔細檢視核心模組與關鍵路徑
3. **跨模組分析**：檢查不同模組間的整合與一致性
4. **歷史分析**：透過 git log 了解程式碼演進軌跡
5. **測試驗證**：執行測試與 linting 工具

## 輸出報告格式

### 嚴重問題（Critical Issues）
- 影響系統穩定性、安全性的重大問題
- 必須立即處理

### 重要問題（Major Issues）
- 影響程式碼品質、可維護性的問題
- 應該優先處理

### 建議改善（Recommendations）
- 可以提升程式碼品質的優化建議
- 可以排程處理

### 優秀實踐（Good Practices）
- 值得保持與推廣的良好設計

## 執行此審查

執行順序：
1. 先執行所有自動化工具掃描
2. 閱讀專案 README 和 CLAUDE.md 了解專案脈絡
3. 檢查專案結構與檔案組織
4. 深入審查核心模組與關鍵檔案
5. 分析跨模組整合與資料流
6. 整理發現並產生詳細報告

請以專業、客觀、建設性的方式提出所有發現，並為每個問題提供具體的改善建議與優先級評估。
