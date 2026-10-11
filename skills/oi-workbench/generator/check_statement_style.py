#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""题面风格硬约束检查器（2026-10-11 用户口径：题面禁止出现（）与 ——，禁止答案提示）。

规则（ERROR，必须为 0）：
  1. 全角括号 `（` `）`：题面正文一律不使用括号做解释/补充（约束、澄清、附件引用都改写为分句或表格）。
     例外：Markdown 标题行 `# 题名（pid）` 属于内部标识，不在正文里出现——但仍建议整卷 PDF/题包只露出题名，
     故本检查器默认**标题行也一并检查**，如确实需要保留 pid 标注可加 `--allow-title-paren`。
  2. 破折号 `——`：不使用破折号做解释。
  3. 答案提示：任何形式的"答案必为/恒为/一定等于…""此时答案…""答案不超过/至少…""只需输出…"等
     直接揭示输出量级或结论的表述（样例解释中针对该样例的说明不算，见 `--sample-explain-ok`）。

规则（WARN，建议为 0）：
  a. 半角括号内出现 ≥2 个连续汉字（多半是中文解释性括注）；
  b. 正文出现 `--`（半角双连字符）。

用法：
  python check_statement_style.py <题目目录或 problem.md> [更多...]
  python check_statement_style.py --vol <卷目录>        # 检查该卷下所有含 problem.md 的题目
  python check_statement_style.py --vol <卷目录> --allow-title-paren
退出码：存在 ERROR 时为 1，否则 0。
"""
import argparse
import os
import re
import sys

# 答案提示类表述
HINT_PATTERNS = [
    (r'答案[^。；\n]{0,10}(必|恒|一定|就|均|全)(为|是|等于)', '直接给出答案结论'),
    (r'此时答案', '直接给出答案结论'),
    (r'答案(至少|至多|不超过|不大于|不小于|保证|一定)', '提示答案量级/范围'),
    (r'(只需|只要|直接)输出', '提示输出方式'),
    (r'输出即可', '提示输出方式'),
    (r'答案就是', '直接给出答案结论'),
]


def find_problems(paths):
    out = []
    for p in paths:
        p = os.path.abspath(p)
        if os.path.isfile(p) and p.endswith('.md'):
            out.append(p)
        elif os.path.isdir(p):
            if os.path.isfile(os.path.join(p, 'problem.md')):
                out.append(os.path.join(p, 'problem.md'))
            else:
                for d in sorted(os.listdir(p)):
                    q = os.path.join(p, d, 'problem.md')
                    if os.path.isfile(q):
                        out.append(q)
    return out


def check_file(path, allow_title_paren=False, sample_explain_ok=True):
    text = open(path, encoding='utf-8').read()
    lines = text.split('\n')
    errors, warns = [], []
    in_sample_explain = False
    for i, ln in enumerate(lines, 1):
        stripped = ln.strip()
        # 样例解释区段标记（### 样例解释 N 之后 到 下一个 ## 标题之前）
        if stripped.startswith('###') and '样例解释' in stripped:
            in_sample_explain = True
        elif stripped.startswith('## ') or stripped.startswith('# '):
            in_sample_explain = False
        is_title = stripped.startswith('# ')
        if ('（' in ln or '）' in ln) and not (allow_title_paren and is_title):
            errors.append((i, '全角括号', ln.strip()[:120]))
        if '——' in ln:
            errors.append((i, '破折号 ——', ln.strip()[:120]))
        if stripped.startswith('- ') and stripped[2:].startswith('**') and '样例输入' in stripped:
            pass
        # 答案提示（样例解释内针对该样例的说明放行，除非 --no-sample-explain-ok）
        if not (sample_explain_ok and in_sample_explain):
            for pat, why in HINT_PATTERNS:
                m = re.search(pat, ln)
                if m:
                    errors.append((i, '答案提示：' + why + ' → ' + m.group(0), ln.strip()[:120]))
                    break
        for m in re.finditer(r'\(([^()]{0,80})\)', ln):
            inner = m.group(1)
            if len(re.findall(r'[\u4e00-\u9fff]', inner)) >= 2:
                warns.append((i, '半角括号内含中文说明', ln.strip()[:120]))
                break
        if re.search(r'(?<!-)--(?!-)', ln):
            warns.append((i, '出现半角 --', ln.strip()[:120]))
    return errors, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('paths', nargs='*', help='题目目录、卷目录或 problem.md')
    ap.add_argument('--vol', default=None, help='卷目录，检查其下所有题目')
    ap.add_argument('--allow-title-paren', action='store_true', help='允许 Markdown 标题行里的 （pid） 标注')
    ap.add_argument('--no-sample-explain-ok', action='store_true', help='样例解释区段也严格检查答案提示')
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass
    paths = list(a.paths)
    if a.vol:
        paths.append(a.vol)
    files = find_problems(paths)
    if not files:
        print('没有找到任何 problem.md'); return 1
    total_err = total_warn = 0
    for f in files:
        errs, warns = check_file(f, a.allow_title_paren, not a.no_sample_explain_ok)
        total_err += len(errs)
        total_warn += len(warns)
        tag = 'OK' if not errs else 'ERROR %d' % len(errs)
        print('[%s] %s' % (tag, f))
        for i, why, ln in errs:
            print('    E L%-4d %s｜%s' % (i, why, ln))
        for i, why, ln in warns:
            print('    W L%-4d %s｜%s' % (i, why, ln))
    print('\n合计：ERROR %d 处，WARN %d 处，共检查 %d 个题面' % (total_err, total_warn, len(files)))
    print('结论：', '通过' if total_err == 0 else '不通过 ❌（题面禁止出现（）与 ——，禁止答案提示）')
    return 0 if total_err == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
