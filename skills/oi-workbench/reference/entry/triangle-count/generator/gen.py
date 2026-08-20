#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三角形计数（triangle）数据生成器。

按题面「数据范围」测试点表格逐档生成 N=20 个测试点：

| 测试点 | n<=   | a_i<=   | 特殊性质 |
| 1,2    | 10    | 10^3    | 无       |
| 3,4    | 100   | 10^3    | A        |
| 5~7    | 500   | 10^6    | 无       |
| 8~10   | 500   | 10^9    | A        |
| 11~14  | 2000  | 10^6    | B        |
| 15~18  | 5000  | 10^9    | 无       |
| 19,20  | 5000  | 10^9    | A        |

特殊性质 A：所有 a_i 互不相同。
特殊性质 B：a_i 已按非降序给出。
"""
import os
import random
import sys

random.seed(20250104)

# (n, a_max, sorted_flag, distinct_flag)
POINTS = [
    (10, 1000, False, False),        # 1
    (10, 1000, False, False),        # 2
    (100, 1000, False, True),        # 3
    (100, 1000, False, True),        # 4
    (500, 10**6, False, False),      # 5
    (500, 10**6, False, False),      # 6
    (500, 10**6, False, False),      # 7
    (500, 10**9, False, True),       # 8
    (500, 10**9, False, True),       # 9
    (500, 10**9, False, True),       # 10
    (2000, 10**6, True, False),      # 11
    (2000, 10**6, True, False),      # 12
    (2000, 10**6, True, False),      # 13
    (2000, 10**6, True, False),      # 14
    (5000, 10**9, False, False),     # 15
    (5000, 10**9, False, False),     # 16
    (5000, 10**9, False, False),     # 17
    (5000, 10**9, False, False),     # 18
    (5000, 10**9, False, True),      # 19
    (5000, 10**9, False, True),      # 20
]


def gen_vals(n, a_max, sorted_flag, distinct_flag):
    if distinct_flag:
        # 该性质档均满足 n <= a_max，可保证互不相同
        vals = random.sample(range(1, a_max + 1), n)
    else:
        vals = [random.randint(1, a_max) for _ in range(n)]
    if sorted_flag:
        vals.sort()
    return vals


def clear_data(out):
    """清空 data 目录下旧 in/out。"""
    if os.path.isdir(out):
        for f in os.listdir(out):
            if f.endswith(".in") or f.endswith(".out"):
                os.remove(os.path.join(out, f))
    os.makedirs(out, exist_ok=True)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "data"
    clear_data(out)
    for idx, (n, a_max, sorted_flag, distinct_flag) in enumerate(POINTS, 1):
        vals = gen_vals(n, a_max, sorted_flag, distinct_flag)
        with open(os.path.join(out, f"{idx}.in"), "w", encoding="utf-8") as f:
            f.write(f"{n}\n")
            f.write(" ".join(map(str, vals)) + "\n")


if __name__ == "__main__":
    main()
