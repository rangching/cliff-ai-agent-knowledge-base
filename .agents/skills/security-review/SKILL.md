---
name: security-review
description: 涉及 Authentication、Authorization、Secrets、Encryption、Network、Permissions、Database、File upload、External API 或 Infrastructure 時使用。
---

# 安全性審查

先遵守根目錄 AGENTS.md。

1. 讀 scope、diff 與資料流，確認 trust boundary、使用者身分、權限及敏感資料保存位置。
2. 檢查認證、授權、secret handling、加密、TLS、網路輸入、資料庫與檔案路徑／上傳驗證。
3. CI／infrastructure 變更檢查 token 最小權限、第三方 action 固定 SHA、事件來源、未受信任輸入及 secrets 暴露。
4. 不可在 privileged workflow checkout 或執行 PR 不受信任程式；禁止將 PR body 插入 shell。
5. 將可重現 findings、嚴重程度、影響、修正與殘餘風險寫進 PR Security Impact；敏感證據使用核准私有管道。
6. 本 repo 原有 `nocheckcertificate=True` 是已知風險，本次未修改；後續 production 修正由 Claude 持鎖並另開 Issue/PR。
