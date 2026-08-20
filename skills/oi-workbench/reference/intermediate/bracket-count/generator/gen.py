#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bracket-count 数据生成器（严格对齐 problem.md 数据范围表格，共 20 点）。

seed = 20250107（题名给定），所有生成可复现。

测试点表格（题面为准）：
  - 点 1..2        n<=10    d<=n            无特殊性质
  - 点 3..5        n<=100   d<=n            特殊性质 A (d<=10)
  - 点 6..8        n<=100   d<=n            无特殊性质
  - 点 9..11       n<=1000  d=1             特殊性质 B (d=1)
  - 点 12..14      n<=1000  d<=10           特殊性质 A
  - 点 15..17      n<=5000  d=1             特殊性质 B (d=1)
  - 点 18..20      n<=5000  d<=n            无特殊性质

整体约束：1<=n<=5000，1<=d<=n。
输出：data/1.in .. data/20.in，每行 "n d"。
"""
import os
import random
import sys

SEED = 20250107

def gen(path, idx, n, d):
    with open(os.path.join(path, f"{idx}.in"), "w", encoding="utf-8") as f:
        f.write(f"{n} {d}\n")

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "data"
    os.makedirs(out, exist_ok=True)
    rnd = random.Random(SEED)

    # 每个点: (n, d)，手工保证边界/极限覆盖 + 随机填充满足当档约束。
    configs = [
        # 点 1..2：n<=10，d<=n，无特殊性质
        (1, 1),
        (10, 10),
        # 点 3..5：n<=100，特殊性质 A（d<=10）
        (100, 10),
        (50, 1),
        (80, rnd.randint(1, min(10, 80))),
        # 点 6..8：n<=100，无特殊性质
        (100, 100),
        (100, rnd.randint(10, 100)),
        (99, rnd.randint(1, 99)),
        # 点 9..11：n<=1000，特殊性质 B（d=1）
        (1000, 1),
        (500, 1),
        (1000, 1),
        # 点 12..14：n<=1000，特殊性质 A（d<=10）
        (1000, 10),
        (800, rnd.randint(1, 10)),
        (1000, rnd.randint(1, 10)),
        # 点 15..17：n<=5000，特殊性质 B（d=1）
        (5000, 1),
        (3000, 1),
        (5000, 1),
        # 点 18..20：n<=5000，无特殊性质
        (5000, 5000),
        (5000, rnd.randint(1000, 5000)),
        (4000, rnd.randint(1, 4000)),
    ]
    assert len(configs) == 20, len(configs)

    # 清空旧 in/out
    for fn in os.listdir(out):
        if fn.endswith(".in") or fn.endswith(".out"):
            os.remove(os.path.join(out, fn))

    for idx, (n, d) in enumerate(configs, 1):
        # 防御性钳制，确保满足整体约束（1<=n<=5000, 1<=d<=n）
        n = max(1, min(5000, n))
        d = max(1, min(n, d))
        gen(out, idx, n, d)

if __name__ == "__main__":
    main()
