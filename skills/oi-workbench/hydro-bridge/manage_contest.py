#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
manage_contest.py —— 用 Hydro API 管理比赛与团队（OI 场景）。

用法:
    # 创建 OI 规则比赛（部分分），挂题
    python manage_contest.py contest-create \
        --base https://hydro.example.com --user root --password 密码 \
        --title "OI 模拟赛" --date 2025-03-01 --time 08:30 --duration 3.5 \
        --rule oi --pids 1000,1001,1002

    # 比赛加选手（uid 从 Hydro 用户列表获取）
    python manage_contest.py contest-add-users ... --tid <tid> --uids 2,3,4

    # 建团队并塞人
    python manage_contest.py group-update --name "高一集训队" --uids 2,3,4 ...

    # 比赛用户建议: 选手 uid 可通过 GET /d/{domain}/user 或网页查看
"""

import argparse
import sys

from hydro_api import HydroClient


def common_args(ap):
    ap.add_argument("--base", required=True)
    ap.add_argument("--user", default=None)
    ap.add_argument("--password", default=None)
    ap.add_argument("--cookie", default=None)
    ap.add_argument("--domain", default="system")
    ap.add_argument("--dry-run", action="store_true")


def client(args):
    if args.cookie:
        return HydroClient(args.base, cookie=args.cookie, domain=args.domain)
    if args.user and args.password:
        return HydroClient(args.base, username=args.user, password=args.password, domain=args.domain)
    sys.exit("需要 --user/--password 或 --cookie")


def cmd_contest_create(args):
    oj = client(args)
    tid = oj.create_contest(
        title=args.title,
        begin_at_date=args.date,
        begin_at_time=args.time,
        duration_hours=args.duration,
        content=args.content or "",
        rule=args.rule,
        pids=[int(x) for x in args.pids.split(",")] if args.pids else None,
        rated=args.rated,
        auto_hide=args.auto_hide,
        lock_minutes=args.lock,
    )
    print(f"[ok] 比赛已创建: {args.base}/d/{args.domain}/contest/{tid}")
    return tid


def cmd_contest_add_users(args):
    oj = client(args)
    uids = [int(x) for x in args.uids.split(",")]
    oj.contest_add_users(args.tid, uids)
    print(f"[ok] 已加入 {len(uids)} 名选手到比赛 {args.tid}")


def cmd_contest_remove_user(args):
    oj = client(args)
    oj.contest_remove_user(args.tid, int(args.uid))
    print(f"[ok] 已移除选手 {args.uid}")


def cmd_group_update(args):
    oj = client(args)
    uids = [int(x) for x in args.uids.split(",")] if args.uids else []
    oj.create_group(args.name, uids)
    print(f"[ok] 团队 {args.name} 已更新（{len(uids)} 名成员）")


def cmd_group_list(args):
    oj = client(args)
    groups = oj.list_groups()
    for g in groups if isinstance(groups, list) else []:
        print(g)


def main():
    ap = argparse.ArgumentParser(description="Hydro 比赛/团队管理")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("contest-create", help="创建比赛（默认 OI 规则）")
    common_args(p)
    p.add_argument("--title", required=True)
    p.add_argument("--date", required=True, help="开始日期 YYYY-MM-DD（服务器时区）")
    p.add_argument("--time", required=True, help="开始时间 HH:mm")
    p.add_argument("--duration", type=float, required=True, help="时长（小时）")
    p.add_argument("--rule", default="oi", help="oi|acm|ioi|strictioi|homework|ledo")
    p.add_argument("--pids", default="", help="逗号分隔的题目 docId，如 1000,1001")
    p.add_argument("--content", default="")
    p.add_argument("--rated", action="store_true")
    p.add_argument("--auto-hide", action="store_true", help="比赛期间自动隐藏题目")
    p.add_argument("--lock", type=int, default=None, help="封榜（结束前 N 分钟）")

    p = sub.add_parser("contest-add-users")
    common_args(p)
    p.add_argument("--tid", required=True)
    p.add_argument("--uids", required=True)

    p = sub.add_parser("contest-remove-user")
    common_args(p)
    p.add_argument("--tid", required=True)
    p.add_argument("--uid", required=True)

    p = sub.add_parser("group-update", help="创建/更新团队（域内分组）")
    common_args(p)
    p.add_argument("--name", required=True)
    p.add_argument("--uids", default="")

    p = sub.add_parser("group-list")
    common_args(p)

    args = ap.parse_args()
    if args.dry_run:
        print(f"[dry-run] 命令 {args.cmd}，参数如上，未发送请求")
        return
    {"contest-create": cmd_contest_create,
     "contest-add-users": cmd_contest_add_users,
     "contest-remove-user": cmd_contest_remove_user,
     "group-update": cmd_group_update,
     "group-list": cmd_group_list}[args.cmd](args)


if __name__ == "__main__":
    main()
