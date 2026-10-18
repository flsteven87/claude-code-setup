# Matt skills 同步分支

只在每日更新同步 Matt Pocock skills 時讀取本文件。`~/.agents/skills` 是唯一副本：Codex 直接讀取，Claude 透過 `~/.claude/setup.sh` 建立的連結讀取。目標是讓這些副本跟進官方內容，同時保護本機 handoff 與任何真正的 local delta。

## 1. 取得基線與上游

1. `old_head`：`~/.agents` 最近一個 `chore(skills): sync Matt skills to upstream <sha>` commit 記載的 upstream SHA。
2. 把 `https://github.com/mattpocock/skills` 淺層 clone 到暫存目錄（深度足以包含 `old_head`），取得 `new_head`。官方 manifest 是 `.claude-plugin/plugin.json` 的 `skills`；`managed = manifest skills - ./skills/productivity/handoff`，分別在 `old_head` 與 `new_head` 計算。
3. 對每個 `old_managed` 名稱，把 `~/.agents/skills/<name>`（忽略本機 `agents/openai.yaml`）與 `old_head` 的對應目錄比較，分類為 `matches_old`、`local_delta` 或 `missing`。

完成條件：每個舊受管名稱只有一個分類；本機自訂 skill 不在受管集合內。

## 2. 選路徑

- **Fast path**：`old_head == new_head`。跳過逐檔同步與語意掃描，直接進入驗證。
- **Delta path**：HEAD 改變。執行下一節後再驗證。

## 3. Delta path

1. `matches_old` 且仍在 `new_managed`：以 `new_head` 的官方目錄更新 `~/.agents/skills/<name>`，保留本機 `agents/openai.yaml`。
2. `local_delta` 且仍在 `new_managed`：只把 `old_head..new_head` 的上游差異套到本機副本，保留 local delta；衝突時保留原狀，列入需要人工並附最小 diff 來源。
3. 新增至 `new_managed` 的名稱：安裝官方副本，並依 `disable-model-invocation` 建立對應的 `agents/openai.yaml`。
4. 從 `new_managed` 移除或改名的舊名稱：只有 `matches_old` 才移除；`local_delta` 保留並列入需要人工。
5. 只對 `old_head..new_head` 的相關 skill、README、rules、references 做語意差異稽核。聚焦 `disable-model-invocation`、commit、publish、external-write 與 completion contract；語意改變只回報，不改寫本機 policy、adapter 或自訂 skill。
6. 在 `~/.agents` 落一個只含 Matt 受管目錄的 commit：`chore(skills): sync Matt skills to upstream <new_head 短 SHA>`。

完成條件：每個新增、保留、更新、移除的受管名稱都能由 old/new manifest 與 ownership 分類解釋；非 Matt skill 未改變。

## 4. 共通驗證

1. 執行 `bash ~/.claude/setup.sh`，確認每個 `~/.agents/skills` 名稱都有 Claude 連結、沒有懸空連結。
2. 對變更的 skill 跑 `skill-creator` 的 `quick_validate.py`；上游原有的 Claude 專屬 frontmatter 鍵不算新失敗。
3. 若本次 delta 涉及 ship、handoff 或其 contract references，再驗證唯一 canonical ship 是 `~/.agents/skills/ship/SKILL.md`，Claude `/ship` 是薄 adapter，兩個 handoff 都只寫 primary checkout 的 root `MEMORY.md`。未涉及時沿用最近已通過的 checkpoint，不做全域語意重掃。

完成條件：連結與驗證都通過；任何保留的 local delta 都出現在報告與 memory retry key 中。
