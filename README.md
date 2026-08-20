# dsh-oi-workbench

OI 出题工作台 —— DeepSeek Harness 的 **skill-first 插件**：核心是 `oi-workbench` 技能，
另附 Python 外部管理 UI、HOJ/Hydro 桥接脚本与系统斜杠命令自动注册。

安装后，在任意会话中可用 `oi-workbench` 技能：按内部整理的知识点速查锁定知识点，
设计测试点表格与特殊性质，针对性构造数据，制作大样例附件，本地评测，打包 **Hydro / HOJ**
原生题目包，并把题目/比赛/团队发布到 Hydro 或 HOJ；还提供 Python 外部管理 UI 和
`/hoj`、`/oiwb`、`/oj` 系统斜杠命令。用户还可**自行添加自己的知识库速查卡与原创参考题**
（见「用户自定义知识库 / 参考题」一节）。

## 安装

```bash
dsh plugin --profile web add dsh-oi-workbench
# 或 GitHub 仓库方式：
# dsh plugin --profile web add github:your-name/dsh-oi-workbench
```

安装后**重启 DeepSeek Harness** 生效。

安装时会自动：
- 安装 `@etby-studio/dsh-commands` 命令发现插件；
- 在 profile 层插入 `dsh-commands`，并让其直接扫描插件内的 `commands/register/`；
- 因此 `/hoj`、`/oiwb`、`/oj` 系统斜杠命令随插件安装自动注册，无需手动复制。

## 使用

在会话中直接描述需求即可，例如：

> 使用 oi-workbench 技能，帮我出两道 入门组 题：一道贪心+堆，一道简单 DP。
> 每道 25 个测试点、2 个特殊性质档、附带大样例 zip，最后打成 Hydro 包，再导到 HOJ。

技能会按 `skills/oi-workbench/SKILL.md` 工作流执行：
知识点锁定 → 测试点表格设计 → 题面（零做法提示）→ 代码矩阵 →
数据构造与击杀矩阵验证 → 本地评测 → Hydro/HOJ 打包 → 发布。

## 内容

```text
skills/oi-workbench/
├── SKILL.md               # 出题工作流（技能入口，含评测约定）
├── knowledge-base/        # 内部整理的知识点速查：入门级/提高级/专家级
├── specs/                 # 规范：测试点表格、数据构造、题面风格、变式、用户自定义内容
├── templates/             # 模板：题面、分数表、题目包、知识库卡片
├── generator/             # Hydro/HOJ 打包器 + 校验器 + 本地评测器（Python 标准库）
├── hydro-bridge/          # Hydro OJ 对接（登录/题目/比赛/团队）
├── hoj-bridge/            # HOJ 完整管理对接（题目/比赛/训练/用户/团队/公告/标签/评测）
├── ui/                    # Python 外部管理 UI（hoj_ui.py + hoj-admin.html + user_content.py）
├── commands/              # 斜杠指令文档 + 自动注册命令文件（register/）
├── reference/             # 原创参考题（入门级 4 题 + 提高级 4 题）
└── examples/              # 示例题（果园分装，含完整验证记录）
```

## 用户自定义知识库 / 参考题（批次 1）

用户可自行增删改查 **reference / knowledge-base**，数据存于 `~/.dsh-oi-workbench/`
（`kb/` 与 `reference/`），不侵入插件安装目录；技能「锁定知识点」时并入使用，
同名 `topic` 以用户卡为准，`level` 允许自定义新增。规范见
`skills/oi-workbench/specs/user-content.md`，命令见
`skills/oi-workbench/commands/kb.md`。

```powershell
# 知识库卡片：新增 / 检索 / 校验
python skills/oi-workbench/ui/user_content.py kb add --topic 并查集 --level 提高级 --summary "..."
python skills/oi-workbench/ui/user_content.py kb search 并查集
python skills/oi-workbench/ui/user_content.py kb validate

# 参考题：校验后加入用户层 / 列出
python skills/oi-workbench/ui/user_content.py ref add my-problem --level 提高级 --id my-p1
python skills/oi-workbench/ui/user_content.py ref list
```

## 路线图 / TODO（未完成功能）

以下能力已规划未完成，将按 `version-records/ROADMAP.md` 分批填充（不含版本号承诺）：

- [ ] **故事题面 + 故事设计能力**：原创故事构造复杂剧情、知识点融入题面；`story-card` 故事设计能力。
- [ ] **一次性出一场比赛**：一段描述 → 多题 + 故事主线 + 数据 + 打包 + 一键建赛。
- [ ] **连续剧情 / 连载**：同场共享主线 + 跨场次连载；`story.yaml` 剧本仓库 + 连续性检查。
- [ ] **支持 spj 和交互题（完整评测）**：当前已提供基础本地 spj（checker 按 exit 0=AC）与包级
      `judge.spj` / `checker` / `interactor` 字段；待补 testlib 标准 checker、交互题 interactor 的
      真机评测与配套样例验证。
- [ ] **支持 testlib.h**：spj / 交互题 checker / interactor 统一改用 Codeforces 标准
      `testlib.h`（自动链接内置 `testlib.h`，本地评测与远程 OJ 行为一致）。

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

# 一键校验全部自出参考题
python generator\build_all_reference.py

# 发布到 HOJ
python hoj-bridge\publish_problem.py --base https://hoj.example.com --user root --problem-dir examples\demo

# HOJ 管理
python hoj-bridge\manage_hoj.py --help
```

## 斜杠命令

插件安装后自动注册以下系统命令（通过 `@etby-studio/dsh-commands` 扫描 `commands/register/`）：

| 命令 | 作用 |
|---|---|
| `/hoj` | 启动 HOJ 外部管理 UI |
| `/oiwb` | OI Workbench 通用入口 |
| `/oj` | `/oiwb` 的别名 |
| `/hoj problems` | HOJ 题目列表 |
| `/hoj contests` | HOJ 比赛列表 |
| `/hoj publish <目录>` | 发布题目到 HOJ |
| `/hoj rejudge <submitId>` | 重判提交 |
| `/oiwb kb list\|show\|search\|add\|edit\|rm\|validate` | 用户自定义知识库（见 commands/kb.md） |
| `/oiwb ref list\|show\|add\|rm\|validate` | 用户自定义参考题（见 commands/kb.md） |

## UI 管理

UI 使用 **Python 外部管理 UI**（不依赖 DSH 内部 `render_ui`）：

```bash
python skills/oi-workbench/ui/hoj_ui.py --host 0.0.0.0 --port 6163 --base https://hoj.example.com
```

- 浏览器访问：`http://localhost:6163/`
- 手机/局域网访问：`http://<本机IP>:6163/`
- 服务端代理 HOJ API，保存 Cookie，避免 `file://` 和 CORS 问题
- 通用指令根为 `/oiwb`（别名 `/oj`），HOJ 子命令见 `skills/oi-workbench/commands/hoj.md`

## 依赖

- npm：`@etby-studio/dsh-commands`（MIT），用于系统斜杠命令注册；其传递依赖为 MIT / ISC / BSD 类宽松协议；
- Python：出题/打包/对接/UI 脚本均使用 Python 3 标准库，无第三方 Python 包；
- 本地编译验证需要 g++（C++14，建议按 `-O2 -std=c++14 -static`）；
- 发布到 Hydro/HOJ 需要你自己的实例与账号。

## 参考

- Hydro 题目包格式：<https://docs.hydro.ac/zh/docs/Hydro/user/problem-format>
- HOJ 导入格式：<https://github.com/HimitZH/HOJ/blob/master/docs/docs/use/import-problem.md>
- 自出参考题：`reference/entry/`、`reference/intermediate/`

## License

项目采用 **Apache License 2.0**，覆盖本仓库原创代码、脚本、配置、模板、文档与参考题。
详见 [LICENSE](LICENSE) 与 [NOTICE.md](NOTICE.md)。

- npm 依赖：仅 `@etby-studio/dsh-commands`（MIT，用于系统斜杠命令注册）；
- Python 依赖：仅标准库。
