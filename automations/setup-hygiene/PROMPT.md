# 使用者層級 Setup Hygiene

完整讀取並遵循 `$HOME/.agents/skills/setup-hygiene/SKILL.md`，執行一次 projectless setup
integrity 巡檢。Skill 定義方法與可自動修復範圍；本文件只定義定期 job 的執行契約。

## 執行契約

- 從 `$HOME` 執行，使用 `$HOME/.local/state/setup-hygiene/state.md` 作為唯一狀態來源；缺少時
  建立精簡初始狀態。
- 以 live environment 與 skill 的唯讀 scan 為事實來源。檢查 coherence 與 sediment；版本、
  安裝、marketplace、plugin、MCP registry 與 runtime health 交回每日開發工具更新。
- 無人值守完成 scan、triage、skill 明定的 safe repairs、驗證、state replacement 與報告。
  其他項目使用 `review` 或 `handoff`，不等待輸入。
- 保密輸出；秘密只報變數名稱或來源類型。產品 repo、Orca workspace、專案狀態、Git 歷史、
  OAuth、permission policy、recovery records 與 macOS Trash 保持原 owner。
- 不建立、修改或輸出任何 scheduler registration、cadence change 或 automation directive。

## 完成輸出

用繁體中文輸出可獨立閱讀的報告。先給 setup integrity 結論，再列每個 surface 的實際盤點
數量、new/changed findings、safe repairs 與驗證、review/handoff、closed/open retry keys，以及
未進入的 ownership boundaries。Clean surfaces 合併為含數量的一行；沒有項目時明寫「無」。

最後確認 scan totals 已對帳、每個 finding 只有一個 verdict、state 已保持精簡，且本次沒有
執行 daily updater 的責任。
