# dsh-oi-workbench

OI 出题工作台 —— DeepSeek Harness 的 **skill-first 插件**：核心是 `oi-workbench` 技能，
另附 HOJ/Hydro 桥接脚本、出题工具链，以及 DSH Web GUI 的**原生「OI 工作台」面板**。

安装后，在任意会话中可用 `oi-workbench` 技能：按内部整理的知识点速查锁定知识点，
设计测试点表格与特殊性质，针对性构造数据，制作大样例附件，本地评测，打包 **Hydro / HOJ**
原生题目包，并把题目/比赛/团队发布到 Hydro 或 HOJ。用户还可**自行添加自己的知识库速查卡与原创参考题**
（见「用户自定义知识库 / 参考题」一节）。

Web GUI 侧边栏会新增「OI 工作台」入口，打开原生主面板即可浏览题目、检查/构建/本地评测、
管理 OJ 连接档案与比赛计划，无需在对话里逐条敲命令。

## 运行环境

- DeepSeek Harness **>= 0.2.1-rc.2**（插件通过 `dsh.engines.dsh` 声明兼容范围；
  旧版本会被平台按版本门禁跳过，不加载也不注册技能）；
- Node.js >= 20；
- Python 3（出题/打包/对接脚本仅用标准库）；
- 本地编译验证需要 g++（C++14，建议 `-O2 -std=c++14 -static`）；
- 发布到 Hydro/HOJ 需要你自己的实例与账号。

## 安装

```bash
dsh plugin --profile web add @muyangplus/dsh-oi-workbench
# 或 GitHub 仓库方式：
# dsh plugin --profile web add github:muyangplus/dsh-oi-workbench
```

安装后**重启 DeepSeek Harness** 生效。安装会自动注册：

- `oi-workbench` 技能（由插件宿主侧注册，不依赖独立 skill-filesystem patch）；
- `oiwb_status` 工具（返回工作台根目录、题目数量、skill 注册状态）；
- Web GUI 原生面板（侧边栏「OI 工作台」）。

## 使用

在会话中直接描述需求即可，例如：

> 使用 oi-workbench 技能，帮我出两道 入门组 题：一道贪心+堆，一道简单 DP。
> 每道 25 个测试点、2 个特殊性质档、附带大样例 zip，最后打成 Hydro 包，再导到 HOJ。

技能会按 `skills/oi-workbench/SKILL.md` 工作流执行：
知识点锁定 → 测试点表格设计 → 题面（零做法提示）→ 代码矩阵 →
数据构造与击杀矩阵验证 → 本地评测 → Hydro/HOJ 打包 → 发布。

也可以在 Web GUI 侧边栏打开「OI 工作台」面板：总览 / 题目 / OJ / 比赛 / 帮助 五个标签页，
把上述流程中的检查、构建、本地评测、连接测试与整场构建搬到原生 UI 里完成。

## 能力

### DSH 原生面板（0.3.0 起）
- 侧边栏「OI 工作台」行 + 主面板页签（总览 / 题目 / OJ / 比赛 / 帮助）；
- 总览：工作台根目录、插件版本、题目数、skill 注册状态；
- 题目：扫描 `spec.json` 题目目录，显示题面/题解/std/数据/测试点数徽标，一键检查、构建
  （Hydro / HOJ / 两者）、本地评测、打开目录，并展示命令输出与耗时；
- OJ：管理 Hydro/HOJ 连接档案（实例地址、账号、凭据**环境变量名**），连接测试；
  面板不保存明文密码或 Token；
- 比赛：保存比赛计划（标题 + 题目列表），一键构建整场交付物；
- 安全边界：所有路径必须位于工作台根目录内，批量操作先 `--dry-run`。

### 出题工作流
- 知识点锁定：内置入门/提高/专家知识库速查 + 用户自定义知识库/参考题；
- 测试点与分数表：灵活分档、特殊性质、25 点等分/不等分；
- 数据构造与验证：生成器、击杀矩阵、对拍、本地评测（`generator/local_judge.py`）；
- 盲审：`generator/blind_review.py --release / --problem`。

### 题面与样例
- 复杂背景故事 / story-card：`generator/story_card.py`、`specs/story-design.md`；
- 完整样例平铺打包：`generator/package_samples.py`（`1/2/3.in/.out`）；
- 整卷 PDF：`generator/build_statement_pdf.py`（官方风格封面/页眉页脚/样例行号）；
- 连续剧情 / 连载：`story.yaml` + `generator/story_continuity.py`。

### 打包与交付
- Hydro / HOJ 原生包：`generator/build_package.py` / `build_hoj_package.py`；
- Lemon 评测机数据：`generator/export_lemon.py`（含 `<contest>.cdf` 与 std 选手）；
- 一键整场：`generator/build_contest.py` / `generator/generate_contest.py`。

### 特殊评测
- testlib checker 与交互题 interactor：`generator/local_judge.py`
  （内置 `generator/testlib/testlib.h` v0.9.41，MIT，附 LICENSE/README）；
- spj/交互样例验证自动化：`generator/validate_spj.py`。

### 发布
- Hydro / HOJ 桥接：`hydro-bridge/`、`hoj-bridge/`；
- 管理面：DSH Web GUI 原生面板（oj/题目/比赛/工作台），凭据只经环境变量引用。

## 内容

```text
lib/                       # 插件运行时代码（构建产物，npm 包内容）
skills/oi-workbench/
├── SKILL.md               # 出题工作流（技能入口，含评测约定与面板用法）
├── knowledge-base/        # 内部整理的知识点速查：入门级/提高级/专家级
├── specs/                 # 规范：测试点表格、数据构造、题面风格、故事题面、变式、用户自定义内容、原生面板
├── templates/             # 模板：题面、分数表、题目包、知识库卡片
├── generator/             # Hydro/HOJ 打包器 + 校验器 + 本地评测器 + PDF/Lemon/样例打包器（Python 标准库）
├── hydro-bridge/          # Hydro OJ 对接（登录/题目/比赛/团队）
├── hoj-bridge/            # HOJ 完整管理对接（题目/比赛/训练/用户/团队/公告/标签/评测）
├── reference/             # 原创参考题（入门级 4 题 + 提高级 4 题）
└── examples/              # 示例题（果园分装，含完整验证记录）
```

## 用户自定义知识库 / 参考题

用户可自行维护 **reference / knowledge-base**，数据存于 `~/.dsh-oi-workbench/`
（`kb/` 与 `reference/`），不侵入插件安装目录；技能「锁定知识点」时并入使用，
同名 `topic` 以用户卡为准，`level` 允许自定义新增。规范见
`skills/oi-workbench/specs/user-content.md`；直接维护 `~/.dsh-oi-workbench/` 下对应文件即可。

## TODO

已完成：

- 出题工作流：知识点锁定、测试点/分数表、数据构造/击杀矩阵、本地评测、盲审；
- 题面与样例：复杂背景故事/story-card、完整样例平铺、整卷 PDF、连续剧情/连载；
- 一键整场：`build_contest.py` / `generate_contest.py`（story + story.yaml + 全套交付）；
- 特殊评测：testlib checker、交互题 interactor、`validate_spj.py`；
- 清理：移除 Python 外部 UI 与系统斜杠命令；
- **DSH 0.2.1 适配**：插件版本门禁（`dsh.engines.dsh`）、`@deepseek-ai/cordis` /
  新版 `dsh-tools` API、skill 由插件宿主侧注册；
- **DSH 原生 UI 管理能力**：侧边栏「OI 工作台」+ 主面板（题目/OJ/比赛/工作台管理）。

下一步：

- [ ] 面板内接入真实 OJ 登录态（Cookie / Token 只走凭据服务引用，不落盘明文）；
- [ ] 面板内直接发起发布（Hydro/HOJ）并回显进度，默认 `--dry-run` 预演；
- [ ] 出题任务的会话内进度条（复用 `oiwb_status` 与面板状态快照）。

## 常用命令

```powershell
# 打包/校验 Hydro
python generator\build_package.py examples\demo --out P01.zip
python generator\verify_package.py P01.zip

# 打包/校验 HOJ
python generator\build_hoj_package.py examples\demo --out P01-hoj.zip
python generator\verify_hoj_package.py P01-hoj.zip

# 本地评测
python generator\local_judge.py examples\demo --source std\std.cpp

# 完整样例打包（平铺 1/2/3 + 更新题面引用）
python generator\package_samples.py --problems examples\demo --story-dir <故事题面目录> --combined samples.zip

# 整卷 PDF（官方风格封面/注意事项/页眉页脚）
python generator\build_statement_pdf.py --contest "LKCP" --subtitle "2026 第二轮认证" --problems examples\demo --out paper.pdf

# Lemon 评测机比赛数据（含 std 选手与 .cdf）
python generator\export_lemon.py --contest LKCP --problems examples\demo --out dist\lemon

# 一键校验全部自出参考题
python generator\build_all_reference.py

# 发布到 HOJ
python hoj-bridge\publish_problem.py --base https://hoj.example.com --user root --problem-dir examples\demo

# HOJ 管理
python hoj-bridge\manage_hoj.py --help
```

## 依赖

- npm：插件宿主侧只依赖 DSH 平台提供的 peer（`@deepseek-ai/cordis`、`@deepseek-ai/dsh-tools`、
  `@deepseek-ai/dsh-skill` 等），无第三方 npm 运行时依赖；
- 浏览器侧只用 DSH Web shell 已注入的基线模块（React 等），不内联第二份运行时；
- Python：出题/打包/对接脚本均使用 Python 3 标准库，无第三方 Python 包；
- 本地编译验证需要 g++（C++14，建议按 `-O2 -std=c++14 -static`）；
- 发布到 Hydro/HOJ 需要你自己的实例与账号。

## 参考

- Hydro 题目包格式：<https://docs.hydro.ac/zh/docs/Hydro/user/problem-format>
- HOJ 导入格式：<https://github.com/HimitZH/HOJ/blob/master/docs/docs/use/import-problem.md>
- 自出参考题：`reference/entry/`、`reference/intermediate/`

## License

项目采用 **Apache License 2.0**，覆盖本仓库原创代码、脚本、配置、模板、文档与参考题。
详见 [LICENSE](LICENSE) 与 [NOTICE.md](NOTICE.md)。

- npm 依赖：无强制依赖；纯 skill 插件；
- Python 依赖：仅标准库。
