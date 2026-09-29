# cfnew-private

cfnew Worker 的部署仓库。上游：https://github.com/byJoey/cfnew

## 文件说明

| 文件 | 说明 |
| --- | --- |
| `worker.js` | Worker 源码（上游明文版），部署的即是此文件 |
| `upstream.sha` | 上次同步的上游 commit，用于自动更新时比对 |
| `wrangler.toml` | 手动用 wrangler 部署时的配置模板（UUID 填占位符，真值勿提交） |
| `deploy.py` | 通过 Cloudflare API 部署的脚本（Action 调用） |
| `.github/workflows/auto-update.yml` | 每天 11:00（北京时间）检查上游更新，有新提交则同步并自动重新部署 |

## 需要手动添加的 Secrets

仓库 Settings → Secrets and variables → Actions → New repository secret：

| 名称 | 值来源 |
| --- | --- |
| `CF_API_TOKEN` | Cloudflare API Token（创建时保存的那一串；若丢失需重新创建一个） |
| `CF_ACCOUNT_ID` | Cloudflare 账户 ID（面板 URL 里也能看到） |
| `WORKER_UUID` | 订阅 UUID（部署时自行设定，不要提交到仓库） |

三个 Secrets 都填好后，自动更新才会真正生效（可先用 Actions 页的 workflow_dispatch 手动跑一次验证）。

## 当前线上状态

- Worker：`cfnew`，兼容日期 `2026-01-20`
- 域名：`v.lepoison.dev`（DNS A 记录 + Worker 路由已绑定）
- 订阅：`https://v.lepoison.dev/<UUID>/sub`（UUID 见 Secrets）
- 配置界面：`https://v.lepoison.dev/<UUID>`（UUID 见 Secrets）
