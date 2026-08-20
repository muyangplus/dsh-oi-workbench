#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_hoj_package.py —— 校验 HOJ 原生导入 zip（纯标准库）。

用法:
    python verify_hoj_package.py <题目包.zip>

检查:
    1. zip 内含 problem_*.json 与同名 problem_*/ 数据目录
    2. JSON 的 samples 每个 input/output 在对应目录中存在
    3. OI 题目 samples 分值之和为 100
    4. judgeMode / judgeCaseMode 合法
    5. spj/interactive 时需要 spjCode 或 spjLanguage 说明
"""

import json
import re
import sys
import zipfile

VALID_JUDGE_MODES = {"default", "spj", "interactive"}
VALID_CASE_MODES = {"default", "subtask_lowest", "subtask_average"}


def main():
    if len(sys.argv) != 2:
        sys.exit("用法: python verify_hoj_package.py <题目包.zip>")
    zpath = sys.argv[1]
    errors, warnings = [], []

    with zipfile.ZipFile(zpath) as z:
        names = set(z.namelist())
        json_names = [n for n in names if re.match(r"^problem_[^/]+\.json$", n)]
        if not json_names:
            errors.append("zip 内缺少 problem_*.json")

        for jn in sorted(json_names):
            base = jn[:-5]          # 去掉 .json
            folder = base + "/"
            try:
                payload = json.loads(z.read(jn).decode("utf-8"))
            except Exception as e:
                errors.append(f"{jn}: JSON 解析失败: {e}")
                continue

            problem = payload.get("problem") or {}
            pid = problem.get("problemId") or base
            title = problem.get("title") or "?"
            type_oi = problem.get("type") == 1
            jm = payload.get("judgeMode") or problem.get("judgeMode") or "default"
            jcm = problem.get("judgeCaseMode") or "default"
            if jm not in VALID_JUDGE_MODES:
                errors.append(f"{jn}: judgeMode 非法: {jm}")
            if jcm not in VALID_CASE_MODES:
                errors.append(f"{jn}: judgeCaseMode 非法: {jcm}")

            samples = payload.get("samples") or []
            if not samples:
                warnings.append(f"{jn}: samples 为空")
            total = 0
            score_seen = False
            for s in samples:
                inp, out = s.get("input"), s.get("output")
                if not inp or not out:
                    errors.append(f"{jn}: sample 缺少 input/output: {s}")
                    continue
                if f"{folder}{inp}" not in names:
                    errors.append(f"{jn}: 输入文件不存在: {folder}{inp}")
                if f"{folder}{out}" not in names:
                    errors.append(f"{jn}: 输出文件不存在: {folder}{out}")
                if type_oi:
                    score = s.get("score")
                    if score is not None:
                        score_seen = True
                        total += int(score)
            if type_oi and score_seen and total != 100:
                errors.append(f"{jn}: OI 总分 = {total}（应为 100）：{pid} {title}")

            if jm in ("spj", "interactive"):
                if not problem.get("spjCode") and not payload.get("judgeExtraFile"):
                    warnings.append(f"{jn}: {jm} 未提供 spjCode/judgeExtraFile，需在 HOJ 后台补充")

            print(f"[info] {jn}: {pid} {title}  type={'OI' if type_oi else 'ACM'} "
                  f"judge={jm} caseMode={jcm} samples={len(samples)}")
            if problem.get("isFileIO"):
                print(f"[info]       file IO: read={problem.get('ioReadFileName')} "
                      f"write={problem.get('ioWriteFileName')}")

    if errors:
        for e in errors:
            print(f"[error] {e}")
        sys.exit(1)
    for w in warnings:
        print(f"[warn] {w}")
    print(f"[ok] {zpath} 校验通过（HOJ 导入布局）")


if __name__ == "__main__":
    main()