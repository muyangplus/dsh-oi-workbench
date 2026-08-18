---
description: OI Workbench 通用指令入口（/oiwb 的别名）
---

同 `/oiwb`：OI Workbench 通用入口。

默认启动 HOJ 外部管理 UI：

1. 定位 `dsh-oi-workbench` 插件目录（通常在 DSH profile 的 `node_modules/dsh-oi-workbench` 下）。
2. 运行：
   ```bash
   python <插件目录>/skills/oi-workbench/ui/hoj_ui.py --host 0.0.0.0 --port 6163 --base https://hoj.example.com
   ```
3. 告诉用户访问 `http://localhost:6163/`。
