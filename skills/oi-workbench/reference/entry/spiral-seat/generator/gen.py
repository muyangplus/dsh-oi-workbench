#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random
import sys

random.seed(20250102)

def gen(path, idx, n, m, k):
    with open(os.path.join(path, f"{idx}.in"), "w", encoding="utf-8") as f:
        f.write(f"{n} {m} {k}\n")

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "data"
    os.makedirs(out, exist_ok=True)
    configs = [
        (3, 4, 5),
        (1, 10, 1),
        (10, 1, 3),
        (10, 10, random.randint(1, 100)),
        (100, 100, random.randint(1, 10000)),
        (1000, 1, random.randint(1, 1000)),
        (100000, 100000, random.randint(1, 10**10)),
        (10**9, 1, random.randint(1, 10**9)),
        (1, 10**9, random.randint(1, 10**9)),
        (10**9, 10**9, random.randint(1, 10**18)),
    ]
    for i, (n, m, k) in enumerate(configs, 1):
        gen(out, i, n, m, k)

if __name__ == "__main__":
    main()