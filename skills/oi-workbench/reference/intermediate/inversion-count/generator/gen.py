#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random
import sys

random.seed(20250108)

def gen(path, idx, n, k):
    with open(os.path.join(path, f"{idx}.in"), "w", encoding="utf-8") as f:
        f.write(f"{n} {k}\n")

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "data"
    os.makedirs(out, exist_ok=True)
    configs = [
        (3, 1),
        (5, 3),
        (10, 5),
        (50, 0),
        (50, 10),
        (100, 100),
        (200, 19900),
        (300, 5),
        (500, 124740),
        (500, 62350),
    ]
    for i, (n, k) in enumerate(configs, 1):
        # ensure k within max
        maxk = n * (n - 1) // 2
        k = max(0, min(k, maxk))
        gen(out, i, n, k)

if __name__ == "__main__":
    main()