---
name: code-review
description: 當用戶要求審查代碼、review PR、檢查代碼品質、找出潛在問題時觸發此 skill
status: active
tags: [core, review]
alternative: superpowers:receiving-code-review  # 更完整版本
updated: 2026-02-07
---

# Code Review Skill

進行專業的代碼審查，遵循業界最佳實踐。

## 審查流程

### 1. 理解上下文
- 先了解這段代碼的目的和預期行為
- 確認相關的需求或 issue

### 2. 檢查項目（依優先順序）

**🔴 Critical（必須修復）**
- 安全漏洞（SQL injection、XSS、敏感資料暴露）
- 邏輯錯誤導致功能不正確
- 資料遺失風險
- 效能嚴重問題（N+1 queries、無限迴圈風險）

**🟠 Major（強烈建議修改）**
- 缺乏錯誤處理
- 違反 DRY 原則的重複代碼
- 缺少必要的型別定義
- 不當的例外處理

**🟡 Minor（建議優化）**
- 命名不夠清晰
- 過長的函數（超過 50 行）
- 缺少註解的複雜邏輯
- 可讀性改進

**🟢 Nitpick（可選）**
- 格式問題
- 風格偏好

### 3. 輸出格式

```markdown
## Code Review Summary

### ✅ 優點
- [列出代碼做得好的地方]

### 🔴 Critical Issues
- **[問題標題]** (Line X-Y)
  - 問題：[描述]
  - 建議：[解決方案]

### 🟠 Major Issues
[同上格式]

### 🟡 Minor Suggestions
[同上格式]

### 📝 General Notes
[其他觀察和建議]
```

## 最佳實踐

1. **建設性回饋**：解釋「為什麼」而不只是「做什麼」
2. **具體可行**：提供具體的改進建議和範例代碼
3. **平衡正負**：也要指出代碼的優點
4. **優先排序**：先處理關鍵問題，再處理小問題
5. **尊重作者**：使用「建議」而非「你應該」的語氣
