#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
story_continuity.py —— 连续剧情/连载连续性检查（story.yaml）。

规范见 specs/story-serial.md，模板见 templates/story.yaml。

用法：
  python generator/story_continuity.py story.yaml
  python generator/story_continuity.py --all <剧本仓库目录>

说明：
  - 仅依赖 Python 标准库，内置轻量 YAML 子集解析（适用于模板结构）。
  - 错误（连续性违反）退出码 1；仅有警告（如未回收伏笔）退出码 0 并提示。
"""
import argparse
import os
import re
import sys

RE_KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):(.*)$")
RE_ITEM = re.compile(r"^-\s*id:\s*(\d+)\s*$")


def parse_flow_list(s):
    s = s.strip()
    if s.startswith("[") and s.endswith("]"):
        return [x.strip().strip("'\"") for x in s[1:-1].split(",") if x.strip()]
    return [s] if s else []


def parse_story(text):
    """解析模板结构的 story.yaml 子集。"""
    data = {"title": "", "previous": "", "episodes": []}
    cur = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "episodes:":
            cur = None
            continue
        m = RE_ITEM.match(line)
        if m:
            cur = {"id": int(m.group(1))}
            data["episodes"].append(cur)
            continue
        m = RE_KEY.match(line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        # 去掉行内注释（# 之后），支持 previous: "" # 注释 这类写法
        if "#" in val:
            val = val.split("#", 1)[0].strip()
        # 去掉标量两端的引号
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "'\"":
            val = val[1:-1].strip()
        if cur is not None:
            if val.startswith("[") and val.endswith("]"):
                cur[key] = parse_flow_list(val)
            else:
                cur[key] = val
        else:
            if val.startswith("[") and val.endswith("]"):
                data[key] = parse_flow_list(val)
            else:
                data[key] = val
    return data


def check_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        return [("读失败", str(e))], []
    data = parse_story(text)
    errors, warns = [], []

    title = data.get("title") or os.path.basename(path)
    episodes = data.get("episodes") or []
    if not episodes:
        return [("剧本为空", "%s: 没有 episodes" % path)], []

    ids = [e.get("id") for e in episodes]
    if any(not isinstance(i, int) or i <= 0 for i in ids):
        errors.append(("id 非法", "%s: episode id 必须为正整数" % path))
    if len(set(ids)) != len(ids):
        errors.append(("id 重复", "%s: episode id 重复" % path))

    introduced_at = {}      # entity -> episode id (首次登场)
    open_threads = set()
    prev_ids = []
    for ep in episodes:
        eid = ep.get("id")
        prev_ids.append(eid)
        introduced = ep.get("introduced") or []
        for ent in introduced:
            if ent in introduced_at and introduced_at[ent] != eid:
                # 同一实体再次声明登场（允许，但若已出现过则视为重复声明警告）
                warns.append(("重复登场声明", "%s ep%s: %s" % (path, eid, ent)))
            introduced_at.setdefault(ent, eid)

        for kind in ("characters", "locations", "props"):
            for ent in ep.get(kind) or []:
                if ent in introduced_at and introduced_at[ent] > eid:
                    errors.append(("未登场先使用", "%s ep%s: %s" % (path, eid, ent)))
                introduced_at.setdefault(ent, eid)

        for t in ep.get("uses_unresolved") or []:
            if t not in open_threads:
                errors.append(("引用不存在伏笔", "%s ep%s: %s" % (path, eid, t)))
            else:
                # 使用后仍保留在 open（只有 resolved 才关闭）
                pass
        for t in ep.get("resolved") or []:
            if t not in open_threads:
                errors.append(("解决不存在伏笔", "%s ep%s: %s" % (path, eid, t)))
            else:
                open_threads.discard(t)
        for t in ep.get("unresolved") or []:
            open_threads.add(t)

    if open_threads:
        warns.append(("未回收伏笔", "%s: %s" % (path, "、".join(sorted(open_threads)))))

    previous = data.get("previous")
    if previous:
        # 单文件无法核对 previous 是否存在；在 --all 模式统一检查
        warns.append(("跨场引用", "%s: previous=%s（在 --all 模式核对）" % (path, previous)))

    return errors, warns


def check_all(root):
    files = []
    for dirpath, _, names in os.walk(root):
        for n in names:
            if n.endswith(".yaml") or n.endswith(".yml"):
                files.append(os.path.join(dirpath, n))
    titles = {}
    for f in files:
        with open(f, encoding="utf-8") as fh:
            d = parse_story(fh.read())
        titles[f] = d.get("title") or os.path.basename(f)
    title_set = set(titles.values())
    all_errors, all_warns = [], []
    for f in files:
        e, w = check_file(f)
        all_errors.extend(e)
        all_warns.extend(w)
        with open(f, encoding="utf-8") as fh:
            d = parse_story(fh.read())
        prev = d.get("previous")
        if prev and prev not in title_set:
            all_errors.append(("跨场缺失", "%s: previous=%s 不存在" % (f, prev)))
    return all_errors, all_warns


def main():
    ap = argparse.ArgumentParser(description="连续剧情/连载连续性检查")
    ap.add_argument("path", nargs="?", help="story.yaml 路径")
    ap.add_argument("--all", metavar="DIR", help="递归检查目录下所有 story.yaml")
    args = ap.parse_args()

    if args.all:
        errors, warns = check_all(args.all)
        label = "全部剧本"
    elif args.path:
        errors, warns = check_file(args.path)
        label = args.path
    else:
        ap.error("需要 path 或 --all DIR")

    for kind, msg in errors:
        print("[error][%s] %s" % (kind, msg))
    for kind, msg in warns:
        print("[warn][%s] %s" % (kind, msg))
    print("---- 连续性检查（%s）：错误 %d，警告 %d ----" % (label, len(errors), len(warns)))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
