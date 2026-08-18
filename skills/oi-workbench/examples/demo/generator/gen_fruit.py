#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_fruit.py —— 「果园分装」确定性数据生成器（固定 seed，可复现）。

25 个测试点 × 4 分，灵活分档（与题面测试点表格一致）：
  1,2        n<=10      无
  3~5        n<=18      无
  6~8        n<=100     A（所有 ai 相等）
  9~11       n<=100     无
  12~14      n<=5000    B（ai 两两不同）
  15~17      n<=5000    无
  18~21      n<=1e5     A
  22~25      n<=1e5     无
用法: python gen_fruit.py [输出目录]
"""
import os
import random
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "data"
os.makedirs(OUT, exist_ok=True)


def emit(idx, n, vals, note=""):
    path = os.path.join(OUT, f"{idx}.in")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{n}\n")
        f.write(" ".join(map(str, vals)) + "\n")
    print(f"{idx:02d}.in  n={n:<6} {note}")


def write(idx, n, gen, seed, note):
    rng = random.Random(seed)
    emit(idx, n, gen(rng, n), note)


# ---- 1,2: n<=10 ----
write(1, 1, lambda r, n: [1], 1, "边界 n=1")
write(2, 2, lambda r, n: [r.randint(1, 100), r.randint(1, 100)], 2, "边界 n=2")
# ---- 3~5: n<=18 ----
write(3, 18, lambda r, n: [r.randint(1, 100) for _ in range(n)], 3, "随机 18")
write(4, 18, lambda r, n: [7] * n, 4, "全同 18")
write(5, 18, lambda r, n: list(range(1, n + 1)), 5, "递增 18")
# ---- 6~8: n<=100, 性质 A（全相等）----
write(6, 100, lambda r, n: [1] * n, 6, "性质A 全 1")
write(7, 99, lambda r, n: [10**9] * n, 7, "性质A 全 1e9")
write(8, 100, lambda r, n: [5] * n, 8, "性质A 全 5")
# ---- 9~11: n<=100 ----
write(9, 100, lambda r, n: [r.randint(1, 1000) for _ in range(n)], 9, "随机 100")
write(10, 100, lambda r, n: [i * 10 for i in range(n, 0, -1)], 10, "递减 100")
write(11, 100, lambda r, n: list(range(1, n + 1)), 11, "递增 100")
# ---- 12~14: n<=5000, 性质 B（两两不同）----
write(12, 5000, lambda r, n: r.sample(range(1, 10**9), n), 12, "性质B 互异 5000")
write(13, 4999, lambda r, n: r.sample(range(1, 10**9), n), 13, "性质B 互异 4999")
write(14, 5000, lambda r, n: [i * 199999 + 1 for i in range(1, n + 1)], 14, "性质B 等差递增")
# ---- 15~17: n<=5000 ----
write(15, 5000, lambda r, n: [r.randint(1, 10**9) for _ in range(n)], 15, "随机 5000")
write(16, 5000, lambda r, n: [10**9] * n, 16, "全同 1e9（击杀 int 溢出）")
write(17, 2, lambda r, n: [10**9, 10**9], 17, "边界 n=2 最大值")
# ---- 18~21: n<=1e5, 性质 A ----
write(18, 100000, lambda r, n: [1] * n, 18, "性质A 全 1 大")
write(19, 100000, lambda r, n: [10**9] * n, 19, "性质A 全 1e9（击杀 int 溢出）")
write(20, 99999, lambda r, n: [2] * n, 20, "性质A 全 2")
write(21, 100000, lambda r, n: [10**8] * n, 21, "性质A 全 1e8（击杀 int 溢出）")
# ---- 22~25: n<=1e5 ----
write(22, 100000, lambda r, n: [r.randint(1, 10**9) for _ in range(n)], 22, "随机 1e5")
write(23, 100000, lambda r, n: [10**9 - i for i in range(n)], 23, "递减 1e9..1（击杀 int 溢出）")
write(24, 100000, lambda r, n: [10**9 if i % 2 == 0 else 1 for i in range(n)], 24, "1e9/1 交替")
write(25, 100000, lambda r, n: [r.randint(10**8, 10**9) for _ in range(n)], 25, "大值随机（击杀 int 溢出）")

print("done: 25 个测试点（灵活档：1,2 / 3-5 / 6-8A / 9-11 / 12-14B / 15-17 / 18-21A / 22-25）")
