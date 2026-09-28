# 架構

本專案是 Python 3.10+ YouTube 字幕知識庫，非 Node／Web framework 專案。
`build_knowledge_base.py` 使用標準函式庫與 `yt_dlp`；README 另列選用 ffmpeg。既有專案沒有 package manager manifest、測試或 CI。
資料流：YouTube → yt-dlp → 分類／字幕清理 → `字幕/` 與 `AI_Agent_影片清單.md`。
正式腳本維持原位，`src/` 僅保留未來模組化入口。

治理流：Issue → advisory Router → 唯一 Writer → feature branch → PR → 獨立 Review → Actions → Human Approval → Human Merge。
Router 不會啟動 Agent、不會管理 credentials，也不是五 Agent orchestrator。

信任邊界：Agent 本地工具權限由各 runtime 控制；GitHub credentials 由管理者發放；main 由 ruleset／branch protection 控制。
CI 使用 GitHub hosted runner、唯讀 token、固定 action SHA、不帶 repo secrets；PR body 以 JSON 讀取，不能插入 shell。
Agent Quality Gate 與 CI 各自產生 required status，避免彼此等待與陳舊 workflow_run 判斷。

已知風險：正式腳本使用 `nocheckcertificate=True` 且部分外部下載例外僅列印。離線測試不代表 YouTube 線上服務、認證或 TLS 安全已驗證。修正另開 production Issue。
本地未追蹤旅遊資料與其他 Skills 不屬於此次 PR，也不會被複製到隔離 worktree。
