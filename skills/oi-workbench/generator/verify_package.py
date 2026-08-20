#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_package.py —— 校验 Hydro 原生题目包 zip（纯标准库）。

用法:
    python verify_package.py <题目包.zip>

检查:
    1. zip 内含 problem.yaml 与 testdata/config.yaml
    2. config.yaml 可解析（极简 YAML），time/memory 存在
    3. subtasks/cases 引用的每个 input/output 都在 testdata/ 下
    4. testdata/ 下每个 .in 都有同名 .out
    5. subtask 分值之和为 100
    6. special/interactive 时 checker/interactor 文件存在
    7. data/sample/ 中每个 .in 有同名 .out
    8. additional_file/ 存在时报告其内容（大样例附件）
"""

import sys
import zipfile


def parse_yaml_simple(text):
    """极简 YAML 解析（仅支持本生成器与常见 Hydro config.yaml 结构）。"""
    data = {}
    lines = text.splitlines()
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val:
                data[key] = val
            else:
                block = []
                j = i + 1
                while j < n:
                    l2 = lines[j]
                    if not l2.strip():
                        j += 1
                        continue
                    if len(l2) - len(l2.lstrip()) <= indent:
                        break
                    block.append(l2)
                    j += 1
                data[key] = parse_yaml_simple("\n".join(block))
                i = j - 1
        i += 1
    return data


def collect_cases(node, out):
    if isinstance(node, dict):
        if "input" in node and "output" in node:
            out.append((node["input"], node["output"]))
        for v in node.values():
            collect_cases(v, out)
    elif isinstance(node, list):
        for v in node:
            collect_cases(v, out)


def main():
    if len(sys.argv) != 2:
        sys.exit("用法: python verify_package.py <题目包.zip>")
    zpath = sys.argv[1]
    errors, warnings = [], []

    with zipfile.ZipFile(zpath) as z:
        names = set(z.namelist())

        if "problem.yaml" not in names:
            errors.append("zip 内缺少 problem.yaml")
        if "testdata/config.yaml" not in names:
            errors.append("zip 内缺少 testdata/config.yaml（Hydro 评测配置）")

        # 数据配对
        td = {n.split("/")[-1] for n in names if n.startswith("testdata/") and n.count("/") == 1
              and n != "testdata/config.yaml"}
        ins = {f[:-3] for f in td if f.endswith(".in")}
        outs = {f[:-4] for f in td if f.endswith(".out")}
        for base in ins - outs:
            errors.append(f"testdata/ 缺少答案文件: {base}.out")
        for base in outs - ins:
            warnings.append(f"testdata/ 有多余答案文件: {base}.out")

        # config.yaml 校验
        cfg = parse_yaml_simple(z.read("testdata/config.yaml").decode("utf-8", "replace"))
        for f in ("time", "memory"):
            if f not in cfg:
                warnings.append(f"config.yaml 缺少 {f}（默认 1000ms/256m 可用）")
        if cfg.get("inputFile") or cfg.get("outputFile"):
            print(f"[info] file IO: 读 {cfg.get('inputFile')} → 写 {cfg.get('outputFile')}")
        subtasks = cfg.get("subtasks")
        if subtasks is not None:
            cases = []
            collect_cases(subtasks, cases)
            for cin, cout in cases:
                if f"testdata/{cin}" not in names:
                    errors.append(f"subtask case 输入不存在: testdata/{cin}")
                if f"testdata/{cout}" not in names:
                    errors.append(f"subtask case 输出不存在: testdata/{cout}")
            # 分值
            def scores(node, acc):
                if isinstance(node, dict):
                    if "score" in node and "cases" in node:
                        acc.append(int(node["score"]))
                    for v in node.values():
                        scores(v, acc)
                elif isinstance(node, list):
                    for v in node:
                        scores(v, acc)
            acc = []
            scores(subtasks, acc)
            if acc and sum(acc) != 100:
                warnings.append(f"subtask 分值之和 = {sum(acc)}（100 为常规值）")
        else:
            cases = cfg.get("cases")
            if cases is not None:
                cs = []
                collect_cases(cases, cs)
                for cin, cout in cs:
                    if f"testdata/{cin}" not in names:
                        errors.append(f"case 输入不存在: testdata/{cin}")
                    if f"testdata/{cout}" not in names:
                        errors.append(f"case 输出不存在: testdata/{cout}")

        # 特殊评测
        if cfg.get("checker"):
            if f"testdata/{cfg['checker']}" not in names:
                errors.append(f"checker 文件不在 testdata/: {cfg['checker']}")
        if cfg.get("interactor"):
            if f"testdata/{cfg['interactor']}" not in names:
                errors.append(f"interactor 文件不在 testdata/: {cfg['interactor']}")

        # 样例配对
        smp = {n.split("/")[-1] for n in names if n.startswith("data/sample/")}
        s_in = {f[:-3] for f in smp if f.endswith(".in")}
        s_out = {f[:-4] for f in smp if f.endswith(".out")}
        for base in s_in - s_out:
            errors.append(f"data/sample/ 缺少答案: {base}.out")

        # 附加文件（大样例等）
        add_files = sorted(n for n in names if n.startswith("additional_file/"))
        if add_files:
            print(f"[info] 附加文件 {len(add_files)} 个: {', '.join(f.split('/')[-1] for f in add_files)}")

    if errors:
        for e in errors:
            print(f"[error] {e}")
        sys.exit(1)
    for w in warnings:
        print(f"[warn] {w}")
    print(f"[ok] {zpath} 校验通过（Hydro 原生布局，测试点/附件齐全）")


if __name__ == "__main__":
    main()
