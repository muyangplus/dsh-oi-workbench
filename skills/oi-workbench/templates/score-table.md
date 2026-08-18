# 分数表模板（score table）

> 出题时复制本表到题卡，逐行填写；与 `specs/score-table-design.md` 配合使用。

## 1. 测试点总览（自由分档）

| 测试点 | 约束 | 特殊性质 | 生成器参数 |
|---|---|---|---|
| $1,2$ | $n\le 10$ | 无 | seed 1-2 |
| $3\sim 5$ | $n\le 18$ | 无 | seed 3-5 |
| $6\sim 8$ | $n\le 10^2$ | A | seed 6-8 |
| $9\sim 11$ | $n\le 10^2$ | 无 | seed 9-11 |
| $12\sim 14$ | $n\le 5000$，$m=1$ | 无 | seed 12-14 |
| $15\sim 17$ | $n\le 5000$ | 无 | seed 15-17 |
| $18\sim 21$ | $n\le 10^5$ | B | seed 18-21 |
| $22\sim 25$ | $n\le 10^5$ | 无 | seed 22-25 |

共 25 个测试点，每个测试点 4 分，总分 100。

## 2. 每档内部构成（边界/极限/定向击杀/随机）

| 档 | 边界 | 极限 | 定向击杀 | 随机 | 小计 |
|---|---|---|---|---|---|
| $n\le 10$ | 1 | 0 | 1 | 0 | 2 |
| $n\le 18$ | 1 | 1 | 1 | 0 | 3 |
| ... | | | | | |

## 3. 特殊性质设计

| 性质 | 定义 | 覆盖测试点 | 生成器实现 |
|---|---|---|---|
| A | $a_i\in\{0,1\}$ | $6\sim 8, 18\sim 21$ | `rng.choice([0,1])` |
| B | 保证 $T=1$ | $18\sim 21$ | 单测 |

## 4. 题面"数据范围"小节成品

```markdown
对于所有测试数据，保证：$1\le m\le n\le 10^5$，$1\le a_i\le 10^9$。

| 测试点 | $n\le$ | 特殊性质 |
|---|---|---|
| $1,2$ | $10$ | 无 |
| ... | ... | ... |
| $22\sim 25$ | $10^5$ | 无 |

特殊性质 A：……
时间限制：1s；空间限制：512MB。
```

## 5. 大样例（附件机制）

- 样例 1-2：题面内联（小）。
- 样例 3+：大样例 `large3.zip`（含 `large3.in` / `large3.ans`），打包进 `additional_file/`，
  题面引用：`（见题目附件 [large3.zip](file://large3.zip)，该样例满足测试点 6~8 的约束。）`

## 6. 打包映射（逐点等分，推荐）

### Hydro

spec.json 用顶层 `cases`（不带 subtasks）：

```json
{
  "title": "题目名",
  "cases": [
    {"input": "1.in", "output": "1.out"},
    {"input": "2.in", "output": "2.out"}
  ]
}
```

Hydro 对无 subtasks 的 cases 自动等分 100 分；不等分时给 case 加 `"score": 5`。
捆绑评测才用 `subtasks` + `if` 依赖。

### HOJ

用 `generator/build_hoj_package.py`：

```json
{
  "title": "题目名",
  "type": "oi",
  "judgeCaseMode": "default",
  "cases": [
    {"input": "1.in", "output": "1.out", "score": 4},
    {"input": "2.in", "output": "2.out", "score": 4}
  ]
}
```

子任务模式：`judgeCaseMode` 为 `subtask_lowest` 或 `subtask_average`，
同组 case 设置相同 `groupNum`（从 1 开始）。
