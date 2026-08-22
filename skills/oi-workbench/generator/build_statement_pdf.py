#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_statement_pdf.py —— 生成一份“官方风格”的整卷 PDF 题面。

能力来源：CSP-S 模拟卷实战经验。
组织方式参考官方 CSP 试卷：
  封面（比赛信息表 + 提交源程序文件名 + 编译选项 + 注意事项）
  + 每题分页（页眉含比赛名与题名，页脚“第 X 页 共 Y 页”）
  + 题目描述 / 输入格式 / 输出格式 / 样例（带行号）/ 样例解释 / 数据范围

用法：
  python generator/build_statement_pdf.py \
      --contest "LKCP 非专业级软件能力认证" \
      --subtitle "2026 第二轮认证" \
      --level "提高级" \
      --time "2026 年 8 月 22 日 13:00~16:00" \
      --problems drafts/csp-s-mock/climb drafts/csp-s-mock/signal \
      --out paper.pdf

说明：
  - 每题目录需含 spec.json（title/io/time/memory/cases）与 problem.md；
  - 若题面用“故事强化版”存放在单独目录，可用 --story-dir 指向含 <英文名>.md 的目录；
  - 依赖 XeLaTeX（TeX Live）+ Fandol 中文字体，Python 仅用标准库。
"""
import argparse
import json
import os
import re
import subprocess
import sys

DEFAULT_NOTES = [
    "文件名（程序名和输入输出文件名）必须使用英文小写。",
    "main 函数的返回值类型必须是 int，程序正常结束时的返回值必须是 0。",
    "若无特殊说明，结果的比较方式为全文比较（过滤行末空格及文末换行）。",
    "选手提交的程序源文件大小不得超过 100 KiB。",
    "提交的程序源文件的放置位置请参考各省的具体要求。",
    "程序可使用的栈空间内存限制与题目的内存限制一致。",
    "禁止在源代码中改变编译器参数（如使用 \\#pragma 命令），禁止使用系统结构相关指令"
    "（如内联汇编）或其他可能造成不公平的方法。",
    "因违反上述规定而出现的问题，申诉时一律不予受理。",
    "只提供 Linux 格式附加样例文件。",
    "全国统一评测时采用的机器配置为：Intel Core Ultra 9 285K CPU @ 3.70 GHz"
    "（关闭睿频与能效核），内存 96 GB。上述时限以此配置为准。",
    "评测在当前最新公布的 NOI Linux 下进行，各语言的编译器版本以此为准。",
]

# ---------- 元数据 ----------

def parse_time(ms_str):
    """'1000ms' -> '1.0 秒'；'250ms' -> '250 ms'"""
    s = str(ms_str).strip().lower()
    if s.endswith("ms"):
        ms = int(s[:-2])
    else:
        try:
            ms = int(float(s) * 1000)
        except Exception:
            return s
    if ms % 1000 == 0:
        return "%g 秒" % (ms // 1000)
    return "%d ms" % ms


def parse_memory(mem_str):
    """'512m' -> '512 MiB'；'1g' -> '1024 MiB'"""
    s = str(mem_str).strip().lower()
    try:
        if s.endswith("g"):
            return "%d MiB" % (int(s[:-1]) * 1024)
        if s.endswith("m"):
            return "%d MiB" % int(s[:-1])
        if s.endswith("mb"):
            return "%d MiB" % int(s[:-2])
        return s
    except Exception:
        return s


def load_problem(problem_dir, story_dir=None):
    spec_path = os.path.join(problem_dir, "spec.json")
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)
    io = spec.get("io") or {}
    if io.get("type") == "file" and io.get("input"):
        stem = os.path.splitext(io["input"])[0]
    else:
        stem = os.path.basename(os.path.normpath(problem_dir))
    if story_dir:
        md_path = os.path.join(story_dir, stem + ".md")
    else:
        md_path = os.path.join(problem_dir, "problem.md")
    with open(md_path, encoding="utf-8") as f:
        md = f.read()
    cases = spec.get("cases") or []
    scores = [c.get("score") for c in cases if c.get("score") is not None]
    equal = len(set(scores)) <= 1
    return {
        "file": stem,
        "name": spec.get("title", stem),
        "cpp": stem + ".cpp",
        "io": io,
        "time": parse_time(spec.get("time", "1000ms")),
        "memory": parse_memory(spec.get("memory", "512m")),
        "points": str(len(cases)),
        "equal": "是" if equal else "否",
        "md": md,
    }


# ---------- Markdown -> LaTeX ----------

def esc_specials(s):
    out = []
    for c in s:
        if c in "&%#_":
            out.append("\\" + c)
        else:
            out.append(c)
    return "".join(out)


def convert_inline(s):
    tokens = []
    i, n = 0, len(s)
    buf = []
    while i < n:
        if s.startswith("$$", i):
            j = s.find("$$", i + 2)
            if j == -1:
                buf.append(s[i:])
                break
            tokens.append(("txt", "".join(buf)))
            buf = []
            tokens.append(("disp", s[i + 2:j]))
            i = j + 2
        elif s[i] == "$":
            j = s.find("$", i + 1)
            if j == -1:
                buf.append(s[i:])
                break
            tokens.append(("txt", "".join(buf)))
            buf = []
            tokens.append(("math", s[i + 1:j]))
            i = j + 1
        else:
            buf.append(s[i])
            i += 1
    tokens.append(("txt", "".join(buf)))
    res = []
    for kind, val in tokens:
        if kind == "disp":
            res.append("\\[\n%s\n\\]" % val.strip())
        elif kind == "math":
            res.append("$" + val + "$")
        else:
            val = re.sub(r"`([^`]+)`", r"\\texttt{\1}", val)
            val = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", val)
            res.append(esc_specials(val))
    return "".join(res)


def heading_latex(h):
    h = h.strip()
    if h.startswith("样例输入"):
        return "【样例 %s 输入】" % h[len("样例输入"):].strip()
    if h.startswith("样例输出"):
        return "【样例 %s 输出】" % h[len("样例输出"):].strip()
    if h.startswith("样例解释"):
        return "【样例 %s 解释】" % h[len("样例解释"):].strip()
    return "【%s】" % h


def table_to_latex(rows):
    ncols = len(rows[0])
    colspec = "|" + "c|" * ncols
    lines = ["\\begin{center}", "\\begin{tabular}{%s}" % colspec, "\\hline"]
    for row in rows:
        if all(re.fullmatch(r":?-+:?", c.strip()) for c in row):
            continue
        cells = [convert_inline(c.strip()) for c in row]
        lines.append(" & ".join(cells) + " \\\\")
        lines.append("\\hline")
    lines.append("\\end{tabular}")
    lines.append("\\end{center}")
    return "\n".join(lines)


def md_to_latex(text):
    out = []
    lines = text.splitlines()
    i, n = 0, len(lines)
    para = []
    table = []
    in_code = False
    code_lines = []

    def flush_para():
        if para:
            out.append(convert_inline(" ".join(para).strip()))
            para.clear()

    while i < n:
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            flush_para()
            if table:
                out.append(table_to_latex(table))
                table = []
            if not in_code:
                in_code = True
                code_lines = []
            else:
                in_code = False
                out.append(
                    "\\begin{Verbatim}[numbers=left,numbersep=8pt,frame=single,fontsize=\\small]\n"
                    + "\n".join(code_lines)
                    + "\n\\end{Verbatim}"
                )
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue
        if stripped.startswith("###"):
            flush_para()
            out.append("\\par\\medskip\\noindent\\textbf{%s}\\par" % convert_inline(stripped[3:].strip()))
            i += 1
            continue
        if stripped.startswith("##"):
            flush_para()
            out.append("\\par\\bigskip\\noindent{\\large\\bfseries %s}\\par" % heading_latex(stripped[2:].strip()))
            i += 1
            continue
        if stripped.startswith("# "):
            flush_para()
            i += 1
            continue
        if stripped.startswith("|"):
            flush_para()
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            table.append(cells)
            i += 1
            continue
        if table:
            out.append(table_to_latex(table))
            table = []
        if stripped.startswith("- "):
            flush_para()
            items = []
            while i < n and lines[i].strip().startswith("- "):
                items.append(convert_inline(lines[i].strip()[2:].strip()))
                i += 1
            out.append("\\begin{itemize}")
            for it in items:
                out.append("\\item %s" % it)
            out.append("\\end{itemize}")
            continue
        if stripped == "":
            flush_para()
            i += 1
            continue
        para.append(line.strip())
        i += 1
    flush_para()
    if table:
        out.append(table_to_latex(table))
    return "\n\n".join(out)


# ---------- 封面 / 题目页 ----------

def row(label, values):
    return "%s & %s \\\\" % (label, " & ".join(str(v) for v in values))


def cover_latex(args, problems):
    n = len(problems)
    colspec = "|p{4.6cm}|" + "c|" * n
    head = [
        "\\begin{center}",
        "{\\LARGE %s}\\\\[2pt]" % args.contest,
        "{\\LARGE %s}\\\\[2pt]" % args.subtitle,
        "{\\Huge\\bfseries %s}\\\\[6pt]" % args.level,
        "时间：%s" % args.time,
        "\\end{center}",
        "\\vspace{0.5em}",
        "\\small",
        "\\begin{center}",
        "\\renewcommand{\\arraystretch}{1.3}",
        "\\begin{tabular}{%s}" % colspec,
        "\\hline",
        row("题目名称", [p["name"] for p in problems]),
        "\\hline",
        row("题目类型", ["传统型"] * n),
        "\\hline",
        row("目录", [p["file"] for p in problems]),
        "\\hline",
        row("可执行文件名", [p["file"] for p in problems]),
        "\\hline",
        row("输入文件名", [p["file"] + ".in" for p in problems]),
        "\\hline",
        row("输出文件名", [p["file"] + ".out" for p in problems]),
        "\\hline",
        row("每个测试点时限", [p["time"] for p in problems]),
        "\\hline",
        row("内存限制", [p["memory"] for p in problems]),
        "\\hline",
        row("测试点数目", [p["points"] for p in problems]),
        "\\hline",
        row("测试点是否等分", [p["equal"] for p in problems]),
        "\\hline",
        "\\end{tabular}",
        "\\end{center}",
        "\\vspace{0.5em}",
        "\\noindent\\textbf{提交源程序文件名}",
        "\\begin{center}",
        "\\renewcommand{\\arraystretch}{1.3}",
        "\\begin{tabular}{%s}" % colspec,
        "\\hline",
        row("对于 C++ 语言", [p["cpp"] for p in problems]),
        "\\hline",
        "\\end{tabular}",
        "\\end{center}",
        "\\vspace{0.4em}",
        "\\noindent\\textbf{编译选项}",
        "\\par\\noindent 对于 C++ 语言：\\texttt{-O2 -std=c++14 -static}",
        "\\par\\medskip\\noindent\\textbf{注意事项（请仔细阅读）}",
        "\\begin{enumerate}\\setlength{\\itemsep}{1pt}",
    ]
    for note in args.notes:
        head.append("\\item %s" % note)
    head.append("\\end{enumerate}")
    head.append("\\normalsize")
    return "\n".join(head)


def problem_latex(p):
    body = md_to_latex(p["md"])
    return "\\problemheader{%s（%s）}\n\n\\begin{center}{\\Large\\bfseries %s（%s）}\\end{center}\n\n%s" % (
        p["name"], p["file"], p["name"], p["file"], body)


# ---------- 文档 ----------

PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[a4paper,top=2.2cm,bottom=2.2cm,left=2.2cm,right=2.2cm]{geometry}
\usepackage{xeCJK}
\usepackage{amsmath,amssymb}
\usepackage{fancyvrb}
\usepackage{fancyhdr}
\usepackage{lastpage}
\usepackage[hidelinks]{hyperref}

\setCJKmainfont{FandolSong-Regular.otf}[BoldFont=FandolSong-Bold.otf]
\setCJKsansfont{FandolHei-Regular.otf}
\setCJKmonofont{FandolSong-Regular.otf}
\setlength{\parindent}{2em}
\linespread{1.25}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small @CL@ \quad @CS@}
\fancyhead[R]{\small @LV@}
\fancyfoot[C]{\small 第 \thepage\ 页 \quad 共 \pageref{LastPage}\ 页}
\renewcommand{\headrulewidth}{0pt}

\newcommand{\problemheader}[1]{%
  \fancyhead[R]{\small @LV@ \quad #1}}

\begin{document}
\thispagestyle{empty}
"""


def main():
    ap = argparse.ArgumentParser(description="生成官方风格整卷 PDF 题面")
    ap.add_argument("--contest", default="LKCP 非专业级软件能力认证")
    ap.add_argument("--subtitle", default="2026 第二轮认证")
    ap.add_argument("--level", default="提高级")
    ap.add_argument("--time", default="2026 年 8 月 22 日 13:00~16:00")
    ap.add_argument("--problems", nargs="+", required=True,
                    help="一个或多个题目目录（含 spec.json 与 problem.md）")
    ap.add_argument("--story-dir", default=None,
                    help="故事强化版题面目录：按 <英文文件名>.md 读取（缺省用各题 problem.md）")
    ap.add_argument("--out", default="paper.pdf")
    ap.add_argument("--workdir", default=None, help="XeLaTeX 工作目录（默认用脚本所在目录）")
    args = ap.parse_args()

    problems = [load_problem(p, args.story_dir) for p in args.problems]
    args.notes = DEFAULT_NOTES
    args.time = args.time.replace("~", "$\\sim$")

    header = (
        PREAMBLE
        .replace("@CL@", args.contest)
        .replace("@CS@", args.subtitle)
        .replace("@LV@", args.level)
    )
    doc = [header, cover_latex(args, problems), "\\clearpage"]
    for p in problems:
        doc.append(problem_latex(p))
        doc.append("\\clearpage")
    doc.append("\\end{document}")

    workdir = os.path.abspath(args.workdir or os.path.dirname(os.path.abspath(args.out)))
    os.makedirs(workdir, exist_ok=True)
    tex_path = os.path.join(workdir, "exam.tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(doc))

    # 两次编译以得到正确的“共 Y 页”
    for _ in range(2):
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", tex_path],
                           cwd=workdir)
        if r.returncode != 0:
            sys.exit("XeLaTeX 编译失败，请检查 %s.log" % (tex_path + ".log"))

    pdf_path = os.path.join(workdir, "exam.pdf")
    if not os.path.exists(pdf_path):
        sys.exit("未生成 exam.pdf，请检查 XeLaTeX 日志")
    out_path = os.path.abspath(args.out)
    if pdf_path != out_path:
        os.replace(pdf_path, out_path)
    print("[ok] PDF: %s" % out_path)


if __name__ == "__main__":
    main()
