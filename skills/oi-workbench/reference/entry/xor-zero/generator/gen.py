#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random
import sys

random.seed(20250103)

def gen(path, idx, n, mode):
    if mode == 0:
        a = [random.randint(0, (1 << 20) - 1) for _ in range(n)]
    elif mode == 1:
        v = random.randint(0, (1 << 20) - 1)
        a = [v] * n
    else:
        a = [random.randint(0, 1) for _ in range(n)]
    with open(os.path.join(path, f"{idx}.in"), "w", encoding="utf-8") as f:
        f.write(f"{n}\n")
        f.write(" ".join(map(str, a)) + "\n")

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "data"
    os.makedirs(out, exist_ok=True)
    configs = [
        (10, 0), (100, 1), (100, 0), (1000, 2), (1000, 0),
        (100000, 1), (100000, 2), (100000, 0), (500000, 2), (500000, 0),
    ]
    for i, (n, mode) in enumerate(configs, 1):
        gen(out, i, n, mode)

if __name__ == "__main__":
    main()