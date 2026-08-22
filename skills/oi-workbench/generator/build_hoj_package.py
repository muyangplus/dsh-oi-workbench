#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_hoj_package.py —— 生成 HOJ（HimitZH/HOJ）原生导入 zip。

文件格式以 HOJ 官方“导出题目”zip 为基准（problem_<pid>.json + problem_<pid>/
内含数据文件与 info），并补充校验。参考实例：HOJ 后台「导出」产物。

用法:
    python build_hoj_package.py <题目目录> [--out <输出.zip>] [--check]

题目目录结构与 Hydro 打包器一致（spec.json / problem.md / data/ / sample/ / std/ ...）。

生成物:
    problem_<pid>.zip
    ├── problem_<pid>.json
    └── problem_<pid>/
        ├── 1.in
        ├── 1.out
        ├── ...
        └── info          # 测试点元数据（mode/judgeCaseMode/version/testCasesSize/testCases）
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
import zipfile

import spec_support

DEFAULT_COMPILE_CPP = "-O2 -std=c++14 -static"
VALID_JUDGE_MODES = {"default", "spj", "interactive"}
VALID_CASE_MODES = {"default", "subtask_lowest", "subtask_average"}
DEFAULT_CODE_TEMPLATES = [{"code": "", "language": "C++"}]


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


def parse_time_ms(value):
    if isinstance(value, (int, float)):
        return int(value)
    s = str(value).strip().lower()
    if s.endswith("ms"):
        return int(float(s[:-2]))
    if s.endswith("s"):
        return int(float(s[:-1]) * 1000)
    try:
        return int(float(s))
    except ValueError:
        return 1000


def parse_memory_mb(value):
    if isinstance(value, (int, float)):
        return int(value)
    s = str(value).strip().lower()
    if s.endswith("mb"):
        return int(float(s[:-2]))
    if s.endswith("m"):
        return int(float(s[:-1]))
    if s.endswith("k"):
        return max(1, int(float(s[:-1]) / 1024))
    try:
        return int(float(s))
    except ValueError:
        return 256


def sanitize(name):
    return re.sub(r"[^0-9A-Za-z_-]", "_", str(name))


def data_pairs(data_dir):
    pairs = []
    if not os.path.isdir(data_dir):
        return pairs
    for f in sorted(os.listdir(data_dir)):
        if f.endswith(".in"):
            base = f[:-3]
            out = base + ".out"
            if os.path.exists(os.path.join(data_dir, out)):
                pairs.append({"input": f, "output": out})
            else:
                ans = base + ".ans"
                if os.path.exists(os.path.join(data_dir, ans)):
                    pairs.append({"input": f, "output": ans})
    return pairs


def build_case_list(spec, pairs):
    """把 spec 的 cases/subtasks 展开为统一 case 列表。

    每个 case: {input, output, score?, groupNum?}
    """
    cases = []
    subtasks = spec.get("subtasks")
    if subtasks:
        for idx, st in enumerate(subtasks, 1):
            st_cases = st.get("cases") or []
            total = int(st.get("score") or 0)
            n = max(1, len(st_cases))
            base = total // n
            rem = total % n
            for j, c in enumerate(st_cases):
                entry = {"input": c["input"], "output": c["output"]}
                if c.get("score") is not None:
                    entry["score"] = int(c["score"])
                else:
                    entry["score"] = base + (1 if j < rem else 0)
                entry["groupNum"] = idx
                cases.append(entry)
        return cases

    # 逐点模式
    spec_cases = spec.get("cases")
    if spec_cases:
        for c in spec_cases:
            entry = {"input": c["input"], "output": c["output"]}
            if c.get("score") is not None:
                entry["score"] = int(c["score"])
            if c.get("groupNum") is not None:
                entry["groupNum"] = int(c["groupNum"])
            cases.append(entry)
        return cases

    # data/ 自动发现
    n = len(pairs)
    for i, p in enumerate(pairs, 1):
        entry = {"input": p["input"], "output": p["output"]}
        cases.append(entry)
    return cases


def fill_default_scores(cases):
    """OI 逐点模式没有明确 score 时按等分 100 分。"""
    if not cases:
        return cases
    if all(c.get("score") is None for c in cases):
        n = len(cases)
        base = 100 // n
        rem = 100 % n
        for i, c in enumerate(cases):
            c["score"] = base + (1 if i < rem else 0)
    return cases


def parse_problem_md_sections(pdir):
    """解析 problem.md 的二级标题，返回 {标题: 内容}。"""
    md_path = os.path.join(pdir, "problem.md")
    if not os.path.exists(md_path):
        return {}
    with open(md_path, encoding="utf-8") as f:
        text = f.read()
    sections = {}
    cur_title = None
    cur_lines = []
    for line in text.splitlines():
        m = re.match(r"^#{1,3}\s+(.*)$", line.strip())
        if m:
            if cur_title is not None:
                sections[cur_title] = "\n".join(cur_lines).strip()
            cur_title = m.group(1).strip()
            cur_lines = []
        else:
            cur_lines.append(line)
    if cur_title is not None:
        sections[cur_title] = "\n".join(cur_lines).strip()
    return sections


def parse_problem_md(pdir):
    """返回 (description, input, output, data_range, hint)。

    hint 优先取 spec 显式值，否则把『数据范围』放入 hint（HOJ 的提示区）。
    """
    sections = parse_problem_md_sections(pdir)

    def pick(*names):
        vals = []
        for title, content in sections.items():
            if any(n in title for n in names) and content:
                vals.append(content)
        return "\n\n".join(vals).strip()

    desc = pick("题目描述", "Description", "题面") or (sections.get("题目描述") or "")
    inp = pick("输入格式", "输入")
    out = pick("输出格式", "输出")
    data_range = pick("数据范围", "数据范围与约定", "Constraints")
    if not desc:
        desc = "\n".join(sections.values()).strip()
    return desc, inp, out, data_range


def build_examples_html(sample_dir):
    if not os.path.isdir(sample_dir):
        return ""
    blocks = []
    for f in sorted(os.listdir(sample_dir)):
        if f.endswith(".in"):
            base = f[:-3]
            out_path = os.path.join(sample_dir, base + ".out")
            if not os.path.exists(out_path):
                out_path = os.path.join(sample_dir, base + ".ans")
            if not os.path.exists(out_path):
                continue
            with open(os.path.join(sample_dir, f), encoding="utf-8") as fi:
                inp = fi.read().rstrip("\n")
            with open(out_path, encoding="utf-8") as fo:
                oup = fo.read().rstrip("\n")
            blocks.append(f"<input>{inp}</input><output>{oup}</output>")
    return "".join(blocks)


def md5_bytes(b):
    return hashlib.md5(b).hexdigest()


def stripped_all(b):
    return b.replace(b" ", b"").replace(b"\t", b"").replace(b"\r", b"").replace(b"\n", b"")


def stripped_eof(b):
    return b.rstrip()


def build_info(ordered_cases, data_dir):
    """生成 HOJ 题目目录内的 info 文件内容（与官方导出一致）。"""
    test_cases = []
    for i, c in enumerate(ordered_cases, 1):
        out_name = c["output"]
        out_path = os.path.join(data_dir, out_name)
        if not os.path.exists(out_path):
            out_path = os.path.join(data_dir, os.path.splitext(out_name)[0] + ".ans")
        with open(out_path, "rb") as f:
            out_bytes = f.read()
        test_cases.append({
            "caseId": 100000 + i,
            "score": int(c.get("score") or 0),
            "inputName": c["input"],
            "outputName": out_name,
            "outputMd5": md5_bytes(out_bytes),
            "outputSize": len(out_bytes),
            "allStrippedOutputMd5": md5_bytes(stripped_all(out_bytes)),
            "EOFStrippedOutputMd5": md5_bytes(stripped_eof(out_bytes)),
        })
    return {
        "mode": "default",
        "judgeCaseMode": "default",
        "version": str(int(time.time() * 1000)),
        "testCasesSize": len(test_cases),
        "testCases": test_cases,
    }


def build_hoj_payload(spec, cases, pdir):
    data_dir = os.path.join(pdir, "data")
    pairs = data_pairs(data_dir)
    case_lookup = {c["input"]: c for c in cases}
    ordered_cases = []
    seen_inputs = set()
    for p in pairs:
        c = case_lookup.get(p["input"], p)
        if c["input"] in seen_inputs:
            continue
        seen_inputs.add(c["input"])
        ordered_cases.append(dict(c))
    for c in cases:
        if c["input"] not in seen_inputs:
            if not os.path.exists(os.path.join(data_dir, c["input"])):
                continue
            ordered_cases.append(dict(c))
            seen_inputs.add(c["input"])
    if not ordered_cases:
        ordered_cases = [dict(c) for c in cases]
    # 数值顺序：1.in, 2.in, ..., 10.in
    ordered_cases.sort(key=lambda c: int(re.sub(r"\D", "", os.path.splitext(c["input"])[0]) or 0))
    ordered_cases = fill_default_scores(ordered_cases)

    mode = spec_support.resolve_mode(spec)
    type_oi = str(spec.get("type", "oi")).lower() in ("1", "oi", "true")
    if mode == "acm":
        type_oi = False
    judge_spec = spec.get("judge") or {}
    judge = spec_support.resolve_judge(spec)
    judge_mode = judge["type"]
    if judge_mode not in VALID_JUDGE_MODES:
        judge_mode = "default"
    if judge.get("interactor"):
        judge_mode = "interactive"
    elif judge.get("spj") or judge.get("checker"):
        judge_mode = "spj"

    jcm = spec.get("judgeCaseMode", "").lower()
    if jcm not in VALID_CASE_MODES:
        jcm = "default"
    if mode == "subtask" and jcm == "default":
        jcm = "subtask_lowest"
    if mode == "acm":
        jcm = "default"

    for c in ordered_cases:
        if type_oi:
            if c.get("score") is None:
                c["score"] = 0
        else:
            c.pop("score", None)
            c.pop("groupNum", None)

    total_score = sum(int(c.get("score") or 0) for c in ordered_cases) if type_oi else None

    desc, inp, out, data_range = parse_problem_md(pdir)
    sample_dir = os.path.join(pdir, "sample")
    examples = build_examples_html(sample_dir)
    memory = parse_memory_mb(spec.get("memory", "256m"))
    io_mode, io_in, io_out = spec_support.resolve_io(spec)
    file_io = {"input": io_in, "output": io_out} if io_mode == "file" else {}
    languages = spec.get("languages") or ["C++"]
    tags = spec.get("tags") or []
    code_templates = spec.get("codeTemplates") or DEFAULT_CODE_TEMPLATES
    hint = spec.get("hint")
    if not hint:
        hint = data_range

    problem = {
        "problemId": str(spec.get("pid") or "P1001"),
        "title": spec["title"],
        "type": 1 if type_oi else 0,
        "judgeMode": judge_mode,
        "judgeCaseMode": jcm,
        "timeLimit": parse_time_ms(spec.get("time", "1000ms")),
        "memoryLimit": memory,
        "stackLimit": int(spec.get("stackLimit", memory)),
        "description": spec.get("description", desc),
        "input": spec.get("input", inp),
        "output": spec.get("output", out),
        "examples": spec.get("examples", examples),
        "difficulty": int(spec.get("difficulty", 0) or 0),
        "ioScore": total_score if total_score is not None else spec.get("ioScore", 100),
        "codeShare": bool(spec.get("codeShare", True)),
        "isRemoveEndBlank": bool(spec.get("isRemoveEndBlank", True)),
        "openCaseResult": bool(spec.get("openCaseResult", True)),
        "auth": int(spec.get("auth", 1)),
        "source": spec.get("source", "OI Workbench"),
        "hint": hint,
        "isRemote": False,
        "isFileIO": bool(file_io),
        "ioReadFileName": file_io.get("input") if file_io else None,
        "ioWriteFileName": file_io.get("output") if file_io else None,
        "isGroup": False,
        "isUploadCase": True,
    }

    if judge_mode in ("spj", "interactive"):
        spj_file = judge_spec.get("spjCode") or judge.get("checker")
        if spj_file:
            spj_path = os.path.join(pdir, "data", spj_file)
            if os.path.exists(spj_path):
                with open(spj_path, encoding="utf-8") as f:
                    problem["spjCode"] = f.read()
        problem["spjLanguage"] = judge_spec.get("language", "C++")
        if judge_spec.get("userExtraFile"):
            problem["userExtraFile"] = judge_spec["userExtraFile"]
        if judge_spec.get("judgeExtraFile"):
            problem["judgeExtraFile"] = judge_spec["judgeExtraFile"]

    samples = []
    for c in ordered_cases:
        s = {"input": c["input"], "output": c["output"]}
        if type_oi:
            s["score"] = int(c.get("score") or 0)
        if jcm in ("subtask_lowest", "subtask_average") and c.get("groupNum") is not None:
            s["groupNum"] = int(c["groupNum"])
        samples.append(s)

    payload = {
        "judgeMode": judge_mode,
        "languages": languages,
        "samples": samples,
        "tags": tags,
        "problem": problem,
        "codeTemplates": code_templates,
    }
    if spec.get("userExtraFile"):
        payload["userExtraFile"] = spec["userExtraFile"]
    if spec.get("judgeExtraFile"):
        payload["judgeExtraFile"] = spec["judgeExtraFile"]
    return payload, ordered_cases


def validate_spec(spec, cases, data_dir):
    errors = []
    if not cases:
        errors.append("samples 为空：data/ 下没有可用测试数据")
    for c in cases:
        inp, out = c.get("input"), c.get("output")
        if not inp or not out:
            errors.append(f"case 缺少 input/output: {c}")
            continue
        if not os.path.exists(os.path.join(data_dir, inp)):
            errors.append(f"case 输入不存在: {inp}")
        if not os.path.exists(os.path.join(data_dir, out)) and not os.path.exists(
                os.path.join(data_dir, os.path.splitext(inp)[0] + ".ans")):
            errors.append(f"case 输出不存在: {out}")
    type_oi = str(spec.get("type", "oi")).lower() in ("1", "oi", "true")
    if type_oi and cases and all(c.get("score") is not None for c in cases):
        total = sum(int(c.get("score") or 0) for c in cases)
        if total != 100:
            errors.append(f"OI 测试点分值之和 = {total}（应为 100）")
    return errors


def main():
    ap = argparse.ArgumentParser(description="生成 HOJ 原生导入 zip")
    ap.add_argument("problem_dir")
    ap.add_argument("--out", default=None)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    pdir = os.path.normpath(args.problem_dir)
    if not os.path.isdir(pdir):
        sys.exit(f"题目目录不存在: {pdir}")
    data_dir = os.path.join(pdir, "data")
    spec = load_spec(pdir)
    pairs = data_pairs(data_dir)
    cases = build_case_list(spec, pairs)

    errors = validate_spec(spec, cases, data_dir)
    if errors:
        for e in errors:
            print(f"[error] {e}")
        sys.exit("HOJ 包校验失败")

    payload, ordered = build_hoj_payload(spec, cases, pdir)
    pid = payload["problem"]["problemId"]
    base = f"problem_{sanitize(pid)}"
    out_zip = args.out or (base + ".zip")

    if args.check:
        print(f"[ok] {len(ordered)} 个测试点；将生成 {base}.json + {base}/（含 info）")
        print(f"     题型={'OI' if payload['problem']['type'] == 1 else 'ACM'} "
              f"judgeMode={payload['judgeMode']} judgeCaseMode={payload['problem']['judgeCaseMode']} "
              f"time={payload['problem']['timeLimit']}ms memory={payload['problem']['memoryLimit']}MB")
        return

    if not os.path.isdir(data_dir):
        sys.exit(f"缺少 data/ 目录: {data_dir}")

    info = build_info(ordered, data_dir)

    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{base}.json", json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
        z.writestr(f"{base}/info", json.dumps(info, ensure_ascii=False, separators=(",", ":")))
        for root, _, files in os.walk(data_dir):
            for f in files:
                full = os.path.join(root, f)
                z.write(full, f"{base}/{f}")
        sample_dir = os.path.join(pdir, "sample")
        if os.path.isdir(sample_dir):
            existing = set(z.namelist())
            for f in sorted(os.listdir(sample_dir)):
                full = os.path.join(sample_dir, f)
                if os.path.isfile(full) and f"{base}/{f}" not in existing:
                    z.write(full, f"{base}/{f}")

    print(f"[ok] 已生成 {out_zip}")
    print(f"     布局: {base}.json + {base}/（{len(ordered)} 个测试点 + info）")
    print("     导入: HOJ 后台『题目管理 → 导入题目』选择本 zip，或 POST /api/file/import-problem")
    if payload["problem"]["type"] == 1:
        print(f"     OI 总分: {payload['problem']['ioScore']}")


if __name__ == "__main__":
    main()
