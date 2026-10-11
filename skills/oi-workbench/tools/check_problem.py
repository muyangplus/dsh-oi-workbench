#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_problem.py —— 题目包完整性/配置检查工具。

用法：
    python tools/check_problem.py <题目目录> [<题目目录> ...]

检查项：
  - problem.md / spec.json / VERIFICATION.md / solution/solution.md
  - sample/1.*、sample/2.*
  - data/ 数量与 spec.json cases 一致
  - std/std.cpp、generator、brute/wrong 是否存在（部分为建议项）
  - 交互题是否有 interactor，SPJ 是否有 checker
  - Markdown 是否为 UTF-8 无 BOM
"""
import json
import os
import sys


def check_utf8_no_bom(path):
    with open(path, "rb") as f:
        raw = f.read(3)
    return not raw.startswith(b"\xef\xbb\xbf")


def check_problem(pdir):
    issues = []
    warns = []
    pdir = os.path.abspath(pdir)

    def has(rel):
        return os.path.exists(os.path.join(pdir, rel))

    # Required
    if not has("problem.md"):
        issues.append("缺少 problem.md")
    if not has("spec.json"):
        issues.append("缺少 spec.json")
    else:
        with open(os.path.join(pdir, "spec.json"), encoding="utf-8") as f:
            try:
                spec = json.load(f)
            except Exception as e:
                issues.append("spec.json 解析失败: %s" % e)
                spec = {}
        cases = spec.get("cases") or []
        data_in = [f for f in os.listdir(os.path.join(pdir, "data")) if f.endswith(".in")] if has("data") else []
        if cases and len(cases) != len(data_in):
            issues.append("spec cases 数 %d != data in 数 %d" % (len(cases), len(data_in)))
        judge = spec.get("judge") or {}
        jtype = judge.get("type") or "default"
        if jtype in ("interactive", "communication") or judge.get("interactor"):
            if not judge.get("interactor"):
                issues.append("交互题未指定 judge.interactor")
            elif not has(os.path.join("data", judge["interactor"])):
                issues.append("缺少 interactor: data/%s" % judge["interactor"])
            if not has("data/grader.cpp"):
                warns.append("交互题缺少 data/grader.cpp（LemonLime NOI 风格）")
            if not has("data/interact.h"):
                warns.append("交互题缺少 data/interact.h")
        if judge.get("spj") or judge.get("checker"):
            if not judge.get("checker"):
                issues.append("SPJ 未指定 judge.checker")
            elif not has(os.path.join("data", judge["checker"])):
                issues.append("缺少 checker: data/%s" % judge["checker"])

    for f in ("1.in", "1.out", "2.in", "2.out"):
        if not has(os.path.join("sample", f)):
            warns.append("缺少 sample/%s" % f)
    if not has("std/std.cpp"):
        issues.append("缺少 std/std.cpp")
    if not has("VERIFICATION.md"):
        warns.append("缺少 VERIFICATION.md")
    if not has("solution/solution.md"):
        warns.append("缺少 solution/solution.md")
    if not has("generator"):
        warns.append("缺少 generator/")
    if not has("brute.cpp") and not has("brute.py"):
        warns.append("缺少 brute.cpp/brute.py")

    for md in ("problem.md", "VERIFICATION.md", "solution/solution.md"):
        p = os.path.join(pdir, md)
        if os.path.exists(p) and not check_utf8_no_bom(p):
            issues.append("%s 含 BOM" % md)

    return issues, warns


def main():
    if len(sys.argv) < 2:
        print("用法: python tools/check_problem.py <题目目录> ...")
        sys.exit(1)
    all_ok = True
    for pdir in sys.argv[1:]:
        print("== %s ==" % pdir)
        issues, warns = check_problem(pdir)
        for w in warns:
            print("  [warn] %s" % w)
        for i in issues:
            print("  [error] %s" % i)
        if issues:
            all_ok = False
            print("  结果: FAIL")
        else:
            print("  结果: OK%s" % ("（有警告）" if warns else ""))
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
