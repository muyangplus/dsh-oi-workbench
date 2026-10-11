#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_contest.py —— 一键构建一场比赛的全部交付产物。

依次调用：
  1. package_samples.py    完整样例平铺 zip + 题面引用更新
  2. build_statement_pdf.py 官方风格整卷 PDF
  3. export_lemon.py        Lemon 评测机数据（含 <contest>.cdf 与 std 选手）
  4. build_package.py       每题 Hydro 原生包
  5. build_hoj_package.py   每题 HOJ 原生包

用法：
  python generator/build_contest.py \
      --contest LKCP --subtitle "2026 第二轮认证" --level "提高级" \
      --time "2026 年 8 月 22 日 13:00~16:00" \
      --problems drafts/csp-s-mock/climb drafts/csp-s-mock/signal \
      --story-dir drafts/csp-s-mock-pdf/story \
      --out dist/csp-s-mock

可用 --skip-* 跳过某一步。
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(script, args):
    cmd = [sys.executable, os.path.join(HERE, script)] + args
    print("\n>>> %s" % " ".join(cmd))
    r = subprocess.run(cmd, cwd=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    if r.returncode != 0:
        sys.exit("[error] %s 失败" % script)
    return r


def main():
    ap = argparse.ArgumentParser(description="一键构建一场比赛的全部交付产物")
    ap.add_argument("--contest", default="LKCP")
    ap.add_argument("--subtitle", default="2026 第二轮认证")
    ap.add_argument("--level", default="提高级")
    ap.add_argument("--time", default="2026 年 8 月 22 日 13:00~16:00")
    ap.add_argument("--problems", nargs="+", required=True, help="题目目录列表")
    ap.add_argument("--story-dir", default=None, help="故事强化版题面目录（可选）")
    ap.add_argument("--out", default="dist/csp-s-mock", help="输出根目录")
    ap.add_argument("--contest-title", default=None, help="Lemon .cdf 的 contestTitle")
    ap.add_argument("--cdf-name", default=None, help="Lemon .cdf 文件名")
    ap.add_argument("--skip-samples", action="store_true")
    ap.add_argument("--skip-pdf", action="store_true")
    ap.add_argument("--skip-lemon", action="store_true")
    ap.add_argument("--skip-hydro", action="store_true")
    ap.add_argument("--skip-hoj", action="store_true")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    common = ["--problems"] + args.problems
    if args.story_dir:
        common += ["--story-dir", args.story_dir]

    if not args.skip_samples:
        run("package_samples.py", common + [
            "--combined", os.path.join(args.out, "%s-完整样例.zip" % args.contest)])
    if not args.skip_pdf:
        run("build_statement_pdf.py", [
            "--contest", args.contest, "--subtitle", args.subtitle,
            "--level", args.level, "--time", args.time,
            "--problems"] + args.problems +
            (["--story-dir", args.story_dir] if args.story_dir else []) +
            ["--out", os.path.join(args.out, "%s-题面.pdf" % args.contest)])
    if not args.skip_lemon:
        lemon_args = ["--contest", args.contest, "--problems"] + args.problems + \
            ["--out", os.path.join(args.out, "lemon")]
        if args.contest_title:
            lemon_args += ["--contest-title", args.contest_title]
        if args.cdf_name:
            lemon_args += ["--cdf-name", args.cdf_name]
        run("export_lemon.py", lemon_args)

    for p in args.problems:
        stem = os.path.basename(os.path.normpath(p))
        if not args.skip_hydro:
            run("build_package.py", [p, "--out",
                                     os.path.join(args.out, "%s-%s.zip" % (args.contest, stem))])
        if not args.skip_hoj:
            run("build_hoj_package.py", [p, "--out",
                                         os.path.join(args.out, "%s-%s-hoj.zip" % (args.contest, stem))])

    print("\n[ok] 比赛构建完成：%s" % args.contest)
    print("     输出目录：%s" % os.path.abspath(args.out))


if __name__ == "__main__":
    main()
