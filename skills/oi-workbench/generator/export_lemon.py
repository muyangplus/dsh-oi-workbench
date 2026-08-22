#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_lemon.py —— 导出 Lemon 评测机比赛数据（含 std 选手与 <比赛>.cdf）。

能力来源：Lemon/LemonLime 实战约定。
结构（经典 Lemon / LemonLime 通用）：
  <contest>/
    <contest>.cdf                              LemonLime 比赛文件（JSON，可直接“打开比赛”）
    data/<英文题名>/<英文题名><1..N>.in|.out   测试点
    source/std/<英文题名>.cpp                  标程选手
    README.txt                                  使用说明/配置表

用法：
  python generator/export_lemon.py \
      --contest LKCP \
      --problems drafts/csp-s-mock/climb drafts/csp-s-mock/signal \
      --out dist/lemon

说明：
  - 每题目录需含 spec.json（title/io/time/memory/cases）、data/、std/std.cpp；
  - 测试点命名采用 Lemon 惯用格式 <题目英文名><编号>.in/.out；
  - 默认打包为 <out>/<contest>-Lemon比赛数据.zip，--no-zip 可只生成目录；
  - 生成 <contest>.cdf：内含全部题目与 std 选手（未评测）；
    若目标目录已有 .cdf（例如用户已用 Lemon 保存过比赛），默认保留原文件，
    用 --force-cdf 可覆盖为新生成的干净 .cdf。
"""
import argparse
import json
import os
import shutil
import zipfile

DEFAULT_NOTE = "每个测试点等分，总分 100。"


def load_problem(problem_dir):
    with open(os.path.join(problem_dir, "spec.json"), encoding="utf-8") as f:
        spec = json.load(f)
    io = spec.get("io") or {}
    if io.get("type") == "file" and io.get("input"):
        stem = os.path.splitext(io["input"])[0]
    else:
        stem = os.path.basename(os.path.normpath(problem_dir))
    cases = spec.get("cases") or []
    scores = [c.get("score") for c in cases if c.get("score") is not None]
    per_point = scores[0] if len(set(scores)) <= 1 and scores else None
    return {
        "file": stem,
        "name": spec.get("title", stem),
        "cpp": stem + ".cpp",
        "io": io,
        "time": spec.get("time", "1000ms"),
        "memory": spec.get("memory", "512m"),
        "npoints": len(cases),
        "per_point": per_point,
        "dir": problem_dir,
    }


def parse_time(t):
    s = str(t).strip().lower()
    if s.endswith("ms"):
        ms = int(s[:-2])
        return "%g 秒" % (ms // 1000) if ms % 1000 == 0 else "%d ms" % ms
    return s


def parse_memory(m):
    s = str(m).strip().lower()
    try:
        if s.endswith("g"):
            return "%d MiB" % (int(s[:-1]) * 1024)
        if s.endswith("m"):
            return "%d MiB" % int(s[:-1])
        return s
    except Exception:
        return s


def time_ms(t):
    s = str(t).strip().lower()
    try:
        if s.endswith("ms"):
            return int(s[:-2])
        if s.endswith("s"):
            return int(float(s[:-1]) * 1000)
        return int(float(s) * 1000)
    except Exception:
        return 1000


def memory_mb(m):
    s = str(m).strip().lower()
    try:
        if s.endswith("g"):
            return int(s[:-1]) * 1024
        if s.endswith("m"):
            return int(s[:-1])
        if s.endswith("mb"):
            return int(s[:-2])
        return int(float(s))
    except Exception:
        return 512


def build_cdf(contest_title, problems):
    """生成 LemonLime <contest>.cdf 内容（JSON 可序列化 dict）。"""
    tasks = []
    for p in problems:
        io = p["io"] or {}
        file_io = io.get("type") == "file"
        n = p["npoints"]
        per_point = p["per_point"] if p["per_point"] else (100 // n if n else 4)
        test_cases = []
        for i in range(1, n + 1):
            test_cases.append({
                "fullScore": per_point,
                "inputFiles": ["%s/%s%d.in" % (p["file"], p["file"], i)],
                "outputFiles": ["%s/%s%d.out" % (p["file"], p["file"], i)],
                "timeLimit": time_ms(p["time"]),
                "memoryLimit": memory_mb(p["memory"]),
            })
        tasks.append({
            "answerFileExtension": "out",
            "comparisonMode": 1,
            "compilerConfiguration": {"g++": "C++14 O2"},
            "diffArguments": "--ignore-space-change --text --brief",
            "inputFileName": io.get("input", "") if file_io else "",
            "outputFileName": io.get("output", "") if file_io else "",
            "problemTitle": p["file"],
            "realPrecision": 3,
            "sourceFileName": p["file"],
            "specialJudge": "",
            "standardInputCheck": False,
            "standardOutputCheck": False,
            "subFolderCheck": False,
            "taskType": 0,
            "testCases": test_cases,
        })
    contestant = {
        "contestantName": "std",
        "sourceFile": [p["cpp"] for p in problems],
        "compileState": [0] * len(problems),
        "compileMesaage": [""] * len(problems),
        "checkJudged": [False] * len(problems),
        "inputFiles": [[] for _ in problems],
        "memoryUsed": [[] for _ in problems],
        "message": [[] for _ in problems],
        "result": [[] for _ in problems],
        "score": [[] for _ in problems],
        "timeUsed": [[] for _ in problems],
        "judgingTime_date": 0,
        "judgingTime_time": 0,
        "judgingTime_timespec": 0,
    }
    return {
        "contestTitle": contest_title,
        "contestants": [contestant],
        "tasks": tasks,
        "version": "1.0",
    }


def build_readme(contest_title, cdf_filename, args, problems):
    rows = []
    total_score = 0
    for p in problems:
        score = p["per_point"] * p["npoints"] if p["per_point"] else 100
        total_score += score
        if (p["io"] or {}).get("type") == "file":
            fin = (p["io"] or {}).get("input", p["file"] + ".in")
            fout = (p["io"] or {}).get("output", p["file"] + ".out")
        else:
            fin, fout = "标准输入", "标准输出"
        rows.append(
            "  %-8s  %-12s %-10s %-11s  %-6s  %-7s  %-6d  %d\n"
            % (p["file"], p["cpp"], fin, fout,
               parse_time(p["time"]), parse_memory(p["memory"]), p["npoints"], score)
        )
    readme = (
        "%s —— Lemon 评测机比赛数据\n" % contest_title
        + "==================================================\n"
        + "比赛：%s / %s\n" % (contest_title, args.subtitle)
        + "时间：%s\n\n" % args.time
        + "目录说明\n--------\n"
        + "  %s              LemonLime 比赛文件（可直接“打开比赛”选择）\n" % cdf_filename
        + "  data\\<英文题名>\\      每题的测试点（<英文题名><编号>.in/.out）\n"
        + "  source\\std\\          标程选手（源码即每题标程，可用来核对数据）\n\n"
        + "各题配置（“控制 → 自动添加试题”时按此填写）\n"
        + "------------------------------------------------\n"
        + "  题目目录      源文件名       输入文件    输出文件    时限     内存     测试点数  分值\n"
        + "".join(rows)
        + "  " + DEFAULT_NOTE + "\n\n"
        + "使用方法（经典 Lemon / LemonLime 通用）\n"
        + "--------------------------------------\n"
        + "1. 打开 Lemon/LemonLime → 文件 → 打开比赛 → 选择本目录下的 %s；\n" % cdf_filename
        + "   若无法直接打开，再“新建比赛”并把保存位置选为本目录，然后“自动添加试题”。\n"
        + "2. 菜单“控制 → 自动添加试题”，按上表为每道题设置时限与内存（打开 .cdf 时已内置）。\n"
        + "3. 建议把比较模式设为“忽略行末空格与文末换行”（全文比较）。\n"
        + "4. 切换到“选手”标签页 → 刷新，即可看到 std 选手（满分 %d）。\n" % total_score
        + "5. “评测全部”即可出分。\n\n"
        + "说明\n----\n"
        + "- 测试点文件命名采用 Lemon 惯用格式 <题目英文名><编号>.in/.out，\n"
        + "  Lemon 会自动识别各题源文件名与输入输出文件名。\n"
        + "- %s 由本工具生成，内含全部题目与 std 选手（未评测状态）。\n" % cdf_filename
    )
    return readme


def main():
    ap = argparse.ArgumentParser(description="导出 Lemon 评测机比赛数据（含 std 选手与 .cdf）")
    ap.add_argument("--contest", default="LKCP")
    ap.add_argument("--subtitle", default="2026 第二轮认证")
    ap.add_argument("--time", default="2026 年 8 月 22 日 13:00~16:00")
    ap.add_argument("--problems", nargs="+", required=True,
                    help="一个或多个题目目录（含 spec.json、data/、std/）")
    ap.add_argument("--out", default="dist/lemon", help="输出根目录")
    ap.add_argument("--no-zip", action="store_true", help="只生成目录，不打 zip")
    ap.add_argument("--force-cdf", action="store_true",
                    help="覆盖已有 <contest>.cdf（默认保留用户已保存的比赛文件）")
    ap.add_argument("--contest-title", default=None,
                    help="写入 .cdf 的 contestTitle（默认等于 --contest）")
    ap.add_argument("--cdf-name", default=None,
                    help="自定义 .cdf 文件名（默认 <contest>.cdf）")
    args = ap.parse_args()

    problems = [load_problem(p) for p in args.problems]
    contest_dir = os.path.join(args.out, args.contest)
    contest_title = args.contest_title or args.contest
    cdf_filename = args.cdf_name or (args.contest + ".cdf")
    if not cdf_filename.lower().endswith(".cdf"):
        cdf_filename += ".cdf"
    cdf_path = os.path.join(contest_dir, cdf_filename)

    preserved_cdf = None
    if os.path.exists(cdf_path) and not args.force_cdf:
        with open(cdf_path, "rb") as f:
            preserved_cdf = f.read()
        print("[info] 保留已有 %s（--force-cdf 可覆盖）" % os.path.basename(cdf_path))
    if os.path.exists(contest_dir):
        shutil.rmtree(contest_dir)
    os.makedirs(os.path.join(contest_dir, "source", "std"))

    for p in problems:
        src_data = os.path.join(p["dir"], "data")
        dst_data = os.path.join(contest_dir, "data", p["file"])
        os.makedirs(dst_data, exist_ok=True)
        for i in range(1, p["npoints"] + 1):
            for ext in ("in", "out"):
                shutil.copyfile(os.path.join(src_data, "%d.%s" % (i, ext)),
                                os.path.join(dst_data, "%s%d.%s" % (p["file"], i, ext)))
        shutil.copyfile(os.path.join(p["dir"], "std", "std.cpp"),
                        os.path.join(contest_dir, "source", "std", p["cpp"]))

    readme = build_readme(contest_title, cdf_filename, args, problems)
    with open(os.path.join(contest_dir, "README.txt"), "w", encoding="utf-8") as f:
        f.write(readme)

    if preserved_cdf is not None:
        with open(cdf_path, "wb") as f:
            f.write(preserved_cdf)
    else:
        cdf = build_cdf(contest_title, problems)
        with open(cdf_path, "w", encoding="utf-8") as f:
            json.dump(cdf, f, ensure_ascii=False, separators=(",", ":"))
        print("[ok] Lemon 比赛文件: %s" % cdf_path)

    print("[ok] Lemon 数据目录: %s" % contest_dir)
    if not args.no_zip:
        zip_path = os.path.join(args.out, "%s-Lemon比赛数据.zip" % args.contest)
        if os.path.exists(zip_path):
            os.remove(zip_path)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(contest_dir):
                for f in files:
                    full = os.path.join(root, f)
                    rel = os.path.relpath(full, args.out).replace(os.sep, "/")
                    z.write(full, rel)
        print("[ok] Lemon zip: %s" % zip_path)


if __name__ == "__main__":
    main()
