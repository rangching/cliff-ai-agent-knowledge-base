"""僅驗證可可靠判定的 PR metadata；實際 review、CI 與 merge 由 ruleset 管理。"""
import json
import os
import re
import urllib.request
from pathlib import Path


def validate(pr):
    errors = []
    body = re.sub(r"<!--.*?-->", "", pr.get("body") or "", flags=re.S)
    # 範本限定同 repo、獨立一行的 Issue 關聯，避免從任意文字猜測。
    issues = re.findall(r"(?im)^(?:closes|fixes|resolves) #([1-9][0-9]*)\s*$", body)
    if not issues:
        errors.append("Related Issue 需填 Closes #123（同 repository Issue）")
    roles = {}
    for key in ("Builder", "Reviewer"):
        values = re.findall(rf"(?im)^{key}:\s*(claude|codex|antigravity|opencode|human:[a-z0-9][a-z0-9-]*)\s*$", body)
        if len(values) != 1:
            errors.append(f"{key} 必須且只能填一個有效角色")
        else:
            roles[key] = values[0].lower()
    if roles.get("Builder") and roles.get("Builder") == roles.get("Reviewer"):
        errors.append("Builder 與 Reviewer 不得相同")
    match = re.search(r"(?im)^## Security Impact\s*\n(.*?)(?=^## |\Z)", body, re.S | re.M)
    impact = match.group(1).strip() if match else ""
    if not impact or impact.lower() in {"n/a", "none", "tbd", "todo"} or impact.startswith(("<", "填具體")):
        errors.append("Security Impact 必須填具體影響或無影響的原因")
    if pr["head"]["ref"] == "main":
        errors.append("請使用 feature branch，不可用 main 作為工作分支")
    return errors, sorted(set(issues))


def main():
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    pr = event["pull_request"]
    errors, issues = validate(pr)
    repo = os.environ["GITHUB_REPOSITORY"]
    for number in issues:
        request = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/issues/{number}",
            headers={"Authorization": "Bearer " + os.environ["GH_TOKEN"],
                     "Accept": "application/vnd.github+json"})
        # API 或網路失敗直接 fail closed；不把 token 印到 log。
        with urllib.request.urlopen(request, timeout=30) as response:
            issue = json.load(response)
        if "pull_request" in issue:
            errors.append(f"#{number} 是 PR，必須關聯 Issue")
    if errors:
        raise SystemExit("\n".join(errors))
    print("Metadata 與 Issue 已驗證；仍須 ci-required、獨立 review 與人類核准。")


if __name__ == "__main__":
    main()
