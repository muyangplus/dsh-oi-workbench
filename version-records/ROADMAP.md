# 分批迭代计划（ROADMAP）

> 交付定位（Q1:a）：**分批次实施计划 + 版本管理方案，先评审后执行**。
> 每批完成 = 本地全绿验证 → 写 changelog → 升版本号（0.1.x 迭代号）→ 用户确认。
> **迭代期间不发布**；下次发布时聚合为 `0.2.0`（见「版本注释」）。
> 状态图例：⬜ 未开始 / 🔵 进行中 / ✅ 已完成

## 决策回溯（对应 Q1–Q5 及评审反馈）

| # | 决策 | 影响 |
|---|---|---|
| Q1 | 交付物 = 分批次计划 + 版本管理方案，先评审后执行 | 本文件 + version-records/ 即为本次交付；功能实现待评审后逐批执行 |
| Q2 | 自定义知识库 = 需要 UI/命令增删改查（非仅仓库内维护） | 批次 1：用户层持久化 + `/oiwb kb` 命令 + Python CLI/UI |
| Q3 | 剧情 = 同场共享主线 + 跨场次连载，同时支持剧情独立/不设剧情 | 批次 3/4/5：剧情三态 `none` / `shared` / `serialized`，`none` 为缺省 |
| Q4 | IO = 标准输入输出 + 从文件读取，另支持一般 OJ 评测模式 | 批次 2：`io` 与 `judge` 双配置项贯通全链路 |
| Q5 | 一次性出一场比赛 = 描述 → 整场（多题 + 主线 + 数据 + 打包 + 建赛） | 批次 4：编排层 + 一键建赛 |
| 评审 | 迭代用 0.1.1、0.1.2 … 递增；暂时不发布；下次发布再调为 0.2 | 版本策略见 `VERSION.md`；迭代期改动只留在 dev 仓库 |

## 总览

| 批次 | 版本 | 内容 | 状态 |
|---|---|---|---|
| 批次 0 | —（基础设施） | 版本管理：本目录 + DEVELOPMENT 纪律 | ✅ 已完成 |
| 批次 1 | 0.1.1 | 用户自定义知识库 / 参考题（增删改查） | ✅ 已完成 |
| 批次 2 | 0.1.2 | 标准 IO / 文件 IO 双模式 + 一般 OJ 评测模式 | ✅ 已完成 |
| 批次 3 | 0.1.3 | 故事题面 + 故事设计能力 | ⬜ |
| 批次 4 | 0.1.4 | 一次性出一场比赛 | ⬜ |
| 批次 5 | 0.1.5 | 连续剧情 / 连载 | ⬜ |

依赖关系：批次 1、2 相互独立，可先行；批次 3 独立；批次 4 依赖 2 + 3；批次 5 依赖 3 + 4。

> **版本注释（用户约定）**：dev 迭代期间维持 `0.1` 主次版本号不变，每完成一个功能批次递增修正号
> （0.1.1 → 0.1.2 → …）；**迭代期间不发布**（不推 public、不 npm）。
> 下次发布时，把迭代期间累积改动聚合调整为 `0.2.0`，再走 public 流程
> （public dev → CI beta → PR main → 正式版 + GitHub Release + tag）。

---

## 批次 0：版本管理基础设施（已完成）

**目标**：建立「更新记录 / 版本号 / 路线图」的单一事实来源，为后续每批的变更留痕。

**交付物（已完成）**
- `version-records/README.md` — 目录用途与更新纪律
- `version-records/VERSION.md` — 版本策略 + 当前版本 + 全版本速览
- `version-records/changelog/v0.1.0.md` — dev 线基线快照
- `version-records/ROADMAP.md` — 本文件
- `DEVELOPMENT.md` 新增「版本记录纪律」一节

**验收**：文件齐备、约定清晰；后续每个批次按本批约定走 changelog + 版本号。

---

## 批次 1（v0.1.1，✅ 已完成）：用户自定义知识库 / 参考题

**用户决策（Q2:c）**：不只是仓库内约定格式，而是要有 UI / 命令做增删改查。

**范围**
1. 用户层持久化目录（与插件本体分离——npm 安装目录是只读的）：
   - 知识库卡片：`~/.dsh-oi-workbench/kb/<level>/<topic>.md`
   - 用户参考题：`~/.dsh-oi-workbench/reference/<level>/<id>/…`
   - 复用现有 `~/.dsh-oi-workbench/`（已存放 `hoj_config.json`）。
2. 目录与格式约定：
   - KB 速查卡片模板 `templates/kb-card.md` + 规范 `specs/user-content.md`：
     frontmatter 含 `topic / level / tags / difficulty / summary / pitfalls`；
   - 用户参考题沿用 `reference/` 现有问题目录结构（problem.md / spec.json / data / sample / std / brute / generator）。
3. 合并加载：技能「锁定知识点」（SKILL.md 第 1 步）先读内置 KB，再叠加用户层 KB；
   同名 `topic` 用户覆盖内置；`level` 允许新增用户自定层级。
4. 增删改查入口：
   - 斜杠命令 `/oiwb kb list|show|add|edit|rm|search`、`/oiwb ref add|…`
     （`commands/register/oiwb.md` 新增子命令）；
   - Python 工具 `ui/user_content.py`（CLI CRUD，斜杠命令桥接；可选：外部 UI 增加「知识库」页签）。
5. 校验：add/edit 强制 frontmatter 齐全、level 合法、topic 唯一；非法输入拒绝并提示。

**涉及文件（预估）**
`skills/oi-workbench/SKILL.md`、`knowledge-base/workflow.md`、新增 `specs/user-content.md`、
新增 `templates/kb-card.md`、`commands/register/oiwb.md`、新增 `ui/user_content.py`、dev `README.md`。

**验收标准**
- 无内置卡也能 `add`；`add` 后立即可被「锁定知识点」检索到；
- 同名 topic 用户覆盖内置；`rm` 只删用户层；全程无需重启；
- 端到端冒烟：用一张自定义知识点卡出一道 25 点的完整题。

---

## 批次 2（v0.1.2，✅ 已完成）：标准 IO / 文件 IO 双模式 + 一般 OJ 评测模式

**用户决策（Q4）**：除标准输入输出外，还要支持「从文件读取」，并支持一般 OJ 评测模式。

**范围**
1. 题目 spec 扩展（`spec.json` 及备考 `problem.yaml`）：
   ```json
   {
     "io":    { "type": "standard" | "file", "input": "xxx.in", "output": "xxx.out" },
     "judge": { "mode": "traditional" | "subtask" | "acm", "spj": false, "checker": "spj.cpp" }
   }
   ```
2. 全链路贯通 `io`：
   - `generator/local_judge.py`：standard 用 stdin/stdout 管道；file 在题目目录临时工作区运行，
     std 读 `xxx.in`、写 `xxx.out`，比对 `xxx.out`；
   - `generator/build_package.py` / `build_hoj_package.py` / `verify_*`：映射 `io` / `judge` 到
     Hydro `config.yaml`（`inputFile/outputFile`、`type: default|subtask|interactive|communication`、`checker`）
     与 HOJ（`fileIO`、`judgeCaseMode`、`spj`）；
   - 样例/大样例：file 模式样例仍内联，文件名按 `io` 约定。
3. 一般 OJ 评测模式：
   - `traditional`（逐点等分/不等分）、`subtask`（捆绑/依赖，现行 OI 模式）、`acm`（逐点即时判定，无部分分）三态；
   - 特殊评测 `spj`（testlib checker / interactor）随 `judge` 配置，并补 `local_judge` 支持；
   - statement 模板「输入输出 / 数据范围」小节按 `io` / `judge` 动态渲染。
4. 模板与规范同步：`templates/statement.md`、`templates/problem.yaml`、
   `specs/data-design.md`、`specs/statement-style.md`。

**验收标准**
- 同一题分别以 standard / file 模式构建、本地评测全绿、双 OJ 打包验证全绿；
- traditional / subtask / acm 三种模式各出一题跑通本地评测；
- 一个 spj 题（输出任意合法解）本地评测 + 打包验证通过。

---

## 批次 3（v0.1.3）：故事题面 + 故事设计能力

**范围**
1. 故事题面规范 `specs/story-statement.md`：
   - 结构：世界观 / 登场人物 → 剧情引入场景 → 机制设定（客观规则，零做法提示）→ 输入 / 输出 → 样例 → 数据范围；
   - **零做法提示红线**：叙事外壳不得出现算法名 / 复杂度 / 结构暗示；
   - 知识点融入指南：让剧情冲突自然指向目标知识点（表驱动示例）。
2. 模板：`templates/story.md`（故事题面骨架）+ `templates/story-card.md`（故事卡片：
   主题 / 核心冲突 / 人物 / 知识节点 / 分题剧情点）。
3. 故事设计能力 `specs/story-design.md`：
   世界观构建、冲突与悬念、角色弧光、命题-剧情绑定矩阵、复杂度控制、连载预留接口；
   SKILL.md 增「以故事包装题目」一节：出题前先出 story-card。
4. 与剧情独立兼容（Q3）：story-card 可选；无故事时走现行 `templates/statement.md`，`none` 为缺省。

**验收标准**
- 用 story-card 出一道完整「原创故事 + 知识点融入」题：题面无做法提示、本地评测全绿、打包验证通过；
- 同一知识点题给出「有故事版」与「无故事版」两份题面，均通过规范检查。

---

## 批次 4（v0.1.4）：一次性出一场比赛

**用户决策（Q5:a）**：由描述直接生成整场比赛（多题 + 故事主线 + 数据 + 打包 + 建赛）。

**范围**
1. 编排层：`generator/build_contest.py` + `verify_contest.py`，输入一份「比赛清单」：
   ```yaml
   contest:
     title:    名称
     rule:     oi | acm            # 批次 2 的赛制配置
     duration: 3h
     level:    [入门级, 提高级, 专家级]
     problems:                     # 知识点矩阵 + 难度曲线
       - { id: A, knowledge: [..], difficulty: .., story_node: .. }
     story:    none | shared | serialized   # Q3 三态
   ```
2. 批量管线：对每道题执行完整出题流程（锁定知识点 → 分数表 → std / brute / wrong →
   数据 → 击杀矩阵 → 故事题面 → 打包），收敛为「比赛包」（多题 + 共同主线 + 大样例）。
3. 建赛自动化：Hydro `manage_contest.py contest-create` 与 HOJ `manage_hoj.py` 赛程子命令
   串成 `/oiwb contest new|build|publish`；shared 模式题目顺序 = 剧情顺序。
4. 技能工作流扩展：SKILL.md 增「出一场比赛」段落。

**验收标准**
- 一段中文描述 → 生成 4 题完整比赛包：每题 25 点、击杀矩阵绿、双 OJ 打包验证全绿；
- （有实例时）一键建赛成功，题目顺序与剧情主线一致；批量操作先 `--dry-run`。

---

## 批次 5（v0.1.5）：连续剧情 / 连载

**用户决策（Q3:c）**：同场共享主线 + 跨场次连载，且支持剧情独立 / 不设剧情。

**范围**
1. 剧本仓库（版本化）：
   - `~/.dsh-oi-workbench/stories/<world>/story.yaml`：世界观 / 人物 / 时间线 / 设定事实（facts）/
     每场比赛进度弧；可随比赛包导出 / 导入（可回滚）。
2. 剧情三态（贯穿批次 3/4/5）：
   - `none`（缺省）：不设剧情，现行行为；
   - `shared`：单场内多题共享主线，题按剧情节点排序（批次 4 已内置）；
   - `serialized`：跨场次连载——出下一场前读取 story.yaml 进度与 facts，续写时校验连续性
     （人物存活、时间线不矛盾、设定不推翻），出完后推进 story.yaml 并记录弧线。
3. 连续性检查 `generator/story_check.py`：新题面 / 新比赛引用的人物、地点、事件与 story.yaml
   不一致时报错并给出修复建议。
4. SKILL.md 增「连载剧情」工作流；命令 `/oiwb story new|advance|check`。

**验收标准**
- 同一世界观连出 2 场（每场 2+ 题）比赛，人物 / 时间线 / 设定无矛盾，story.yaml 自动推进；
- 构造一个故意矛盾设定 → `story_check.py` 拦截并给出修复建议。

---

## 每批推进方式（审计门）

1. 实施该批全部改动到 dev 仓库 → 本地验证全绿（打包 / 评测 / 杀阵矩阵）；
2. 写 `version-records/changelog/v0.1.x.md`，更新 `VERSION.md` 速览与当前版本；
3. package.json 版本升到本次迭代号（0.1.x），提交并推送 `origin-dev main`；
4. **等用户确认**；
5. 迭代期间不发布（不推 public、不 npm）；
6. 用户要求「发布」时：把 0.1.1–0.1.5 聚合调整为 `0.2.0` → 压缩为标准英文 ASCII 提交
   推 public `dev` → CI 出 beta → PR `main` → CI 正式版 + GitHub Release + tag。

## 安全与边界（沿用 DEVELOPMENT.md / SKILL.md）

- 密码 / Token 只用环境变量或命令行参数；不写入代码与提交。
- 用户自定义内容仅读写用户自己的 `~/.dsh-oi-workbench/`；不执行用户内容中的代码。
- 批量建赛 / 发布先 `--dry-run`；任何时刻不直接提交 public `main`。
