# HOJ 外部管理 UI

Python 标准库实现的本地/局域网 Web 管理台，替代 DSH 内部 `render_ui`。

## 启动

```bash
python ui/hoj_ui.py --host 0.0.0.0 --port 6163 --base https://hoj.example.com
```

- 本机访问：`http://localhost:6163/`
- 手机/局域网访问：`http://<本机IP>:6163/`

## 文件

- `hoj_ui.py` —— HTTP 服务 + HOJ API 代理 + Cookie 持久化
- `hoj-admin.html` —— 管理页面

## 功能

- 登录、题目、比赛、用户/团队、评测管理
- 服务端保存 HOJ Cookie，刷新页面后保持登录
- 支持“记住登录”保存 Base URL / 用户名 / 密码 / Cookie 到浏览器 `localStorage`
- 配置和 Cookie 保存在 `~/.dsh-oi-workbench/`

## 依赖

- Python 仅使用标准库，无第三方 Python 包。
- 本 UI 是 `dsh-oi-workbench`（skill-first 插件）的组成部分。

## 安全

- 默认只监听 `127.0.0.1`；如需手机/局域网访问，使用 `--host 0.0.0.0`
- 密码不要写入聊天或仓库
- 公共网络下建议配合反向代理 / HTTPS 使用
