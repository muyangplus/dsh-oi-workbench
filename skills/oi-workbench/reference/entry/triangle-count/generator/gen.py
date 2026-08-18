#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random
import sys

random.seed(20250104)

def gen(path, idx, n, maxv, sorted_flag=False, distinct=False):
    if distinct:
        vals = random.sample(range(1, maxv + 1), min(n, maxv))
        if len(vals) < n:
            vals += [random.randint(1, maxv) for _ in range(n - len(vals))]
    else:
        vals = [random.randint(1, maxv) for _ in range(n)]
    if sorted_flag:
        vals.sort()
    with open(os.path.join(path, f"{idx}.in"), "w", encoding="utf-8") as f:
        f.write(f"{n}\n")
        f.write(" ".join(map(str, vals)) + "\n")

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "data"
    os.makedirs(out, exist_ok=True)
    configs = [
        (10, 1000, False, False),
        (30, 1000, False, True),
        (100, 10**6, False, False),
        (100, 10**9, False, True),
        (1000, 10**6, True, False),
        (1000, 10**9, False, False),
        (3000, 10**6, True, False),
        (3000, 10**9, False, True),
        (5000, 10**9, True, False),
        (5000, 10**9, False, False),
    ]
    for i, (n, maxv, sorted_flag, distinct) in enumerate(configs, 1):
        gen(out, i, n, maxv, sorted_flag, distinct)

if __name__ == "__main__":
    main()