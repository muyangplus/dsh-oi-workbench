# DSH 原生面板规范（Native Panel）

> 适用：DSH >= 0.2.1-rc.2，`@muyangplus/dsh-oi-workbench` 0.3.0。
> 面板是外壳，能力全部来自本技能目录下的 `generator/`、`tools/`、`hydro-bridge/` 与 `hoj-bridge/` 脚本。

## 1. 入口与结构

- 安装插件并重启 DSH 后，Web GUI 侧边栏出现「OI 工作台」，点击打开原生主面板。
- 主面板五个标签页：总览 / 题目 / OJ / 比赛 / 帮助。
- 面板只读写工作台 root（默认当前工作目录，可在插件配置 `rootDir` 指定），不访问 root 之外的路径。

| 标签页 | 展示 | 动作 |
|---|---|---|
| 总览 | 工作台根目录、插件版本、题目数、`oi-workbench` 技能是否注册 | 刷新状态 |
| 题目 | root 下所有含 `spec.json` 的题目目录与徽标 | 检查、构建（Hydro / HOJ / 两者）、本地评测、打开目录 |
| OJ | Hydro/HOJ 连接档案列表与默认档案 | 新增/编辑/删除、设为默认、连接测试 |
| 比赛 | 已保存的比赛计划（标题 + 题目列表） | 新增/编辑/删除、一键构建 |
| 帮助 | 环境要求、按钮与命令对照、安全边界 | 无 |

## 2. 题目发现规则

- 从 root 递归扫描，所有含 `spec.json` 的目录各算一道题；命中后不继续向下钻取。
- 每题返回相对 root 的斜杠路径、绝对路径与徽标：

| 徽标字段 | 含义 |
|---|---|
| `hasProblemMd` | 存在 `problem.md` |
| `hasSolution` | 存在 `solution/solution.md` |
| `hasStd` | 存在 `std/std.cpp` |
| `hasSpec` | 存在 `spec.json`（每道发现的题都有） |
| `caseCount` | `spec.cases` 声明的测试点数，缺失为 0 |
| `hasData` | `data/` 下至少有一个 `.in` |

## 3. Host HTTP API

前缀 `/oi-workbench/api`，响应统一为 JSON 信封：

```json
{ "ok": true, "value": { } }
```

失败时返回 `{ "ok": false, "error": "可读原因" }`，不返回堆栈。

### 3.1 GET /oi-workbench/api/state

返回 `WorkbenchState`：

| 字段 | 类型 | 含义 |
|---|---|---|
| `root` | string | 工作台根目录绝对路径 |
| `version` | string | 插件版本 |
| `skill` | string | 技能 id，固定为 `oi-workbench` |
| `skillRegistered` | boolean | 会话技能目录中是否已注册该技能 |
| `problems` | ProblemEntry[] | 题目列表，字段见 §2 |
| `oj` | OjConfig | OJ 配置：`profiles` 与 `activeProfileId` |
| `contests` | ContestEntry[] | 比赛计划：`id`、`title`、`problems`、`updatedAt` |

### 3.2 GET /oi-workbench/api/problems

返回 `{ root, problems }`，`problems` 为 §2 的题目列表。

### 3.3 POST /oi-workbench/api/action

请求体是一个动作对象，用 `kind` 判别：

| kind | 参数 | 行为 | 等价命令 |
|---|---|---|---|
| `check` | `dir` | 题目完整性检查 | `python tools/check_problem.py <dir>` |
| `build` | `dir`、`target=hydro/hoj/both` | 打题目包 | `python generator/build_package.py` / `build_hoj_package.py` |
| `judge` | `dir`、`source`、`timeLimitMs` | 本地逐点评测 | `python generator/local_judge.py <dir> --source <source> --time <ms>` |
| `open` | `dir` | 打开目录 | 系统文件管理器 |
| `oj-save` | `profile` | 新增或更新连接档案 | 写入 OJ 配置 |
| `oj-delete` | `id` | 删除连接档案 | 写入 OJ 配置 |
| `oj-set-active` | `id` | 设为默认档案 | 写入 OJ 配置 |
| `oj-test` | `id` | 对档案 `base` 做 HTTP 可达性探测 | 不启动登录：只回显状态码与耗时，不发送凭据 |
| `contest-save` | `contest`（`id`/`title`/`problems`） | 保存比赛计划 | 写入比赛配置 |
| `contest-delete` | `id` | 删除比赛计划 | 写入比赛配置 |
| `contest-build` | `id` | 一键构建比赛交付物 | `python generator/build_contest.py --contest <title> --problems <列表> --out dist/<id>` |

响应为 `ActionOutcome`：

| 字段 | 含义 |
|---|---|
| `ok` | 动作是否成功 |
| `message` | 面向用户的一行摘要 |
| `command` | 子进程结果，可选：`ok`、`exitCode`、`stdout`、`stderr`、`durationMs`、`argv` |
| `state` | 写操作后的 `WorkbenchState`；只读动作省略 |

## 4. OJ 连接档案

- 档案字段：`id`、`kind`（`hydro` 或 `hoj`）、`name`、`base`、`user`、`credentialEnv`。
- `credentialEnv` 是**环境变量名**（例如 `HYDRO_PASSWORD`、`HOJ_TOKEN`），不是密码本身；
  配置文件与面板只保存变量名，明文凭据由用户在 shell 环境中提供。
- 连接测试只对档案的 `base` 做 HTTP 可达性探测并回显状态码与耗时，**不发送凭据、不建立登录态**；
  真实登录/发布留待后续迭代，仍按 SKILL.md §8 的命令行流程执行。

## 5. 错误与安全边界

- **路径限制**：所有 `dir` 与题目路径必须位于工作台 root 内；越界或不存在时直接报错，不执行命令。
- **凭据**：只引用环境变量名，不保存明文、不回显明文；日志只打印变量名。
- **远程与批量**：面板的 OJ 操作等价于对应命令行，批量操作先用 `--dry-run` 验证。
- **子进程**：宿主以固定 argv 调用 Python 脚本，工作目录为 root；超时后终止并返回失败原因；
  输出在面板日志区显示，超过显示上限时截断，但保留退出码与 stderr 摘要。
- **无隐式发布**：面板不自动发布题目或比赛到 OJ；发布仍按 SKILL.md §8 显式执行并人工核对。

## 6. 与命令行的等价关系

- 面板动作一律映射到 §3.3 表中的命令，产物、退出码与校验标准同手工执行完全一致。
- 面板不承载出题业务逻辑：知识点锁定、分数表、数据构造、击杀矩阵、盲审等仍按 SKILL.md 工作流执行。
- 面板不替代发布闸口：`blind_review.py` 与 `check_statement_style.py` 仍需在打包/发布前人工或技能内执行。

## 7. 人工验收清单

- [ ] 侧边栏出现「OI 工作台」，五个标签页可切换。
- [ ] 总览显示 root、插件版本、题目数与 skill 注册状态。
- [ ] 至少一道题出现在题目页，检查与构建返回可读日志。
- [ ] 本地评测按指定时限跑通 std，输出逐点结果。
- [ ] 保存 Hydro/HOJ 档案后刷新可见；连接测试对不可达实例给出可读原因（HTTP 状态码或网络错误）。
- [ ] 比赛计划可保存，一键构建产物与 `build_contest.py` 一致。
- [ ] 档案与日志中不出现明文密码或 token。
