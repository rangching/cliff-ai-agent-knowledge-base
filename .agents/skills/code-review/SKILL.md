---
name: code-review
description: 審查 PR 或 Diff 的 regression、錯誤處理、可維護性、API 相容性與 edge cases。
---

# 獨立程式審查

先遵守根目錄 AGENTS.md。

1. 讀 Issue、plan、PR diff 及 base/head SHA；先確認未參與該 PR 實作。
2. 追蹤資料流與呼叫端，檢查 regression、錯誤處理、maintainability、API compatibility、edge cases。
3. 在自己的 worktree 執行測試；診斷不等於取得 production edit 權限。
4. 每個 finding 附嚴重程度、檔案行號、具體觸發條件、影響與建議；避免無證據的猜測。
5. 有實質阻擋問題時回傳 changes_requested；無問題也需說明範圍與未驗證項目。
6. 在 PR 留存 review report，綁定 head SHA。自己做過修正就不再是該 PR 獨立 reviewer；merge 留給人類。
