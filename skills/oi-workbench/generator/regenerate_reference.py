#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
regenerate_reference.py —— 确保 reference 各题 data/ 存在（生成器 + std 生成答案）。

背景：参考题测试数据（data/*.in, *.out）不入库、不进 npm 包。
CI/新克隆环境没有 data/，先跑本脚本按各题 generator/gen.py 现场重造（并用 std 生成 .out），
再执行一致性校验与打包。

用法:
    python skills/oi-workbench/generator/regenerate_reference.py          # 仅补缺失
    python skills/oi-workbench/generator/regenerate_reference.py --force # 强制重建
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "reference"  # skills/oi-workbench/reference
COMPILE = "-O2 -std=c++14 -static"


def problem_dirs():
    for level in ("entry", "intermediate"):
        d = REF / level
        if not d.is_dir():
            continue
        for p in sorted(d.iterdir()):
            if (p / "spec.json").is_file():
                yield p


def ensure_all(force=False):
    done, skipped = [], []
    for p in problem_dirs():
        data = p / "data"
        gen = p / "generator" / "gen.py"
        std = p / "std" / "std.cpp"
        ins = sorted(data.glob("*.in")) if data.is_dir() else []
        if not force and ins:
            continue
        if not (gen.is_file() and std.is_file()):
            skipped.append("%s(缺gen/std)" % p.name)
            continue
        try:
            data.mkdir(parents=True, exist_ok=True)
            for f in data.iterdir():
                f.unlink()
            subprocess.run([sys.executable, str(gen), str(data)], check=True)
            exe = Path(tempfile.gettempdir()) / ("refgen_%s_%s" % (p.parent.name, p.name))
            if os.name == "nt":
                exe = exe.with_suffix(".exe")
            cp = subprocess.run(["g++"] + COMPILE.split() + [str(std), "-o", str(exe)],
                                capture_output=True, text=True)
            if cp.returncode != 0:
                skipped.append("%s(std编译失败)" % p.name)
                continue
            for fin in sorted(data.glob("*.in")):
                out = data / (fin.stem + ".out")
                with open(fin, "rb") as fi, open(out, "wb") as fo:
                    subprocess.run([str(exe)], stdin=fi, stdout=fo, timeout=60, check=True)
            done.append(p.name)
        except Exception as e:  # noqa: BLE001 —— 单题失败不影响其余
            skipped.append("%s(%s)" % (p.name, e))
    if done:
        print("regenerated: %s" % ", ".join(done))
    if skipped:
        print("skipped: %s" % ", ".join(skipped))
    if not done and not skipped:
        print("regenerated: (无缺失)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    ensure_all(a.force)
