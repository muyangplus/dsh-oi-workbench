#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_all_reference.py —— 一键校验/构建 reference/ 下全部自出参考题。

用法:
    python generator/build_all_reference.py            # 只做结构 + Hydro/HOJ --check
    python generator/build_all_reference.py --build    # 额外生成 Hydro/HOJ zip 到 --out
    python generator/build_all_reference.py --out tmp/reference-zips

检查项:
    1. 目录结构：problem.md / spec.json / sample / data / std / brute / generator
    2. data/ 中每个 .in 都有对应 .out
    3. Hydro 包 build_package.py --check
    4. HOJ 包 build_hoj_package.py --check
    5. 若 --build，则实际生成 zip 并调用 verify_package.py / verify_hoj_package.py
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFERENCE_ROOT = ROOT / "reference"


def find_packages():
    packages = []
    for level in ("entry", "intermediate"):
        d = REFERENCE_ROOT / level
        if not d.is_dir():
            continue
        for p in sorted(d.iterdir()):
            if p.is_dir() and (p / "spec.json").exists():
                packages.append(p)
    return packages


def check_structure(pkg):
    errors = []
    for name in ("problem.md", "spec.json", "sample", "data", "std", "generator", "brute.cpp"):
        if not (pkg / name).exists():
            errors.append(f"缺少 {name}")
    if not (pkg / "std" / "std.cpp").exists():
        errors.append("缺少 std/std.cpp")
    if not (pkg / "generator" / "gen.py").exists():
        errors.append("缺少 generator/gen.py")
    data_dir = pkg / "data"
    if data_dir.is_dir():
        ins = sorted(data_dir.glob("*.in"))
        for f in ins:
            out = data_dir / (f.stem + ".out")
            if not out.exists():
                errors.append(f"data 缺少答案: {out.name}")
    return errors


def run_check(pkg, script, *args):
    cmd = [sys.executable, str(ROOT / "generator" / script), str(pkg), *args]
    cp = subprocess.run(cmd, capture_output=True, text=True)
    return cp


def build_package(pkg, out_dir, script, verify_script, suffix):
    pkg_name = pkg.name
    out_zip = out_dir / f"{pkg_name}-{suffix}.zip"
    cmd = [sys.executable, str(ROOT / "generator" / script), str(pkg), "--out", str(out_zip)]
    cp = subprocess.run(cmd, capture_output=True, text=True)
    if cp.returncode != 0:
        return False, cp.stdout + cp.stderr
    vp = subprocess.run([sys.executable, str(ROOT / "generator" / verify_script), str(out_zip)],
                        capture_output=True, text=True)
    if vp.returncode != 0:
        return False, vp.stdout + vp.stderr
    return True, ""


def main():
    ap = argparse.ArgumentParser(description="一键校验/构建自出参考题")
    ap.add_argument("--build", action="store_true", help="实际生成 zip 并校验")
    ap.add_argument("--out", default=None, help="zip 输出目录（配合 --build）")
    args = ap.parse_args()

    packages = find_packages()
    if not packages:
        sys.exit("未找到任何参考题包（reference/*/spec.json）")

    out_dir = None
    if args.build:
        out_dir = Path(args.out) if args.out else ROOT / ".tmp" / "reference-zips"
        out_dir.mkdir(parents=True, exist_ok=True)

    failed = False
    for pkg in packages:
        rel = pkg.relative_to(REFERENCE_ROOT)
        print(f"=== {rel} ===")
        errors = check_structure(pkg)
        if errors:
            for e in errors:
                print(f"  [error] {e}")
            failed = True
            continue

        hydro = run_check(pkg, "build_package.py", "--check")
        if hydro.returncode != 0:
            print("  [error] Hydro --check")
            print(hydro.stdout + hydro.stderr)
            failed = True
        else:
            print("  [ok] Hydro --check")

        hoj = run_check(pkg, "build_hoj_package.py", "--check")
        if hoj.returncode != 0:
            print("  [error] HOJ --check")
            print(hoj.stdout + hoj.stderr)
            failed = True
        else:
            print("  [ok] HOJ --check")

        if args.build:
            ok, msg = build_package(pkg, out_dir, "build_package.py", "verify_package.py", "hydro")
            if not ok:
                print("  [error] Hydro 构建/校验失败")
                print(msg)
                failed = True
            else:
                print(f"  [ok] Hydro zip -> {out_dir / (pkg.name + '-hydro.zip')}")

            ok, msg = build_package(pkg, out_dir, "build_hoj_package.py", "verify_hoj_package.py", "hoj")
            if not ok:
                print("  [error] HOJ 构建/校验失败")
                print(msg)
                failed = True
            else:
                print(f"  [ok] HOJ zip -> {out_dir / (pkg.name + '-hoj.zip')}")

    if failed:
        sys.exit("存在失败项")
    print(f"[ok] 全部 {len(packages)} 个参考题包通过")


if __name__ == "__main__":
    main()