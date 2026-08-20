---
description: OI Workbench 通用指令入口（当前支持 HOJ 外部管理 UI）
---

OI Workbench 通用入口。

子命令：
- `/oiwb panel` 或 `/hoj`：启动 HOJ 外部管理 UI
- `/oiwb hoj problems`：列出 HOJ 题目
- `/oiwb hoj contests`：列出 HOJ 比赛
- `/oiwb hoj publish <题目目录>`：发布题目到 HOJ
- `/oiwb hoj rejudge <submitId>`：重判提交
- `/oiwb kb list|show|search|add|add-file|edit|rm|validate`：用户自定义知识库（见 commands/kb.md）
- `/oiwb ref list|show|add|rm|validate`：用户自定义参考题（见 commands/kb.md）

如果用户输入 `/oiwb` 或 `/oj` 且没有子命令，默认启动 HOJ 外部管理 UI：

1. 定位 `dsh-oi-workbench` 插件目录（通常在 DSH profile 的 `node_modules/dsh-oi-workbench` 下）。
2. 运行：
   ```bash
   python <插件目录>/skills/oi-workbench/ui/hoj_ui.py --host 0.0.0.0 --port 6163 --base https://hoj.example.com
   ```
3. 告诉用户访问 `http://localhost:6163/`。
