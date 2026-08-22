#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
story_card.py —— 故事设计能力：生成“故事卡 + 可直接粘贴的背景故事”。

规范见 specs/story-design.md，模板见 templates/story-card.md。

用法：
  python generator/story_card.py --title 登山选拔 --topic 最长上升子序列 \
      --knowledge 贪心 --knowledge 二分 --knowledge 动态规划 \
      --theme 雪山远征 --characters "队长:冷面王" "队员:铁腿阿强" \
      --scene 报名处 --props "旧口哨:1982年救过7人" "三碗牛肉面:纯属广告" \
      --output story.md
  # 直接插入到题目 problem.md 的「题目描述」开头
  python generator/story_card.py --title 登山选拔 ... --apply problem.md

约定：生成的故事段只做包装，不泄露算法/复杂度/答案量级/64 位等提示。
"""
import argparse
import os
import re

TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates", "story-card.md")


def parse_pairs(items):
    pairs = []
    for it in items or []:
        if ":" in it:
            k, v = it.split(":", 1)
            pairs.append((k.strip(), v.strip()))
        else:
            pairs.append((it.strip(), ""))
    return pairs


def build_story(args, chars, props):
    char_lines = "、".join("%s（%s）" % (n, r) for n, r in chars if r) or "几位当事人"
    prop_lines = "；".join(
        "%s据说%s" % (n, d) if d else n for n, d in props) or "一件没什么用处的旧物"
    scene = args.scene or "现场"
    theme = args.theme or args.topic or "一件寻常小事"
    story = (
        "话说在很久以前，有一桩关于“%s”的旧事，流传到今天的版本已经加进了不少水分。\n"
        "%s。当时在场的%s，各自带着一段说不上有用的经历；有人翻出%s，\n"
        "还有人坚持认为那天的天气、排班表和一句口头禅都至关重要——其实它们与下面的计算毫无关系。\n"
        "事情的经过是这样的：%s。\n"
        "现在，请你根据下面的正式定义完成计算。\n"
    ) % (theme, scene, char_lines, prop_lines, args.topic or "给定一份数据，需要求出某个结果")
    story += "\n<!-- story-card: %s -->\n" % (args.title or args.topic or "untitled")
    return story


def build_card(args, chars, props):
    char_rows = "\n".join("| %s | %s | %s |" % (n, r, "与解题无关") for n, r in chars) or \
        "| - | - | - |"
    prop_rows = "\n".join("- %s：%s" % (n, d) if d else "- %s" % n for n, d in props) or "- -"
    knowledge_rows = "\n".join("- %s：隐入剧情（不出现算法名/提示）" % k for k in args.knowledge) or "- -"
    card = TEMPLATE_CONTENT.format(
        title=args.title or args.topic or "未命名",
        world=args.theme or "待补充",
        char_rows=char_rows,
        scene=args.scene or "待补充",
        prop_rows=prop_rows,
        plot="1. 引入事件\n2. 引出正式问题",
        knowledge_rows=knowledge_rows,
        continuity="涉及角色：%s\n- 涉及场景：%s\n- 未解伏笔：待补充" % (
            "、".join(n for n, _ in chars), args.scene or "待补充"),
    )
    return card


TEMPLATE_CONTENT = """# 故事卡：{title}

> 生成方式：`python generator/story_card.py ...`；规范见 `specs/story-design.md`。

## 主题 / 世界观

{world}

## 角色

| 角色 | 身份 | 无效特征 |
|---|---|---|
{char_rows}

## 场景

{scene}

## 道具 / 无效信息

{prop_rows}

## 剧情主线

{plot}

## 知识点融入点

> 仅内部记录，不得写入题面。

{knowledge_rows}

## 连续性标记

- 涉及角色：{continuity}
"""


def apply_story(problem_path, story):
    with open(problem_path, encoding="utf-8") as f:
        text = f.read()
    if "<!-- story-card" in text:
        print("[skip] %s 已有 story-card 标记，不重复插入" % problem_path)
        return False
    m = re.search(r"^##\s*题目描述\s*$", text, re.M)
    if not m:
        raise SystemExit("problem.md 中未找到「## 题目描述」")
    idx = m.end()
    # 在标题后插入故事段（保留原有正式定义）
    new_text = text[:idx] + "\n\n" + story.strip() + "\n" + text[idx:]
    with open(problem_path, "w", encoding="utf-8") as f:
        f.write(new_text)
    print("[ok] 已插入故事段到 %s" % problem_path)
    return True


def main():
    ap = argparse.ArgumentParser(description="故事卡生成器（含背景故事段落）")
    ap.add_argument("--title", default=None)
    ap.add_argument("--topic", default="给定数据，求一个结果", help="正式问题的一句话描述")
    ap.add_argument("--knowledge", nargs="+", default=[], help="考点（仅记录，不写入题面）")
    ap.add_argument("--theme", default=None, help="主题/世界观")
    ap.add_argument("--characters", nargs="+", default=[], help="角色，格式 名字:身份")
    ap.add_argument("--scene", default=None, help="场景")
    ap.add_argument("--props", nargs="+", default=[], help="道具/无效信息，格式 名称:描述")
    ap.add_argument("--output", default=None, help="输出故事卡文件（缺省仅打印故事段）")
    ap.add_argument("--apply", default=None, help="把生成的故事段插入到指定 problem.md")
    args = ap.parse_args()

    chars = parse_pairs(args.characters)
    props = parse_pairs(args.props)
    story = build_story(args, chars, props)

    if args.apply:
        apply_story(args.apply, story)
        return

    card = build_card(args, chars, props)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(card + "\n\n## 背景故事（可直接粘贴）\n\n" + story + "\n")
        print("[ok] 故事卡: %s" % args.output)
    else:
        print("== 背景故事 ==")
        print(story)
        print("\n== 故事卡 ==")
        print(card)


if __name__ == "__main__":
    main()
