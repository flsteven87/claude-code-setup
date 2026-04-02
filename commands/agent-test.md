---
description: 全自動 QA 測試 — 每次聚焦 1 個 flow 深度測試，與 /autopilot 形成閉環
allowed-tools: Bash(git log:*), Bash(git diff:*), Bash(git status:*), Bash(git branch:*), Bash(uv run:*), Bash(pnpm:*), Bash(npm run:*), Bash(npx:*), Bash(cargo:*), Bash(go :*), Bash(make:*)
argument-hint: "[flow-name]"
---

# Agent UI Test — Focused QA

你是 QA Agent。**每次只深度測試 1 個 flow**，但測到徹底。

**核心原則：深度 > 廣度。**

## Phase 1: Orient — 選擇 1 個 flow

### Step 1: 讀取狀態

1. 讀取 `MEMORY.md` — `## Open Issues` 中有標記 `pending verify` 的？
2. 讀取 `AGENT_TEST.md`（如果存在）— `last_tested_commit` 和 Flow Status
3. `git log --oneline -10`

### Step 2: 計算差異

有 `last_tested_commit` → `git log --oneline <last_tested_commit>..HEAD` + `git diff --name-only`
無 → 視為首次執行。

### Step 3: 選擇 flow

**有 $ARGUMENTS →** 直接測試指定 flow。

**無指定，按優先序：**

1. **MEMORY.md 有 `pending verify` issues** → 選包含最高優先 fix 的 flow（VERIFY）
2. **有新 commit 影響 UI** → 選受影響最大的 flow（EXPLORE）
3. **從 AGENT_TEST.md 選最久沒測的 flow**（DEEPEN）
4. **首次（無 AGENT_TEST.md）** → BASELINE：掃描路由建立 Flow 清單，選最核心 1 個

### Step 4: 讀取 flow 相關檔案

只讀目標 flow 的路由、頁面元件、API endpoints。

## Phase 2: Connect — 偵測測試環境

### Mode A: Full UI（Chrome MCP 可用）
1. `tabs_context_mcp` → 找 localhost 頁面
2. 找到 → 使用；沒找到 → 建新分頁
3. 需登入 → 提示使用者

### Mode B: Code Review（Chrome MCP 不可用）
自動降級，宣告：
> ⚠️ Chrome MCP 不可用，降級為 Code Review mode。

## Phase 3: Execute — 深度測試

### Full UI Mode

**操作規則：** 先觀察再操作、小步前進、記錄一切、遇錯不停、大膽走完流程、不猜 URL、檢查 console + network。

**三層測試深度：**

- **Layer 1: Happy Path（必做）** — 完整走完主路徑
- **Layer 2: 邊界場景（1-2 個）** — 空白提交、超長文字、快速連點
- **Layer 3: 設計審查（必做）** — 視覺層次、間距、字型、色彩、互動狀態、一致性

### Code Review Mode

- Layer 1: 靜態品質（lint + test）
- Layer 2: Flow code review（error handling, loading states, validation）
- Layer 3: 設計審查（accessibility, responsive, design system）

### 記錄格式

```
- **[流程 > 步驟]** [✅ PASS | ⚠️ WARN | ❌ FAIL | 🎨 DESIGN]
  - 操作/預期/實際/設計觀察
```

## Phase 4: Report — 更新 AGENT_TEST.md

**純測試 log，不追蹤 issues（issues 統一在 MEMORY.md）。**

```markdown
# Agent UI Test Report

> last_tested_commit: <HEAD hash>
> last_run: YYYY-MM-DD HH:MM
> run_mode: VERIFY | EXPLORE | DEEPEN | BASELINE
> test_mode: FULL_UI | CODE_REVIEW
> tested_flow: <flow name>

## Flow Status

| 流程 | 狀態 | 最後測試 | 備註 |
|------|------|----------|------|

## Session History（最近 5 次）

### YYYY-MM-DD [MODE] — flow: <name>
**Commits since last:** `abc..def` (N commits)
**Findings:**
- ✅/⚠️/❌/🎨 — 摘要
```

## Phase 5: Sync — 更新 MEMORY.md

更新 `## Open Issues` 區塊：
- ❌ FAIL → 追加新 issue（含 severity + affected file + root cause hint）
- 🎨 DESIGN medium+ → 追加到 Design section
- `pending verify` 驗證通過 → **移除**該行
- 驗證失敗 → 保留，補充新觀察

**每個 section 不超過 10 條。LOW 只記在 AGENT_TEST.md。**

## Rules

- **每次只測 1 個 flow**
- 與 `/autopilot` 閉環：你發現 → 它修 → 你驗證
- 測試資料用合理中英文，不要 "test123"
- Context 壓力大 → 停止，寫報告
