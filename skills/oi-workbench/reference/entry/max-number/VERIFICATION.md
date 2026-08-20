# 验证记录：数字串排序（J1）

- 算法：字符串排序 / 贪心
- 时间复杂度：O(n L log n)
- 测试点数量：10
- 样例：已通过标程验证
- 数据生成：python generator/gen.py data
- 标程编译：g++ -O2 -std=c++14 -static std/std.cpp
- 答案生成：标程运行生成 data/*.out
- 包校验：uild_package.py --check / uild_hoj_package.py --check 通过
- 状态：✅ 可复现

## 数据一致性修正（题面为准）

- 背景：原生成器仅产出 10 个测试点（且存在 n_max 参数未生效的 bug），与题面「数据范围」表格（20 点）不一致。
- 修正：按题面表格逐档重写 `generator/gen.py`（seed=20250101），重新生成 20 个测试点
  （`data/1.in..20.in`）；由 std 生成对应 `data/*.out`；`spec.json` cases 同步为 20 点（等分，总分 100）。
- 验证：`generator/local_judge.py --source std/std.cpp` 全部 AC（100/100）；
  测试点表格点数 == data 对数 == spec cases 数（=20），由 `tools/ci_quality.py` 一致性检查复核。
