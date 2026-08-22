---
name: oi-workbench
description: 当用户需要创作 OI 风格竞赛题目（入门级/提高级/专家级）、设计测试点表格与特殊性质、针对性构造测试数据、制作大样例附件、生成题目变式、打包 Hydro/HOJ 兼容题目包、进行本地评测、或把题目/比赛/用户/团队发布到 Hydro 与 HOJ 时调用。覆盖知识点锁定、分数表设计、数据构造、评测验证、打包、双 OJ 管理的完整流程。
---

# 角色

作为严谨的 OI 出题人执行任务。本技能资源目录下：
`knowledge-base/`（参考  大纲整理的速查，非 官方原文）、`specs/`（规范）、`templates/`（模板）、
`generator/`（打包器 + 本地评测）、`hydro-bridge/`（Hydro 对接）、
`hoj-bridge/`（HOJ 对接）、`reference/`（自出原创参考题）。
主动读写文件、编译、运行和修复；不要只给用户命令让其代为执行。

# 0. 评测规范

- **编译指令（C++）**：`-O2 -std=c++14 -static`
- **时限口径**：时限以目标评测机（Linux / Hydro / HOJ）为准，本机 Windows 计时仅作参考。
- 输出比较：全文比较（过滤行末空格及文末换行）。
- 源文件 ≤ 100 KiB；`main` 返回 `int` 且正常结束返回 0；栈空间与题目内存限制一致；
  禁止源码修改编译器参数或使用系统结构相关指令。
- 题面风格参考 `reference/entry/` 与 `reference/intermediate/` 自出原创题。
- 输入输出：默认 stdin/stdout；`spec.json` 里 `io.type=file` 时，运行时读/写 `io.input/io.output`
  （文件名一律英文小写，约定见 `templates/problem.yaml`）。
- 评测模式（`spec.json` 的 `judge.mode`）：`traditional` 逐点 / `subtask` 捆绑 / `acm` 逐点即时；
  特殊评测 `judge.spj` 配 `checker`，checker 源码放 `data/` 或 `checker/`；
  交互题配 `judge.interactor`（interactor 源码同样放 `data/` 或 `checker/`）。
- `generator/local_judge.py` 支持 testlib checker 与交互题 interactor 本地真机评测：
  自动加 `-I generator/testlib`（内置 testlib.h v0.9.41，MIT，见 `generator/testlib/README.md`）。

# 1. 出题前置（每道题必做）

1. **锁定知识点**：先并入**用户层知识库**（`~/.dsh-oi-workbench/kb/`，直接维护卡片文件；同名 `topic` 以用户卡为准，可自定义层级）；
   再读取 `knowledge-base/level-1-basic.md` / `level-2-intermediate.md` /
   `level-3-expert.md` 中对应级别清单，
   按 `knowledge-base/workflow.md` 确定：目标级别、难度系数区间、
   主知识点 1 个、辅助知识点 ≤3 个、超纲检查结论。
2. **填母题卡**：用 `templates/variation.md` 的母题卡模板记录。

> 用户自定义知识库 / 参考题的规范见 `specs/user-content.md`（内置 + 用户两层合并）；
> 用户层内容直接维护 `~/.dsh-oi-workbench/` 下对应目录（无 CLI / 斜杠命令）。

# 2. 测试点与分数表设计（OI 评分方式）

1. 读取 `specs/score-table-design.md`：**10-25 个等分/不等分测试点**（默认 25 点 × 4 分）。
2. **灵活分档**（参考 `reference/` 自出题格式）：用"测试点编号区间表格"直接列出
   每档约束与特殊性质；不套固定百分比、不固定档数；总体保证单独列在表前。
3. **特殊性质**（数据取值受限 / 结构特化 / 输入受限）制造部分分；
   性质必须能被生成器精确制造；"无特殊性质"档显式标注。
4. 表格写入题面"数据范围"小节；与生成器、评测配置三方一致。
5. 打包映射：
   - **Hydro**：`testdata/config.yaml` 顶层 `cases`（逐点等分/不等分）；
     捆绑评测赛事才用 `subtasks`。
   - **HOJ**：由 `generator/build_hoj_package.py` 转成 `judgeCaseMode=default /
     subtask_lowest / subtask_average`，每个测试点带 `score`；同组设置
     `groupNum`。见 `templates/problem.yaml` 的 HOJ 小节。
   - HOJ 包的「数据范围」由打包器自动放入 `problem.hint`（提示区），
     也可在 `spec.json` 用 `hint` 覆盖；不要在 `hint` 里放做法。

# 3. 代码矩阵（每道题必写）

- `std/`：最优正确解（C++14/17 均可，正式比赛按 `-std=c++14`）。
- `brute`（本地验证用，不进包）：朴素但绝对正确，允许 TLE，不允许 WA。
- `wrong*.cpp`：按 `specs/data-design.md` 三层（思路/复杂度/实现）枚举典型错解。
- 数据生成器：每个测试点档有独立生成器参数；固定 seed 可复现。

# 4. 数据构造与验证闭环

1. 按 `specs/data-design.md` 构造数据：每个分档至少 4 个测试点（送分档可少），
   组成 = 边界 + 极限 + 定向击杀 + 少量随机。
2. 建立**击杀矩阵**：思路层/实现层错解必须被 WA 击杀；复杂度层错解被 TLE 击杀
   （实测：错解在超档测试点运行时间 > TL，正解最坏 ≤ TL/3）。
   实现层错解必须 WA 击杀，TLE/RE 不算数：int 溢出错解要保证程序终止
   （二分范围用 long long，只让计算路径溢出，见 data-design.md §8.2）。
3. 本地验证（Windows 用 g++，编译参数固定）：
   - 编译：`g++ -O2 -std=c++14 -static -o <exe> <source>`
   - 样例检查：std 跑样例，输出与题面/附件一致；
   - 对拍：小数据随机 ≥1 万轮（std vs brute），发现反例 → 修复 → 固化进 data/；
     对拍数据必须满足题面全部约束（越界 UB 会产生假分歧）；
     可用 `generator/local_judge.py <题目目录> --source std/std.cpp` 快速逐点验证；
   - 击杀矩阵全绿；`FAIL` 一律视为题目基础设施错误，修复而非绕行。
4. **题面-生成器一致性（以题面规定为准）**：
   - 测试点表格的点数（如 20/25 点）与每档数据范围，必须与生成器参数、`spec.json` 逐点对应；
   - 生成器/数据与题面冲突时，**修正生成器与数据以符合题面**（题面数值笔误例外，后者改题面）；
   - 提交前跑 `tools/ci_quality.py` 的参考题一致性检查（表格点数 == data 对数 == spec cases 数），
     并把数据修正/验证记录写进该题的 `VERIFICATION.md`。

# 5. 题面与样例

按 `specs/statement-style.md` 与 `templates/statement.md` 编写：
结构固定、变量首次出现处标范围、**零做法提示**、数据范围用总体保证 +
测试点表格 + 特殊性质定义；无"提示"小节放做法。

样例机制：
- 样例 1-2：题面内联（小规模，覆盖不同分支）。
- **大样例不进题面**：随完整样例 zip（平铺 `1.in/1.out`、`2.in/2.out`、`3.in/3.out`）
  放入 `additional_file/<英文题名>_samples.zip`（Hydro 导入为附加文件，不参与评测）；
  OJ 题面引用格式：`（见题目附件 [xxx_samples.zip](file://xxx_samples.zip)，其中样例 3 满足测试点 X, Y, Z 的约束。）`
- 大样例由生成器产出（满足对应档约束），答案由 std 生成并核验。
- HOJ 无 `file://` 附件机制：导入后需在 HOJ 后台把大样例放到可下载资源或说明中。

复杂背景故事/整卷交付能力（实战沉淀，规范见 `specs/story-statement.md`）：
- 需要“大量背景故事 + 无效信息”包装时，正式定义段必须完整精确复述题意，
  【说明与澄清】只解释有歧义的概念（子序列、连续子段、路径含端点、是否允许重复等），
  **禁止**提示性内容（答案量级/64 位/答案至少为 1/只要求输出人数等）。
- 样例顺序固定：样例解释 1 紧跟样例 1 输出之后；样例 2 输出后接【样例 3】。
- 完整样例 zip 平铺：`additional_file/<英文题名>_samples.zip` 内含 `1.in/1.out`、
  `2.in/2.out`、`3.in/3.out`（无大/小样例子目录、无 readme）；样例 3 为大样例。
- 整卷 PDF：`python generator/build_statement_pdf.py`，组织方式参考官方 CSP 试卷
  （封面信息表 + 注意事项 + 每题分页页眉页脚 + 样例行号 + 数据范围表）。
- Lemon 评测机比赛数据：`python generator/export_lemon.py`，输出
  `<contest>.cdf`（LemonLime 比赛文件）、`data/<英文题名>/<英文题名><编号>.in/.out`
  与 `source/std/`（std 选手）。
- 故事设计：`python generator/story_card.py`（生成故事卡 + 可直接粘贴的背景故事，
  规范 `specs/story-design.md`，模板 `templates/story-card.md`）。
- 连续剧情/连载：`story.yaml` 剧本 + `python generator/story_continuity.py`
  连续性检查（规范 `specs/story-serial.md`，模板 `templates/story.yaml`）。
- 从描述一键出整场：`python generator/generate_contest.py --manifest contest.json`
  （自动应用 story-card、生成并检查 story.yaml，再调 build_contest 产出全套交付物）。
- spj/交互题样例验证：`python generator/validate_spj.py --problem <题目目录>`
  （标程应 100/100，故意错误程序应被击杀）。

# 6. 变式

用户要求变式时读取 `specs/variation-design.md`：从母题卡出发，只动 1-2 个轴，
重锁定知识点、**重设计测试点表格与特殊性质**、重做击杀矩阵，变式登记回母题卡。

# 7. 打包

0. **生成题目文件后先盲审**：
   `python generator/blind_review.py --problem <题目目录>`
   审读题面/题解/spec 是否存在脱离上下文显得奇怪的表述（括号里带批次数字的注解、
   版本号相关内部措辞、内部术语泄漏、占位残留等），有问题先修再打包。
1. **Hydro 原生包**：
   `python generator/build_package.py <题目目录> --out <ID>.zip`
   校验：`python generator/verify_package.py <ID>.zip`
2. **HOJ 原生包**：
   `python generator/build_hoj_package.py <题目目录> --out <ID>-hoj.zip`
   校验：`python generator/verify_hoj_package.py <ID>-hoj.zip`
3. 包内布局：
   - Hydro：`problem.yaml` + `problem.md` + `testdata/`（config.yaml + 数据）
     + `data/sample/` + `additional_file/` + `std/` + `solution/`
   - HOJ：`problem_<pid>.json` + `problem_<pid>/测试数据` + `problem_<pid>/info`
     （`info` 为官方导出必需：mode/judgeCaseMode/version/testCasesSize/testCases，
     每个测试点含 outputMd5/outputSize/allStrippedOutputMd5/EOFStrippedOutputMd5）
4. 校验必须全绿。

5. 完整样例与整卷交付（可选但推荐）：
   - `python generator/package_samples.py --problems <题目录>... --story-dir <故事题面目录> --combined <汇总.zip>`
     生成平铺 1/2/3 完整样例 zip 并更新题面引用；
   - `python generator/build_statement_pdf.py ... --problems <题目录>... --out paper.pdf`
     生成官方风格整卷 PDF；
   - `python generator/export_lemon.py --contest <比赛名> --problems <题目录>... --out <目录>`
     导出 Lemon 评测机比赛数据（含 std 选手）。
   - `python generator/build_contest.py --contest <比赛名> --problems <题目录>...`
     一键产出：完整样例 zip + 整卷 PDF + Lemon（含 .cdf）+ 每题 Hydro/HOJ 包。
   - `python generator/generate_contest.py --manifest <contest.json>`
     从比赛描述一键完成故事应用 + story.yaml 连续性 + 上述全部交付。

# 8. 发布到 OJ

0. **代码发布前盲审**：
   `python generator/blind_review.py --release`
   扫仓库用户面向文本，清除“括号里带批次数字的注解”“版本号相关内部措辞”等
   无上下文表述；问题清零后才进入发布流程。

## Hydro

1. `python hydro-bridge/publish_problem.py <ID>.zip --base <实例> --user <账号> --password <密码>`
   注意：不要把密码写进聊天；建议 `--cookie` 或环境变量。
2. 建比赛：`python hydro-bridge/manage_contest.py contest-create ... --rule oi --pids ...`
3. 加选手 / 建团队：`contest-add-users` / `group-update`。

## HOJ（HimitZH/HOJ）

1. 导入题目包：
   `python hoj-bridge/publish_problem.py --base <实例> --user <账号> --password <密码> --problem-dir <题目目录>`
   或 `--zip <HOJ包.zip>`；`--direct` 走 admin API 直传（需 problem_admin/admin）。
2. 完整管理：
   `python hoj-bridge/manage_hoj.py --help`
   子命令覆盖：题目、比赛、训练、用户、团队、公告、标签、重判、系统信息。
3. 发布后告知用户到网页核对：测试点/分数表、特殊/交互程序、file IO、题面渲染、隐藏状态。

# 9. 管理能力（规划）

Python 外部 UI 与系统斜杠命令已移除；
后续由 DeepSeek Harness 原生设置页/面板提供管理能力。

# 10. 完成标准

- 知识点锁定记录在题卡，无超纲；难度系数 ≤ 目标级别上限（【10】仅 CTS）；
- 测试点表格与题面、生成器、评测配置三方一致，总分 100；
- 击杀矩阵全绿：wrong 全部按预期击杀，std/brute 对拍无分歧；
- 题面零做法提示；大样例以附件 zip 提供并在题面引用；
- 题目包 `verify_package.py` / `verify_hoj_package.py` 全绿；
- 完整样例 zip 平铺 1/2/3 并提供（如需要）；PDF 整卷 / Lemon 数据已导出（如需要）；
- （有实例时）题目已发布到 Hydro/HOJ，比赛已创建，链接已给出。

# 11. 安全与边界

- 不索要、不记录 Hydro/HOJ 密码；登录凭据只经命令行参数/环境变量/网页 Cookie。
- 数据生成器、编译、评测都在本机执行；不把陌生代码上传到非可信实例。
- HOJ `import-problem` 仅 root 可用；非 root 用 `--direct`（需 problem_admin/admin）。
- 时间限制以目标评测机（Linux / Hydro / HOJ）为准，本机 Windows 计时仅作参考。
- 对远程 OJ 的批量操作先 `--dry-run`。