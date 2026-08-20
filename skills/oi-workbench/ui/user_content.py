#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
user_content.py —— 用户自定义知识库 / 参考题 增删改查（仅 Python 标准库）。

批次 1（v0.1.1）产物：让用户可以在 `~/.dsh-oi-workbench/` 下维护自己的
知识库速查卡片（kb/）与原创参考题（reference/），由技能在「锁定知识点」
等环节与内置内容合并使用（同名 topic 以用户卡为准，level 允许自定义新增）。

存储布局（默认根 `~/.dsh-oi-workbench`，可用 `--home` 覆盖以便测试）:
    <root>/kb/<level-dir>/<topic>.md            # 知识库速查卡片（frontmatter 见 templates/kb-card.md）
    <root>/reference/<level-dir>/<id>/...       # 用户参考题（problem.md/spec.json/data/sample/std/brute/generator）

层级目录名约定（与内置 knowledge-base/ 对齐）:
    入门级 -> level-1-basic / 提高级 -> level-2-intermediate / 专家级 -> level-3-expert
    自定义层级 -> ASCII slug（不可用字符替换为 '-', 空则回退 custom）

用法:
    python ui/user_content.py [--home DIR] kb list [--with-builtin]
    python ui/user_content.py [--home DIR] kb show <topic>
    python ui/user_content.py [--home DIR] kb search <keyword>
    python ui/user_content.py [--home DIR] kb add --topic T --level L [--tags a,b] [--summary S] [--pitfalls S] [--body S] [--difficulty N]
    python ui/user_content.py [--home DIR] kb add-file <md-file> [--level L] [--force]
    python ui/user_content.py [--home DIR] kb edit --topic T [--level L] [--tags a,b] [--summary S] [--pitfalls S] [--difficulty N]
    python ui/user_content.py [--home DIR] kb rm --topic T [--level L]
    python ui/user_content.py [--home DIR] kb validate
    python ui/user_content.py [--home DIR] ref list
    python ui/user_content.py [--home DIR] ref show <id> [--level L]
    python ui/user_content.py [--home DIR] ref add <题目目录> [--level L] [--id ID] [--force]
    python ui/user_content.py [--home DIR] ref rm <id> [--level L]
    python ui/user_content.py [--home DIR] ref validate <题目目录>

退出码: 0 成功; 1 参数/校验错误; 2 未找到。
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# 内置层级 -> 目录名（与 knowledge-base/level-N-*.md 对齐）
BUILTIN_LEVELS = {
    "入门级": "level-1-basic",
    "提高级": "level-2-intermediate",
    "专家级": "level-3-expert",
}
LEVEL_DIR_TO_NAME = {v: k for k, v in BUILTIN_LEVELS.items()}

SKILL_DIR = Path(__file__).resolve().parent.parent          # skills/oi-workbench
BUILTIN_KB_DIR = SKILL_DIR / "knowledge-base"

CARD_REQUIRED_FIELDS = ("topic", "level", "summary")
INVALID_NAME = re.compile(r'[\\/:*?"<>|\s]+')


class UserContentError(Exception):
    pass


# ---------- helpers ----------

def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_name(name):
    name = (name or "").strip()
    s = INVALID_NAME.sub("-", name)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "untitled"


def level_dir(level):
    level = (level or "").strip()
    if not level:
        raise UserContentError("level 不能为空")
    if level in BUILTIN_LEVELS:
        return BUILTIN_LEVELS[level]
    if level in LEVEL_DIR_TO_NAME:
        return level  # 已传入目录名
    slug = re.sub(r"[^0-9A-Za-z_-]+", "-", level)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "custom"


def level_name_from_dir(d):
    return LEVEL_DIR_TO_NAME.get(d, d)


def resolve_within(root, *parts):
    root = Path(root).resolve()
    p = root.joinpath(*parts).resolve()
    ok = str(p) == str(root) or str(p).startswith(str(root) + "\\") or str(p).startswith(str(root) + "/")
    if not ok:
        raise UserContentError("非法路径（越出数据根目录）: %s" % p)
    return p


def strip_quotes(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        return s[1:-1].strip()
    return s


def parse_frontmatter(text):
    """返回 (meta, body)。无法解析时返回 ({}, text)。"""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text
    raw = lines[1:end]
    body = "\n".join(lines[end + 1:]).lstrip("\n")
    meta = {}
    i = 0
    while i < len(raw):
        line = raw[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^([A-Za-z0-9_]+)\s*:\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key = m.group(1)
        val = m.group(2).strip()
        if val == "|":
            block = []
            i += 1
            while i < len(raw):
                l = raw[i]
                if l.strip() == "" or l.startswith(" "):
                    block.append(l.lstrip() if l.strip() else l)
                    i += 1
                else:
                    break
            meta[key] = "\n".join(block).strip("\n")
        elif val.startswith("["):
            items = [strip_quotes(x) for x in val.strip("[]").split(",") if x.strip()]
            meta[key] = items
            i += 1
        elif val == "":
            items = []
            i += 1
            first = True
            while i < len(raw):
                l = raw[i]
                lst = re.match(r"^[-*]\s+(.*)$", l.strip())
                indented = l.startswith(" ") or l.startswith("\t")
                if lst and (indented or first):
                    items.append(strip_quotes(lst.group(1)))
                    i += 1
                    first = False
                else:
                    break
            meta[key] = items
        else:
            meta[key] = strip_quotes(val)
            i += 1
    return meta, body


def render_card(meta, body=""):
    out = ["---"]
    keys = list(CARD_REQUIRED_FIELDS) + [k for k in meta if k not in CARD_REQUIRED_FIELDS]
    for key in keys:
        if key not in meta:
            continue
        val = meta[key]
        if isinstance(val, list):
            if val:
                out.append("%s:" % key)
                out.extend("  - %s" % item for item in val)
            else:
                out.append("%s: []" % key)
        elif isinstance(val, str) and "\n" in val:
            out.append("%s: |" % key)
            out.extend("  %s" % line for line in val.splitlines())
        else:
            out.append("%s: %s" % (key, val))
    out.append("---")
    text = "\n".join(out)
    if body and body.strip():
        text += "\n\n" + body.strip() + "\n"
    else:
        text += "\n"
    return text


def load_card_file(path):
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    return meta, body


def validate_card_meta(meta, origin):
    errors = []
    for f in CARD_REQUIRED_FIELDS:
        if not meta.get(f):
            errors.append("缺少必填字段 %r" % f)
    d = meta.get("difficulty")
    if d not in (None, ""):
        try:
            d = int(d)
            if not (0 <= d <= 10):
                errors.append("difficulty 需在 0~10 之间，当前 %r" % meta.get("difficulty"))
        except (TypeError, ValueError):
            errors.append("difficulty 需为整数，当前 %r" % meta.get("difficulty"))
    if errors:
        raise UserContentError("%s: %s" % (origin, "; ".join(errors)))


def user_cards(home):
    root = ensure_dir(kb_root(home))
    cards = []
    for ldir in sorted(p for p in root.iterdir() if p.is_dir()):
        for md in sorted(p for p in ldir.iterdir() if p.suffix.lower() == ".md"):
            meta, _ = load_card_file(md)
            cards.append({
                "path": md,
                "level_dir": ldir.name,
                "level": meta.get("level") or level_name_from_dir(ldir.name),
                "topic": meta.get("topic") or md.stem,
                "meta": meta,
            })
    return cards


def find_user_card(home, topic, level=None):
    found = [c for c in user_cards(home) if c["topic"] == topic]
    if level:
        found = [c for c in found if c["level"] == level]
    return found


def kb_root(home):
    return Path(home) / "kb"


def ref_root(home):
    return Path(home) / "reference"


# ---------- kb subcommands ----------

def cmd_kb_list(args):
    rows = user_cards(args.home)
    if rows:
        for r in rows:
            print("[user] topic=%-20s level=%-20s tags=%s summary=%s" % (
                r["topic"], r["level"],
                ",".join(r["meta"].get("tags") or []) or "-",
                (r["meta"].get("summary") or "")[:40]))
    else:
        print("[INFO] 用户层暂无知识库卡片。")
    print("[INFO] 内置速查见 knowledge-base/level-1-basic.md / level-2-intermediate.md / level-3-expert.md（可用 kb search 一并检索）。")


def cmd_kb_show(args):
    found = find_user_card(args.home, args.topic)
    if not found:
        print("[ERROR] 用户层未找到 topic=%r；可先 `kb search %s` 或按内置速查表检索。" % (args.topic, args.topic))
        sys.exit(2)
    c = found[0]
    meta = c["meta"]
    print("== 用户知识库卡片（source=user, level=%s） ==" % c["level"])
    print("主题: %s" % c["topic"])
    if meta.get("difficulty") is not None:
        print("难度系数: %s" % meta["difficulty"])
    if meta.get("tags"):
        print("标签: %s" % ", ".join(meta["tags"]) if isinstance(meta["tags"], list) else meta["tags"])
    if meta.get("summary"):
        print("概述: %s" % meta["summary"])
    if meta.get("pitfalls"):
        print("易错点:")
        print(meta["pitfalls"])
    body = c["path"].read_text(encoding="utf-8").split("---", 2)[-1].strip()
    if body:
        print("---- 正文 ----")
        print(body)
    print("[OK] 文件: %s" % c["path"])


def cmd_kb_search(args):
    kw = args.keyword.lower()
    hits = []
    for c in user_cards(args.home):
        hay = json.dumps(c["meta"], ensure_ascii=False) + c["path"].read_text(encoding="utf-8")
        if kw in hay.lower():
            hits.append(("user", str(c["path"])))
    if BUILTIN_KB_DIR.is_dir():
        for f in BUILTIN_KB_DIR.glob("*.md"):
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for ln, line in enumerate(text.splitlines(), 1):
                if kw in line.lower():
                    hits.append(("builtin", "%s:%d" % (f.name, ln)))
    if not hits:
        print("[INFO] 未检索到 %r。" % args.keyword)
    for src, loc in hits[:60]:
        print("[%s] %s" % (src, loc))
    if len(hits) > 60:
        print("[INFO] 共 %d 条命中，仅显示前 60 条。" % len(hits))


def cmd_kb_add(args):
    if not args.topic:
        raise UserContentError("缺少 --topic")
    if not args.level:
        raise UserContentError("缺少 --level")
    meta = {"topic": args.topic.strip(), "level": args.level.strip()}
    if args.difficulty is not None:
        meta["difficulty"] = args.difficulty
    if args.tags:
        meta["tags"] = [t.strip() for t in args.tags.split(",") if t.strip()]
    if args.summary is not None:
        meta["summary"] = args.summary.strip()
    if args.pitfalls is not None:
        meta["pitfalls"] = args.pitfalls.strip("\n")
    validate_card_meta(meta, "kb add")
    ldir = level_dir(meta["level"])
    target = resolve_within(kb_root(args.home), ldir, safe_name(meta["topic"]) + ".md")
    if target.exists():
        raise UserContentError("用户层已存在 topic=%r（%s）；请用 edit 修改或先 rm。" % (meta["topic"], target))
    ensure_dir(target.parent)
    target.write_text(render_card(meta, args.body or ""), encoding="utf-8")
    print("[OK] 已新增知识库卡片 topic=%s level=%s" % (meta["topic"], meta["level"]))
    print("[INFO] 文件: %s" % target)
    print("[INFO] 合并规则：锁定知识点时同名 topic 以本用户卡为准。")


def cmd_kb_add_file(args):
    src = Path(args.file)
    if not src.is_file():
        raise UserContentError("卡片文件不存在: %s" % src)
    meta, body = load_card_file(src)
    level = meta.get("level") or args.level
    if not level:
        raise UserContentError("卡片 frontmatter 缺 level，且未提供 --level")
    meta["level"] = level
    if not meta.get("topic"):
        meta["topic"] = src.stem
    validate_card_meta(meta, "kb add-file")
    ldir = level_dir(level)
    target = resolve_within(kb_root(args.home), ldir, safe_name(meta["topic"]) + ".md")
    if target.exists() and not args.force:
        raise UserContentError("目标已存在: %s（加 --force 覆盖）" % target)
    ensure_dir(target.parent)
    target.write_text(render_card(meta, body), encoding="utf-8")
    print("[OK] 已导入卡片 topic=%s level=%s" % (meta["topic"], level))
    print("[INFO] 文件: %s" % target)


def cmd_kb_edit(args):
    found = find_user_card(args.home, args.topic, args.level)
    if not found:
        print("[ERROR] 用户层未找到 topic=%r%s；可先 `kb add`。" % (
            args.topic, ("（level=%s）" % args.level) if args.level else ""))
        sys.exit(2)
    if len(found) > 1:
        print("[ERROR] topic=%r 在多个 level 下存在：%s；请用 --level 指定。" % (
            args.topic, ", ".join(c["level"] for c in found)))
        sys.exit(1)
    c = found[0]
    meta, body = load_card_file(c["path"])
    changed = []
    if args.summary is not None:
        meta["summary"] = args.summary.strip()
        changed.append("summary")
    if args.pitfalls is not None:
        meta["pitfalls"] = args.pitfalls.strip("\n")
        changed.append("pitfalls")
    if args.tags is not None:
        meta["tags"] = [t.strip() for t in args.tags.split(",") if t.strip()]
        changed.append("tags")
    if args.difficulty is not None:
        meta["difficulty"] = args.difficulty
        changed.append("difficulty")
    if args.level is not None:
        new_dir = level_dir(args.level)
        if new_dir != c["level_dir"]:
            ntarget = resolve_within(kb_root(args.home), new_dir, c["path"].name)
            ensure_dir(ntarget.parent)
            meta["level"] = args.level
            c["path"].write_text(render_card(meta, body), encoding="utf-8")
            c["path"].unlink()
            c["path"] = ntarget
            changed.append("level(移动至 %s)" % new_dir)
        else:
            meta["level"] = args.level
            changed.append("level")
    validate_card_meta(meta, "kb edit")
    c["path"].write_text(render_card(meta, body), encoding="utf-8")
    print("[OK] 已更新 topic=%s 字段: %s" % (args.topic, ", ".join(changed) or "无"))
    print("[INFO] 文件: %s" % c["path"])


def cmd_kb_rm(args):
    found = find_user_card(args.home, args.topic, args.level)
    if not found:
        print("[ERROR] 用户层未找到 topic=%r%s；删除只作用于用户卡片。" % (
            args.topic, ("（level=%s）" % args.level) if args.level else ""))
        sys.exit(2)
    if len(found) > 1:
        print("[ERROR] topic=%r 在多个 level 下存在：%s；请用 --level 指定。" % (
            args.topic, ", ".join(c["level"] for c in found)))
        sys.exit(1)
    c = found[0]
    c["path"].unlink()
    try:
        c["path"].parent.rmdir()
    except OSError:
        pass
    print("[OK] 已删除用户知识库卡片 topic=%s（文件: %s）" % (args.topic, c["path"]))


def cmd_kb_validate(args):
    cards = user_cards(args.home)
    if not cards:
        print("[INFO] 用户层无卡片，校验通过（0 张）。")
        return
    failed = 0
    for c in cards:
        try:
            validate_card_meta(c["meta"], str(c["path"]))
            if safe_name(c["topic"]) != c["path"].stem:
                print("[WARN] %s: 文件名 %r 与 topic %r 不一致，建议重命名。" % (c["path"], c["path"].stem, c["topic"]))
            print("[OK] %s" % c["path"])
        except UserContentError as e:
            print("[ERROR] %s" % e)
            failed += 1
    if failed:
        print("[ERROR] 共 %d 张卡片校验失败。" % failed)
        sys.exit(1)
    print("[OK] 用户层 %d 张卡片全部通过。" % len(cards))


# ---------- ref subcommands ----------

def validate_ref_dir(d):
    d = Path(d)
    issues = []
    if not d.is_dir():
        return ["目录不存在: %s" % d], "-"
    for f in ("problem.md", "spec.json", "std/std.cpp"):
        if not (d / f).is_file():
            issues.append("缺少 %s" % f)
    data = d / "data"
    if not data.is_dir():
        issues.append("缺少 data/ 目录")
    else:
        ins = sorted(data.glob("*.in"))
        outs = sorted(data.glob("*.out"))
        ins_base = {p.stem for p in ins}
        outs_base = {p.stem for p in outs}
        if not ins:
            issues.append("data/ 下无 *.in")
        pairs = ins_base & outs_base
        if not pairs:
            issues.append("data/ 下无匹配的 in/out 测试点对")
        elif len(ins_base) != len(outs_base):
            issues.append("data/ 下 in/out 数量不一（%d in vs %d out）" % (len(ins_base), len(outs_base)))
    sample = d / "sample"
    if sample.is_dir() and not list(sample.glob("*.in")):
        issues.append("sample/ 下无样例")
    spec = d / "spec.json"
    title = "-"
    if spec.is_file():
        try:
            title = str(json.loads(spec.read_text(encoding="utf-8")).get("title", "-"))
        except Exception:
            issues.append("spec.json 无法解析为 JSON")
    return issues, title


def cmd_ref_validate(args):
    issues, title = validate_ref_dir(args.dir)
    if not issues:
        print("[OK] 参考题目录完整（title=%s, dir=%s）" % (title, args.dir))
    else:
        for issue in issues:
            print("[ERROR] %s: %s" % (args.dir, issue))
        sys.exit(1)


def iter_ref_problems(home):
    root = ref_root(home)
    if not root.is_dir():
        return
    for ldir in sorted(p for p in root.iterdir() if p.is_dir()):
        for pid in sorted(p for p in ldir.iterdir() if p.is_dir()):
            yield ldir.name, pid


def cmd_ref_list(args):
    any_row = False
    for ldir_name, pid in iter_ref_problems(args.home):
        issues, title = validate_ref_dir(pid)
        level = level_name_from_dir(ldir_name)
        status = "完整" if not issues else ("缺: " + "; ".join(issues[:2]))
        print("[user] id=%-18s level=%-12s title=%s (%s)" % (pid.name, level, title, status))
        any_row = True
    if not any_row:
        print("[INFO] 用户层暂无参考题。")


def cmd_ref_show(args):
    candidates = []
    root = ref_root(args.home)
    if args.level:
        p = resolve_within(root, level_dir(args.level), safe_name(args.id))
        candidates = [p] if p.is_dir() else []
    elif root.is_dir():
        for ldir in (p for p in root.iterdir() if p.is_dir()):
            p = ldir / safe_name(args.id)
            if p.is_dir():
                candidates.append(p)
    if not candidates:
        print("[ERROR] 用户层未找到参考题 id=%r%s。" % (
            args.id, ("（level=%s）" % args.level) if args.level else ""))
        sys.exit(2)
    p = candidates[0]
    issues, title = validate_ref_dir(p)
    print("== 用户参考题 id=%s title=%s ==" % (p.name, title))
    if issues:
        for issue in issues:
            print("[ERROR] %s: %s" % (p, issue))
        sys.exit(1)
    for sub in sorted(x for x in p.iterdir() if x.is_dir()):
        print("[INFO] %s/ （%d 项）" % (sub.name, len(list(sub.iterdir()))))
    print("[OK] 目录: %s" % p)


def cmd_ref_add(args):
    src = Path(args.dir).resolve()
    if not src.is_dir():
        raise UserContentError("题目目录不存在: %s" % src)
    issues, title = validate_ref_dir(src)
    if issues:
        for issue in issues:
            print("[ERROR] %s" % issue)
        print("[ERROR] 来源目录不完整，未添加。")
        sys.exit(1)
    level = args.level
    if not level:
        src_s = str(src).replace("\\", "/")
        if "/entry/" in src_s:
            level = "入门级"
        elif "/intermediate/" in src_s:
            level = "提高级"
        elif "expert" in src_s:
            level = "专家级"
        else:
            level = "入门级"
    pid = safe_name(args.id or src.name)
    dest = resolve_within(ref_root(args.home), level_dir(level), pid)
    if dest.exists() and not args.force:
        raise UserContentError("目标已存在: %s（加 --force 覆盖）" % dest)
    ensure_dir(dest)
    for item in src.iterdir():
        if item.name in ("__pycache__",) or item.suffix in (".pyc",):
            continue
        if item.is_dir():
            shutil.copytree(item, dest / item.name, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest / item.name)
    issues, title2 = validate_ref_dir(dest)
    if issues:
        print("[ERROR] 复制后校验未通过: %s" % "; ".join(issues))
        sys.exit(1)
    print("[OK] 已添加用户参考题 id=%s level=%s title=%s" % (pid, level, title2))
    print("[INFO] 目录: %s" % dest)


def cmd_ref_rm(args):
    root = ref_root(args.home)
    candidates = []
    if args.level:
        p = resolve_within(root, level_dir(args.level), safe_name(args.id))
        candidates = [p] if p.is_dir() else []
    elif root.is_dir():
        for ldir in (p for p in root.iterdir() if p.is_dir()):
            p = ldir / safe_name(args.id)
            if p.is_dir():
                candidates.append(p)
    if not candidates:
        print("[ERROR] 用户层未找到参考题 id=%r%s。" % (
            args.id, ("（level=%s）" % args.level) if args.level else ""))
        sys.exit(2)
    if len(candidates) > 1:
        print("[ERROR] id=%r 在多个 level 下存在：%s；请用 --level 指定。" % (
            args.id, ", ".join(c.parent.name for c in candidates)))
        sys.exit(1)
    p = candidates[0]
    shutil.rmtree(p)
    print("[OK] 已删除用户参考题 id=%s（目录: %s）" % (args.id, p))


# ---------- main ----------

def build_parser():
    p = argparse.ArgumentParser(prog="user_content.py", description="用户自定义知识库 / 参考题 增删改查")
    p.add_argument("--home", default=str(Path.home() / ".dsh-oi-workbench"),
                   help="数据根目录（默认 ~/.dsh-oi-workbench）")
    sub = p.add_subparsers(dest="cmd", required=True)

    kb = sub.add_parser("kb", help="知识库卡片")
    kbsub = kb.add_subparsers(dest="action", required=True)
    l = kbsub.add_parser("list")
    l.add_argument("--with-builtin", action="store_true", help="（保留位）是否附带内置速查提示")
    s = kbsub.add_parser("show")
    s.add_argument("topic")
    sr = kbsub.add_parser("search")
    sr.add_argument("keyword")
    a = kbsub.add_parser("add")
    a.add_argument("--topic")
    a.add_argument("--level")
    a.add_argument("--tags")
    a.add_argument("--summary")
    a.add_argument("--pitfalls")
    a.add_argument("--body")
    a.add_argument("--difficulty", type=int)
    af = kbsub.add_parser("add-file")
    af.add_argument("file")
    af.add_argument("--level")
    af.add_argument("--force", action="store_true")
    e = kbsub.add_parser("edit")
    e.add_argument("--topic", required=True)
    e.add_argument("--level")
    e.add_argument("--tags")
    e.add_argument("--summary")
    e.add_argument("--pitfalls")
    e.add_argument("--difficulty", type=int)
    r = kbsub.add_parser("rm")
    r.add_argument("--topic", required=True)
    r.add_argument("--level")
    v = kbsub.add_parser("validate")

    rf = sub.add_parser("ref", help="用户参考题")
    rfsub = rf.add_subparsers(dest="action", required=True)
    rfl = rfsub.add_parser("list")
    rfs = rfsub.add_parser("show")
    rfs.add_argument("id")
    rfs.add_argument("--level")
    rfa = rfsub.add_parser("add")
    rfa.add_argument("dir")
    rfa.add_argument("--level")
    rfa.add_argument("--id")
    rfa.add_argument("--force", action="store_true")
    rfr = rfsub.add_parser("rm")
    rfr.add_argument("id")
    rfr.add_argument("--level")
    rfv = rfsub.add_parser("validate")
    rfv.add_argument("dir")
    return p


def main(argv=None):
    p = build_parser()
    args = p.parse_args(argv)
    handlers = {
        ("kb", "list"): cmd_kb_list, ("kb", "show"): cmd_kb_show,
        ("kb", "search"): cmd_kb_search, ("kb", "add"): cmd_kb_add,
        ("kb", "add-file"): cmd_kb_add_file, ("kb", "edit"): cmd_kb_edit,
        ("kb", "rm"): cmd_kb_rm, ("kb", "validate"): cmd_kb_validate,
        ("ref", "list"): cmd_ref_list, ("ref", "show"): cmd_ref_show,
        ("ref", "add"): cmd_ref_add, ("ref", "rm"): cmd_ref_rm,
        ("ref", "validate"): cmd_ref_validate,
    }
    fn = handlers.get((args.cmd, args.action))
    if not fn:
        p.print_help()
        sys.exit(1)
    try:
        fn(args)
        return 0
    except UserContentError as e:
        print("[ERROR] %s" % e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
