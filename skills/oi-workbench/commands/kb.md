# `/oiwb kb` 与 `/oiwb ref` — 用户自定义知识库 / 参考题

> 批次 1（v0.1.1）新增。规范见 `specs/user-content.md`，模板见 `templates/kb-card.md`。

这些子命令让用户自行增删改查自己的 **reference / knowledge-base**，数据存于
`~/.dsh-oi-workbench/`（`kb/` 与 `reference/`），不影响插件安装目录。

**执行方式**：在 DSH profile 的插件目录下运行
`python skills/oi-workbench/ui/user_content.py ...`（Python 标准库，无第三方依赖）。
定位插件目录：通常在 `<profile>/node_modules/dsh-oi-workbench` 下。

## `/oiwb kb ...`

| 子命令 | 说明 | 示例 |
|---|---|---|
| `/oiwb kb list` | 列出用户层知识库卡片 | `/oiwb kb list` |
| `/oiwb kb show <topic>` | 显示某卡片全文 | `/oiwb kb show 并查集` |
| `/oiwb kb search <关键字>` | 全文检索（用户层 + 内置） | `/oiwb kb search dp` |
| `/oiwb kb add --topic T --level L [--tags --summary --pitfalls --body --difficulty]` | 新增卡片 | `/oiwb kb add --topic 双指针 --level 提高级 --tags 排序,双指针 --summary "..."` |
| `/oiwb kb add-file <md路径> [--level L]` | 从模板文件导入卡片 | `/oiwb kb add-file kb-双指针.md` |
| `/oiwb kb edit --topic T [--level --tags --summary --pitfalls --difficulty]` | 修改卡片 | `/oiwb kb edit --topic 双指针 --summary "更新..."` |
| `/oiwb kb rm --topic T [--level L]` | 删除用户卡（只删用户层） | `/oiwb kb rm --topic 双指针` |
| `/oiwb kb validate` | 校验全部用户卡 | `/oiwb kb validate` |

常用参数：
- `--level`：入门级 / 提高级 / 专家级，或自定义层级；
- `--tags`：逗号分隔；
- `--difficulty`：0–10 整数。

## `/oiwb ref ...`

| 子命令 | 说明 | 示例 |
|---|---|---|
| `/oiwb ref list` | 列出用户层参考题 | `/oiwb ref list` |
| `/oiwb ref show <id> [--level L]` | 显示某题目录结构 | `/oiwb ref show relay-mst` |
| `/oiwb ref add <题目目录> [--level L] [--id ID]` | 校验后加入用户层 | `/oiwb ref add my-problem --level 提高级 --id my-p1` |
| `/oiwb ref rm <id> [--level L]` | 删除用户层参考题 | `/oiwb ref rm my-p1` |
| `/oiwb ref validate <题目目录>` | 校验题目目录完整 | `/oiwb ref validate my-problem` |

参考题须包含 `problem.md`、`spec.json`、`data/`（≥1 对 in/out）、`sample/`、
`std/std.cpp`；`brute.cpp`、`generator/gen.py` 建议一并加入。

## 技能合并用法（给 Agent 的提示）

1. 「锁定知识点」先 `kb list` / `kb search <知识点>` 看用户层是否有卡；
2. 命中 → `kb show <topic>` 取全文，**以用户卡为准**；未命中 → 用内置速查表；
3. 用户参考题在出题时可作为「原创参考/变式母题」：`ref list` → `ref show <id>` 浏览结构。
