#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三组分配（team-assign）数据生成器。

按题面「数据范围」测试点表格逐档生成 20 个测试点（n 均为偶数）：
- 1,2     : n<=10，无特殊性质
- 3,4     : n<=30，无特殊性质
- 5..7    : n<=60，特殊性质 A（a_{i,2}=a_{i,3}=0）
- 8..10   : n<=60，无特殊性质
- 11..13  : n<=100，特殊性质 B（a_{i,3}=0）
- 14..16  : n<=100，特殊性质 C（三列在 [0, 2*10^4] 独立均匀随机）
- 17..20  : n<=100，无特殊性质

总体约束：2<=n<=100 且 n 为偶数；0<=a_{i,j}<=2*10^4。
"""
import os
import random
import sys

random.seed(20250105)


def gen(path, idx, n, prop):
    lines = []
    for _ in range(n):
        if prop == 'A':
            v = [random.randint(0, 20000), 0, 0]
        elif prop == 'B':
            v = [random.randint(0, 20000), random.randint(0, 20000), 0]
        else:  # 'none' 与 'C' 都是三列在 [0,20000] 内随机
            v = [random.randint(0, 20000) for _ in range(3)]
        lines.append(" ".join(map(str, v)))
    with open(os.path.join(path, "%d.in" % idx), "w", encoding="utf-8") as f:
        f.write("%d\n" % n)
        f.write("\n".join(lines) + "\n")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "data"
    os.makedirs(out, exist_ok=True)
    # (n, prop)
    configs = [
        (6, 'none'),
        (10, 'none'),
        (20, 'none'),
        (30, 'none'),
        (40, 'A'),
        (60, 'A'),
        (60, 'A'),
        (60, 'none'),
        (50, 'none'),
        (40, 'none'),
        (100, 'B'),
        (80, 'B'),
        (100, 'B'),
        (100, 'C'),
        (100, 'C'),
        (80, 'C'),
        (100, 'none'),
        (100, 'none'),
        (100, 'none'),
        (100, 'none'),
    ]
    assert len(configs) == 20
    for i, (n, prop) in enumerate(configs, 1):
        gen(out, i, n, prop)


if __name__ == "__main__":
    main()
