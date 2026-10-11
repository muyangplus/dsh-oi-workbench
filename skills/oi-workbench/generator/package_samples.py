#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
package_samples.py —— 为每道题打包“完整测试样例”zip（平铺格式）。

规则：
  - zip 内平铺 1.in/1.out、2.in/2.out、3.in/3.out、4.in/4.out ...；
  - 样例 1、2 取题目目录 sample/1.*、sample/2.*；
  - 样例 3 及之后为大样例，默认取 data/6，可指定多个大样例；
  - 题面“样例 N”引用使用通用 PDF 风格：
      见选手目录下的 <题目>/<题目>2.in 与 <题目>/<题目>2.ans。
      该样例满足测试点 <区间> 的约束条件。
  - 若 sample/2 缺失（如交互题），会跳过该文件并给出警告，不中断打包。
"""
import argparse
import json
import os
import zipfile


def load_stem(problem_dir):
    with open(os.path.join(problem_dir, "spec.json"), encoding="utf-8") as f:
        spec = json.load(f)
    io = spec.get("io") or {}
    if io.get("type") == "file" and io.get("input"):
        return os.path.splitext(io["input"])[0]
    return os.path.basename(os.path.normpath(problem_dir))


def split_sections(text):
    lines = text.splitlines(keepends=True)
    sections = []
    cur = None
    for ln in lines:
        if ln.startswith("## ") and not ln.startswith("### "):
            if cur is not None:
                sections.append(cur)
            cur = [ln, []]
        else:
            if cur is None:
                cur = ["", []]
            cur[1].append(ln)
    if cur is not None:
        sections.append(cur)
    return sections


def join_sections(sections):
    out = []
    for head, body in sections:
        if head:
            out.append(head)
        out.extend(body)
    return "".join(out)


def reorder_explain(sections):
    idx_explain = next((i for i, (h, _) in enumerate(sections)
                        if h.startswith("## 样例解释")), None)
    idx_out1 = next((i for i, (h, _) in enumerate(sections)
                     if h.startswith("## 样例输出 1")), None)
    if idx_explain is None or idx_out1 is None or idx_explain == idx_out1 + 1:
        return sections
    sec = sections.pop(idx_explain)
    if idx_explain < idx_out1:
        idx_out1 -= 1
    sections.insert(idx_out1 + 1, sec)
    return sections


def remove_old_sample3(sections):
    keep = []
    for sec in sections:
        h = sec[0]
        if h.startswith("## 样例") and "解释" not in h:
            num_str = h[len("## 样例"):].strip().split()[0] if h[len("## 样例"):].strip() else ""
            if num_str.isdigit() and int(num_str) >= 3:
                continue
        keep.append(sec)
    return keep


def replace_sample3(sections, ref_lines_list):
    sections = remove_old_sample3(sections)
    insert_at = len(sections)
    for i, (h, _) in enumerate(sections):
        if h.startswith("## 数据范围"):
            insert_at = i
            break
    new_secs = []
    for ref_lines in ref_lines_list:
        new_secs.append([ref_lines[0], ref_lines[1:]])
    sections[insert_at:insert_at] = new_secs
    return sections


def update_md(path, ref_lines_list):
    if not os.path.exists(path):
        return False
    text = open(path, encoding="utf-8").read()
    secs = split_sections(text)
    secs = reorder_explain(secs)
    secs = replace_sample3(secs, ref_lines_list)
    new_text = join_sections(secs)
    if new_text != text:
        open(path, "w", encoding="utf-8").write(new_text)
        return True
    return False


def build_per_problem(problem_dir, stem, big_points):
    add_dir = os.path.join(problem_dir, "additional_file")
    os.makedirs(add_dir, exist_ok=True)
    zip_path = os.path.join(add_dir, "%s_samples.zip" % stem)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in ("1.in", "1.out", "2.in", "2.out"):
            src = os.path.join(problem_dir, "sample", f)
            if os.path.exists(src):
                z.write(src, f)
            else:
                print("  [warn] missing sample file: %s" % src)
        for idx, bp in enumerate(big_points, start=3):
            z.write(os.path.join(problem_dir, "data", "%d.in" % bp), "%d.in" % idx)
            z.write(os.path.join(problem_dir, "data", "%d.out" % bp), "%d.out" % idx)
    print("  [ok] %s" % zip_path)
    return zip_path


def build_combined(problems, big_points, out_zip):
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for problem_dir, stem in problems:
            for f in ("1.in", "1.out", "2.in", "2.out"):
                src = os.path.join(problem_dir, "sample", f)
                if os.path.exists(src):
                    z.write(src, "%s/%s" % (stem, f))
            for idx, bp in enumerate(big_points, start=3):
                z.write(os.path.join(problem_dir, "data", "%d.in" % bp), "%s/%d.in" % (stem, idx))
                z.write(os.path.join(problem_dir, "data", "%d.out" % bp), "%s/%d.out" % (stem, idx))
    print("  [ok] %s" % out_zip)


def main():
    ap = argparse.ArgumentParser(description="打包完整测试样例 zip（平铺 1/2/3/...）")
    ap.add_argument("--problems", nargs="+", required=True,
                    help="一个或多个题目目录（含 spec.json、sample/、data/）")
    ap.add_argument("--big-points", nargs="+", type=int, default=None,
                    help="大样例对应的隐藏数据点编号列表，例如 --big-points 6 12 18")
    ap.add_argument("--big-ranges", nargs="+", default=None,
                    help="每个大样例满足的测试点区间，例如 --big-ranges \"6, 7, 8\" \"12, 13, 14\"")
    ap.add_argument("--big-point", type=int, default=6, help="兼容旧参数：单大样例数据点编号")
    ap.add_argument("--big-range", default="6, 7, 8", help="兼容旧参数：单大样例测试点区间")
    ap.add_argument("--story-dir", default=None, help="故事强化版题面目录（可选）")
    ap.add_argument("--combined", default=None, help="汇总 zip 路径（可选）")
    args = ap.parse_args()

    big_points = args.big_points or [args.big_point]
    big_ranges = args.big_ranges or [args.big_range]
    if len(big_points) != len(big_ranges):
        raise SystemExit("--big-points 与 --big-ranges 数量必须一致")

    problems = [(p, load_stem(p)) for p in args.problems]
    print("== 打包每题完整样例 zip（平铺 1/2/3/...） ==")
    for problem_dir, stem in problems:
        build_per_problem(problem_dir, stem, big_points)

    print("== 更新题面（样例解释顺序 + 样例 N 引用） ==")
    for problem_dir, stem in problems:
        ref_lines_list = []
        for i, (bp, rng) in enumerate(zip(big_points, big_ranges), start=3):
            file_no = i - 1  # 样例 3 -> 文件 2, 样例 4 -> 文件 3
            ref_lines_list.append([
                "## 样例 %d\n" % i,
                "\n",
                "见选手目录下的 %s/%s%d.in 与 %s/%s%d.ans。\n" % (stem, stem, file_no, stem, stem, file_no),
                "该样例满足测试点 %s 的约束条件。\n" % rng,
                "\n",
            ])
        o = update_md(os.path.join(problem_dir, "problem.md"), ref_lines_list)
        s = False
        if args.story_dir:
            s = update_md(os.path.join(args.story_dir, stem + ".md"), ref_lines_list)
        print("  [md] %s  OJ:%s  story:%s" % (stem, "改" if o else "-", "改" if s else "-"))

    if args.combined:
        print("== 打包汇总完整样例 zip ==")
        build_combined(problems, big_points, args.combined)
    print("done")


if __name__ == "__main__":
    main()
