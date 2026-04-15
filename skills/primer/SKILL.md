---
name: primer
description: Quickly orient in a new or unfamiliar project — scans directory structure, reads CLAUDE.md/README, identifies entry points, reports project purpose, tech stack, key files, and dependencies. Triggers on '/primer', 'prime context', 'get me up to speed', '了解這個專案', '快速了解'.
---

# Prime Context

請幫我快速了解這個專案：

## 步驟

1. **專案結構**
   - 執行 `tree -L 2` 或 `ls -la` 了解目錄結構

2. **讀取關鍵文件**
   - 讀取 `CLAUDE.md`（如存在）了解開發規範
   - 讀取 `README.md` 了解專案背景

3. **分析核心代碼**
   - 讀取 `src/` 或根目錄的關鍵檔案
   - 識別主要的 entry points

## 請回報

- 專案結構概覽
- 專案目的和目標
- 關鍵檔案及其用途
- 重要的依賴套件
- 重要的配置文件
- 技術棧摘要
