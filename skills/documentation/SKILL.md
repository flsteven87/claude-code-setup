---
name: documentation
description: 當用戶要求寫文檔、README、API 文檔、註解、說明文件時觸發此 skill
status: active
tags: [core, docs]
updated: 2026-02-07
---

# Documentation Skill

生成清晰、完整、易維護的技術文檔。

## 文檔類型模板

### README.md 結構

```markdown
# 專案名稱

簡短描述專案做什麼（1-2 句）

## 功能特色

- ✨ 特色 1
- 🚀 特色 2
- 🔒 特色 3

## 快速開始

### 前置需求

- Node.js >= 18
- [其他依賴]

### 安裝

\`\`\`bash
npm install your-package
\`\`\`

### 基本使用

\`\`\`javascript
// 最簡單的使用範例
\`\`\`

## 文檔

- [完整文檔](./docs)
- [API 參考](./docs/api.md)
- [範例](./examples)

## 貢獻指南

歡迎貢獻！請閱讀 [CONTRIBUTING.md](./CONTRIBUTING.md)

## 授權

MIT License - 詳見 [LICENSE](./LICENSE)
```

### API 文檔格式

```markdown
## functionName(param1, param2)

簡短描述功能。

### 參數

| 參數 | 類型 | 必填 | 預設值 | 說明 |
|------|------|------|--------|------|
| param1 | string | ✅ | - | 參數說明 |
| param2 | object | ❌ | {} | 參數說明 |

### 回傳值

`Promise<Result>` - 回傳值說明

### 範例

\`\`\`javascript
const result = await functionName('value', { option: true });
console.log(result);
// 輸出：{ ... }
\`\`\`

### 錯誤處理

| 錯誤類型 | 觸發條件 |
|----------|----------|
| ValidationError | 當 param1 為空時 |

### 相關

- [relatedFunction](#relatedfunction)
```

### 代碼註解規範

```typescript
/**
 * 函數的簡短描述
 *
 * 詳細說明（如需要）。解釋函數的用途、
 * 重要的實作細節、或使用注意事項。
 *
 * @param name - 參數說明
 * @param options - 選項物件
 * @param options.timeout - 超時時間（毫秒）
 * @returns 回傳值說明
 * @throws {ErrorType} 何時會拋出此錯誤
 *
 * @example
 * ```ts
 * const result = await myFunction('test', { timeout: 5000 });
 * ```
 */
```

## 撰寫原則

### 1. 讀者優先
- 假設讀者是新手
- 從「為什麼」開始，再講「怎麼做」
- 使用清晰的標題結構

### 2. 範例驅動
- 每個概念都附帶範例
- 範例應該可以直接執行
- 從簡單到複雜

### 3. 保持更新
- 文檔和代碼同步更新
- 標註版本變更
- 移除過時內容

### 4. 結構清晰
- 使用一致的格式
- 善用視覺層次（標題、列表、代碼塊）
- 適當使用表格和圖表

## 檢查清單

撰寫文檔時確認：

- [ ] 目標讀者明確
- [ ] 包含快速開始指南
- [ ] 所有參數都有說明
- [ ] 包含實際可運行的範例
- [ ] 錯誤情況有文件說明
- [ ] 無拼字和文法錯誤
