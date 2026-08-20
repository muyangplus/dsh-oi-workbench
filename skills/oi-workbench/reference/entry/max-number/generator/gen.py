#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数字串排序（max-number）数据生成器。

按题面「数据范围」测试点表格逐档生成 20 个测试点（1.in..20.in）。
特殊性质 A：所有 s_i 长度相等；特殊性质 B：所有 s_i 长度 <= 3。
每个测试点严格满足对应档的 n 上限 / sum|s| 上限与特殊性质。
"""
import os
import random
import sys

random.seed(20250101)


def gen_str(L):
    """生成长度为 L 的数字串：首位 1-9，其余 0-9，无前导零。"""
    s = str(random.randint(1, 9))
    for _ in range(L - 1):
        s += str(random.randint(0, 9))
    return s


def gen_case(path, idx, n_max, sum_max, prop):
    """生成一个测试点。

    prop: 'none' | 'A'（所有串等长） | 'B'（长度<=3）
    保证 1<=n<=n_max，总长度<=sum_max，每串长度 1..10（A 串等长，B 长度<=3）。
    """
    # 尽量压到各档上限，兼顾少量随机小数据
    if random.random() < 0.7:
        n = n_max
    else:
        n = random.randint(1, n_max)
    # 每个串长度至少 1，因此 n 不能超过 sum_max
    if n > sum_max:
        n = sum_max
    if n <= 0:
        n = 1

    lines = []
    if prop == 'A':
        # 所有串等长 L，n*L <= sum_max
        maxL = min(10, sum_max // n)
        if maxL <= 0:
            maxL = 1
        if random.random() < 0.7:
            L = maxL
        else:
            L = random.randint(1, maxL)
        lines = [gen_str(L) for _ in range(n)]
    elif prop == 'B':
        # 长度 <= 3，且总长 <= sum_max
        remaining = sum_max
        max_len = 3
        for _ in range(n):
            L = random.randint(1, max_len)
            # 为后面预留至少 1 的长度
            leftover = n - len(lines) - 1
            L = min(L, remaining - leftover)
            if L <= 0:
                L = 1
            lines.append(gen_str(L))
            remaining -= L
    else:
        # 无特殊性质：长度 1..10，总长 <= sum_max
        remaining = sum_max
        max_len = 10
        for _ in range(n):
            L = random.randint(1, max_len)
            leftover = n - len(lines) - 1
            L = min(L, remaining - leftover)
            if L <= 0:
                L = 1
            lines.append(gen_str(L))
            remaining -= L

    with open(os.path.join(path, f"{idx}.in"), "w", encoding="utf-8") as f:
        f.write(f"{n}\n")
        f.write("\n".join(lines) + "\n")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "data"
    os.makedirs(out, exist_ok=True)

    # 每档：(n_max, sum_max, prop) —— 与题面测试点表格逐点对齐
    configs = [
        # 点1
        (2, 20, 'none'),
        # 点2..3
        (10, 100, 'none'),
        (10, 100, 'none'),
        # 点4..5（特殊性质 A）
        (1000, 10_000, 'A'),
        (1000, 10_000, 'A'),
        # 点6..8
        (1000, 10_000, 'none'),
        (1000, 10_000, 'none'),
        (1000, 10_000, 'none'),
        # 点9..12（特殊性质 A）
        (100_000, 100_000, 'A'),
        (100_000, 100_000, 'A'),
        (100_000, 100_000, 'A'),
        (100_000, 100_000, 'A'),
        # 点13..16（特殊性质 B）
        (100_000, 1_000_000, 'B'),
        (100_000, 1_000_000, 'B'),
        (100_000, 1_000_000, 'B'),
        (100_000, 1_000_000, 'B'),
        # 点17..20
        (100_000, 1_000_000, 'none'),
        (100_000, 1_000_000, 'none'),
        (100_000, 1_000_000, 'none'),
        (100_000, 1_000_000, 'none'),
    ]
    for i, (n_max, sum_max, prop) in enumerate(configs, 1):
        gen_case(out, i, n_max, sum_max, prop)


if __name__ == "__main__":
    main()
