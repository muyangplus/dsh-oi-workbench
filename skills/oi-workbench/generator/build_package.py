#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_package.py —— 生成 Hydro 原生题目包 zip（纯 Python 标准库，无依赖）。

包格式依据 Hydro 官方源码（packages/hydrooj/src/model/problem.ts import 逻辑，
packages/common/types.ts ProblemConfigFile）逐字段验证。

用法:
    python build_package.py <题目目录> [--out <输出.zip>] [--check]

题目目录结构:
    <题目目录>/
    ├── spec.json         # 可选：题目配置（见下）。缺省时自动生成
    ├── problem.md        # 题面（Markdown，推荐）→ 导入后即成为题目内容
    ├── data/             # 隐藏测试数据 1.in / 1.out ...（必需）
    ├── sample/           # 样例 1.in / 1.out ...（可选；导入为展示样例 + 测试数据）
    ├── additional_file/  # 附加文件（可选）：大样例 zip 等，题面用 file:// 引用
    ├── std/              # std.cpp（可选；导入为 AC 评测记录）
    └── solution/         # 题解（可选）

spec.json 字段:
{
  "title": "题目名",
  "pid": "P1000",              # 可选；缺省自动编号
  "tags": ["知识点1"],
  "time": "1000ms",            # 或数字毫秒
  "memory": "256m",
  "difficulty": 0,             # 0-10
  "hidden": false,
  "cases": [                   # 逐点模式（默认，OI 推荐：10-25 个测试点等分/不等分）
    {"input": "1.in", "output": "1.out"},
    {"input": "2.in", "output": "2.out", "score": 5}   # 不等分时给 score
  ],
  "subtasks": [                # 捆绑/依赖模式（深入系列部分赛事才用）
    {"score": 20, "type": "min", "if": [], "cases": [{"input": "1.in", "output": "1.out"}]}
  ],
  "judge": {"type": "default"} # default|special|interactive（checker/interactor 源码放 data/ 并在 spec 指明）
}

生成的 zip 布局（与 Hydro import 逻辑完全对应）:
    problem.zip
    ├── problem.yaml          # title/pid/tag/content/difficulty/hidden
    ├── problem.md            # 题面
    ├── testdata/
    │   ├── config.yaml       # 评测配置（time/memory/subtasks/checker）
    │   └── 1.in / 1.out ...
    ├── data/sample/          # 样例（同时进 testdata 与附加文件）
    ├── std/                  # 标程（导入为 AC 记录）
    └── solution/             # 题解
"""

import argparse
import json
import os
import sys
import zipfile


def load_spec(pdir):
    spec_path = os.path.join(pdir, "spec.json")
    if os.path.exists(spec_path):
        with open(spec_path, encoding="utf-8") as f:
            spec = json.load(f)
    else:
        spec = {}
    spec.setdefault("title", os.path.basename(os.path.normpath(pdir)))
    spec.setdefault("time", "1000ms")
    spec.setdefault("memory", "256m")
    return spec


def ms_to_hydro(value):
    if isinstance(value, (int, float)):
        return f"{int(value)}ms"
    return value


def build_problem_yaml(spec):
    lines = [f"title: {json.dumps(spec['title'], ensure_ascii=False)}"]
    if spec.get("pid"):
        lines.append(f"pid: {spec['pid']}")
    tags = spec.get("tags") or []
    if tags:
        lines.append("tag:")
        for t in tags:
            lines.append(f"  - {json.dumps(str(t), ensure_ascii=False)}")
    if spec.get("difficulty"):
        lines.append(f"difficulty: {int(spec['difficulty'])}")
    if spec.get("hidden"):
        lines.append("hidden: true")
    return "\n".join(lines) + "\n"


def build_config_yaml(spec, data_files, subtask_cases):
    """生成 testdata/config.yaml（ProblemConfigFile）。"""
    lines = []
    jtype = (spec.get("judge") or {}).get("type", "default")
    if jtype != "default":
        lines.append(f"type: {jtype}")
    lines.append(f"time: {ms_to_hydro(spec.get('time', '1000ms'))}")
    lines.append(f"memory: {spec.get('memory', '256m')}")
    lines.append(f"score: 100")

    judge = spec.get("judge") or {}
    if judge.get("checker"):
        lines.append(f"checker_type: testlib")
        lines.append(f"checker: {judge['checker']}")
    if judge.get("interactor"):
        lines.append(f"interactor: {judge['interactor']}")

    subtasks = spec.get("subtasks")
    cases = spec.get("cases")
    if subtasks:
        lines.append("subtasks:")
        for idx, st in enumerate(subtasks, 1):
            score = st.get("score")
            lines.append(f"  - id: {idx}")
            if score is not None:
                lines.append(f"    score: {int(score)}")
            lines.append(f"    type: {st.get('type', 'sum')}")
            deps = st.get("if") or []
            if deps:
                lines.append(f"    if: {list(deps)}")
            st_cases = st.get("cases")
            if st_cases:
                lines.append("    cases:")
                for c in st_cases:
                    lines.append(f"      - input: {c['input']}")
                    lines.append(f"        output: {c['output']}")
    else:
        # 逐点模式（默认，OI 推荐：10-25 个等分/不等分测试点综合测试）。
        # spec.json 的顶层 cases 决定顺序；未写时按 data/ 文件排序。
        lines.append("cases:")
        for c in (cases or [{"input": f, "output": os.path.splitext(f)[0] + ".out"} for f in data_files]):
            lines.append(f"  - input: {c['input']}")
            lines.append(f"    output: {c['output']}")
            if c.get("score") is not None:
                lines.append(f"    score: {int(c['score'])}")
    return "\n".join(lines) + "\n"


def validate(spec, data_dir):
    issues = []
    pairs = sorted(
        (f, os.path.splitext(f)[0] + ".out")
        for f in os.listdir(data_dir) if f.endswith(".in")
    )
    for _, out in pairs:
        if not os.path.exists(os.path.join(data_dir, out)):
            issues.append(f"缺少答案文件: {out}")
    subtasks = spec.get("subtasks")
    cases = spec.get("cases")
    if subtasks:
        total = sum(int(s.get("score") or 0) for s in subtasks)
        if total != 100:
            issues.append(f"subtask 分值之和 = {total}（应为 100）")
        seen = set()
        for st in subtasks:
            if st.get("type") not in ("min", "max", "sum"):
                issues.append(f"subtask type 非法: {st.get('type')}")
            for c in st.get("cases", []):
                inp = c.get("input")
                if inp in seen:
                    issues.append(f"case 重复: {inp}")
                seen.add(inp)
                if not os.path.exists(os.path.join(data_dir, inp)):
                    issues.append(f"case 输入不存在: {inp}")
    elif cases:
        seen = set()
        for c in cases:
            inp = c.get("input")
            if inp in seen:
                issues.append(f"case 重复: {inp}")
            seen.add(inp)
            if not os.path.exists(os.path.join(data_dir, inp)):
                issues.append(f"case 输入不存在: {inp}")
    return issues, pairs


def main():
    ap = argparse.ArgumentParser(description="生成 Hydro 原生题目包 zip")
    ap.add_argument("problem_dir")
    ap.add_argument("--out", default=None)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    pdir = os.path.normpath(args.problem_dir)
    if not os.path.isdir(pdir):
        sys.exit(f"题目目录不存在: {pdir}")
    data_dir = os.path.join(pdir, "data")
    if not os.path.isdir(data_dir):
        sys.exit(f"缺少 data/ 目录: {data_dir}")

    spec = load_spec(pdir)
    issues, pairs = validate(spec, data_dir)
    if issues:
        for i in issues:
            print(f"[error] {i}")
        sys.exit("spec/数据校验失败")
    if not pairs:
        sys.exit("data/ 下没有 .in 文件")

    out_zip = args.out or (os.path.basename(pdir) + ".zip")
    if args.check:
        print(f"[ok] 数据点 {len(pairs)} 个；将生成: problem.yaml + testdata/config.yaml + data/ + problem.md")
        return

    problem_yaml = build_problem_yaml(spec)
    config_yaml = build_config_yaml(spec, [f for f, _ in pairs],
                                     spec.get("subtasks"))

    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("problem.yaml", problem_yaml)
        # 题面
        md = os.path.join(pdir, "problem.md")
        if os.path.exists(md):
            z.write(md, "problem.md")
        # 测试数据 + config.yaml
        for f, o in pairs:
            z.write(os.path.join(data_dir, f), f"testdata/{f}")
            z.write(os.path.join(data_dir, o), f"testdata/{o}")
        z.writestr("testdata/config.yaml", config_yaml)
        # 样例（Hydro: data/sample/* 同时进 testdata 与附加文件）
        sample_dir = os.path.join(pdir, "sample")
        if os.path.isdir(sample_dir):
            for f in sorted(os.listdir(sample_dir)):
                full = os.path.join(sample_dir, f)
                if os.path.isfile(full):
                    z.write(full, f"data/sample/{f}")
        # 标程（导入为 AC 评测记录）
        std_dir = os.path.join(pdir, "std")
        if os.path.isdir(std_dir):
            for f in sorted(os.listdir(std_dir)):
                full = os.path.join(std_dir, f)
                if os.path.isfile(full):
                    z.write(full, f"std/{f}")
        # 题解
        sol_dir = os.path.join(pdir, "solution")
        if os.path.isdir(sol_dir):
            for root, _, files in os.walk(sol_dir):
                for f in files:
                    full = os.path.join(root, f)
                    rel = os.path.relpath(full, pdir).replace("\\", "/")
                    z.write(full, rel)
        # 附加文件（大样例 zip 等）：additional_file/ 目录内容 → zip 的 additional_file/，
        # Hydro 导入为附加文件（选手可下载，不进评测数据），题面用 file:// 引用。
        add_dir = os.path.join(pdir, "additional_file")
        if os.path.isdir(add_dir):
            for root, _, files in os.walk(add_dir):
                for f in files:
                    full = os.path.join(root, f)
                    rel = os.path.relpath(full, os.path.join(pdir, "additional_file"))
                    z.write(full, f"additional_file/{rel.replace(os.sep, '/')}")

    print(f"[ok] 已生成 {out_zip}")
    extra = []
    if os.path.isdir(os.path.join(pdir, "sample")):
        extra.append("data/sample")
    if os.path.isdir(os.path.join(pdir, "std")):
        extra.append("std")
    if os.path.isdir(os.path.join(pdir, "additional_file")):
        extra.append("additional_file")
    print(f"     布局: problem.yaml + problem.md + testdata/（含 config.yaml，{len(pairs)} 个数据点）"
          + (f" + {' + '.join(extra)}" if extra else ""))
    print("     导入: 网页『从 Hydro 导入』选择本 zip，或 POST /d/{domain}/problem/import/hydro")


if __name__ == "__main__":
    main()
