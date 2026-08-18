#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random
import sys

random.seed(20250101)

def gen_case(path, idx, n_max, len_max, sum_max=None):
    n = random.randint(1, n_max)
    total = 0
    lines = []
    for _ in range(n):
        L = random.randint(1, len_max)
        if sum_max is not None:
            L = min(L, max(1, sum_max - total))
            if L <= 0:
                L = 1
        total += L
        s = str(random.randint(1, 9))
        s += ''.join(str(random.randint(0, 9)) for _ in range(L - 1))
        lines.append(s)
    with open(os.path.join(path, f"{idx}.in"), "w", encoding="utf-8") as f:
        f.write(f"{n}\n")
        f.write("\n".join(lines) + "\n")

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "data"
    os.makedirs(out, exist_ok=True)
    configs = [
        (1, 2, 2),
        (2, 4, 3),
        (3, 10, 5),
        (4, 100, 5),
        (5, 1000, 10),
        (6, 1000, 10),
        (7, 10000, 10),
        (8, 100000, 10),
        (9, 100000, 3),
        (10, 100000, 10),
    ]
    for i, (n, lmax, lmax2) in enumerate(configs, 1):
        gen_case(out, i, n, lmax2)

if __name__ == "__main__":
    main()