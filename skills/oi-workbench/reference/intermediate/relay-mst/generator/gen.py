#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络中继（relay-mst）数据生成器。

按题面「数据范围」测试点表格逐档生成 25 个测试点：
- 1..4    : n<=50,  m<=200,  k=0，无特殊性质
- 5,6     : n<=100, m<=300,  k<=5，特殊性质 A
- 7,8     : n<=200, m<=500,  k<=5，无特殊性质
- 9,10    : n<=500, m<=2000, k<=5，特殊性质 A
- 11..14  : n<=1000,m<=5000, k<=5，特殊性质 A
- 15..18  : n<=1000,m<=5000, k<=5，无特殊性质
- 19..25  : n<=1000,m<=5000, k<=5，无特殊性质

特殊性质 A：所有 c_j = 0，且每个中继站至少有一条费用为 0 的直达链路
（生成时对每个 j 保证至少一个 b_{j,i} = 0）。
图保证连通：先随机生成一棵生成树，再加足够多的随机边到 m 条。
"""
import os
import random
import sys

random.seed(20250106)


def gen(path, idx, n, m, k, special_a):
    edges = []
    # 1) 随机生成树，保证原 n 座城市由原有道路两两可达（1-indexed 节点 1..n）
    for i in range(1, n):
        u = i + 1
        v = random.randrange(i) + 1
        w = random.randint(0, 10 ** 9)
        edges.append((u, v, w))
    # 2) 追加随机边直到 m 条
    while len(edges) < m:
        u = random.randint(1, n)
        v = random.randint(1, n)
        if u == v:
            continue
        w = random.randint(0, 10 ** 9)
        edges.append((u, v, w))
    random.shuffle(edges)
    lines = ["%d %d %d" % (n, len(edges), k)]
    for u, v, w in edges:
        lines.append("%d %d %d" % (u, v, w))
    # 3) 中继站
    for j in range(k):
        if special_a:
            c = 0
            bs = [random.randint(0, 10 ** 9) for _ in range(n)]
            # 保证至少一个 b_{j,i} = 0
            bs[random.randrange(n)] = 0
        else:
            c = random.randint(0, 10 ** 9)
            bs = [random.randint(0, 10 ** 9) for _ in range(n)]
        lines.append(str(c) + " " + " ".join(map(str, bs)))
    with open(os.path.join(path, "%d.in" % idx), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "data"
    os.makedirs(out, exist_ok=True)
    # (n, m, k, special_a)
    configs = [
        (10, 20, 0, False),
        (25, 60, 0, False),
        (50, 200, 0, False),
        (50, 200, 0, False),
        (100, 300, 5, True),
        (80, 250, 5, True),
        (200, 500, 5, False),
        (150, 400, 4, False),
        (500, 2000, 5, True),
        (400, 1500, 4, True),
        (1000, 5000, 5, True),
        (1000, 5000, 5, True),
        (800, 4000, 5, True),
        (700, 3500, 4, True),
        (1000, 5000, 5, False),
        (1000, 5000, 4, False),
        (900, 4000, 5, False),
        (600, 3000, 2, False),
        (1000, 5000, 5, False),
        (1000, 5000, 5, False),
        (1000, 5000, 5, False),
        (1000, 5000, 5, False),
        (1000, 5000, 5, False),
        (1000, 5000, 5, False),
        (1000, 5000, 5, False),
    ]
    assert len(configs) == 25
    for i, (n, m, k, special_a) in enumerate(configs, 1):
        gen(out, i, n, m, k, special_a)


if __name__ == "__main__":
    main()
