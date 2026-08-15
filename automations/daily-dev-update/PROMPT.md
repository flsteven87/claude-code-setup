# 每日開發工具更新

更新這台 Mac 的使用者層級開發工具。主場是 Claude Code，並涵蓋與 Codex 共用的 CLI、套件管理器與 runtime。

## 完成契約

- **Projectless**：從 `$HOME` 執行，只讀寫本文件允許的使用者層級工具、設定與兩份 maintenance memory。產品 repo、目前 Orca workspace、專案依賴、lockfile、`.mcp.json`、graph 與未提交工作保持不變。
- **無人值守**：執行、驗證、寫回 memory、輸出報告。需要互動、sudo、OAuth、破壞性移除、來源信任或重大遷移時記為跳過；不等待輸入。
- **單次嘗試**：確定性錯誤不重試；暫時性網路錯誤最多重試一次。單項失敗後繼續獨立項目。
- **保密**：只報 credential 是否存在及來源類型，不輸出 token、cookie、authorization header、秘密環境變數或個資。
- **排程邊界**：Orca 已管理本工作。保持所有 Codex、ChatGPT 與 Orca 排程不變，不輸出 automation directive。

## 每日流程

### 1. 建立基線

1. 切換到 `$HOME`，以 `~/.claude/automations/daily-dev-update/memory.md` 為讀取來源；缺少時才 fallback 至 Codex mirror。只讀最近一次 daily checkpoint 與其後仍有效的 follow-up，已解決事項視為已關閉。
2. 對 Claude Code、Codex、Homebrew、Node/npm/Corepack/pnpm、Bun、gh、Mole、mise、uv tools、rustup/rustc/cargo 記錄實際 `command -v` 與版本。Node 工具鏈以解析到的 binary 為準，不只相信版本字串。
3. 用有界的 DNS／HTTPS probe 檢查本次需要的官方 registry。probe 失敗時仍做本機 health/version 檢查，但跳過依賴該網路的更新，不進入反覆 reconnect。

完成條件：每個受管工具都有「目前路徑、目前版本、更新來源、是否可更新」四個欄位；秘密值未進入輸出。

### 2. 更新 Claude 與 marketplaces

1. 先判斷 Claude Code 安裝型態。native install 且自動更新健康時記錄狀態；只有官方更新路徑支援且需要時才執行，最後跑 `claude doctor`。
2. 從 Claude 設定／官方 list 指令取得目前 marketplaces 與 user-scope plugins，不在本文快取名稱或版本。逐一用官方 marketplace update 指令刷新；project-scope、bundled、primary-runtime、curated 與 App-managed 項目保持原狀，除非它們提供明確的 user-level 更新介面。
3. 刷新 Codex 官方支援的 Git marketplaces。保留 runtime／App 管理的 cache，不直接修改 `~/.claude/plugins/cache/` 或 `~/.codex/plugins/cache/`。
4. **Matt 分支**：刷新 mattpocock 前，完整讀取同目錄的 `MATT-SYNC.md`，依其中 fast path 或 delta path 執行。

完成條件：每個已設定 marketplace 都有刷新結果；plugin scope 與 enabled state 未被意外改變；Matt 完成其分支的驗證門檻。

### 3. 更新 MCP 與專用工具

1. MCP 採 **config-only** 稽核：讀既有 user-level 設定與套件 registry metadata。浮動版本只確認可解析；固定版本缺乏 migration 證據時保持不變。
2. MCP 稽核不建立連線，不執行 `claude mcp list`、`codex mcp list` 或任何會做 health probe／啟動 stdio server 的命令。OAuth 狀態只沿用可信的既有狀態；Notion 與 Slack 依使用者決定維持跳過，直到未來明確要求。
3. Code Review Graph 只用 `uv tool upgrade code-review-graph` 與 `code-review-graph --version`。Graphify／`graphifyy` 保持未安裝；CRG install、build、update、postprocess、watch、daemon、embed、server、schema、graph DB 與 repo hooks 保持不變。release notes 要求 installer 或 schema migration 時列入需要人工。

完成條件：每個 MCP／專用工具都標為 current、updated、fixed-and-held、auth-skipped 或 failed；MCP 稽核本身沒有啟動 server，且沒有專案 graph 寫入。

### 4. 更新共用 CLI 與 runtimes

1. 先讀套件管理器的 outdated／dry-run 結果，再建立精確 target list。Homebrew untrusted-tap 保護保持啟用。
2. 自動更新已安裝工具的安全線：
   - CLI、libraries 與有版本名稱的 runtime formula：允許同一 major 內的 patch／minor。
   - NVM default Node：允許同一 major 內的 patch／minor；搬移相同的 global package 名稱，驗證後才切換 default，舊 Node 暫留供 rollback／`.nvmrc`。
   - npm/pnpm/Bun globals 與 uv tools：允許同一 major 內的正常更新；保留既有安全政策與 install-script allowlist。
   - gh、Mole、mise、rustup 與其他已安裝 CLI：只走官方 package manager 或 self-updater。
3. 需要人工的遷移線：major 版本變更、unversioned runtime 跨 major、FFmpeg 跨 major、GUI casks、macOS、Xcode、Simulator runtimes、sudo、互動登入與不可信來源。只報一次版本差異與原因；相同 unresolved key 在版本／原因未變時不重複展開。
4. Codex 先判斷安裝來源並比對官方最新版。已是最新且 memory 記錄 standalone updater 不支援時，視為 current，不重跑已知必敗 updater；只有安裝來源、目前版本或最新版改變時重新評估。

完成條件：每個 target 都只有一個終態；所有已更新工具通過最小 runtime check，且沒有專案依賴操作。

### 5. 驗證與寫回

1. 重跑所有已更新工具的版本／官方 health check。Homebrew 更新後檢查 `brew missing`；formula 更新執行相應 linkage 或直接 runtime check。避免任何會啟動 MCP server 的 health/list 指令。
2. 對照基線，確認實際版本、binary path、global package 名稱集合與重要 enabled state；不以安裝命令 exit 0 取代驗證。
3. 分別在 `~/.claude/automations/daily-dev-update/memory.md` 與 `~/.codex/automations/automation/memory.md` 附加同一個 timestamp checkpoint。只保存版本差異、驗證、未解 blocker、使用者決定與下次 retry key；完整敘事留給 Orca run history。
4. Memory 內一律以 `$HOME` 或 `~` 表示家目錄，並在寫後檢查本次新增段落沒有絕對家目錄或秘密。

完成條件：每個變更都有驗證證據；兩份 checkpoint 等價且精簡；所有未完成項目都有明確原因與下次觸發條件。

## 最終報告

用繁體中文輸出可獨立閱讀的報告：

- **已更新**：逐項 `舊版 → 新版`。
- **已是最新**：合併成一行。
- **跳過**：項目、原因、未來重試條件。
- **失敗**：錯誤重點與受影響範圍。
- **需要人工**：只列真正需要登入、授權或遷移決策的事項。
- **驗證**：列出實際執行的 health/linkage/runtime gates。

沒有項目的區段寫「無」。最後一句確認 projectless 邊界與 memory 寫回結果；不要提議後續排程操作。
