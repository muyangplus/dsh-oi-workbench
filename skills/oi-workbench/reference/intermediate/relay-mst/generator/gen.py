#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random
import sys

random.seed(20250106)

def gen(path, idx, n, m, k, mode):
    edges = []
    # ensure connected random spanning tree
    for i in range(1, n):
        u = i
        v = random.randrange(i)
        w = random.randint(0, 10**9)
        edges.append((u + 1, v + 1, w))
    while len(edges) < m:
        u = random.randint(1, n)
        v = random.randint(1, n)
        if u == v: continue
        w = random.randint(0, 10**9)
        edges.append((u, v, w))
    random.shuffle(edges)
    lines = [f"{n} {len(edges)} {k}"]
    for u, v, w in edges:
        lines.append(f"{u} {v} {w}")
    for j in range(k):
        c = 0 if mode == 0 else random.randint(0, 10**9)
        bs = []
        for i in range(n):
            if mode == 0 and random.random() < 0.3:
                bs.append(0)
            else:
                bs.append(random.randint(0, 10**9))
        lines.append(str(c) + " " + " ".join(map(str, bs)))
    with open(os.path.join(path, f"{idx}.in"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "data"
    os.makedirs(out, exist_ok=True)
    configs = [
        (5, 8, 0, 0),
        (10, 30, 1, 0),
        (20, 60, 2, 1),
        (30, 100, 3, 0),
        (50, 150, 4, 1),
        (80, 200, 5, 0),
        (100, 300, 5, 1),
        (200, 500, 5, 0),
        (500, 2000, 5, 1),
        (1000, 5000, 5, 0),
    ]
    for i, (n, m, k, mode) in enumerate(configs, 1):
        gen(out, i, n, m, k, mode)

if __name__ == "__main__":
    main()