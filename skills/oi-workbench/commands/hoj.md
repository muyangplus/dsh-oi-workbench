# HOJ 斜杠指令

`oi-workbench` 使用**通用根指令 `/oiwb`（别名 `/oj`）**，HOJ 作为子命令。

> 系统级注册：插件通过 `cordis.patch.yml` 让 `@etby-studio/dsh-commands`（MIT）直接扫描
> `commands/register/`，安装后自动注册 `/hoj`、`/oiwb`、`/oj` 三个系统斜杠命令，无需手动复制。

## 通用指令

| 指令 | 说明 |
|---|---|
| `/oiwb` 或 `/oj` | 打开默认管理面板 |
| `/oiwb panel` | 启动 Python 外部 UI：`python ui/hoj_ui.py --host 0.0.0.0 --port 6163 --base <HOJ地址>` |
| `/oiwb hoj problems` | 列出 HOJ 题目 |
| `/oiwb hoj contests` | 列出 HOJ 比赛 |
| `/oiwb hoj publish <题目目录>` | 发布题目到 HOJ |
| `/oiwb hoj rejudge <submitId>` | 重判指定提交 |

## 兼容别名

| 指令 | 说明 |
|---|---|
| `/hoj` 或 `/hoj-panel` | `/oiwb panel` 的别名 |
| `/hoj help` | 显示 HOJ 指令列表 |
| `/hoj problems` | `/oiwb hoj problems` 的别名 |
| `/hoj contests` | `/oiwb hoj contests` 的别名 |
| `/hoj publish <题目目录>` | `/oiwb hoj publish` 的别名 |
| `/hoj rejudge <submitId>` | `/oiwb hoj rejudge` 的别名 |

## 外部 UI 启动

```bash
python ui/hoj_ui.py --host 0.0.0.0 --port 6163 --base https://hoj.example.com
# 浏览器打开 http://localhost:6163/
```

## 执行映射

```bash
python hoj-bridge/manage_hoj.py problem-list --base ... --user ... --password ...
python hoj-bridge/manage_hoj.py contest-list ...
python hoj-bridge/publish_problem.py --problem-dir <题目目录> ...
python hoj-bridge/manage_hoj.py judge-rejudge --submit-id <submitId> ...
```

> 凭据优先使用环境变量 `HOJ_PASSWORD` 或 `--cookie`，不要把密码写进聊天记录。
> 后续新增 Hydro 时，可继续扩展 `/oiwb hydro ...`，不会影响 `/hoj` 兼容用法。
