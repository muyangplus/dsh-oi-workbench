# dsh-oi-workbench

OI 出题工作台 —— DeepSeek Harness 的 **skill-first 插件**：核心是 `oi-workbench` 技能，
另附 HOJ/Hydro 桥接脚本与出题工具链。

安装后，在任意会话中可用 `oi-workbench` 技能：按内部整理的知识点速查锁定知识点，
设计测试点表格与特殊性质，针对性构造数据，制作大样例附件，本地评测，打包 **Hydro / HOJ**
原生题目包，并把题目/比赛/团队发布到 Hydro 或 HOJ。用户还可**自行添加自己的知识库速查卡与原创参考题**
（见「用户自定义知识库 / 参考题」一节）。

## 安装

```bash
dsh plugin --profile web add @muyangplus/dsh-oi-workbench
# 或 GitHub 仓库方式：
# dsh plugin --profile web add github:muyangplus/dsh-oi-workbench
```

安装后**重启 DeepSeek Harness** 生效。

安装会自动注册 `oi-workbench` 技能（核心功能），插件本身**不依赖**第三方 npm 包。


## 使用

在会话中直接描述需求即可，例如：

> 使用 oi-workbench 技能，帮我出两道 入门组 题：一道贪心+堆，一道简单 DP。
> 每道 25 个测试点、2 个特殊性质档、附带大样例 zip，最后打成 Hydro 包，再导到 HOJ。

技能会按 `skills/oi-workbench/SKILL.md` 工作流执行：
知识点锁定 → 测试点表格设计 → 题面（零做法提示）→ 代码矩阵 →
数据构造与击杀矩阵验证 → 本地评测 → Hydro/HOJ 打包 → 发布。

## 能力

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
- 管理：Python 外部 UI 与系统斜杠命令已移除；后续由 DSH 原生设置页/面板提供。

## 内容

```text
skills/oi-workbench/
├── SKILL.md               # 出题工作流（技能入口，含评测约定）
├── knowledge-base/        # 内部整理的知识点速查：入门级/提高级/专家级
├── specs/                 # 规范：测试点表格、数据构造、题面风格、变式、用户自定义内容
├── templates/             # 模板：题面、分数表、题目包、知识库卡片
├── generator/             # Hydro/HOJ 打包器 + 校验器 + 本地评测器 + PDF/Lemon/样例打包器（Python 标准库）
├── hydro-bridge/          # Hydro OJ 对接（登录/题目/比赛/团队）
├── hoj-bridge/            # HOJ 完整管理对接（题目/比赛/训练/用户/团队/公告/标签/评测）
├── reference/             # 原创参考题（入门级 4 题 + 提高级 4 题）
└── examples/              # 示例题（果园分装，含完整验证记录）
```

## 用户自定义知识库 / 参考题

用户可自行增删改查 **reference / knowledge-base**，数据存于 `~/.dsh-oi-workbench/`
（`kb/` 与 `reference/`），不侵入插件安装目录；技能「锁定知识点」时并入使用，
同名 `topic` 以用户卡为准，`level` 允许自定义新增。规范见
`skills/oi-workbench/specs/user-content.md`；用户层内容直接维护
`~/.dsh-oi-workbench/kb/` 与 `~/.dsh-oi-workbench/reference/` 下对应文件。

## TODO

已完成：

- [x] 复杂背景故事题面 / story-card / 完整样例打包 / 整卷 PDF / Lemon 导出
- [x] 一键出整场比赛（build_contest / generate_contest）
- [x] 连续剧情 / 连载（story.yaml + story_continuity）
- [x] spj / 交互题本地评测（testlib + interactor）
- [x] 移除 Python UI 管理与斜杠命令内容

未完成：

- [ ] DSH 原生 UI 管理能力（设置页/面板替代 Python UI）

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

## 依赖

- npm：纯 skill 插件，无第三方 npm 运行时依赖；
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
