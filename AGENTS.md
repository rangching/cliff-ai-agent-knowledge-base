# Repository Agent 規範

所有回覆、文件與操作說明預設使用台灣繁體中文；程式碼與精確名稱保留原文。
此文件是 repo 共用最高層級規範，工具個別設定不得放寬以下限制。

## Source of Truth
GitHub is the single source of truth. 使用 Issue、PR、Commit、Diff、Review comment、Test report、Artifact 與 Markdown 交接，不依賴聊天記憶。私密內容只保存於核准的私有儲存區；GitHub 僅留去識別摘要與參照。

## Branch Rules
- Never push directly to main. Every code change must use a branch.
- Every production change must go through Pull Request.
- Agent 不得 merge 自己建立或修改的 PR；所有 merge 由人類核准並執行。

## Role Assignment
| 工具 | 角色 | 權限與邊界 |
| --- | --- | --- |
| Claude Code | Primary Builder | Read、Edit、Shell、Tests、Commit、Push feature branch；依 plan 實作及修正 review |
| Codex | Reviewer / Debugger | Read、Tests、診斷 Shell、Diff／Regression／Security review；production edit 預設禁止 |
| Antigravity | Research / Google Specialist | Google、Gemini、Cloud、Firebase、Android 查證及隔離 sandbox prototype；不得修改 production branch |
| OpenCode | Local / Private Worker | 本地模型、私密、離線、低成本、文件與低風險任務；取得 Writer Lock 後才可寫入 |
| VS Code | Cockpit | IDE、Terminal、Git、worktree、PR 與 CI 操作入口 |
| GitHub | Single Source of Truth | 正式紀錄與 Agent 訊息交換 |
| GitHub Actions | Deterministic Quality Gate | 實際執行測試與檢查 |

只有人類明確指定 `Codex is assigned as Builder` 並記錄於 Issue 後，Codex 才能修改 production code；該任務必須交由另一位獨立 reviewer。此次治理建置授權涵蓋規範、CI 與測試，不改正式 Python 腳本。

## Writer Lock
At any time, only one agent may have Writer permission for a task or branch.
本 repo 初期採更保守的一次一位 Writer，其餘 Agent 僅讀取或執行隔離診斷。
人類在 Issue 記錄 writer、branch、scope、UTC 開始時間與狀態；先確認舊 writer 已停止、提交並交接，再釋放與指派。
逾時不能自動搶鎖。研究 prototype 及 OpenCode patch 也是寫入，必須取得鎖。
各 Agent 使用不同 working tree；細節見 [流程](docs/MULTI_AGENT_WORKFLOW.md)。

## Required Workflow
1. Understand issue
2. Produce plan（assumptions、scope、risk、acceptance criteria）
3. Create branch，取得 Writer Lock
4. Implement
5. Run tests，保留失敗與成功紀錄
6. Open PR
7. Independent reviewer reviews
8. Resolve findings
9. CI passes（GitHub Actions 實際結果；AI 自述不算）
10. Human approves
11. Human merges

## Skills
- 需求與計畫 → [planning](.agents/skills/planning/SKILL.md)
- Feature implementation → [implementation](.agents/skills/implementation/SKILL.md)
- PR review → [code-review](.agents/skills/code-review/SKILL.md)
- Auth/security/network changes → [security-review](.agents/skills/security-review/SKILL.md)
- Test validation → [testing](.agents/skills/testing/SKILL.md)

## Safety
Never：直接 push main、暴露 secrets、停用測試讓 CI 變綠、默默忽略失敗、重寫無關程式、merge 自己的 PR、在未授權 scope 修改 infrastructure。
Router 與本文件是協定，不是作業系統或 GitHub 權限隔離。不得假稱已自動執行鎖定、路由或人工核准；實際強制措施見 DEVELOPMENT.md。
