# DSH 原生 UI 管理能力设计

> 目标：用 DeepSeek Harness 原生设置页与面板管理 OJ、题目、比赛与工作台。
> 状态：原生面板已实现，接入说明与能力清单见下文。

## 0. 原生实现

已按 DSH 插件 UI 模式实现原生面板：

```text
src/
├── index.ts          # host 插件：webServer API + 状态工具
└── client/index.ts   # client 面板：settings.section 插槽
lib/
├── index.js          # host 入口（ESM）
└── client.js         # client 面板 bundle
```

- 在 DSH 侧边栏底部、设置上方注册“OI 工作台”入口（`sidebar.footer.action`），点击打开面板。
- host 侧提供 `/oi-workbench/api/problems`、`/problems/check`、`/problems/build`、`/oj/test`。
- 面板支持题目列表、完整性检查、Hydro/HOJ 构建。

构建：

```bash
npm run build
```

安装后需在 `cordis.patch.yml` 中同时注册 `dsh-oi-workbench` 插件本体与 skill provider。

## 1. 目标

在 DeepSeek Harness（DSH）原生设置页/面板中提供图形化管理能力，替代旧的 Python 外部 UI 与系统斜杠命令，覆盖：

- OJ 实例管理
- 题目管理
- 比赛管理
- 出题工作台管理

## 2. 总体架构

```text
DSH 原生面板（设置页/仪表盘）
        │
        ▼
后端服务层（本地 HTTP / RPC / 命令封装）
        │
        ├── generator/       打包、验证、盲审、样例、PDF、Lemon
        ├── hydro-bridge/    Hydro OJ 操作
        ├── hoj-bridge/      HOJ OJ 操作
        ├── tools/check_problem.py  题目完整性检查
        └── 本地文件系统（题目包目录、比赛目录）
```

原则：

- DSH 面板只负责展示与交互；
- 所有业务逻辑复用现有 `generator` / `bridge` 脚本；
- 不把密码写入面板配置，只引用环境变量 / cookie / 密钥文件。

## 3. 功能模块

### 3.1 OJ 管理

- 实例列表：名称、类型（Hydro/HOJ）、Base URL、状态（在线/离线）。
- 新增/编辑/删除实例。
- 连接测试：调用 `hydro_api.py` / `hoj_api.py` 的 ping/version 接口。
- 凭据管理：
  - Hydro：Cookie / Token；
  - HOJ：用户名 + 密码 / Token；
  - 统一存到 DSH 安全存储，不落明文到题目目录。

### 3.2 题目管理

- 题目包列表：扫描 `dist/*`、`drafts/*` 或用户指定目录。
- 单题详情：`problem.md`、`spec.json`、数据点、样例、std、solution、VERIFICATION。
- 操作：
  - 完整性检查：调用 `tools/check_problem.py`
  - 盲审：调用 `generator/blind_review.py`
  - 打包：调用 `generator/build_package.py` / `build_hoj_package.py`
  - 发布：调用 `hydro-bridge/publish_problem.py` / `hoj-bridge/publish_problem.py`
  - 预览：渲染 `problem.md`，展示数据范围表、样例、SPJ/交互配置。

### 3.3 比赛管理

- 比赛列表与状态。
- 创建/编辑比赛：
  - 关联 OJ 实例；
  - 选择题目；
  - 设置时间、赛制（OI/ACM）、选手列表。
- 操作：
  - 创建比赛：`hydro-bridge/manage_contest.py` / `hoj-bridge/manage_hoj.py`
  - 添加选手/团队
  - 查看评测状态/成绩
  - 导出 Lemon 数据：`generator/export_lemon.py`

### 3.4 出题工作台

- 知识点锁定向导：读取 `knowledge-base/`，生成母题卡。
- 题目生成流水线：
  1. 生成题面/数据/标程/暴力/错解
  2. 本地验证（编译、对拍、击杀矩阵）
  3. 盲审
  4. 打包
  5. 发布
- 每个步骤在面板中显示日志、状态、失败原因。

## 4. DSH 面板建议

| 面板 | 内容 |
|---|---|
| OJ 设置页 | 实例列表、连接测试、凭据配置 |
| 题目库 | 题目列表、详情、操作按钮、日志 |
| 比赛管理 | 比赛列表、编辑、选手管理、评测状态 |
| 工作台 | 新建题目向导、流水线进度、验证结果 |
| 全局日志 | 最近操作、错误堆栈、产物路径 |

## 5. 后端接口草案

```text
GET    /api/oj               列出 OJ 实例
POST   /api/oj/test          测试连接
POST   /api/problems/check   检查题目包
POST   /api/problems/build   构建 Hydro/HOJ 包
POST   /api/problems/publish 发布题目
POST   /api/contests         创建比赛
POST   /api/contests/:id/users 添加选手
POST   /api/workbench/generate 生成题目
GET    /api/workbench/status 查询流水线状态
```

## 6. 安全边界

- 不索要、不记录 Hydro/HOJ 密码；
- 登录凭据只经环境变量 / Cookie / 安全存储传入；
- 所有数据生成、编译、评测在本机执行；
- 不把陌生代码上传到不可信实例；
- 对远程 OJ 的批量操作先 `--dry-run`。

## 7. 实施步骤

1. 定义面板数据模型与接口契约（本设计）。
2. 把现有 `generator` / `bridge` 脚本封装为无 UI 依赖的服务层。
3. 在 DSH 设置页/面板注册入口。
4. 实现 OJ 管理 → 题目管理 → 比赛管理 → 工作台，按依赖顺序推进。
5. 接入 `tools/check_problem.py` 与 `docs/lessons-learned.md` 作为质量保障。

## 8. 完成标准

- 面板可管理至少一个 Hydro/HOJ 实例。
- 可从面板完成：检查题目包 → 构建 → 发布 → 创建比赛 → 添加选手。
- 工作台可跑通一次完整出题流水线并展示日志。
- 无明文密码落盘。
