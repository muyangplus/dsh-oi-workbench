#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
local_judge.py —— 本地评测脚本（OI/OI 风格）。

编译命令固定遵循全国统一评测规范：
    g++ -O2 -std=c++14 -static -o <exe> <source>

用法:
    python local_judge.py <题目目录> \
        --source std/std.cpp \
        --time 1000 --memory 512 \
        [--compile "-O2 -std=c++14 -static"] \
        [--file-io number.in number.out]

说明:
    - 支持 stdio 与 file IO。
    - 输出比较按 OI 规则：全文比较（过滤行末空格及文末换行）。
    - Windows 本地时间只能作参考，正式时限以“全国统一评测机
      Intel Core Ultra 9 285K @ 3.70GHz，关闭睿频与能效核，96GB 内存”为准。
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

DEFAULT_COMPILE = "-O2 -std=c++14 -static"
DEFAULT_TIME_MS = 1000
DEFAULT_MEMORY_MB = 512


def load_spec(pdir):
    path = os.path.join(pdir, "spec.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def parse_time_ms(value):
    if isinstance(value, (int, float)):
        return int(value)
    s = str(value).strip().lower()
    if s.endswith("ms"):
        return int(float(s[:-2]))
    if s.endswith("s"):
        return int(float(s[:-1]) * 1000)
    return int(float(s))


def parse_memory_mb(value):
    if isinstance(value, (int, float)):
        return int(value)
    s = str(value).strip().lower()
    if s.endswith("mb"):
        return int(float(s[:-2]))
    if s.endswith("m"):
        return int(float(s[:-1]))
    return int(float(s))


def normalize_output(s):
    """OI 全文比较：过滤行末空格及文末换行。"""
    lines = [line.rstrip() for line in s.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def get_score_map(pdir, cases_count):
    spec = load_spec(pdir)
    cases = spec.get("cases")
    scores = {}
    if cases:
        for i, c in enumerate(cases, 1):
            base = c.get("input", "")
            if c.get("score") is not None:
                scores[base] = int(c["score"])
    if not scores and cases_count:
        base = 100 // cases_count
        rem = 100 % cases_count
        for i in range(1, cases_count + 1):
            scores[f"{i}.in"] = base + (1 if i <= rem else 0)
    return scores


def compile_source(source, out_exe, compile_flags):
    cmd = ["g++"] + compile_flags.split() + [source, "-o", out_exe]
    print(f"[compile] {' '.join(cmd)}")
    return subprocess.run(cmd, capture_output=True, text=True)


def run_stdio(exe, in_path, timeout):
    with open(in_path, "rb") as fin:
        st = time.perf_counter()
        cp = subprocess.run([exe], stdin=fin, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=timeout)
        elapsed_ms = (time.perf_counter() - st) * 1000
    return cp, elapsed_ms


def run_fileio(exe, workdir, in_path, read_name, write_name, timeout):
    shutil.copyfile(in_path, os.path.join(workdir, read_name))
    out_path = os.path.join(workdir, write_name)
    if os.path.exists(out_path):
        os.remove(out_path)
    st = time.perf_counter()
    try:
        cp = subprocess.run([exe], cwd=workdir, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    finally:
        elapsed_ms = (time.perf_counter() - st) * 1000
    if os.path.exists(out_path):
        with open(out_path, encoding="utf-8", errors="replace") as f:
            output = f.read()
    else:
        output = ""
    return cp, elapsed_ms, output


def main():
    ap = argparse.ArgumentParser(description="本地 OI 评测器")
    ap.add_argument("problem_dir")
    ap.add_argument("--source", default="std/std.cpp")
    ap.add_argument("--compile", default=DEFAULT_COMPILE)
    ap.add_argument("--time", type=int, default=None, help="单点时限 ms，默认取 spec.json time")
    ap.add_argument("--memory", type=int, default=None, help="内存限制 MB，默认取 spec.json memory")
    ap.add_argument("--file-io", nargs=2, metavar=("READ", "WRITE"), default=None)
    args = ap.parse_args()

    pdir = os.path.normpath(args.problem_dir)
    spec = load_spec(pdir)
    time_ms = args.time or parse_time_ms(spec.get("time", "1000ms"))
    memory_mb = args.memory or parse_memory_mb(spec.get("memory", "256m"))
    timeout = max(0.05, time_ms / 1000.0 * 1.5 + 0.5)  # 给本地一点余量；正式时限按 time_ms

    data_dir = os.path.join(pdir, "data")
    if not os.path.isdir(data_dir):
        sys.exit(f"缺少 data/ 目录: {data_dir}")
    pairs = []
    for f in sorted(os.listdir(data_dir)):
        if f.endswith(".in"):
            base = f[:-3]
            out = base + ".out"
            if not os.path.exists(os.path.join(data_dir, out)):
                out = base + ".ans"
            if os.path.exists(os.path.join(data_dir, out)):
                pairs.append((f, out))
    if not pairs:
        sys.exit("data/ 下没有 .in/.out 配对")

    file_io = args.file_io or (spec.get("fileIO") and (spec["fileIO"].get("input"), spec["fileIO"].get("output"))) or None
    source = os.path.join(pdir, args.source)
    if not os.path.exists(source):
        sys.exit(f"源代码不存在: {source}")

    with tempfile.TemporaryDirectory(prefix="oiwb-judge-") as tmp:
        exe = os.path.join(tmp, "program.exe" if os.name == "nt" else "program")
        cp = compile_source(source, exe, args.compile)
        if cp.returncode != 0:
            print(cp.stdout)
            print(cp.stderr)
            sys.exit("编译失败")
        print("[ok] 编译成功")

        score_map = get_score_map(pdir, len(pairs))
        total = 100
        got = 0
        results = []
        for idx, (in_name, out_name) in enumerate(pairs, 1):
            in_path = os.path.join(data_dir, in_name)
            exp_path = os.path.join(data_dir, out_name)
            try:
                if file_io:
                    workdir = os.path.join(tmp, f"case{idx}")
                    os.makedirs(workdir, exist_ok=True)
                    cp, elapsed_ms, actual = run_fileio(
                        exe, workdir, in_path, file_io[0], file_io[1], timeout)
                else:
                    cp, elapsed_ms = run_stdio(exe, in_path, timeout)
                    actual = cp.stdout.decode("utf-8", "replace") if isinstance(cp.stdout, bytes) else cp.stdout
                if cp.returncode != 0:
                    verdict = "RE"
                    detail = (cp.stderr or "").decode("utf-8", "replace")[-200:] if isinstance(cp.stderr, bytes) else (cp.stderr or "")[-200:]
                elif elapsed_ms > time_ms:
                    verdict = "TLE"
                    detail = f"{elapsed_ms:.1f}ms > {time_ms}ms"
                else:
                    with open(exp_path, encoding="utf-8", errors="replace") as f:
                        expected = f.read()
                    if normalize_output(actual) == normalize_output(expected):
                        verdict = "AC"
                        detail = f"{elapsed_ms:.1f}ms"
                    else:
                        verdict = "WA"
                        detail = f"{elapsed_ms:.1f}ms"
            except subprocess.TimeoutExpired:
                verdict = "TLE"
                elapsed_ms = timeout * 1000
                detail = f">= {timeout*1000:.0f}ms"
            except Exception as e:
                verdict = "RE"
                elapsed_ms = 0
                detail = str(e)[-200:]

            score = score_map.get(in_name)
            if score is None:
                # 动态等分
                base = total // len(pairs)
                rem = total % len(pairs)
                score = base + (1 if idx <= rem else 0)
            if verdict == "AC":
                got += score
            results.append((idx, in_name, verdict, score, detail))
            print(f"  [{idx}] {in_name}: {verdict} +{score if verdict == 'AC' else 0} ({detail})")

    print(f"[result] {got}/{total}")
    if got == total:
        print("[ok] 全部 AC")
    else:
        print("[warn] 存在非 AC 测试点")


if __name__ == "__main__":
    main()