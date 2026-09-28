# 多 Agent 標準流程

```text
User / Issue → Router → Claude Code
                         Plan → Branch → Implement → Test
                                      ↓
                                 Pull Request
                                      ↓
                       Codex Review → Debug → Regression → Test
                                      ↓
                                GitHub Actions
                           FAIL → Claude 修正 → 重新 Review / CI
                           PASS → Human Approval → Human Merge
```

Google 工作：Issue → Antigravity Research → research.md／prototype → Claude implementation。
Local/private 工作：Issue（去識別摘要）→ OpenCode → artifact／patch／report（核准私有位置）→ 正式 Builder 整合。
Antigravity 交付 research.md 必含問題、官方來源 URL、查證日期、版本、實驗步驟、結果、限制與建議；prototype 放隔離 sandbox branch，不直接改 production branch。
OpenCode 使用本地模型前先核對 provider，避免把 private 任務傳至雲端。低風險 refactor 仍需 Writer Lock、PR 與 reviewer。

## Router 與 Labels
`.agents/router.yaml` 是 advisory 設定。Phase 1/2 由人類依它指派，不會因貼 label 就啟動 Agent。
Labels：`agent:claude`、`agent:codex`、`agent:antigravity`、`agent:opencode`；`task:feature`、`task:bug`、`task:review`、`task:research`、`task:security`；`risk:low`、`risk:medium`、`risk:high`。
`task:feature` → Claude；`task:review`／security／bug 診斷 → Codex；research／Google → Antigravity；private／offline → OpenCode。Bug 的正式修正仍交 Claude。
同時命中 private 與 Google 時，先由人類確認資料邊界；不得先送雲端再補授權。

## Writer Lock 與 Artifact 交接
人類在同一個 Issue 記錄：

```text
Writer: claude
Branch: feature/issue-123
Scope: 列出允許修改的檔案與目的
Started (UTC): 實際開始時間
Status: held / released
Last commit: 完整 SHA
Evidence: PR / review / CI run / artifact URL
Next owner: 明確指派，不能自行搶鎖
```

本期為人工序列化協定，GitHub comment 不具原子鎖定能力。所有待寫任務須先檢查 repo 有無 held lock。
前任停止寫入 → 提交並推送 feature branch → 留存 Diff、測試命令／結果、未解問題 → 人類確認釋放 → 指派新 writer。
鎖逾時、Agent 中斷、離線時由人類確認程序已停止後處理；沒有自動 timeout takeover。
Review report 需綁 head SHA、finding 行號／影響／重現方式、測試證據與結論。修正後重新 review，不用聊天中的「已修好」代替證據。
Codex 若被指派 Builder，由另一未參與實作的 reviewer 審查；不能自己證明獨立性。

## 三階段導入
| 階段 | 導入內容 | 驗收與邊界 |
| --- | --- | --- |
| Phase 1 | AGENTS、branch protection、Claude Builder、Codex Reviewer、PR template、基本 CI | 人類完成分支保護，首個 PR 真正跑完 CI 與獨立 review |
| Phase 2 | Skills、Router、Labels、Worktree、Security review、Agent Quality Gate | 本 PR 提供這些設定；以手動路由／Writer 交接運作，驗證失敗 metadata 會阻擋 |
| Phase 3 | Orchestrator、Issue 自動路由、自動 Review loop、Antigravity／OpenCode workers | 導入具原子性的集中 Writer lease、權限代理、審計、重試上限與成本限制後才啟用；仍保留人類批准與 merge |

下一階段不得把 advisory YAML 誤當 orchestrator。先分離 Agent 身分、落實 merge 禁令，再做有限重試的自動審查迴圈。私密資料不因導入自動路由而放寬處理範圍。
