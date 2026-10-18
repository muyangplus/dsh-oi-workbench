# 用户自定义内容规范（User Content）

> 定义用户如何自行添加 **reference / knowledge-base**，以及技能如何使用这些内容。
> 实现方式：直接维护 `~/.dsh-oi-workbench/` 下的目录与文件；题目/OJ/比赛的管理面由 DSH 原生面板承载，
> 见 `specs/native-panel.md`。

## 1. 目标

- 内置知识库 / 参考题随插件发布是**只读**的；
- 用户需要能自行维护自己的知识库速查卡与原创参考题，且不要求重启、不侵入插件安装目录；
- 自定义内容在与内置内容合并时**有明确优先级**：同名 `topic` 以用户卡为准；
  `level` 允许用户新增自定义层级。

## 2. 存储布局

默认数据根目录：`~/.dsh-oi-workbench/`。

```text
~/.dsh-oi-workbench/
├── kb/                            # 用户知识库速查卡片
│   ├── level-1-basic/<topic>.md
│   ├── level-2-intermediate/<topic>.md
│   ├── level-3-expert/<topic>.md
│   └── <custom-level-slug>/<topic>.md
└── reference/                     # 用户参考题（与内置 reference/ 同构）
    ├── level-1-basic/<id>/{problem.md,spec.json,data,sample,std,brute.cpp,generator/}
    └── ...
```

### 层级目录名映射

| 层级 | 目录 |
|---|---|
| 入门级 | `level-1-basic` |
| 提高级 | `level-2-intermediate` |
| 专家级 | `level-3-expert` |
| 自定义 | 小写 ASCII slug（非 `[0-9A-Za-z_-]` 替换为 `-`；空则回退 `custom`） |

文件名/目录名建议按安全化规则书写：`\\ / : * ? " < > |` 与空白替换为 `-`。

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
`key: |` 多行块。技能按轻量解析规则读取，非 YAML 全集，请按模板格式书写。

### 3.2 增删改查（直接维护文件）

| 操作 | 做法 |
|---|---|
| 新增 | 按 `templates/kb-card.md` 写卡片，保存为 `kb/<level>/<topic>.md` |
| 查看/搜索 | 用编辑器打开，或让技能在会话中读取 `kb/` 与内置 `knowledge-base/` |
| 修改 | 直接编辑卡片文件；改 `level` 时把文件移动到对应层级目录 |
| 删除 | 删除 `kb/<level>/<topic>.md` |
| 校验 | 对照 §3.1 字段与模板自查；frontmatter 不按模板书写时技能读不到该卡片 |

### 3.3 合并规则（技能使用侧）

「锁定知识点」（SKILL.md 第 1 步 / `knowledge-base/workflow.md`）：
1. 先读内置速查表（`knowledge-base/level-*.md`）；
2. 再叠加用户层卡片（会话内列出/检索 `~/.dsh-oi-workbench/kb/`，命中后读取卡片全文）；
3. **同名 `topic` 用户卡优先**；用户卡可新增知识点或自定义层级；
4. 超纲检查：同时对照内置速查表，用户自定义层级内容仍按目标级别上限约束。

## 4. 用户参考题（ref）

- 结构完全沿用内置 `reference/` 标准：`problem.md`、`spec.json`、`data/`（≥1 对 in/out）、
  `sample/`、`std/std.cpp` 必选；题目目录内的 `brute.cpp` 与 `generator/` 下的生成器脚本建议。
- 增删改查：直接维护 `~/.dsh-oi-workbench/reference/...`：

| 操作 | 做法 |
|---|---|
| 新增 | 按上述结构准备题目目录，整体复制到 `reference/<level>/<id>/` |
| 查看 | 直接打开题目目录 |
| 删除 | 删除 `reference/<level>/<id>/` |
| 校验 | `python tools/check_problem.py <题目目录>`（工具在技能目录内，对任意题目目录可用） |

## 5. 安全与边界

- 用户层读写限定在 `~/.dsh-oi-workbench/` 之内，不触碰插件安装目录；
- 不执行用户内容中的代码；密码/Token 不写入用户层；
- 用户层数据属于个人环境，**不进插件包**（如需随包发布，另行评估）。

## 6. 验收

- [ ] 用户层目录为空时技能正常运行；按模板新建卡片后技能可读到；
- [ ] 同名 topic 用户卡覆盖内置（锁定知识点优先用用户卡）；
- [ ] 删除用户层卡片不影响内置 `knowledge-base/`；
- [ ] frontmatter 不按模板书写时，该卡片不参与合并；
- [ ] 完整结构的 `reference/<level>/<id>/` 能通过 `tools/check_problem.py` 校验；
- [ ] 全程无需重启。
