---
name: implementation
description: 依核准 plan 實作 feature、修正 bug 或 refactor，控制修改範圍並更新測試。
---

# 受控實作

先遵守根目錄 AGENTS.md。

1. 先讀 Issue 與 plan，確認自己是被指派的 Builder 且持有唯一 Writer Lock。
2. Claude 為預設 Builder；Codex 修改 production 前必須有明確 `Codex is assigned as Builder` 指派。
3. 在隔離 working tree 的 feature branch 實作，禁止直接 push main。
4. 控制 scope，保留既有有效設定；新增或更新能重現問題的測試。
5. 執行 testing skill，將命令、結果、限制、commit SHA 寫進 PR。
6. 等待獨立 reviewer，逐項回應 findings。不得自行 merge；完成提交及交接後由人類釋放 Writer Lock。
