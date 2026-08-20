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
    # (n, k) —— 与题面「数据范围」表格逐点对齐（25 点）
    configs = [
        (1, 0), (10, 0),              # 1..2: n<=10
        (10, 5), (50, 0), (50, 10),   # 3..5: n<=50, A(k<=10)
        (100, 20), (100, 100), (100, 4950),        # 6..8: n<=100
        (200, 19890), (200, 19895), (200, 19900),  # 9..11: n<=200, B(k>=n(n-1)/2-10)
        (300, 100), (300, 30000), (300, 44850),    # 12..14: n<=300
        (500, 0), (500, 3), (500, 7), (500, 10),   # 15..18: n<=500, A(k<=10)
        (500, 50000), (500, 100000), (500, 124000),  # 19..25: n<=500, 无
        (500, 124700), (500, 124740), (500, 124745),
        (500, 1000),
    ]
    for i, (n, k) in enumerate(configs, 1):
        maxk = n * (n - 1) // 2
        k = max(0, min(k, maxk))
        gen(out, i, n, k)

if __name__ == "__main__":
    main()
