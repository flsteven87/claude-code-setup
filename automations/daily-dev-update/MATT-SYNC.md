# Matt skills 同步分支

只在每日更新準備刷新 `mattpocock` marketplace 時讀取本文件。目標是讓上游管理副本跟進官方內容，同時保護本機 handoff 與任何真正的 local delta。

## 1. 更新前快照

1. 記錄 marketplace clone 的 `old_head`，並從該 commit 的官方 manifest 取得 `old_managed = upstream skills - ./skills/productivity/handoff`。
2. 對每個 `old_managed` 名稱，把 `~/.agents/skills/<name>` 與 `old_head` 中對應目錄比較。分類為 `matches_old`、`local_delta` 或 `missing`；不要用目前工作樹推測舊上游內容。
3. 記錄自持 manifest 的 version、skills 清單與 symlink target。

完成條件：每個舊受管名稱只有一個分類；本機自訂 skill 不在受管集合內。

## 2. 刷新並選路徑

用 Claude 官方 marketplace update 指令刷新，取得 `new_head` 與新官方 manifest；計算 `desired = upstream skills - ./skills/productivity/handoff`。

- **Fast path**：`old_head == new_head` 且官方 manifest／`desired` 未變。跳過逐檔同步與語意掃描，直接進入驗證。
- **Delta path**：HEAD、manifest 或 `desired` 任一改變。執行下一節後再驗證。

完成條件：使用 HEAD 與 manifest 的實際差異選路徑，不靠日期或版本猜測。

## 3. Delta path

1. `matches_old` 且仍在 `desired`：以 `new_head` 的官方目錄更新 `~/.agents/skills/<name>`。
2. `local_delta` 且仍在 `desired`：保留原狀，列入需要人工並附最小 diff 來源。
3. 新增至 `desired` 的名稱：安裝官方副本。
4. 從 `desired` 移除或改名的舊名稱：只有 `matches_old` 才移除；`local_delta` 保留並列入需要人工。
5. 只對 `old_head..new_head` 的相關 skill、README、rules、references 做語意差異稽核。聚焦 `disable-model-invocation`、commit、publish、external-write 與 completion contract；語意改變只回報，不改寫本機 policy、adapter 或自訂 skill。

完成條件：每個新增、保留、更新、移除的受管名稱都能由 old/new manifest 與 ownership 分類解釋；非 Matt skill 未改變。

## 4. 共通驗證

1. 執行 `uv run python ~/.claude/scripts/reconcile_matt_manifest.py --write --runtime`。這是自持 manifest 的唯一寫入路徑；不手動拼接 manifest，也不修改 symlink 指向的上游內容。
2. 執行 Claude plugin validation。確認 symlink、每個 `SKILL.md`、shadowing plugin、runtime inventory 與 `Matt-managed subset == desired`。
3. 若本次 delta 涉及 ship、handoff 或其 contract references，再驗證唯一 canonical ship 是 `~/.agents/skills/ship/SKILL.md`，Claude `/ship` 是薄 adapter，兩個 handoff 都只寫 primary checkout 的 root `MEMORY.md`。未涉及時沿用最近已通過的 checkpoint，不做全域語意重掃。

完成條件：reconcile 與 plugin validation 都通過；任何保留的 local delta 都出現在報告與 memory retry key 中。
