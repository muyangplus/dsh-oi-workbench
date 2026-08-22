# 用户自定义内容规范（User Content）

> 批次 1（v0.1.1）产物。定义用户如何自行添加 **reference / knowledge-base**，
> 以及技能如何使用这些内容。实现方式：直接维护 `~/.dsh-oi-workbench/` 下的目录与文件。

## 1. 目标

- 内置知识库 / 参考题随插件发布是**只读**的；
- 用户需要能自行维护自己的知识库速查卡与原创参考题，且不要求重启、不侵入插件安装目录；
- 自定义内容在与内置内容合并时**有明确优先级**：同名 `topic` 以用户卡为准；
  `level` 允许用户新增自定义层级。

## 2. 存储布局

默认数据根目录：`~/.dsh-oi-workbench/`（与 `hoj_config.json` 同层；`--home` 可覆盖以便测试）。

```text
~/.dsh-oi-workbench/
├── kb/                            # 用户知识库速查卡片
│   ├── level-1-basic/<topic>.md
│   ├── level-2-intermediate/<topic>.md
│   ├── level-3-expert/<topic>.md
│   └── <custom-level-slug>/<topic>.md
├── reference/                     # 用户参考题（与内置 reference/ 同构）
│   ├── level-1-basic/<id>/{problem.md,spec.json,data,sample,std,brute.cpp,generator/}
│   └── ...
└── hoj_config.json                # （既有，HOJ UI 配置）
```

### 层级目录名映射

| 层级 | 目录 |
|---|---|
| 入门级 | `level-1-basic` |
| 提高级 | `level-2-intermediate` |
| 专家级 | `level-3-expert` |
| 自定义 | 小写 ASCII slug（非 `[0-9A-Za-z_-]` 替换为 `-`；空则回退 `custom`） |

文件名/目录名均做安全化：`\\ / : * ? " < > |` 与空白替换为 `-`。

## 3. 知识库卡片（kb）

### 3.1 卡片格式（frontmatter）

模板见 `templates/kb-card.md`。字段：

| 字段 | 必填 | 说明 |
|---|---|---|
| `topic` | 是 | 主题名（唯一；同名以用户卡为准） |
| `level` | 是 | 层级（见映射表，可自定义） |
| `summary` | 是 | 一句话概述 |
| `difficulty` | 否 | 0–10 整数 |
| `tags` | 否 | 列表 |
| `pitfalls` | 否 | 多行易错点 |

frontmatter 支持：`key: value`、`key: [a, b]`、`key:` + `- item` 列表、
`key: |` 多行块。工具用轻量解析器读取，非 YAML 全集，请按模板格式书写。

### 3.2 增删改查（直接维护文件）

| 命令 | 作用 |
|---|---|
| `kb list` | 列出用户层全部卡片 |
| `kb show <topic>` | 显示某卡片全文（含正文） |
| `kb search <kw>` | 全文检索用户层 + 内置 knowledge-base |
| `kb add --topic T --level L [--tags --summary --pitfalls --body --difficulty]` | 新增卡片 |
| `kb add-file <md> [--level L] [--force]` | 导入一张已按模板写的卡片文件 |
| `kb edit --topic T [--level --tags --summary --pitfalls --difficulty]` | 修改（level 变动会移动文件） |
| `kb rm --topic T [--level L]` | 只删用户层卡片 |
| `kb validate` | 校验全部用户层卡片 |

### 3.3 合并规则（技能使用侧）

「锁定知识点」（SKILL.md 第 1 步 / `knowledge-base/workflow.md`）：
1. 先读内置速查表（`knowledge-base/level-*.md`）；
2. 再叠加用户层卡片（首次用 `kb list` / `kb search`，命中后用 `kb show` 取全文）；
3. **同名 `topic` 用户卡优先**；用户卡可新增知识点或自定义层级；
4. 超纲检查：同时对照内置速查表，用户自定义层级内容仍按目标级别上限约束。

## 4. 用户参考题（ref）

- 结构完全沿用内置 `reference/` 标准：`problem.md`、`spec.json`、`data/`（≥1 对 in/out）、
  `sample/`、`std/std.cpp` 必选；`brute.cpp`、`generator/gen.py` 建议。
- 增删改查：直接维护 `~/.dsh-oi-workbench/reference/...`：

| 命令 | 作用 |
|---|---|
| `ref list` | 列出用户层参考题与完整度 |
| `ref show <id> [--level L]` | 显示某题目录结构 |
| `ref add <题目目录> [--level L] [--id ID] [--force]` | 校验后复制进用户层（level 自动推断：源路径含 entry→入门级、intermediate→提高级，否则需指定） |
| `ref rm <id> [--level L]` | 删除用户层参考题 |
| `ref validate <题目目录>` | 校验完整性 |

## 5. 安全与边界

- 工具只在新写/删除于**用户数据根目录之内**（路径越界拒绝）；
- 不执行用户内容中的代码；密码/Token 不落库；
- 用户层数据属于个人环境，**不进插件包**（如需随包发布，另行评估）。

## 6. 验收

- [ ] 无内置卡片也可 `kb add`，`kb list`/`kb search`/`kb show` 立即可见；
- [ ] 同名 topic 用户卡覆盖内置（锁定知识点优先用用户卡）；
- [ ] `kb rm` 只删用户层；`kb validate` 对非法卡片报错；
- [ ] `ref add` 对不完整目录拒绝；完整目录复制后校验通过；
- [ ] 全程无需重启。
