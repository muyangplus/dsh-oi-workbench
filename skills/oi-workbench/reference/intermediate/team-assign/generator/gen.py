#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random
import sys

random.seed(20250105)

def gen(path, idx, n, mode):
    lines = []
    for _ in range(n):
        if mode == 0:
            v = [random.randint(0, 20000) for _ in range(3)]
        elif mode == 1:
            v = [random.randint(0, 20000), 0, 0]
        elif mode == 2:
            v = [random.randint(0, 20000), random.randint(0, 20000), 0]
        else:
            v = [random.randint(0, 20000) for _ in range(3)]
        lines.append(" ".join(map(str, v)))
    with open(os.path.join(path, f"{idx}.in"), "w", encoding="utf-8") as f:
        f.write(f"{n}\n")
        f.write("\n".join(lines) + "\n")

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "data"
    os.makedirs(out, exist_ok=True)
    configs = [
        (2, 0), (4, 0), (10, 0), (20, 1), (30, 0),
        (50, 2), (80, 1), (100, 0), (100, 2), (100, 0),
    ]
    for i, (n, mode) in enumerate(configs, 1):
        gen(out, i, n, mode)

if __name__ == "__main__":
    main()