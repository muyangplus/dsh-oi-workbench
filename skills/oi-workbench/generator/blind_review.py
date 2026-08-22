#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
blind_review.py —— 盲审工具（文本表达审读）。

在两处闸口运行：
1. 代码发布前（发布测试版 / 正式版前）：
       python generator/blind_review.py --release [<仓库根>]
2. 生成题目文件后：
       python generator/blind_review.py --problem <题目目录>

检查“脱离上下文显得奇怪 / 不合体”的文本表述：
- 未解释的内部语境泄漏：`（批次 N）`、`批次 N：`、`版本约定 / 版本号承诺`、
  `按 version-records/ROADMAP.md 分批填充`、changelog / ROADMAP / v0.x 版本号等；
- 硬件规格泄漏：CPU 型号 / 主频（GHz/MHz）/ 内存大小 / 睿频 / 能效核 / 评测机基准等；
- 无上下文时间/事件注解：如 “（OI 2025 后固定）”“（2025 定稿规范）”这类括号注解；
- 时间/变化措辞：“不再”等隐含“曾经/后续”的表述，用户面向文本中应避免；
- 括号内部表述：括号内出现“不再 / 批次 / 版本 / v0.x / 档约束 / n= / 随机 / std /
  生成器 / 对拍 / 击杀矩阵 / 打包 / 本地评测”等内部或数据构造语境时提示；
- 解释性括号（problem 模式）：题面/题解正文中括号内包含中文解释性文字的段落应改写
  （如“（可选）”“（即……）”“（包括起点和终点）”）；数学范围括号如 `（$1\\le n\\le 10^5$）`
  不含中文，允许保留；
- 占位符 / 半成品残留：TODO / TBD / FIXME / XXX / 待补充 / 待完善 / 占位 / lorem 等；
- 编码问题：非法 UTF-8、替换符 U+FFFD、NUL 字节；
- 行尾空白、异常重复标点、以“，：、；”收尾的未完句。

`--fix` 仅做安全自动修复：去行尾空白、去文件头 BOM；其余一律只报不修。

退出码：发现任何问题返回 1，否则返回 0。
"""

import argparse
import os
import re
import sys

# Windows 控制台默认 GBK 会乱码中文输出，统一 UTF-8
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------------------------------------------------------------------------
# 模式与作用域
# ---------------------------------------------------------------------------

# 未解释的“批次 N”注解（如 “（批次 1）”“批次 2：”）
BATCH_ANNOT = re.compile(r"[（(]\s*批次\s*\d+\s*[）)]")
BATCH_HEAD = re.compile(r"批次\s*\d+\s*[：:]")

# 版本约定类内部语境（用户面向文本中出现显得奇怪）
VERSION_CONV = re.compile(r"版本约定|版本号承诺|分批填充|按\s*`?\s*version-records/ROADMAP")

# 硬件规格泄漏（用户面向文本不应出现具体机器配置/型号）
HARDWARE = re.compile(
    r"Intel|AMD|Apple\s+(?:M|A)\d|Core Ultra|Core\s*i[3-9]|Ryzen|GHz|MHz|睿频|"
    r"能效核|性能核|Turbo|E[- ]?cores?|P[- ]?cores?|评测机基准|评测机配置|"
    r"CPU\s*@|内存\s*\d+\s*(?:GB|MB)|\d+\s*GB\s*内存"
)

# 无上下文的时间/事件注解（如 “（OI 2025 后固定）”“（2025 定稿规范）”）
CONTEXT_PAREN = re.compile(r"[（(][^）)]{0,24}(?:后固定|后生效|起固定|后起|定稿规范|后定稿)[）)]")

# 时间/变化措辞：“不再”隐含“曾经/后续”语境
NO_MORE = re.compile(r"不再")

# 括号内部表述：括号内出现内部/数据构造/版本/变化措辞时提示
PAREN_INTERNAL = re.compile(
    r"[（(][^）)]{0,90}(?:不再|后固定|后生效|后起|定稿|批次\s*\d|版本|"
    r"v\d+(?:\.\d+)?|档约束|n\s*=|随机|std|生成器|对拍|击杀矩阵|打包|本地评测)[^）)]{0,90}[）)]"
)

# 解释性括号：仅全角括号内含中文说明文字（半角括号多为数学/代码/英文，放行）
EXPLAIN_PAREN = re.compile(r"[（][^（）]*[\u4e00-\u9fff][^（）]*[）]")

# 占位符 / 半成品残留
PLACEHOLDER = re.compile(r"\bTODO\b|\bTBD\b|\bFIXME\b|\bXXX\b|\blorem\b|待补充|待完善|待续|此处示例|示例内容")

# 内部开发术语（仅题目文件模式检查：题面/题解不应出现）
INTERNAL_LEAK = re.compile(
    r"spec\.json|生成器|对拍|击杀矩阵|本地评测|打包|changelog|ROADMAP|"
    r"version-records|templates/|SKILL\.md|verification\.md|verify_package|"
    r"build_hoj|build_package|local_judge"
)

# 异常重复标点
WEIRD_PUNCT = re.compile(r"[？?]{2,}|[！!]{2,}|[。]{2,}|[，,][。]|[。][，,]|[，,]{2,}")

# 行尾空白
TRAILING_WS = re.compile(r"[ \t]+$")

# 以未完句标点收尾
UNFINISHED_END = re.compile(r"[，：、；]$")

TEXT_EXT = {".md", ".txt"}
ROADMAP_BULLET = re.compile(r"^\s*-\s*\[[ xX]\]")

SCOPE_DOC = "doc"        # 用户面向文档
SCOPE_PROBLEM = "problem"  # 题面/题解/题目 spec
SCOPE_RECORD = "record"  # version-records（批次/版本号属合法语境）


def has_encoding_issue(text):
    return "\ufffd" in text or "\x00" in text


def classify(path, mode):
    """根据文件路径判定审读作用域。"""
    norm = path.replace("\\", "/")
    base = os.path.basename(norm).lower()
    if "/version-records/" in norm:
        return SCOPE_RECORD
    if base == "spec.json" or base == "problem.md" or "/solution/" in norm:
        return SCOPE_PROBLEM
    return SCOPE_DOC


def should_skip(path, mode="generic"):
    norm = path.replace("\\", "/")
    # 代码/数据/样例目录一律跳过
    skip_dirs = (".git/", "node_modules/", "/public/",
                 "/data/", "/sample/", "/__pycache__/")
    # 仅发布前整仓扫描时跳过 scratch 目录；显式 --problem 目标不受此限制
    if mode == "release":
        skip_dirs += ("/.tmp/", "/_tmp_")
    if any(d in norm for d in skip_dirs):
        return True
    if norm.endswith("/VERIFICATION.md"):
        # 验证记录属内部文档：只做 doc 级检查，不按题面严格审
        return False
    ext = os.path.splitext(norm)[1].lower()
    # 只审文本：markdown / txt / 题目的 spec.json；代码与二进制一律跳过
    if ext in (".py", ".js", ".yml", ".yaml", ".html", ".ps1", ".sh",
               ".tgz", ".zip", ".pyc", ".exe", ".cpp", ".h"):
        return True
    if ext == ".json":
        return not norm.endswith("spec.json")
    return ext not in TEXT_EXT


def line_checks(line, lineno, scope, is_roadmap_bullet):
    issues = []
    if TRAILING_WS.search(line):
        issues.append(("行尾空白", "…"))
    if scope != SCOPE_RECORD:
        if BATCH_ANNOT.search(line):
            issues.append(("无上下文批次注解", BATCH_ANNOT.search(line).group(0)))
        if BATCH_HEAD.search(line):
            issues.append(("无上下文批次标注", BATCH_HEAD.search(line).group(0)))
        if VERSION_CONV.search(line):
            issues.append(("版本约定泄漏", VERSION_CONV.search(line).group(0)))
        m = HARDWARE.search(line)
        if m:
            issues.append(("硬件规格泄漏", m.group(0)))
        m = CONTEXT_PAREN.search(line)
        if m:
            issues.append(("无上下文时间注解", m.group(0)))
        m = NO_MORE.search(line)
        if m:
            issues.append(("时间/变化措辞", m.group(0)))
    if scope == SCOPE_PROBLEM:
        m = EXPLAIN_PAREN.search(line)
        if m:
            issues.append(("解释性括号", m.group(0)))
        m = PAREN_INTERNAL.search(line)
        if m:
            issues.append(("括号内部表述", m.group(0)))
        if INTERNAL_LEAK.search(line):
            issues.append(("内部术语泄漏", INTERNAL_LEAK.search(line).group(0)))
    # 路线图（标题/条目）里的 TODO 属合法语境；其余视为残留
    is_todo_heading = line.lstrip().startswith("#") and "TODO" in line
    roadmap_context = scope != SCOPE_PROBLEM and (
        is_roadmap_bullet or is_todo_heading or ("路线图" in line and "TODO" in line))
    if not (roadmap_context and re.search(r"\bTODO\b", line)):
        m = PLACEHOLDER.search(line)
        if m:
            issues.append(("占位/残留", m.group(0)))
    m = WEIRD_PUNCT.search(line)
    if m:
        issues.append(("异常重复标点", m.group(0)))
    return issues


def scan_text(path, scope, do_fix):
    """读取文件做逐行检查；返回 (issues, fixed_lines)。"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError as e:
        return [("编码", f"{path}: 非法 UTF-8（{e}）")], None
    except OSError as e:
        return [("读失败", f"{path}: {e}")], None

    issues = []
    if has_encoding_issue(text):
        issues.append(("编码", f"{path}: 含替换符 U+FFFD 或 NUL 字节"))
    if text.startswith("\ufeff"):
        issues.append(("BOM", f"{path}: 文件头含 BOM"))

    lines = text.splitlines()
    fixed_lines = []
    changed = False
    for idx, raw in enumerate(lines, 1):
        line = raw.rstrip("\r")
        is_roadmap = bool(ROADMAP_BULLET.match(line))
        for kind, frag in line_checks(line, idx, scope, is_roadmap):
            issues.append((kind, f"{path}:{idx}: {frag}  ->  {line.strip()}"))
        new = TRAILING_WS.sub("", line)
        if new != line:
            changed = True
        fixed_lines.append(new)

    if do_fix and (changed or text.startswith("\ufeff")):
        content = "\n".join(fixed_lines)
        if content:
            content += "\n"
        content = content.lstrip("\ufeff")
        try:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
        except OSError as e:
            issues.append(("写失败", f"{path}: {e}"))
        else:
            issues.append(("已修复", f"{path}: 去除行尾空白/BOM"))
    return issues, None


def scan_paths(paths, mode, do_fix):
    all_issues = []
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in (".git", "node_modules")]
                for name in sorted(files):
                    full = os.path.join(root, name)
                    if should_skip(full, mode):
                        continue
                    scope = classify(full, mode)
                    issues, _ = scan_text(full, scope, do_fix)
                    all_issues.extend(issues)
        else:
            if not os.path.isfile(p):
                all_issues.append(("路径错误", f"{p}: 不存在"))
                continue
            if should_skip(p, mode):
                continue
            scope = classify(p, mode)
            all_issues.extend(scan_text(p, scope, do_fix)[0])
    return all_issues


def default_repo_scan(root):
    """发布前扫描仓库用户面向文本。"""
    skip_dirs = (".git", "node_modules", ".tmp", "_tmp_", "public")
    paths = []
    for entry in sorted(os.listdir(root)):
        full = os.path.join(root, entry)
        if entry in skip_dirs:
            continue
        paths.append(full)
    return paths


def main():
    ap = argparse.ArgumentParser(description="盲审工具：发布前 / 生成题目后审读文本表达")
    ap.add_argument("paths", nargs="*", help="要审读的文件或目录（通用模式）")
    ap.add_argument("--release", nargs="?", const=True, default=None,
                    help="代码发布前扫描插件仓库用户面向文本（可带仓库根路径）")
    ap.add_argument("--problem", metavar="DIR", help="生成题目文件后审读该题目目录")
    ap.add_argument("--fix", action="store_true", help="安全自动修复：去行尾空白与 BOM")
    args = ap.parse_args()

    if args.release is not None:
        default_root = os.path.abspath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
        root = default_root if args.release is True or not args.release else args.release
        paths = default_repo_scan(root)
        mode = "release"
        label = f"发布前盲审（仓库：{root}）"
    elif args.problem:
        paths = [args.problem]
        mode = "problem"
        label = f"题目盲审（目录：{args.problem}）"
    elif args.paths:
        paths = args.paths
        mode = "generic"
        label = "盲审"
    else:
        ap.error("需要 --release / --problem / 或至少一个路径")

    print(f"== {label} ==")
    issues = scan_paths(paths, mode, args.fix)

    by_kind = {}
    for kind, msg in issues:
        by_kind.setdefault(kind, []).append(msg)

    for kind, msgs in sorted(by_kind.items()):
        if kind in ("已修复", "读失败", "写失败", "路径错误"):
            for m in msgs:
                print(f"[{kind}] {m}")
            continue
        for m in msgs:
            print(f"[{kind}] {m}")

    warn_kinds = {"BOM"}  # 非阻断：仅提示
    bad = [m for k, ms in by_kind.items()
           if k not in ("已修复", "BOM") for m in ms]
    print(f"---- {label} 结束：问题 {len(bad)} 项，提示 {sum(len(v) for k, v in by_kind.items() if k in warn_kinds)} 项，"
          f"自动修复 {len(by_kind.get('已修复', []))} 项 ----")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
