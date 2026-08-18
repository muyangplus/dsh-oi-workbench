---
description: 启动 HOJ 外部管理 UI（Python 服务，默认端口 6163）
---

启动 HOJ 外部管理 UI：

1. 定位 `dsh-oi-workbench` 插件目录（通常在 DSH profile 的 `node_modules/dsh-oi-workbench` 下）。
2. 运行：
   ```bash
   python <插件目录>/skills/oi-workbench/ui/hoj_ui.py --host 0.0.0.0 --port 6163 --base https://hoj.example.com
   ```
   如果用户提供了真实 HOJ 地址，用该地址替换 `https://hoj.example.com`。
3. 启动后告诉用户访问：
   - 本机：`http://localhost:6163/`
   - 手机/局域网：`http://<本机IP>:6163/`
4. 提示用户可以在页面中修改 HOJ 地址并点击“保存配置”。
