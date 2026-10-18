# 每日開發工具更新

更新這台 Mac 的使用者層級開發工具。主場是 Claude Code，並涵蓋與 Codex 共用的 CLI、套件管理器與 runtime。

## 完成契約

- **Projectless**：從 `$HOME` 執行，只修改本文件允許的使用者層級工具、設定與兩份 maintenance memory；允許唯讀檢查專案的 runtime 設定與引用。產品 repo、目前 Orca workspace、專案依賴、lockfile、`.mcp.json`、graph 與未提交工作保持不變。
- **無人值守**：執行、驗證、寫回 memory、輸出報告。先套用本文的 standing approval；只有仍缺少互動、sudo、OAuth session、受支援介面或安全執行條件時才記為技術阻塞，不等待輸入。
- **單次嘗試**：確定性錯誤不重試；暫時性網路錯誤最多重試一次。單項失敗後繼續獨立項目。
- **保密**：只報 credential 是否存在及來源類型，不輸出 token、cookie、authorization header、秘密環境變數或個資。
- **排程邊界**：Orca 已管理本工作。保持所有 Codex、ChatGPT 與 Orca 排程不變，不輸出 automation directive。

## 每日流程

### Project runtime ownership and retirement

Before updating or retiring a runtime, read the registered Orca repository paths and their Git worktree paths through the public CLI. Inspect runtime version files, package engine/package-manager constraints, CI pins, launch scripts and virtual-environment interpreter links read-only. Include mise tracked configs, user launch agents, wrappers and uv tool environments. Record unavailable paths or failed queries as unknown coverage; an incomplete reference scan prevents removal.

Treat each project version file and its package-manager constraints as the owner of that project's runtime. Keep project files unchanged. Report a project-owned version gap with the exact owning path and required project validation; it is a separate repository change, not permission to rewrite pins in this job. Resolve executable symlinks before counting installations: aliases and wrappers are entry points, while independently managed copies may both be required. An older pin still needed by another project is held with that project's path as evidence.

After successful updates, retire only exact obsolete user-runtime installations with a verified retained replacement under the same manager. Require a manager dry-run where supported, a complete reference scan, no active process/open executable using the old installation, no unique global packages, and no unresolved rollback or reproduction requirement. Inspect Python virtual-environment base-interpreter links as well as version selectors. Use the manager's exact-version uninstall route; a broad prune suggestion alone is insufficient because explicit command-line selectors and other projects' CI pins may be outside its index. If any condition is uncertain, retain the installation and record the missing evidence. Preserve project environments, system runtimes and App-managed releases.

Verify removed paths are absent, retained project-selected executables still resolve and run, and project configuration hashes are unchanged. Report retired installations and measured reclaimed bytes separately from update outcomes, reconciling inventory removals with the prior checkpoint. Each retained duplicate needs its owner/reference or one concrete condition for reassessment.

### 1. 建立基線

1. 切換到 `$HOME`，執行 `python3 ~/.claude/scripts/read_maintenance_checkpoint.py`，只讀最近一次 daily checkpoint 與其後的 follow-up；已解決事項視為已關閉。Reader 只在 Claude memory 不存在時使用 Codex mirror；格式錯誤或讀取失敗必須回報，不能視為空盤點。歷史保留在原檔，舊 header 的排程與版本描述不代表現況。
2. 對 Claude Code、Codex、Homebrew、Node/npm/Corepack/pnpm、Bun、gh、Mole、mise、uv tools、rustup/rustc/cargo 記錄實際 `command -v` 與版本。Node 工具鏈以解析到的 binary 為準，不只相信版本字串。
3. 用有界的 DNS／HTTPS probe 檢查本次需要的官方 registry。probe 失敗時仍做本機 health/version 檢查，但跳過依賴該網路的更新，不進入反覆 reconnect。

Completion gate: build one in-memory inventory from the named tool families and the installed user-scope package/marketplace lists. Each item has a stable name, resolved executable or package location, installation owner, installed version, official stable target, update route, eligibility, and verification result. Reconcile the inventory with the prior checkpoint; account for additions, removals, fixed pins and independently managed copies. A successful empty query means no items; a failed query means unknown coverage, never current. Cache freshness and probe failures must remain visible.

Read the current `~/.local/state/setup-hygiene/state.md` and accept every open finding owned by this updater. Revalidate its evidence before acting; record a disposition and discharge condition for each accepted key in the maintenance checkpoint. Leave structural repairs and scheduler ownership with Setup Hygiene. The two jobs can run concurrently: consume the latest completed checkpoint with its timestamp, and pick up newer findings on the next run.

### 2. 更新 Claude 與 marketplaces

1. 先判斷 Claude Code 安裝型態。native install 且自動更新健康時記錄狀態；只有官方更新路徑支援且需要時才執行，最後跑 `claude doctor`。
2. 從 Claude 設定／官方 list 指令取得目前 marketplaces 與 user-scope plugins，不在本文快取名稱或版本。逐一用官方 marketplace update 指令刷新；project-scope、bundled、primary-runtime、curated 與 App-managed 項目保持原狀，除非它們提供明確的 user-level 更新介面。
3. 刷新 Codex 官方支援的 Git marketplaces。保留 runtime／App 管理的 cache，不直接修改 `~/.claude/plugins/cache/` 或 `~/.codex/plugins/cache/`。
4. **Matt 分支**：完整讀取同目錄的 `MATT-SYNC.md`，依其中 fast path 或 delta path 同步 `~/.agents/skills` 的 Matt 副本。

完成條件：每個已設定 marketplace 都有刷新結果；plugin scope 與 enabled state 未被意外改變；Matt 完成其分支的驗證門檻。

### 3. 更新 MCP 與專用工具

1. MCP 採 **config-only** 稽核：讀既有 user-level 設定與套件 registry metadata。浮動版本只確認可解析；固定版本缺乏 migration 證據時保持不變。
2. MCP 稽核不建立連線，不執行 `claude mcp list`、`codex mcp list` 或任何會做 health probe／啟動 stdio server 的命令。OAuth 狀態只沿用可信的既有狀態；Notion 與 Slack 已有使用者 standing approval，但 config-only daily run 不發起互動式 OAuth。缺少可信 session 時標為 `auth-skipped` 技術阻塞，不列為等待批准。
3. Code Review Graph 只用 `uv tool upgrade code-review-graph` 與 `code-review-graph --version`。Graphify／`graphifyy` 保持未安裝；CRG install、build、update、postprocess、watch、daemon、embed、server、schema、graph DB 與 repo hooks 保持不變。release notes 要求 installer 或 schema migration 時列入需要人工。

完成條件：每個 MCP／專用工具都標為 current、updated、fixed-and-held、auth-skipped 或 failed；MCP 稽核本身沒有啟動 server，且沒有專案 graph 寫入。

### 4. 更新共用 CLI 與 runtimes

1. 先讀套件管理器的 outdated／dry-run 結果，再建立精確 target list。Homebrew untrusted-tap 保護保持啟用。
2. 自動更新已安裝工具的安全線：
   - CLI、libraries 與有版本名稱的 runtime formula：允許同一 major 內的 patch／minor。
   - NVM default Node：允許同一 major 內的 patch／minor；搬移相同的 global package 名稱，驗證後才切換 default，舊 Node 暫留供 rollback／`.nvmrc`。
   - npm/pnpm/Bun globals 與 uv tools：允許同一 major 內的正常更新；保留既有安全政策與 install-script allowlist。
   - gh、Mole、mise、rustup 與其他已安裝 CLI：只走官方 package manager 或 self-updater。
3. **Standing approval**：`anomalyco/tap/opencode`、`steipete/tap/codexbar`、gcloud CLI、McBopomofo 與 Orca app cask 的官方更新已獲使用者長期授權，可包含 major／GUI／這兩個既有第三方來源。每次仍先確認安裝來源、簽章與精確 transaction，再用官方 package manager 或 updater 執行；Orca 僅限 app cask，排程設定不在此授權內。Codex 未來若提供受支援的 rollout repair，也已獲授權在備份與 dry-run 可用時執行並觀察驗證，不直接修改資料庫。
   - McBopomofo 以 `~/Library/Input Methods/McBopomofo.app` 的實際 bundle version 為權威；實際版本已符合 cask 時，把落後 receipt 視為 current，不為對齊 receipt 重跑 installer。需要更新時先驗證下載與內嵌 payload 的版本／簽章，觀察 installer 的完成畫面後再讀回實際 bundle；若 installer 落盤版本低於已驗證 payload，保留可復原舊副本並用該 payload staged replacement，最後驗證執行中程序版本。
4. 技術阻塞線：sudo、互動登入、缺少受支援 updater／repair、簽章或來源改變、破壞性 reset，以及會中斷本次宿主而無法留下驗證的更新。這些項目標明缺少的執行條件與重試觸發，不列為等待使用者批准。其他未列入 standing approval 的 major 版本、unversioned runtime 跨 major、FFmpeg 跨 major、GUI casks、macOS、Xcode、Simulator runtimes 與不可信來源仍維持人工遷移線。
5. Codex installation ownership and update:
   - Resolve `command -v codex` through all symlinks and compare its actual version with the official stable release. For a standalone binary under `<owner-home>/packages/standalone/releases/<release>/bin/codex`, verify that `<owner-home>/packages/standalone/current/bin/codex` resolves to that binary. Derive the owner home from this verified layout; account IDs are runtime data.
   - Run the official updater with the installation owner home scoped to that command: `env CODEX_HOME="<owner-home>" "<visible-codex-path>" update`. Keep the session's global environment, account selection, config, credentials and databases unchanged. The default `~/.codex` may differ from the Orca account home that owns the executable.
   - If installation detection fails, compare the effective home with the verified owner home. A corrected owner home permits one bounded retry; an error under the wrong home does not establish that standalone updates are unsupported. If the correctly scoped updater still fails, record the exact error and the installed/latest versions, resolved executable, owner home and update route as the retry key.
   - After updating, resolve the visible command again and verify its version and the owner home's `current` target against the official stable release. Run `codex doctor --summary` with the same owner home. For a model-availability repair, also query `model/list` from a fresh app-server under that home and distinguish catalog availability from a successful inference. Existing processes may continue running the old executable; retain releases used by active sessions.
   - Mark Codex current only when the installed version matches the verified stable release. When it remains behind, report the unresolved update prominently on every run; deduplicate troubleshooting details rather than the outstanding version gap.

Completion gate: every inventoried item has exactly one outcome: `updated`, `current`, `held`, `blocked`, or `failed`. Use `current` only after a successful fresh version comparison; `held` requires a named policy/pin, and `blocked` requires a missing technical condition. Every eligible item left behind needs the exact failed route and next executable recovery. Verify the executable users actually invoke and any separately managed copy being updated; updating Homebrew Python does not establish that uv Python was updated.

Choose verification by artifact type. For macOS App bundles, use the applicable App assessment; for standalone signed CLI code, verify the signature/expected publisher and use `codesign --verify --strict -vvvv -R=notarized --check-notarization <binary>` when notarization is the required gate. An App-only `spctl` message that code is valid but not an app is an inconclusive test of a CLI, not proof of corrupt signing. A plain `--check-notarization` without the `notarized` requirement does not establish that requirement passed. Follow [Apple's artifact-specific guidance](https://developer.apple.com/forums/thread/130560). Preserve an actual failed requirement as a blocker; use the verified official package-manager route only after all applicable gates pass. Keep Gatekeeper, quarantine, signatures and install-script protections intact.

Recovery is evidence-driven. Before carrying forward an unsupported-updater verdict for an outdated tool, check its current official update documentation and installation owner once per run. Correct a demonstrated path/home/metadata mismatch or use another officially documented route that preserves the existing owner. Retry only after that correction or changed evidence. Preserve trust, signature and authorization boundaries. If the running host prevents activation, report installed-versus-running versions and the exact independent maintenance step instead of claiming completion.

### 5. 驗證與寫回

For Codex diagnostics, scope `CODEX_HOME` to the exact home being measured and use an empty temporary working directory outside `$HOME` and product repositories. A doctor launched from `$HOME` can load `~/.codex/config.toml` as project configuration when the active home is Orca-managed, producing an ignored `notify` warning. Distinguish this invocation collision from invalid user configuration; preserve notification and hook trust settings. Report each home separately and remove the disposable directory after diagnostics.

For an npm update blocked by `EALLOWREMOTE` despite a registry-name/version request, inspect the exact stack and registry metadata first. The npm bundled-dependency path can misclassify the registry tarball. A permitted recovery is the official npm local-tarball installation route: download only the exact official registry artifact, verify its registry-provided integrity and Node engine constraints, dry-run the same global install, then install under the existing manager. Keep remote/script policy unchanged, verify global package names and the invoked npm version, and remove the downloaded artifact after success. Failed integrity or an unpermitted local-file policy remains blocked.

1. 重跑所有已更新工具的版本／官方 health check。Homebrew 更新後檢查 `brew missing`；formula 更新執行相應 linkage 或直接 runtime check。避免任何會啟動 MCP server 的 health/list 指令。
2. 對照基線，確認實際版本、binary path、global package 名稱集合與重要 enabled state；不以安裝命令 exit 0 取代驗證。
3. Append the same compact timestamp checkpoint to `~/.claude/automations/daily-dev-update/memory.md` and `~/.codex/automations/automation/memory.md`. Include inventory/outcome counts, unmeasured coverage, version deltas, verification, every unresolved updater-owned Hygiene key, durable decisions and exact retry conditions. Check by code that inventory totals equal outcome totals and that both new checkpoint sections match. Full narrative belongs in Orca run history. If either memory exceeds 100,000 bytes or 400 lines, report the excess and identify the durable decisions/open keys to retain before a separately scoped compaction; never silently drop history.
4. Memory 內一律以 `$HOME` 或 `~` 表示家目錄，並在寫後檢查本次新增段落沒有絕對家目錄或秘密。

完成條件：每個變更都有驗證證據；兩份 checkpoint 等價且精簡；所有未完成項目都有明確原因與下次觸發條件。

## 最終報告

用繁體中文輸出可獨立閱讀的報告：

Lead with whether every eligible update was verified or the run completed with unresolved updates. List unresolved eligible updates and unmeasured coverage before successes, including unchanged blockers. Report reconciled totals for all five outcomes and the timestamp of the consumed Hygiene checkpoint. Orca `completed` records run termination; it does not prove tool-update success.

- **已更新**：逐項 `舊版 → 新版`。
- **已是最新**：合併成一行。
- **跳過**：項目、原因、未來重試條件。
- **失敗**：錯誤重點與受影響範圍。
- **需要人工**：只列尚未取得 standing approval 的登入、授權或遷移決策；已獲批准但缺少技術條件的項目列在「跳過」或「失敗」。
- **驗證**：列出實際執行的 health/linkage/runtime gates。

沒有項目的區段寫「無」。最後一句確認 projectless 邊界與 memory 寫回結果；不要提議後續排程操作。
