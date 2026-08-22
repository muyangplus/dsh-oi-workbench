#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_contest.py —— 从“比赛描述（manifest）”一键生成整场比赛交付物。

整合能力：
  - story-card：按 manifest 为每题生成背景故事并幂等插入 problem.md；
  - story.yaml：由 manifest 生成连载剧本并做连续性检查；
  - build_contest.py：一键产出完整样例 + 整卷 PDF + Lemon(.cdf) + 每题 Hydro/HOJ 包。

用法：
  python generator/generate_contest.py --manifest contest.json
  python generator/generate_contest.py --manifest contest.json --skip-story --skip-check

manifest.json 示例：
{
  "contest": "LKCP",
  "subtitle": "2026 第二轮认证",
  "level": "提高级",
  "time": "2026 年 8 月 22 日 13:00~16:00",
  "contestTitle": "LKCP 非专业级软件能力认证",
  "cdfName": "LKCP.cdf",
  "out": "dist/csp-s-mock",
  "story": {
    "title": "银河远征第一场",
    "previous": "",
    "episodes": [
      {"id": 1, "title": "选拔", "characters": ["队长"], "locations": ["报名处"],
       "props": ["旧口哨"], "plot": "选拔队员", "unresolved": ["牛肉面之谜"]}
    ]
  },
  "problems": [
    {"dir": "drafts/csp-s-mock/climb", "title": "登山选拔",
     "topic": "选出体能值严格递增且保持顺序的最多人",
     "knowledge": ["贪心", "二分", "动态规划"],
     "theme": "雪山远征", "scene": "报名处",
     "characters": ["队长:冷面王", "队员:铁腿阿强"],
     "props": ["旧口哨:1982年救过7人", "三碗牛肉面:纯属广告"],
     "applyStory": true}
  ]
}
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load_manifest(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def apply_stories(m):
    from story_card import parse_pairs, build_story, apply_story
    for p in m.get("problems", []):
        if not p.get("applyStory"):
            continue
        chars = parse_pairs(p.get("characters") or [])
        props = parse_pairs(p.get("props") or [])
        args = argparse.Namespace(
            title=p.get("title"), topic=p.get("topic", "给定数据求一个结果"),
            theme=p.get("theme"), scene=p.get("scene"))
        story = build_story(args, chars, props)
        apply_story(os.path.join(p["dir"], "problem.md"), story)


def build_story_yaml(m, out_dir):
    story = m.get("story") or {}
    episodes = story.get("episodes") or []
    if not episodes:
        # 默认：每题一集
        for i, p in enumerate(m.get("problems", []), 1):
            episodes.append({
                "id": i,
                "title": p.get("title", "ep%d" % i),
                "introduced": (p.get("characters") or [])[:1] + [p.get("scene")] if p.get("scene") else [],
                "characters": [c.split(":")[0] for c in p.get("characters") or []],
                "locations": [p["scene"]] if p.get("scene") else [],
                "props": [x.split(":")[0] for x in p.get("props") or []],
                "plot": p.get("topic", ""),
            })
    lines = [
        "# 连续剧情 / 连载剧本（由 generate_contest.py 生成）",
        "title: %s" % story.get("title", m.get("contest", "contest")),
        'previous: "%s"' % story.get("previous", ""),
        "",
        "episodes:",
    ]
    for ep in episodes:
        lines.append("  - id: %s" % ep.get("id"))
        lines.append("    title: %s" % ep.get("title"))
        for key in ("introduced", "characters", "locations", "props",
                    "uses_unresolved", "resolved", "unresolved"):
            vals = ep.get(key) or []
            if vals:
                lines.append("    %s: [%s]" % (key, ", ".join(str(v) for v in vals)))
        lines.append("    plot: %s" % ep.get("plot", ""))
    os.makedirs(out_dir, exist_ok=True)
    yaml_path = os.path.join(out_dir, m.get("contest", "contest") + ".story.yaml")
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return yaml_path


def check_story(yaml_path):
    r = subprocess.run([sys.executable, os.path.join(HERE, "story_continuity.py"), yaml_path],
                       capture_output=True, text=True)
    print(r.stdout)
    if r.returncode != 0:
        sys.exit("[error] story.yaml 连续性检查失败")
    return True


def run_build_contest(m):
    cmd = [sys.executable, os.path.join(HERE, "build_contest.py"),
           "--contest", m.get("contest", "LKCP"),
           "--subtitle", m.get("subtitle", ""),
           "--level", m.get("level", "提高级"),
           "--time", m.get("time", ""),
           "--out", m.get("out", "dist")]
    cmd += ["--problems"] + [p["dir"] for p in m.get("problems", [])]
    if m.get("contestTitle"):
        cmd += ["--contest-title", m["contestTitle"]]
    if m.get("cdfName"):
        cmd += ["--cdf-name", m["cdfName"]]
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit("[error] build_contest.py 失败")


def main():
    ap = argparse.ArgumentParser(description="从 manifest 一键生成整场比赛交付物")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--skip-story", action="store_true", help="跳过 story-card 应用")
    ap.add_argument("--skip-check", action="store_true", help="跳过 story.yaml 连续性检查")
    args = ap.parse_args()

    m = load_manifest(args.manifest)
    out_dir = os.path.join(m.get("out", "dist"), m.get("contest", "LKCP"))

    if not args.skip_story:
        print("== 应用 story-card ==")
        apply_stories(m)

    yaml_path = build_story_yaml(m, out_dir)
    print("[ok] story.yaml: %s" % yaml_path)
    if not args.skip_check:
        print("== 连续性检查 ==")
        check_story(yaml_path)

    print("== 一键构建比赛 ==")
    run_build_contest(m)
    print("[ok] 整场比赛生成完成")


if __name__ == "__main__":
    main()
