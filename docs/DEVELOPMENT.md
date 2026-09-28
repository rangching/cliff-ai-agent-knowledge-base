# 開發與驗證

## 環境與命令
使用 Python 3.10 或 3.12、venv 與 pip；沒有 Node package manager。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-ci.txt
.venv/bin/ruff check .
.venv/bin/python -m compileall -q build_knowledge_base.py scripts tests
.venv/bin/python scripts/check_stack.py
.venv/bin/python -m unittest discover -s tests -v
```

CI 相依版本固定，yt-dlp 版本用於可重現離線測試；上線抓取前以獨立 PR 評估升級，不在 CI 每次安裝最新版。正式抓取有網路與檔案副作用，測試不得執行 `main()`。
Lint 採 E9/F63/F7/F82 的基本正確性檢查；unit tests 驗證檔名與集數；integration tests 使用暫存 VTT 與 mocked yt-dlp，無 YouTube 請求。
Type check：N/A，既有程式沒有型別標註或 mypy 設定。Build：N/A，沒有發行套件；compileall 只驗證編譯，不宣稱產品 build 完成。
GitHub Actions 的 `ci-required` 聚合 Python 3.10／3.12，失敗或取消不能通過。

## Branch / Worktree Isolation

```text
main
worktree/
├── claude/       feature branch，持鎖才寫入
├── codex/        review branch／detached head，診斷
├── antigravity/  sandbox branch，prototype 也需持鎖
└── opencode/     private/local branch，持鎖才寫入
```

禁止多 Agent 修改同一 working tree。VS Code 分別開啟 worktree，用 Terminal 執行驗證、Source Control 檢視 Diff、GitHub PR 檢視審查與 Actions。
使用不同 branch、git worktree 或 clone；在 Codex 優先使用內建 managed worktree。
隔離不等於取得 Writer 權限；本 repo 僅允許一位 Writer，其他環境只能讀取與診斷。
不要把私密程式或本機憑證放進公開 repo、CI artifact 或雲端 Agent。

## 必須由 GitHub 管理者設定
目前導入時 main 未受保護；本 PR 不自動修改帳號／組織存取政策。
在 Settings → Rules → Rulesets 或 Branches 保護 `main`：

- Require a pull request before merging；禁止一般直接 push。
- 至少 1 位獨立人類 approval；dismiss stale approvals，require approval of most recent reviewable push，resolve conversations。
- Require status checks：`ci-required` 與 `agent-metadata`；第一次 Actions 跑完後選擇 GitHub Actions 來源，require branch up to date。
- 禁止 force push 與刪除；規則套用管理員，不給 Agent bypass。
- 僅人類 merge；關閉 auto-merge。Agent 使用獨立 credentials，禁止使用可 bypass 的管理員 token。
- GitHub 同一個 write token 常同時能 push 與 merge，無法只靠 AGENTS.md 精確阻擋。若需硬性限制，使用可審計的 GitHub App／代理服務，只開 feature push、禁 merge endpoint，再配合 ruleset。
- 人類帳號也可能被 Agent 共用；GitHub approval 本身不能證明操作的是人類。必須分離人類／Agent 身分並由人類實際操作最後批准與合併。

`agent-metadata` 只檢查指派文字、有效 Issue、工作分支及 Security Impact；不把 Reviewer 欄當成真實 review。
CI 是否成功交給另一個 required check；直接 push 必須事前由 GitHub 拒絕，事後 workflow 無法撤銷 push。
PR 更新 body 會重跑 metadata；commit 更新會重跑全部。Gate 的程式本身也在 PR 內，須人工特別審查 `.github/`、`scripts/`、AGENTS 與相依設定，不能把它當不可篡改的安全邊界。
可額外配置組織層 required workflow 與真實人類 CODEOWNERS；不要填不存在的 team／帳號。

官方參考：[Branch protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)、[Actions security](https://docs.github.com/en/actions/reference/security/secure-use)。
