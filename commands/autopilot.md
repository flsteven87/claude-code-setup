---
description: Fully autonomous E2E workflow — auto-detects work or executes given task
allowed-tools: Bash(git add:*), Bash(git commit:*), Bash(git push:*), Bash(git status:*), Bash(git log:*), Bash(git diff:*), Bash(git branch:*), Bash(git checkout:*), Bash(git stash:*), Bash(pnpm:*), Bash(npm run:*), Bash(npx:*), Bash(uv run:*), Bash(node:*), Bash(cargo:*), Bash(go :*), Bash(gh:*), Bash(curl:*), Bash(make:*)
argument-hint: "[task description]"
---

# Autopilot Mode

Execute with full autonomy. Do NOT stop to ask for confirmation between phases.

**核心原則：一次只做 1 件事，做完做好。** 小 scope、完整交付、乾淨 commit。

## Phase 0: PRE-CHECK (30 seconds)

```bash
git status --porcelain          # dirty state?
git log --oneline -1            # 最近 commit
```

- **有 dirty state** → 先 `git stash` 或提醒處理
- **最近 commit 是自己** → 避免重複工作

## Phase 1: ORIENT & SCOPE

**讀取 MEMORY.md** — 這是唯一的工作來源。

### If task is provided ($ARGUMENTS):
→ 評估 scope。太大（>10 files）→ 主動拆小，只做最核心部分。

### If no task — discover work from MEMORY.md:

**依序檢查（找到就停）：**

1. `## Open Issues` — 有 HIGH severity？（緊急修復）
2. `## Active Work` — 有 🔴 高優先待完成？（繼續未完成工作）
3. `## Current Phase` — 讀取對應 memory file 的 tasks（戰略對齊）
4. `## Open Issues` — 有 MED/LOW？
5. `docs/plans/` — 有未完成的 plan？

→ 選 **1 個** deliverable。
→ 全部為空 → `strategic-next` skill 分析下一步。
→ 連 strategic-next 也無建議 → 執行 `/roadmap`。

宣告選擇和原因（1-2 句），立即開始。

## Phase 2: PLAN (skip if trivial)

**Skip** if < 3 files and no architectural decisions.

Otherwise, create a structured plan (use `create_plan` tool).

## Phase 3: IMPLEMENT

- Follow `CLAUDE.md` standards strictly
- Match existing codebase patterns
- Use subagents for independent parallel work

### Skill Toolbox — 依情境主動使用：

- **UI/UX 設計** → `ui-ux-pro-max` skill
- **除錯卡關** → `superpowers:systematic-debugging`
- **寫測試** → `superpowers:test-driven-development`
- **AI agent 開發** → `ai-agents` skill
- **Subagent context** → `iterative-retrieval` skill

**Chrome MCP 限制：只允許 `read_console_messages` 讀 log。** 不操作 UI。

## Phase 4: VERIFY

**用 subagent 執行驗證，只回報 PASS/FAIL + 錯誤摘要：**

1. 讀取 `CLAUDE.md` 尋找 project-specific lint/test 指令
2. 偵測專案類型執行對應檢查：
   - `pyproject.toml` → `uv run ruff check .` + `uv run pytest --tb=short -q`
   - `package.json` → `lint` + `type-check` + `test`
   - `Cargo.toml` → `cargo check` + `cargo test`
   - `go.mod` → `go vet ./...` + `go test ./...`
3. Monorepo → 對每個子目錄分別執行

**Runtime log 檢查：** 用 `read_console_messages` 檢查 console 錯誤。

有錯誤 → 修復後重新驗證。

## Phase 5: REVIEW

**用 subagent 讀取 `git diff --name-only` 的所有變更檔案，依 8 維度檢查：**

1. 架構一致性（CLAUDE.md violations？）
2. DRY 與模組化
3. 命名與慣例
4. 程式碼品質
5. 安全性
6. 效能
7. 型別安全
8. Legacy 清理

Subagent 直接修復能修的，回報需討論的。修復後重跑 Phase 4。

## Phase 6: WRAP UP

### Update MEMORY.md:

更新 `## Active Work` 區塊：
- Last session 日期和摘要
- Next priority 列表（🔴/🟡/🟢）

更新 `## Open Issues` 區塊：
- 修復了 issue → 移除該行
- 發現新 issue → 追加（含 severity）
- 新的 lasting knowledge → 寫入對應 memory file

### Commit & Push:
```bash
git add <related files>
git commit -m "<conventional commit message>

Co-Authored-By: Oz <oz-agent@warp.dev>"
git push origin HEAD
```

- Conventional commit（簡潔英文，不提 AI/Claude）
- 修復 issue 時含 refs：`fix(ui): resolve spacing (#D-2)`

## Rules

- Be autonomous — decide and document, don't block on user input
- If stuck >2 attempts → pivot to alternative approach
- **ONE small deliverable per run** — scope > ~5 files 時主動拆小
- Keep context lean — use subagents for heavy exploration and verification
- **Context hygiene** — context 壓力大時主動結束並更新 MEMORY.md
