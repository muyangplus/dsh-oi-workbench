#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_spj.py —— 特殊评测（spj/交互题）样例验证自动化。

为带 `judge.spj`（checker 或 interactor）的题目自动验证：
  1. 标程在本地评测下应全 AC；
  2. 一个故意输出错误答案的程序应被特殊评测判为 WA（不能 100/100）。

用法：
  python generator/validate_spj.py --problem <题目目录>
  python generator/validate_spj.py --problem <题目目录> --source-std std/std.cpp
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def load_spec(pdir):
    with open(os.path.join(pdir, "spec.json"), encoding="utf-8") as f:
        return json.load(f)


def bad_source(spec, interactive):
    io = spec.get("io") or {}
    file_io = io.get("type") == "file" and io.get("input")
    if interactive:
        return (
            "#include <iostream>\n"
            "using namespace std;\n"
            "int main(){ int x; if(cin>>x){} cout<<0<<endl; return 0; }\n"
        )
    if file_io:
        return (
            "#include <cstdio>\n"
            "int main(){ freopen(\"%s\",\"r\",stdin); freopen(\"%s\",\"w\",stdout);\n"
            "  long long x; while(scanf(\"%%lld\",&x)==1){} printf(\"0\\n\"); return 0; }\n"
        ) % (io["input"], io["output"])
    return (
        "#include <iostream>\n"
        "int main(){ long long x; while(std::cin>>x){} std::cout<<0<<std::endl; return 0; }\n"
    )


def run_local(pdir, source, timeout=300):
    cmd = [sys.executable, os.path.join(HERE, "local_judge.py"), pdir, "--source", source]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    text = (r.stdout or "") + (r.stderr or "")
    m = re.search(r"\[result\]\s*(\d+)/100", text)
    score = int(m.group(1)) if m else None
    return score, text


def main():
    ap = argparse.ArgumentParser(description="spj/交互题样例验证自动化")
    ap.add_argument("--problem", required=True)
    ap.add_argument("--source-std", default="std/std.cpp")
    args = ap.parse_args()

    pdir = os.path.normpath(args.problem)
    spec = load_spec(pdir)
    judge = spec.get("judge") or {}
    if not judge.get("spj"):
        print("[skip] 非特殊评测题目（judge.spj=false），无需验证")
        return

    interactive = bool(judge.get("interactor"))
    kind = "interactor" if interactive else "checker"
    print("== 验证 %s（%s）==" % (pdir, kind))

    # 1) 标程应全 AC（local_judge 内部会把 pdir 与 --source 拼接，这里传相对路径）
    score_std, out_std = run_local(pdir, args.source_std)
    if score_std != 100:
        print("[FAIL] 标程未全 AC：%s" % score_std)
        print(out_std[-500:])
        sys.exit(1)
    print("[ok] 标程 100/100")

    # 2) 错误程序应被击杀（不能 100）
    bad = bad_source(spec, interactive)
    with tempfile.NamedTemporaryFile("w", suffix=".cpp", delete=False, encoding="utf-8") as f:
        f.write(bad)
        bad_path = f.name
    try:
        score_bad, out_bad = run_local(pdir, bad_path)
        if score_bad == 100:
            print("[FAIL] 错误程序竟然 100/100，特殊评测未生效")
            print(out_bad[-500:])
            sys.exit(1)
        print("[ok] 错误程序被击杀：%s/100" % score_bad)
    finally:
        os.unlink(bad_path)

    print("[ok] %s 样例验证通过" % kind)


if __name__ == "__main__":
    main()
