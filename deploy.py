#!/usr/bin/env python3
"""把 worker.js 部署到 Cloudflare Workers（供 GitHub Action 调用）。

需要的环境变量（来自仓库 Secrets）：
  CF_API_TOKEN  - Cloudflare API Token（需 Workers Scripts 写权限）
  CF_ACCOUNT_ID - Cloudflare 账户 ID
  WORKER_UUID   - 订阅访问 UUID，写入 Worker 环境变量 u
"""
import io
import json
import os
import sys
import urllib.request
import urllib.error
import uuid as uuidlib

SCRIPT_NAME = "cfnew"
COMPAT_DATE = "2026-01-20"


def main() -> int:
    try:
        token = os.environ["CF_API_TOKEN"]
        account = os.environ["CF_ACCOUNT_ID"]
        worker_uuid = os.environ["WORKER_UUID"]
    except KeyError as exc:
        print(f"缺少环境变量: {exc}", file=sys.stderr)
        return 2

    with open("worker.js", "r", encoding="utf-8") as fh:
        code = fh.read()
    if len(code) < 100_000 or "export default" not in code:
        print("worker.js 校验未通过（体积过小或缺少入口），拒绝部署", file=sys.stderr)
        return 2

    boundary = "----cfdeploy" + uuidlib.uuid4().hex
    metadata = {
        "main_module": "worker.js",
        "compatibility_date": COMPAT_DATE,
        "bindings": [{"type": "plain_text", "name": "u", "text": worker_uuid}],
    }
    buf = io.BytesIO()

    def field(name: str, value: str) -> None:
        buf.write(f"--{boundary}\r\n".encode())
        buf.write(f'Content-Disposition: form-data; name="{name}"\r\n'.encode())
        buf.write(b"Content-Type: application/json\r\n\r\n")
        buf.write(value.encode("utf-8"))
        buf.write(b"\r\n")

    def filefield(name: str, filename: str, content: str) -> None:
        buf.write(f"--{boundary}\r\n".encode())
        buf.write(
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode()
        )
        buf.write(b"Content-Type: application/javascript+module\r\n\r\n")
        buf.write(content.encode("utf-8"))
        buf.write(b"\r\n")

    field("metadata", json.dumps(metadata))
    filefield("worker.js", "worker.js", code)
    buf.write(f"--{boundary}--\r\n".encode())

    url = f"https://api.cloudflare.com/client/v4/accounts/{account}/workers/scripts/{SCRIPT_NAME}"
    req = urllib.request.Request(url, data=buf.getvalue(), method="PUT")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", "replace")
        print(f"部署失败 HTTP {exc.code}: {err[:500]}", file=sys.stderr)
        return 1
    if not data.get("success"):
        print(f"部署失败: {json.dumps(data)[:500]}", file=sys.stderr)
        return 1
    print("部署成功 deployment_id:", data["result"].get("deployment_id"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
