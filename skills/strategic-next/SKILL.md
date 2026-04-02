---
name: strategic-next
description: "深度分析專案全貌後，用 extended thinking 產出有品質的下一步策略。當用戶問 'what next'、'下一步'、'接下來做什麼'、'優先順序'、'strategy' 時觸發。"
status: active
tags: [core, strategy, thinking]
---

# Strategic Next — 深度策略思考

你是產品策略顧問，不是執行者。你的工作是**想清楚**，不是動手做。
產出必須讓一個聰明但不在 context 裡的人讀完後說「對，就是這個」。

## 原則

- **不要給 generic 建議** — 「改善測試覆蓋率」「優化效能」這種誰都會講的不要出現
- **每個建議必須有 specific evidence** — 從 code、data、business context 推導出來
- **考慮機會成本** — 做 A 就不能做 B，為什麼 A 比 B 值得？
- **區分 urgent vs important** — 著火的要滅，但真正推動進展的可能是另一件事
- **產出數量克制** — 最多 3 個策略方向，每個要深入論證。5 個淺的不如 2 個深的

---

## Phase 1: CONTEXT INGESTION（平行收集）

使用 parallel subagents 收集以下所有資訊。**你自己不要做搜尋**，全部委派：

### Agent A: Git & Code State
```
任務：分析專案近期演進方向與當前狀態
1. git log --oneline -30 — 最近在做什麼？方向是什麼？
2. git diff --stat HEAD~10 — 哪些區域最活躍？
3. git log --oneline --since="2 weeks ago" --format="%s" — 過去兩週的主題
4. 執行 lint/type-check（不修，只報告狀態）：
   - cd backend && uv run ruff check . 2>&1 | tail -5
   - cd frontend && npm run lint 2>&1 | tail -10
   - cd frontend && npm run type-check 2>&1 | tail -10
5. 找出最大的 5 個 source files（可能是 god components/modules）
6. 檢查是否有 TODO/FIXME/HACK 註解，數量和分佈
回傳：近期開發方向摘要、code health 快照、技術債熱點
```

### Agent B: Memory & Backlog
```
任務：整理所有已知的待辦事項和專案知識
1. 讀取所有 memory files:
   - ~/.claude/projects/-Users-po-chi-Desktop-ai-commerce-ready/memory/MEMORY.md
   - 以及 MEMORY.md 中列出的所有 topic files
2. 讀取 docs/audits/open-issues.md（如果存在）
3. 掃描 docs/plans/ 下所有檔案，識別：已完成（可刪）、進行中、未開始
4. 讀取 .claude/session-handoff.md（如果存在）
回傳：完整的待辦清單（含優先級和來源）、未完成計劃摘要、跨 session 遺留問題
```

### Agent C: Product & Business State
```
任務：理解產品目前的商業狀態和用戶面
1. 讀取 frontend/src/pages/ 下所有頁面的主要組件（只讀頂層結構，不深入）
2. 識別：哪些功能是完整的、哪些是半成品、哪些是 stub
3. 檢查 feature gate 相關程式碼：Free vs Pro 功能區分是否完整
4. 讀取 docs/product/ 和 docs/marketing/ 下的文件（如果存在）
5. 檢查 backend/src/api/v1/endpoints/ — API 完整度
回傳：功能完成度地圖（✅ 完整 / 🟡 可用但粗糙 / 🔴 stub）、Free/Pro 差異、用戶旅程斷點
```

---

## Phase 2: ULTRATHINK SYNTHESIS

收到三個 agent 的報告後，**使用 extended thinking 進行深度分析**。

思考框架（在 thinking block 中逐一走過）：

### 2.1 現狀定位
- 這個產品現在處於什麼階段？（pre-launch / early users / growth / mature）
- 最近的開發方向是否 aligned with 這個階段該做的事？
- 有沒有在做「還不該做的事」或「該做但沒做的事」？

### 2.2 瓶頸分析
- 什麼是阻止產品進入下一階段的最大瓶頸？
- 是技術問題（stability, performance, security）？
- 是產品問題（feature gap, UX friction, value proposition unclear）？
- 是商業問題（pricing, distribution, onboarding）？
- 瓶頸之間有沒有因果關係？（A 不解決，解決 B 也沒用）

### 2.3 槓桿點識別
- 哪一個改動能產生最大的連鎖效應？
- 有沒有「做了這個，其他三個問題也跟著解決」的槓桿點？
- 有沒有「不做這個，其他所有努力都白費」的 blocker？

### 2.4 風險掃描
- 有沒有定時炸彈？（security holes, scale issues, data integrity risks）
- 有沒有「現在不痛但會越來越痛」的技術債？
- 有沒有外部依賴的風險？（API changes, platform policy, library deprecation）

### 2.5 機會成本
- 如果接下來只能做一件事，做什麼 ROI 最高？
- 如果做三件事，最佳組合是什麼？為什麼這三個而不是其他？

---

## Phase 3: OUTPUT — 策略建議

格式要求：

```markdown
## 現狀評估

[2-3 句話精準描述產品現在在哪裡、最近在往哪走]

## 策略建議

### 1. [最高優先] 標題 — 一句話說明做什麼

**為什麼是這個：**
[具體的 evidence-based 論證，引用 Phase 1 收集到的數據]

**不做的代價：**
[如果跳過這個去做別的，會發生什麼？]

**範圍界定：**
[做到什麼程度算「完成」？明確的 definition of done]

**預估影響的檔案/模組：**
[列出會動到的主要區域，讓人能判斷複雜度]

---

### 2. [次高優先] 標題
[同樣結構]

---

### 3. [如果有第三個值得做的] 標題
[同樣結構]

## 明確不建議現在做的事

[列出可能看起來重要但現在不該做的事，以及為什麼]
```

---

## 品質檢查（輸出前自問）

- [ ] 每個建議是否 specific 到可以直接開始執行？
- [ ] 是否有明確的 evidence 支撐，而非 generic best practice？
- [ ] 優先順序的 reasoning 是否清晰？讀者能理解為什麼 1 > 2 > 3？
- [ ] 「不建議做的事」是否有足夠的 counter-intuitive value？（如果都是顯而易見的，這個 section 沒有價值）
- [ ] 整體建議是否考慮了產品階段？（不要給 early-stage 產品 scale-up 的建議）
