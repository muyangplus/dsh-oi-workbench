#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异或为零（xorzero）数据生成器。

按题面「数据范围」测试点表格逐档生成 N=20 个测试点：

| 测试点 | n<=       | 特殊性质 |
| 1      | 10        | 无       |
| 2,3    | 100       | A        |
| 4,5    | 100       | 无       |
| 6~8    | 10^3      | A        |
| 9~11   | 10^3      | 无       |
| 12~14  | 10^5      | B        |
| 15~17  | 10^5      | 无       |
| 18~20  | 5*10^5    | 无       |

整体约束：0 <= a_i < 2^20。
特殊性质 A：所有 a_i 均相等。
特殊性质 B：a_i ∈ {0, 1}。
"""
import os
import random
import sys

random.seed(20250103)

MASK = (1 << 20) - 1

# (n, mode)：mode 0=随机，1=全相等，2=0/1
POINTS = [
    (10, 0),                       # 1
    (100, 1),                      # 2
    (100, 1),                      # 3
    (100, 0),                      # 4
    (100, 0),                      # 5
    (1000, 1),                     # 6
    (1000, 1),                     # 7
    (1000, 1),                     # 8
    (1000, 0),                     # 9
    (1000, 0),                     # 10
    (1000, 0),                     # 11
    (100000, 2),                   # 12
    (100000, 2),                   # 13
    (100000, 2),                   # 14
    (100000, 0),                   # 15
    (100000, 0),                   # 16
    (100000, 0),                   # 17
    (500000, 0),                   # 18
    (500000, 0),                   # 19
    (500000, 0),                   # 20
]


def gen_vals(n, mode):
    if mode == 1:
        v = random.randint(0, MASK)
        return [v] * n
    if mode == 2:
        return [random.randint(0, 1) for _ in range(n)]
    return [random.randint(0, MASK) for _ in range(n)]


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
    for idx, (n, mode) in enumerate(POINTS, 1):
        vals = gen_vals(n, mode)
        with open(os.path.join(out, f"{idx}.in"), "w", encoding="utf-8") as f:
            f.write(f"{n}\n")
            f.write(" ".join(map(str, vals)) + "\n")


if __name__ == "__main__":
    main()
