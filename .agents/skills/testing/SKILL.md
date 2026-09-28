---
name: testing
description: 驗證 unit/integration tests、lint、type check、build 或 GitHub Actions 結果時使用。
---

# 可驗證測試

先遵守根目錄 AGENTS.md。

1. 從 manifest、lockfile、CI 與 DEVELOPMENT.md 確認實際技術棧。
2. 執行 repo 適用的 unit、integration、lint、type check、build；不存在的階段明確標記 N/A 與理由。
3. 此 repo 執行 `python -m unittest discover -s tests -v`、`ruff check .`、`python -m compileall -q build_knowledge_base.py scripts tests` 及 `python scripts/check_stack.py`。
4. 外部 YouTube 抓取不是 deterministic test；使用 temp fixture 與 mock，不能在驗證中重建正式資料。
5. 記錄命令、環境、head SHA、exit code、失敗原因、GitHub run URL。不得關閉測試或隱藏錯誤。
6. 本地通過是預檢；只以最新 PR commit 的 GitHub Actions 成功與必要檢查判斷可合併。
