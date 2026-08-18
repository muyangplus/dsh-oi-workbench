# 验证记录：网络中继（S2）

- 算法：枚举子集 + Kruskal
- 时间复杂度：O(2^k (m+nk) log)
- 测试点数量：10
- 样例：已通过标程验证
- 数据生成：python generator/gen.py data
- 标程编译：g++ -O2 -std=c++14 -static std/std.cpp
- 答案生成：标程运行生成 data/*.out
- 包校验：uild_package.py --check / uild_hoj_package.py --check 通过
- 状态：✅ 可复现
