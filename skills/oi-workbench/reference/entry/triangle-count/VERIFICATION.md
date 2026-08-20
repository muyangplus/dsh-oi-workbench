# 验证记录：三角形计数（J4）

- 算法：排序 + 双指针
- 时间复杂度：O(n^2)
- 测试点数量：10
- 样例：已通过标程验证
- 数据生成：python generator/gen.py data
- 标程编译：g++ -O2 -std=c++14 -static std/std.cpp
- 答案生成：标程运行生成 data/*.out
- 包校验：uild_package.py --check / uild_hoj_package.py --check 通过
- 状态：✅ 可复现

## 数据一致性修正（题面为准）

- 背景：原数据仅 10 个测试点，与题面「数据范围」表格（20 点）不符。
- 修正：严格按题面测试点表格逐档重写 `generator/gen.py`（seed=20250104，N=20）：
  - 点 1..2：n≤10，a_i≤10^3，无特殊性质；
  - 点 3..4：n≤100，a_i≤10^3，特殊性质 A（两两互不相同）；
  - 点 5..7：n≤500，a_i≤10^6，无特殊性质；
  - 点 8..10：n≤500，a_i≤10^9，特殊性质 A；
  - 点 11..14：n≤2000，a_i≤10^6，特殊性质 B（已按非降序给出）；
  - 点 15..18：n≤5000，a_i≤10^9，无特殊性质；
  - 点 19..20：n≤5000，a_i≤10^9，特殊性质 A。
  重新生成 `data/1.in..20.in`，用 std 生成 `data/1.out..20.out`；同步 `spec.json` 的 `cases` 为 20 项（每项 5 分，总分 100），删除遗留 subtasks，保留 time/memory 等字段。
- 验证：
  - `local_judge.py triangle-count --source std/std.cpp` → **[result] 100/100**；
  - 测试点表格点数 20 == data 中 .in 对数 20 == spec.json cases 数 20；
  - seed=20250104；std 未改动（O(n^2) 最大规模约 110ms < 1s，无超时）。
