# 生成器与本地评测（generator/）

把「题目目录」打包为 **Hydro** / **HOJ** 原生题目包，并支持本地 OI 评测。

## 使用

```powershell
# Hydro 包
python generator/build_package.py examples\demo --out P01.zip
python generator/verify_package.py P01.zip

# HOJ 包
python generator/build_hoj_package.py examples\demo --out P01-hoj.zip
python generator/verify_hoj_package.py P01-hoj.zip

# 本地评测（C++ 固定 -O2 -std=c++14 -static）
python generator/local_judge.py examples\demo --source std\std.cpp

# 故事卡生成（TODO1）
python generator/story_card.py --title 登山选拔 --topic 最长上升子序列 --characters "队长:冷面王" --output story.md

# 连续剧情/连载连续性检查（TODO3）
python generator/story_continuity.py templates/story.yaml
python generator/story_continuity.py --all <剧本仓库目录>

# 一键出整场比赛（TODO2）：完整样例 + PDF + Lemon(.cdf) + Hydro/HOJ
python generator/build_contest.py --contest LKCP --problems <题目目录>... --story-dir <故事目录> --out dist

# 从比赛描述 manifest 一键生成整场（generate_contest）
python generator/generate_contest.py --manifest contest.json

# spj/交互题样例验证自动化（标程 AC + 错误程序被击杀）
python generator/validate_spj.py --problem <题目目录>

# 一键校验 reference/ 全部自出参考题
python generator/build_all_reference.py
# 一键构建并校验 Hydro/HOJ zip
python generator/build_all_reference.py --build --out tmp/reference-zips

# 盲审：代码发布前审读仓库文本
python generator/blind_review.py --release
# 盲审：生成题目文件后审读该题目目录
python generator/blind_review.py --problem examples\demo
```

## 题目目录结构

```text
P01/
├── spec.json      # 配置（title/pid/tags/time/memory/subtasks/judgeCaseMode/fileIO/...）
├── problem.md     # 题面 Markdown
├── data/          # 隐藏测试数据 1.in/1.out（必需）
├── sample/        # 样例（可选）
├── std/           # 标程（可选）
└── solution/      # 题解（可选）
```

## spec.json 示例（OI 部分分，双 OJ 通用）

```json
{
  "title": "合并果子",
  "pid": "P1001",
  "tags": ["贪心", "堆"],
  "time": "1000ms",
  "memory": "256m",
  "stackLimit": 256,
  "type": "oi",
  "judgeCaseMode": "default",
  "languages": ["C++"],
  "cases": [
    {"input": "1.in", "output": "1.out", "score": 5},
    {"input": "2.in", "output": "2.out", "score": 5}
  ],
  "compile": {"cpp": "-O2 -std=c++14 -static"}
}
```

## 生成物布局

### Hydro（build_package.py）

| zip 内路径 | 导入行为 |
|---|---|
| `problem.yaml` | 标题/pid/标签/难度 |
| `problem.md` | 题面内容 |
| `testdata/config.yaml` | 评测配置：time/memory/subtasks/checker |
| `testdata/*.in/.out` | 测试数据 |
| `data/sample/*` | 展示样例 + 测试数据 |
| `std/*` | 导入为 AC 评测记录 |
| `solution/*` | 题解 |

### HOJ（build_hoj_package.py）

以 HOJ 官方「导出题目」zip 格式为基准：

```text
P01-hoj.zip
├── problem_P1001.json   # HOJ 导入 JSON（judgeMode/languages/samples/tags/problem/codeTemplates）
└── problem_P1001/       # 测试数据 1.in/1.out ... + info（官方导出必需）
```

- `problem_P1001/` 内必须包含 `info`（mode/judgeCaseMode/version/testCasesSize/testCases，
  每个测试点含 outputMd5/outputSize/allStrippedOutputMd5/EOFStrippedOutputMd5）。
- `problem.hint` 默认自动填充题面 `## 数据范围` 小节（也可在 spec.json 用 `hint` 覆盖），
  导入后显示在 HOJ 题目的「提示」区。
- `verify_hoj_package.py` 检查：info 存在、info.testCases 与 samples 一致、outputMd5 匹配、
  samples 文件存在、OI 总分 100、judgeMode/judgeCaseMode 合法、problem 关键字段齐全。

## 盲审（blind_review.py）

两道闸口各跑一次，审读“脱离上下文显得奇怪 / 不合体”的文本表达：

```powershell
# 代码发布前：扫仓库用户面向文本
python generator/blind_review.py --release
# 生成题目文件后：审读题目目录（problem.md / solution / spec.json 等）
python generator/blind_review.py --problem <题目目录>
# 通用：审读指定文件/目录；--fix 只做安全修复（去行尾空白/BOM）
python generator/blind_review.py <路径>...
```

检查项：

- 无上下文内部语境泄漏：括号里带“批次 + 数字”的注解、批次数字后带冒号的标题、
  “版本号相关内部措辞”、按内部路线图文档分批推进的表述，以及 changelog / ROADMAP / v0.x 版本号等；
- 硬件规格泄漏：CPU 型号、主频数值、内存规格、核开关特性、评测机器硬件信息等；
- 无上下文时间/事件注解：形如“某某后固定”“某某定稿”的括号注解；
- 题目文件内部术语泄漏：spec.json / 生成器 / 对拍 / 击杀矩阵 / 本地评测 / 打包 等；
- 占位 / 半成品残留：TODO / TBD / FIXME / XXX / 待补充 / 待完善 / 占位 等（路线图条目内 TODO 豁免）；
- 编码问题（非法 UTF-8 / 替换符 / NUL）、行尾空白、异常重复标点、以“，：、；”收尾的未完句。

退出码：发现问题返回 1（发布/打包前应清零）；BOM 仅提示、不阻断。

## 本地评测（local_judge.py）

- 编译：`g++ -O2 -std=c++14 -static`
- 支持 stdio 与 `spec.json` 中的 `fileIO`
- 输出比较：OI 全文比较（过滤行末空格及文末换行）
- 逐点输出 AC/WA/TLE/RE 与得分
- 支持 testlib checker（`judge.checker`）与交互题 interactor（`judge.interactor`）：
  自动加 `-I generator/testlib`；内置 testlib.h v0.9.41（MIT，见 `testlib/README.md`）
- Windows 本地时间仅参考；正式时限以全国统一评测机为准

## 完整样例 / 整卷 PDF / Lemon（实战能力）

```powershell
# 完整样例打包：additional_file/<题>_samples.zip 平铺 1/2/3 + 更新题面引用
python generator/package_samples.py --problems examples/demo --story-dir <故事题面目录> --combined samples.zip

# 整卷 PDF：官方风格封面信息表/注意事项/页眉页脚/样例行号
python generator/build_statement_pdf.py --contest "LKCP" --subtitle "2026 第二轮认证" \
    --problems examples/demo --story-dir <故事题面目录> --out paper.pdf

# Lemon 评测机比赛数据：<比赛>.cdf + data/<题>/<题><编号>.in/.out + source/std 选手
python generator/export_lemon.py --contest LKCP --problems examples/demo --out dist/lemon
# 可自定义 .cdf 的 contestTitle 与文件名（默认 contestTitle=--contest，文件=<contest>.cdf）
python generator/export_lemon.py --contest LKCP --contest-title "LKCP 非专业级软件能力认证" \
    --cdf-name LKCP2026.cdf --problems examples/demo --out dist/lemon
```

约定：

- **完整样例 zip 平铺**：`1.in/1.out`、`2.in/2.out`、`3.in/3.out`，无大/小样例子目录、无 readme；
  样例 3 为大样例（默认 `data/6`）。
- **PDF 大样例引用**：`见选手目录下的 <题>/<题>3.in 与 <题>/<题>3.ans。该样例满足测试点 6, 7, 8 的约束条件。`
- **Lemon 目录**：`<contest>.cdf`（LemonLime 比赛文件）+ `data/<英文题名>/<英文题名><编号>.in/.out`
  + `source/std/<英文题名>.cpp`（std 选手）。

## 导入 OJ

- Hydro：网页「从 Hydro 导入」或 `python hydro-bridge/publish_problem.py`
- HOJ：后台「题目管理 → 导入题目」或 `python hoj-bridge/publish_problem.py`