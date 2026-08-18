---
name: oi-workbench
description: 当用户需要创作 OI 风格竞赛题目（入门级/提高级/专家级）、设计测试点表格与特殊性质、针对性构造测试数据、制作大样例附件、生成题目变式、打包 Hydro/HOJ 兼容题目包、进行本地评测、或把题目/比赛/用户/团队发布到 Hydro 与 HOJ 时调用。覆盖知识点锁定、分数表设计、数据构造、评测验证、打包、双 OJ 管理与 UI 管理的完整流程。
---

# 角色

作为严谨的 OI 出题人执行任务。本技能资源目录下：
`knowledge-base/`（参考  大纲整理的速查，非 官方原文）、`specs/`（规范）、`templates/`（模板）、
`generator/`（打包器 + 本地评测）、`hydro-bridge/`（Hydro 对接）、
`hoj-bridge/`（HOJ 对接）、`ui/`（Python 外部管理 UI）、
`commands/`（斜杠指令说明）、`reference/`（自出原创参考题）。
主动读写文件、编译、运行和修复；不要只给用户命令让其代为执行。

# 0. 全国统一评测规范（OI 2025 后固定）

- **编译指令（C++）**：`-O2 -std=c++14 -static`
- **评测机基准**：Intel Core Ultra 9 285K CPU @ 3.70 GHz（关闭睿频与能效核），内存 96 GB；
  所有时限均以此配置为准，本地 Windows 计时只作参考。
- 输出比较：全文比较（过滤行末空格及文末换行）。
- 源文件 ≤ 100 KiB；`main` 返回 `int` 且正常结束返回 0；栈空间与题目内存限制一致；
  禁止源码修改编译器参数或使用系统结构相关指令。
- 题面风格参考 `reference/entry/` 与 `reference/intermediate/` 自出原创题。

# 1. 出题前置（每道题必做）

1. **锁定知识点**：读取 `knowledge-base/level-1-basic.md` / `level-2-intermediate.md` /
   `level-3-expert.md` 中对应级别清单，
   按 `knowledge-base/workflow.md` 确定：目标级别、难度系数区间、
   主知识点 1 个、辅助知识点 ≤3 个、超纲检查结论。
2. **填母题卡**：用 `templates/variation.md` 的母题卡模板记录。

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

# 5. 题面与样例

按 `specs/statement-style.md` 与 `templates/statement.md` 编写：
结构固定、变量首次出现处标范围、**零做法提示**、数据范围用总体保证 +
测试点表格 + 特殊性质定义；无"提示"小节放做法。

样例机制：
- 样例 1-2：题面内联（小规模，覆盖不同分支）。
- **大样例不进题面**：放 `large_sample/`，打成 zip 后放入 `additional_file/`
  （Hydro 打包进 `additional_file/`，导入为附加文件，不参与评测）；
  题面引用格式：`（见题目附件 [xxx.zip](file://xxx.zip)，该样例满足测试点 X~Y 的约束。）`
- 大样例由生成器产出（满足对应档约束），答案由 std 生成并核验。
- HOJ 无 `file://` 附件机制：导入后需在 HOJ 后台把大样例放到可下载资源或说明中。

# 6. 变式

用户要求变式时读取 `specs/variation-design.md`：从母题卡出发，只动 1-2 个轴，
重锁定知识点、**重设计测试点表格与特殊性质**、重做击杀矩阵，变式登记回母题卡。

# 7. 打包

1. **Hydro 原生包**：
   `python generator/build_package.py <题目目录> --out <ID>.zip`
   校验：`python generator/verify_package.py <ID>.zip`
2. **HOJ 原生包**：
   `python generator/build_hoj_package.py <题目目录> --out <ID>-hoj.zip`
   校验：`python generator/verify_hoj_package.py <ID>-hoj.zip`
3. 包内布局：
   - Hydro：`problem.yaml` + `problem.md` + `testdata/`（config.yaml + 数据）
     + `data/sample/` + `additional_file/` + `std/` + `solution/`
   - HOJ：`problem_<pid>.json` + `problem_<pid>/测试数据`
4. 校验必须全绿。

# 8. 发布到 OJ

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

# 9. UI 管理功能

## 9.1 斜杠指令（Slash Commands）

采用**通用根指令 + 子命令**设计，避免把指令绑定死到单个 OJ，方便后续扩展 Hydro / 其他 OJ。

| 指令 | 执行动作 |
|---|---|
| `/oiwb` 或 `/oj` | 打开 OI Workbench 默认管理面板 |
| `/oiwb panel` | 启动 Python 外部 UI（`python ui/hoj_ui.py`）并打开 HOJ 管理页 |
| `/oiwb hoj problems` | HOJ 题目列表 |
| `/oiwb hoj contests` | HOJ 比赛列表 |
| `/oiwb hoj publish <题目目录>` | 发布题目到 HOJ |
| `/oiwb hoj rejudge <submitId>` | 重判指定 HOJ 提交 |
| `/hoj` 或 `/hoj-panel` | `/oiwb panel` 的别名（启动 Python 外部 UI） |
| `/hoj help` | 显示 HOJ 指令列表（兼容旧用法） |

> 这些是技能级斜杠指令：用户输入 `/oiwb ...` / `/oj ...` / `/hoj ...` 时，按本表解析并执行。
> 后续新增 Hydro 等平台时，只需增加 `/oiwb hydro ...` 子命令，不需要改掉 `/hoj`。

## 9.2 外部 Python UI（推荐）

不再使用 DSH 内部 `render_ui`，改为启动 **Python 外部管理 UI**：

```bash
python ui/hoj_ui.py --host 0.0.0.0 --port 6163 --base https://hoj.example.com
```

- 浏览器访问：`http://localhost:6163/`
- 手机/局域网访问：`http://<本机IP>:6163/`
- UI 页面：`ui/hoj-admin.html`
- Python 服务端代理 HOJ API，并保存 HOJ Cookie，避免 `file://` 与 CORS 问题
- 配置和 Cookie 保存到 `~/.dsh-oi-workbench/`

## 9.3 旧版浏览器单页

`ui/hoj-admin.html` 也可单独用浏览器打开，但**必须通过 `python ui/hoj_ui.py` 提供 HTTP 服务**，
不要直接用 `file://` 打开。

# 10. 完成标准

- 知识点锁定记录在题卡，无超纲；难度系数 ≤ 目标级别上限（【10】仅 CTS）；
- 测试点表格与题面、生成器、评测配置三方一致，总分 100；
- 击杀矩阵全绿：wrong 全部按预期击杀，std/brute 对拍无分歧；
- 题面零做法提示；大样例以附件 zip 提供并在题面引用；
- 题目包 `verify_package.py` / `verify_hoj_package.py` 全绿；
- （有实例时）题目已发布到 Hydro/HOJ，比赛已创建，链接已给出。

# 11. 安全与边界

- 不索要、不记录 Hydro/HOJ 密码；登录凭据只经命令行参数/环境变量/网页 Cookie。
- 数据生成器、编译、评测都在本机执行；不把陌生代码上传到非可信实例。
- HOJ `import-problem` 仅 root 可用；非 root 用 `--direct`（需 problem_admin/admin）。
- 时间限制以目标评测机（Linux / Hydro / HOJ）为准，本机 Windows 计时仅作参考。
- 对远程 OJ 的批量操作先 `--dry-run`。