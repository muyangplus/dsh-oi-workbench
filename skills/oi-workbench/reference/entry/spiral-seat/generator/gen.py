#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""螺旋座位（spiral-seat）数据生成器。

按题面「数据范围」测试点表格逐档生成 20 个测试点（1.in..20.in）。
特殊性质 A：n == m；特殊性质 B：k 位于最外圈。
每个测试点严格满足对应档的 n,m 上限、k<=n*m 与特殊性质。
"""
import os
import random
import sys

random.seed(20250102)


def outer_k(n, m):
    """在最外圈随机选一格，返回其标准螺旋编号 k（保证 k 位于最外圈）。

    螺旋编号（外圈）：顶行从左到右、右列从上到下（不含左上角）、
    底行从右到左（不含右下角）、左列从下到上（不含左下/左上）。
    """
    top = m                       # 顶行 (1,c), c=1..m
    right = max(n - 1, 0)         # 右列 (r,m), r=2..n
    bottom = max(m - 1, 0)        # 底行 (n,c), c=1..m-1
    left = max(n - 2, 0)          # 左列 (r,1), r=2..n-1
    total = top + right + bottom + left
    p = random.randrange(total)

    if p < top:
        c = p + 1
        return c                                  # (1,c)
    p -= top
    if p < right:
        r = p + 2
        return m + (r - 1)                        # (r,m)
    p -= right
    if p < bottom:
        c = (m - 1) - p                           # c = m-1 .. 1
        return m + (n - 1) + (m - c)              # (n,c)
    p -= bottom
    r = (n - 1) - p                               # r = n-1 .. 2
    return m + (n - 1) + (m - 1) + (n - r)        # (r,1)


def gen_nm(n_max, m_max):
    if random.random() < 0.7:
        n = n_max
        m = m_max
    else:
        n = random.randint(1, n_max)
        m = random.randint(1, m_max)
    return n, m


def gen_case(path, idx, n, m, k):
    with open(os.path.join(path, f"{idx}.in"), "w", encoding="utf-8") as f:
        f.write(f"{n} {m} {k}\n")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "data"
    os.makedirs(out, exist_ok=True)

    # 每档：(n_max, m_max, prop)，prop 为 'none'|'A'|'B'
    configs = [
        # 点1..2（n,m<=10）
        (10, 10, 'none'),
        (10, 10, 'none'),
        # 点3..4（n,m<=100，A：n==m）
        (100, 100, 'A'),
        (100, 100, 'A'),
        # 点5..7（n,m<=10^3）
        (1000, 1000, 'none'),
        (1000, 1000, 'none'),
        (1000, 1000, 'none'),
        # 点8..10（n,m<=10^5，A：n==m）
        (100_000, 100_000, 'A'),
        (100_000, 100_000, 'A'),
        (100_000, 100_000, 'A'),
        # 点11..14（n,m<=10^9，B：k 位于最外圈）
        (10**9, 10**9, 'B'),
        (10**9, 10**9, 'B'),
        (10**9, 10**9, 'B'),
        (10**9, 10**9, 'B'),
        # 点15..20（n,m<=10^9）
        (10**9, 10**9, 'none'),
        (10**9, 10**9, 'none'),
        (10**9, 10**9, 'none'),
        (10**9, 10**9, 'none'),
        (10**9, 10**9, 'none'),
        (10**9, 10**9, 'none'),
    ]

    for i, (n_max, m_max, prop) in enumerate(configs, 1):
        if prop == 'A':
            if random.random() < 0.7:
                n = m = n_max
            else:
                n = m = random.randint(1, n_max)
            k = random.randint(1, n * m)
        elif prop == 'B':
            n, m = gen_nm(n_max, m_max)
            k = outer_k(n, m)
        else:
            n, m = gen_nm(n_max, m_max)
            k = random.randint(1, n * m)
        gen_case(out, i, n, m, k)


if __name__ == "__main__":
    main()
