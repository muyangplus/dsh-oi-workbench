#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
local_judge.py —— 本地评测脚本（OI 风格，支持 standard/file IO、spj、三种计分模式）。

编译命令固定遵循全国统一评测规范：
    g++ -O2 -std=c++14 -static -o <exe> <source>

用法:
    python local_judge.py <题目目录> \
        --source std/std.cpp \
        --time 1000 --memory 512 \
        [--compile "-O2 -std=c++14 -static"] \
        [--file-io READ WRITE]

IO 与评测模式从 spec.json 读取（约定见 spec_support.py / templates/problem.yaml）：
    "io":    { "type": "standard"|"file", "input": "xxx.in", "output": "xxx.out" }
    "judge": { "spj": bool, "checker": "spj.cpp", "interactor": "interactor.cpp",
               "mode": "traditional"|"subtask"|"acm" }
旧字段兼容：spec.fileIO 等效 io.type=file；judge.type=special 等效 spj。

说明:
    - standard：stdin/stdout 管道；file：临时工作区，std 读/写 io 文件名，比对写出的文件。
    - spj：按 testlib 命令行约定调用 checker <input> <output> <answer>，
      退出码 0 = AC，否则 WA（checker 源码放 data/ 或 checker/ 下）。
    - 计分：traditional/acm 逐点；subtask 捆绑（组内全 AC 且依赖组通过才计分）。
    - 输出比较：全文比较（过滤行末空格及文末换行）。
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import tempfile
import time

DEFAULT_COMPILE = "-O2 -std=c++14 -static"
DEFAULT_TIME_MS = 1000
DEFAULT_MEMORY_MB = 512

try:
    from spec_support import resolve_io, resolve_judge, resolve_mode
except ImportError:  # 兜底：在被以非规则方式调用时也能工作
    def resolve_io(spec):
        io = spec.get("io") or {}
        if isinstance(io, dict) and io.get("type") == "file":
            return "file", io.get("input") or "problem.in", io.get("output") or "problem.out"
        fio = spec.get("fileIO")
        if isinstance(fio, dict) and (fio.get("input") or fio.get("output")):
            return "file", fio.get("input") or "problem.in", fio.get("output") or "problem.out"
        return "standard", None, None

    def resolve_judge(spec):
        judge = dict(spec.get("judge") or {})
        jtype = judge.get("type") or "default"
        if jtype == "special":
            jtype = "default"
            judge["spj"] = True
        if jtype in ("interactive", "communication"):
            judge["spj"] = True
        return {"type": jtype, "spj": bool(judge.get("spj")),
                "checker": judge.get("checker"), "interactor": judge.get("interactor")}

    def resolve_mode(spec):
        mode = (spec.get("judge") or {}).get("mode")
        if mode in ("traditional", "subtask", "acm"):
            return mode
        if str(spec.get("type", "oi")).lower() in ("acm", "0", "false"):
            return "acm"
        return "subtask" if spec.get("subtasks") else "traditional"


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
            scores["%d.in" % i] = base + (1 if i <= rem else 0)
    return scores


def compile_source(source, out_exe, compile_flags, include_dirs=None):
    cmd = ["g++"] + compile_flags.split()
    for d in include_dirs or []:
        cmd.append("-I" + d)
    cmd += [source, "-o", out_exe]
    print("[compile] %s" % " ".join(cmd))
    return subprocess.run(cmd, capture_output=True, text=True)


def find_checker_source(pdir, name):
    for d in ("data", "checker"):
        p = os.path.join(pdir, d, name)
        if os.path.isfile(p):
            return p
    return None


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


def run_checker(checker_exe, in_path, actual_path, exp_path, timeout):
    st = time.perf_counter()
    try:
        cp = subprocess.run([checker_exe, in_path, actual_path, exp_path],
                            capture_output=True, text=True, timeout=timeout)
        elapsed_ms = (time.perf_counter() - st) * 1000
    except subprocess.TimeoutExpired:
        return None, timeout * 1000
    return cp, elapsed_ms


def _pump(src, dst):
    """把 src 管道的数据搬运到 dst 管道，直到 EOF。

    使用 os.read 而非 BufferedReader.read(n)：Windows 管道在未满 n 字节时
    可能阻塞到 EOF，导致交互题死锁；os.read 能立即返回已到达的字节。
    """
    try:
        fd = src.fileno()
        while True:
            data = os.read(fd, 4096)
            if not data:
                break
            dst.write(data)
            dst.flush()
    except Exception:
        pass
    finally:
        try:
            dst.close()
        except Exception:
            pass


def run_interactive(exe, interactor_exe, in_path, exp_path, output_path, workdir, timeout):
    """运行交互题：solution <-> interactor 双向管道；interactor 退出码 0 = AC。

    testlib interactor 参数约定：<input-file> <output-file> <answer-file>，
    output-file 为 interactor 写参与者输出的文件。
    使用两个泵线程中转 solution 与 interactor 之间的数据，避免管道 EOF 死锁。
    """
    st = time.perf_counter()
    try:
        inter = subprocess.Popen(
            [interactor_exe, in_path, output_path, exp_path],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sol = subprocess.Popen(
            [exe], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, cwd=workdir)

        t1 = threading.Thread(target=_pump, args=(sol.stdout, inter.stdin), daemon=True)
        t2 = threading.Thread(target=_pump, args=(inter.stdout, sol.stdin), daemon=True)
        t1.start()
        t2.start()

        try:
            sol.wait(timeout=timeout)
            inter.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            sol.kill()
            inter.kill()
            sol.wait()
            inter.wait()
            return {"timeout": True, "elapsed_ms": timeout * 1000}

        t1.join(timeout=1)
        t2.join(timeout=1)
        elapsed_ms = (time.perf_counter() - st) * 1000

        def read_err(pipe):
            try:
                if pipe is None:
                    return ""
                data = pipe.read()
                return data.decode("utf-8", "replace")
            except Exception:
                return ""

        sol_err = read_err(sol.stderr)
        inter_err = read_err(inter.stderr)
        msg = (inter_err + sol_err).strip().replace("\n", " ")[:200]
        return {
            "timeout": False,
            "elapsed_ms": elapsed_ms,
            "sol_rc": sol.returncode,
            "inter_rc": inter.returncode,
            "inter_msg": msg,
        }
    except Exception as e:
        return {"timeout": False, "elapsed_ms": 0, "error": str(e)}


def main():
    ap = argparse.ArgumentParser(description="本地 OI 评测器（standard/file IO，spj，三态计分）")
    ap.add_argument("problem_dir")
    ap.add_argument("--source", default="std/std.cpp")
    ap.add_argument("--compile", default=DEFAULT_COMPILE)
    ap.add_argument("--time", type=int, default=None, help="单点时限 ms，默认取 spec.json time")
    ap.add_argument("--memory", type=int, default=None, help="内存限制 MB，默认取 spec.json memory")
    ap.add_argument("--file-io", nargs=2, metavar=("READ", "WRITE"), default=None)
    ap.add_argument("--testlib-dir", default=None,
                    help="testlib.h 所在目录（默认 generator/testlib）")
    args = ap.parse_args()

    pdir = os.path.normpath(args.problem_dir)
    spec = load_spec(pdir)
    time_ms = args.time or parse_time_ms(spec.get("time", "1000ms"))
    memory_mb = args.memory or parse_memory_mb(spec.get("memory", "256m"))
    timeout = max(0.05, time_ms / 1000.0 * 1.5 + 0.5)

    data_dir = os.path.join(pdir, "data")
    if not os.path.isdir(data_dir):
        sys.exit("缺少 data/ 目录: %s" % data_dir)
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

    io_mode, io_in, io_out = resolve_io(spec)
    judge = resolve_judge(spec)
    mode = resolve_mode(spec)
    file_io = args.file_io or (None if io_mode == "standard" else (io_in, io_out))
    source = os.path.join(pdir, args.source)
    if not os.path.exists(source):
        sys.exit("源代码不存在: %s" % source)

    print("[mode] judge.mode=%s io=%s%s" % (
        mode, io_mode, " spj=%s" % judge["checker"] if judge["spj"] and judge["checker"] else ""))

    with tempfile.TemporaryDirectory(prefix="oiwb-judge-") as tmp:
        exe = os.path.join(tmp, "program.exe" if os.name == "nt" else "program")
        cp = compile_source(source, exe, args.compile)
        if cp.returncode != 0:
            print(cp.stdout)
            print(cp.stderr)
            sys.exit("编译失败")
        print("[ok] 编译成功")
        # 预热：新编译 exe 首次启动会被本机杀软/装载器拖慢（首个测试点假 TLE），先跑一小段丢弃结果。
        try:
            if file_io:
                wu = os.path.join(tmp, "warmup")
                os.makedirs(wu, exist_ok=True)
                with open(os.path.join(wu, file_io[0]), "w", encoding="utf-8") as f:
                    f.write("0 0\n")
                subprocess.run([exe], cwd=wu, stdin=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            else:
                subprocess.run([exe], input=b"0 0\n", stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, timeout=5)
        except Exception:
            pass

        testlib_dir = args.testlib_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "testlib")
        testlib_h = os.path.join(testlib_dir, "testlib.h")

        def ensure_testlib(src):
            if not os.path.exists(testlib_h):
                with open(src, encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                if re.search(r'#\s*include\s*[<"]testlib\.h[>"]', text):
                    sys.exit(
                        "checker/interactor 使用 testlib.h，但未找到 %s；"
                        "请按 generator/testlib/README.md 放置官方 testlib.h（MIT）" % testlib_h)

        checker_exe = None
        interactor_exe = None
        if judge["spj"]:
            interactor = judge.get("interactor")
            checker = judge.get("checker")
            if interactor:
                interactor_src = find_checker_source(pdir, interactor)
                if not interactor_src:
                    sys.exit("交互题未找到 interactor 源码: %s（期望在 data/ 或 checker/）" % interactor)
                ensure_testlib(interactor_src)
                interactor_exe = os.path.join(tmp, "interactor.exe" if os.name == "nt" else "interactor")
                icp = compile_source(interactor_src, interactor_exe, args.compile, [testlib_dir])
                if icp.returncode != 0:
                    print(icp.stdout)
                    print(icp.stderr)
                    sys.exit("interactor 编译失败")
            if checker:
                checker_src = find_checker_source(pdir, checker)
                if not checker_src:
                    sys.exit("spj 未找到 checker 源码: %s（期望在 data/ 或 checker/）" % checker)
                ensure_testlib(checker_src)
                checker_exe = os.path.join(tmp, "checker.exe" if os.name == "nt" else "checker")
                ccp = compile_source(checker_src, checker_exe, args.compile, [testlib_dir])
                if ccp.returncode != 0:
                    print(ccp.stdout)
                    print(ccp.stderr)
                    sys.exit("checker 编译失败")

        score_map = get_score_map(pdir, len(pairs))
        subtasks = spec.get("subtasks")
        verdicts = {}
        results = []
        for idx, (in_name, out_name) in enumerate(pairs, 1):
            in_path = os.path.join(data_dir, in_name)
            exp_path = os.path.join(data_dir, out_name)
            try:
                if file_io:
                    workdir = os.path.join(tmp, "case%d" % idx)
                    os.makedirs(workdir, exist_ok=True)
                    cp, elapsed_ms, actual_text = run_fileio(
                        exe, workdir, in_path, file_io[0], file_io[1], timeout)
                    actual_path = os.path.join(workdir, file_io[1])
                    if not os.path.exists(actual_path):
                        with open(actual_path, "w", encoding="utf-8") as f:
                            f.write(actual_text or "")
                else:
                    cp, elapsed_ms = run_stdio(exe, in_path, timeout)
                    actual_text = cp.stdout.decode("utf-8", "replace") if isinstance(cp.stdout, bytes) else (cp.stdout or "")
                    workdir = os.path.join(tmp, "case%d" % idx)
                    os.makedirs(workdir, exist_ok=True)
                    actual_path = os.path.join(workdir, "actual.out")
                    with open(actual_path, "w", encoding="utf-8") as f:
                        f.write(actual_text)

                if cp.returncode != 0:
                    verdict = "RE"
                    detail = (cp.stderr or "").decode("utf-8", "replace")[-200:] if isinstance(cp.stderr, bytes) else (cp.stderr or "")[-200:]
                elif elapsed_ms > time_ms:
                    verdict = "TLE"
                    detail = "%.1fms > %dms" % (elapsed_ms, time_ms)
                elif interactor_exe:
                    ir = run_interactive(
                        exe, interactor_exe, in_path, exp_path,
                        os.path.join(os.path.dirname(actual_path), "participant.out"),
                        os.path.dirname(actual_path), timeout)
                    if ir.get("timeout"):
                        verdict = "TLE"
                        detail = ">= %.0fms" % ir["elapsed_ms"]
                    elif ir.get("error"):
                        verdict = "RE"
                        detail = ir["error"]
                    elif ir["sol_rc"] != 0:
                        verdict = "RE"
                        detail = "solution exit=%d%s" % (ir["sol_rc"], (" " + ir["inter_msg"]) if ir["inter_msg"] else "")
                    elif ir["inter_rc"] == 0:
                        verdict = "AC"
                        detail = "%.1fms%s" % (ir["elapsed_ms"], (" " + ir["inter_msg"]) if ir["inter_msg"] else "")
                    else:
                        verdict = "WA"
                        detail = "%.1fms%s" % (ir["elapsed_ms"], (" " + ir["inter_msg"]) if ir["inter_msg"] else "")
                elif checker_exe:
                    ck, ck_ms = run_checker(checker_exe, in_path, actual_path, exp_path, timeout)
                    if ck is None:
                        verdict = "TLE"
                        detail = "checker >= %.0fms" % ck_ms
                    else:
                        verdict = "AC" if ck.returncode == 0 else "WA"
                        msg = ((ck.stdout or "") + (ck.stderr or "")).strip().replace("\n", " ")[:120]
                        detail = "%.1fms%s" % (elapsed_ms, (" " + msg) if msg else "")
                else:
                    with open(exp_path, encoding="utf-8", errors="replace") as f:
                        expected = f.read()
                    detail = "%.1fms" % elapsed_ms
                    verdict = "AC" if normalize_output(actual_text) == normalize_output(expected) else "WA"
            except subprocess.TimeoutExpired:
                verdict = "TLE"
                elapsed_ms = timeout * 1000
                detail = ">= %.0fms" % (timeout * 1000)
            except Exception as e:
                verdict = "RE"
                elapsed_ms = 0
                detail = str(e)[-200:]

            verdicts[in_name] = verdict
            results.append((idx, in_name, out_name, verdict, detail))
            if subtasks:
                print("  [%d] %s: %s (%s)" % (idx, in_name, verdict, detail))
            else:
                score = score_map.get(in_name)
                if score is None:
                    base = 100 // len(pairs)
                    rem = 100 % len(pairs)
                    score = base + (1 if idx <= rem else 0)
                results[-1] = (idx, in_name, out_name, verdict, detail)
                print("  [%d] %s: %s +%d (%s)" % (idx, in_name, verdict, score if verdict == "AC" else 0, detail))

        # 计分
        got = 0
        if subtasks:
            passed = set()
            for gidx, st in enumerate(subtasks, 1):
                deps = st.get("if") or []
                st_cases = [c["input"] for c in (st.get("cases") or [])]
                ok = all(verdicts.get(c) == "AC" for c in st_cases) and all(d in passed for d in deps)
                gscore = int(st.get("score") or 0)
                if ok:
                    passed.add(gidx)
                    got += gscore
                print("  [subtask %d] %s +%d (case 依赖: %s)" % (gidx, "AC" if ok else "WA", gscore if ok else 0, deps or "-"))
        else:
            for idx, in_name in enumerate([p[0] for p in pairs], 1):
                score = score_map.get(in_name)
                if score is None:
                    base = 100 // len(pairs)
                    rem = 100 % len(pairs)
                    score = base + (1 if idx <= rem else 0)
                if verdicts.get(in_name) == "AC":
                    got += score

    print("[result] %d/100" % got)
    if got == 100:
        print("[ok] 全部 AC")
    else:
        print("[warn] 存在非 AC 测试点")


if __name__ == "__main__":
    main()
