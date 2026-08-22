#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
package_samples.py —— 为每道题打包“完整测试样例”zip（平铺格式）。

能力来源：CSP-S 模拟卷实战约定。
规则：
  - zip 内平铺 1.in/1.out、2.in/2.out、3.in/3.out（无大/小样例子目录、无 readme）；
  - 样例 1、2 取题目目录 sample/1.*、sample/2.*；
  - 样例 3（大样例）默认取 data/6.*，满足测试点 6~8 约束（可用 --big-point/--big-range 调整）；
  - 每题 zip 放入 <题目目录>/additional_file/<英文题名>_samples.zip；
  - 同时更新 OJ 题面：把【样例解释 1】移到【样例输出 1】之后，并把样例 3 段改为
    “（见题目附件 [xxx_samples.zip](file://xxx_samples.zip)，其中样例 3 满足测试点 X, Y, Z 的约束。）”；
  - 可另给 --story-dir，按同样规则更新故事强化版题面（PDF 用）。

用法：
  python generator/package_samples.py \
      --problems drafts/csp-s-mock/climb drafts/csp-s-mock/signal \
      --story-dir drafts/csp-s-mock-pdf/story \
      --combined dist/CSP-S-模拟-完整样例.zip
"""
import argparse
import json
import os
import zipfile

OJ_REF = [
    "## 样例 3\n",
    "\n",
    "（见题目附件 [{f}_samples.zip](file://{f}_samples.zip)，其中样例 3 满足测试点 {r} 的约束。）\n",
    "\n",
]
STORY_REF = [
    "## 样例 3\n",
    "\n",
    "见选手目录下的 {f}/{f}3.in 与 {f}/{f}3.ans。\n",
    "该样例满足测试点 {r} 的约束条件。\n",
    "\n",
]


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


def replace_sample3(sections, ref_lines):
    idx = next((i for i, (h, _) in enumerate(sections)
                if h.startswith("## 样例") and "3" in h and "解释" not in h), None)
    if idx is not None:
        sections.pop(idx)
    insert_at = len(sections)
    for i, (h, _) in enumerate(sections):
        if h.startswith("## 数据范围"):
            insert_at = i
            break
    sections.insert(insert_at, [ref_lines[0], ref_lines[1:]])
    return sections


def update_md(path, ref_lines):
    if not os.path.exists(path):
        return False
    text = open(path, encoding="utf-8").read()
    secs = split_sections(text)
    secs = reorder_explain(secs)
    secs = replace_sample3(secs, ref_lines)
    new_text = join_sections(secs)
    if new_text != text:
        open(path, "w", encoding="utf-8").write(new_text)
        return True
    return False


def build_per_problem(problem_dir, stem, big_point):
    add_dir = os.path.join(problem_dir, "additional_file")
    os.makedirs(add_dir, exist_ok=True)
    zip_path = os.path.join(add_dir, "%s_samples.zip" % stem)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(problem_dir, "sample", "1.in"), "1.in")
        z.write(os.path.join(problem_dir, "sample", "1.out"), "1.out")
        z.write(os.path.join(problem_dir, "sample", "2.in"), "2.in")
        z.write(os.path.join(problem_dir, "sample", "2.out"), "2.out")
        z.write(os.path.join(problem_dir, "data", "%d.in" % big_point), "3.in")
        z.write(os.path.join(problem_dir, "data", "%d.out" % big_point), "3.out")
    print("  [ok] %s" % zip_path)
    return zip_path


def build_combined(problems, big_point, out_zip):
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for problem_dir, stem in problems:
            for f in ("1.in", "1.out", "2.in", "2.out"):
                z.write(os.path.join(problem_dir, "sample", f), "%s/%s" % (stem, f))
            z.write(os.path.join(problem_dir, "data", "%d.in" % big_point), "%s/3.in" % stem)
            z.write(os.path.join(problem_dir, "data", "%d.out" % big_point), "%s/3.out" % stem)
    print("  [ok] %s" % out_zip)


def main():
    ap = argparse.ArgumentParser(description="打包完整测试样例 zip（平铺 1/2/3）")
    ap.add_argument("--problems", nargs="+", required=True,
                    help="一个或多个题目目录（含 spec.json、sample/、data/）")
    ap.add_argument("--big-point", type=int, default=6, help="大样例对应的隐藏数据点编号（默认 6）")
    ap.add_argument("--big-range", default="6, 7, 8", help="大样例满足的测试点区间（默认 6, 7, 8）")
    ap.add_argument("--story-dir", default=None, help="故事强化版题面目录（可选，同步 PDF 题面）")
    ap.add_argument("--combined", default=None, help="汇总 zip 路径（可选）")
    args = ap.parse_args()

    problems = [(p, load_stem(p)) for p in args.problems]
    print("== 打包每题完整样例 zip（平铺 1/2/3） ==")
    for problem_dir, stem in problems:
        build_per_problem(problem_dir, stem, args.big_point)

    print("== 更新题面（样例解释顺序 + 样例 3 引用） ==")
    for problem_dir, stem in problems:
        o = update_md(os.path.join(problem_dir, "problem.md"),
                      [ln.format(f=stem, r=args.big_range) for ln in OJ_REF])
        s = False
        if args.story_dir:
            s = update_md(os.path.join(args.story_dir, stem + ".md"),
                          [ln.format(f=stem, r=args.big_range) for ln in STORY_REF])
        print("  [md] %s  OJ:%s  story:%s" % (stem, "改" if o else "-", "改" if s else "-"))

    if args.combined:
        print("== 打包汇总完整样例 zip ==")
        build_combined(problems, args.big_point, args.combined)
    print("done")


if __name__ == "__main__":
    main()
