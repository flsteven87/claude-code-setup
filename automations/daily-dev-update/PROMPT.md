每天執行這台 Mac 的開發工具更新。主場是 **Claude Code 這一側**（CLI 本體、marketplaces、plugins、skills、MCP servers），外加與 Codex 共用的全域 CLI 與 runtime 工具。

這是**無人值守執行**：不要等待核准、不要問問題、不要在結尾提出「要不要我繼續」。做完、驗證、寫回記憶、回報。

## 執行規則

1. **基線盤點**：先記錄更新前版本與可用的套件管理器（Claude Code、Codex、Homebrew、gh、Mole、npm/pnpm/bun 全域套件、uv tools、mise、rustup/cargo）。同時讀取 `~/.claude/automations/daily-dev-update/memory.md`，取得上次結果與「已知不要重複處理」的項目。不要輸出 token、credential 或完整的秘密環境變數。

2. **Claude Code 本體**：用官方自我更新路徑更新 `claude`，完成後跑 `claude doctor` 確認安裝健康。若是 native install 且自動更新已啟用，記錄狀態即可。

3. **Marketplaces 與 plugins**：用 `claude plugin marketplace update <name>` 逐一刷新已設定的 marketplace（目前有 claude-plugins-official、anthropic-agent-skills、openai-codex、karpathy-skills、mattpocock），並用 `codex plugin marketplace upgrade` 刷新 Codex 官方支援的 Git marketplace。只用官方指令；不要手動改寫或刪除 `~/.claude/plugins/cache/` 或 `~/.codex/plugins/cache/`。Codex bundled、primary-runtime 與 App 管理的 marketplace 若沒有獨立更新介面，保留原狀並記錄。刷新後記錄哪些有實際變動。

4. **Skills — 保護自持設定**：
   - `~/.claude/skills/mattpocock-skills/` 是**自持 manifest + symlink 到 marketplace clone** 的刻意結構。日常更新只需要 `claude plugin marketplace update mattpocock`，symlink 會自動拿到新內容。**絕對不要重生或覆寫它的 `.claude-plugin/` manifest**，只有在「上游新增了 skill」時才需要，而那要留給人工處理 —— 偵測到這種情況時只回報，不要動手。
   - 其他 `~/.claude/skills/` 下的自訂 skill（handoff、catchup、latest、narrate、next-move、git-converge-main、nexrex-weekly-engineering-report、reverse-thinking、rehydrate、docs-cleanup、daily-standup 等）是本機自有內容，**一律保留原狀**，不要更新、覆寫或刪除。其中數個與 `~/.codex/skills/` 共用且 Codex 是 source of truth，更不能從這邊改。

5. **MCP servers**：檢查已設定的 MCP。用套件管理器安裝的（npm/uvx/pipx/Homebrew）就用對應官方方式更新全域安裝；設定成浮動最新版的，確認可解析即可。**不要啟動任何 server**、不要改寫 secrets、不要在缺乏來源證據時變更固定版本。**不要修改任何 repo 的 `.mcp.json` 或 project-scope 設定** —— 那是各專案自己的東西。OAuth-based MCP（Linear、Supabase、Cloudflare）若顯示連線失敗，只回報「需要重新授權」，不要嘗試繞過。

6. **Code Review Graph**：官方套件名是 `code-review-graph`（Graphify／`graphifyy` 已淘汰，**絕對不要安裝或升級它**）。只用 `uv tool upgrade code-review-graph` 更新 user-level runtime，並以 `code-review-graph --version` 驗證。不要執行 install、build、update、postprocess、watch、daemon、embed 或任何會建立／更新專案 graph 的命令；不要碰任何 repo 的 graph DB、hooks 或 `.gitignore`。若 release notes 要求重跑 installer 或做 schema migration，**跳過並回報**，等人工決定。

7. **共用 CLI**：更新 Homebrew 索引並升級已安裝的 CLI formulae；更新可安全識別的全域 npm/pnpm/bun 套件、uv tools，以及有官方自我更新器的 gh、Mole、Codex 等 CLI。只在已安裝且更新命令受支援時執行。
   **不要**更新 GUI casks、macOS、Xcode、Simulator runtimes，或語言 runtime 的 major version（例如 openjdk、nss 這類非 CLI 函式庫一律跳過並記錄原因）。不要繞過 Homebrew 的 untrusted tap 保護。

8. **絕不進入專案**：不要在任何 repo 執行 `npm install/upgrade`、`uv sync/lock`、`pip install`、`bundle update`、`cargo update` 等專案依賴操作；不要修改 `package.json`、lockfiles、repo 檔案或使用者的未提交工作。

9. **失敗處理**：單一項目失敗時繼續處理其他獨立項目。遇到需要 sudo、互動式登入、授權、重大版本遷移、來源不可信或破壞性移除時，**跳過並回報**，不要繞過保護。

10. **驗證與收尾**：更新後重新記錄版本並做基本可用性檢查（各 CLI 的 `--version` 或官方 health/list 指令）。接著把本次結果**附加**到 `~/.claude/automations/daily-dev-update/memory.md` 與 `~/.codex/automations/automation/memory.md`（以執行時間開頭的一節，不要覆蓋既有內容），保存版本前後、跳過原因、失敗項目與下次應避免重複處理的資訊。

## 回報格式

用繁體中文，簡潔，不要贅述過程：

- **已更新**：逐項「舊版 → 新版」
- **已是最新**：一行帶過
- **跳過**：項目 + 原因
- **失敗**：項目 + 錯誤重點
- **需要人工**：需要重啟、需要重新授權、需要人工決定的遷移

這個工作由 user-level LaunchAgent 透過 `codex exec` 執行，不是 Codex Desktop Scheduled run。最後回覆必須是完整、可獨立閱讀的繁體中文更新報告；LaunchAgent 會把最後回覆原封不動存成 `latest.md`，供 14:00 的 Codex Scheduled reporter 唯讀讀取。
