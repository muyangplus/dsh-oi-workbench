#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publish_problem.py —— 把生成的题目包发布到 Hydro OJ。

用法:
    python publish_problem.py <题目包.zip> \
        --base https://hydro.example.com \
        --user root --password 密码 \
        [--domain system] \
        [--pid P1000] [--hidden] [--difficulty 3] \
        [--tag "模拟,数学"] \
        [--title 覆盖标题] [--dry-run]

流程（对应 Hydro 网页操作，字段来自源码）:
    1. 登录（POST /d/{domain}/login）
    2. 创建题目（POST /d/{domain}/problem/create，取 zip 内 problem.yaml 的 title/tag/pid）
    3. 上传数据包（POST /d/{domain}/p/{pid}/files，multipart zip 自动解压进 testdata）
    4. 打印结果 URL

提示:
    - 也可以不写 --password，改用 --cookie "xxx" 直接带会话。
    - --dry-run 只打印将要执行的操作，不发请求。
    - 若实例开启了两步验证等额外安全策略，请先网页登录后把 Cookie 传给 --cookie。
"""

import argparse
import json
import re
import sys
import zipfile

from hydro_api import HydroClient


def read_package_meta(zip_path):
    """读取题目包根 problem.yaml 的 title/pid/tag（极简解析）。"""
    meta = {}
    with zipfile.ZipFile(zip_path) as z:
        if "problem.yaml" in z.namelist():
            text = z.read("problem.yaml").decode("utf-8", "replace")
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("title:"):
                    meta["title"] = line.split(":", 1)[1].strip().strip('"').strip("'")
                elif line.startswith("pid:"):
                    meta["pid"] = line.split(":", 1)[1].strip().strip('"').strip("'")
                elif line.startswith("tag:") or (line.startswith("- ") and "tag" not in meta):
                    pass
    return meta


def main():
    ap = argparse.ArgumentParser(description="发布 Hydro 题目包")
    ap.add_argument("zip_path")
    ap.add_argument("--base", required=True, help="Hydro 实例地址，如 https://hydro.example.com")
    ap.add_argument("--user", default=None)
    ap.add_argument("--password", default=None)
    ap.add_argument("--cookie", default=None, help="已有会话 Cookie（与 user/password 二选一）")
    ap.add_argument("--domain", default="system")
    ap.add_argument("--pid", default=None, help="自定义题目 pid（默认取包内 problem.yaml 的 pid）")
    ap.add_argument("--title", default=None, help="覆盖标题")
    ap.add_argument("--hidden", action="store_true")
    ap.add_argument("--difficulty", type=int, default=0)
    ap.add_argument("--tag", default="", help="逗号分隔标签")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    meta = read_package_meta(args.zip_path)
    title = args.title or meta.get("title") or "未命名"
    pid = args.pid or meta.get("pid") or ""
    tag = [t.strip() for t in args.tag.split(",") if t.strip()]

    print(f"[plan] 题目: {title}  pid={pid or '(自动编号)'}  标签={tag or '(无)'}")
    print(f"[plan] 目标: {args.base}/d/{args.domain}  隐藏={args.hidden}  难度={args.difficulty}")
    if args.dry_run:
        print("[dry-run] 未发送任何请求")
        return

    if args.cookie:
        oj = HydroClient(args.base, cookie=args.cookie, domain=args.domain)
    elif args.user and args.password:
        oj = HydroClient(args.base, username=args.user, password=args.password, domain=args.domain)
        print(f"[ok] 已登录 {args.user}")
    else:
        sys.exit("需要 --user/--password 或 --cookie")

    real_pid = oj.create_problem(
        title=title, content="(题面见数据包 statement/ 或后台编辑)",
        pid=pid, hidden=args.hidden, difficulty=args.difficulty, tag=tag,
    )
    print(f"[ok] 已创建题目: {args.base}/d/{args.domain}/p/{real_pid}")

    res = oj.upload_testdata(real_pid, args.zip_path)
    print(f"[ok] 数据包已上传: {args.zip_path}")
    print(f"[next] 请到网页核对评测配置(config.yaml subtasks)与题面: "
          f"{args.base}/d/{args.domain}/p/{real_pid}/edit")
    return real_pid


if __name__ == "__main__":
    main()
