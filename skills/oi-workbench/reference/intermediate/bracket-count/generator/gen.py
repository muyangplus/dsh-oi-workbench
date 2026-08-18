#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random
import sys

random.seed(20250107)

def gen(path, idx, n, d):
    with open(os.path.join(path, f"{idx}.in"), "w", encoding="utf-8") as f:
        f.write(f"{n} {d}\n")

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "data"
    os.makedirs(out, exist_ok=True)
    configs = [
        (3, 2), (5, 5), (10, 10), (50, 1), (100, 10),
        (500, 1), (1000, 10), (2000, 500), (5000, 1), (5000, 5000),
    ]
    for i, (n, d) in enumerate(configs, 1):
        gen(out, i, n, d)

if __name__ == "__main__":
    main()