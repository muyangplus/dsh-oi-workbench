#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
manage_hoj.py —— HOJ（HimitZH/HOJ）完整管理命令行。

覆盖：登录、题目、比赛、训练、用户、团队、公告、标签、评测重判、系统信息。

用法示例:

    # 题目
    python hoj-bridge\\manage_hoj.py problem-list --base ... --user root --password ...
    python hoj-bridge\\manage_hoj.py problem-delete --base ... --pid 1000

    # 比赛（OI）
    python hoj-bridge\\manage_hoj.py contest-create --base ... --title "OI 模拟" \
        --type 1 --start "2025-11-01T08:30:00.000Z" --end "2025-11-01T12:00:00.000Z" \
        --auth 0 --duration-seconds 12600

    # 用户批量导入
    python hoj-bridge\\manage_hoj.py user-batch-insert --base ... --users-file users.csv

安全提示：
    - 密码优先用环境变量 HOJ_PASSWORD 或 --cookie，不要明文写入聊天。
    - 所有请求都在本机执行，不把凭据写进仓库。
"""

import argparse
import csv
import json
import os
import sys


def common_args(ap):
    ap.add_argument("--base", required=True)
    ap.add_argument("--user", default=None)
    ap.add_argument("--password", default=None, help="或用环境变量 HOJ_PASSWORD")
    ap.add_argument("--cookie", default=None)
    ap.add_argument("--dry-run", action="store_true")


def get_client(args):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from hoj_api import HojClient
    password = args.password or os.environ.get("HOJ_PASSWORD")
    if not args.cookie and not (args.user and password):
        sys.exit("需要 --user/--password（或环境变量 HOJ_PASSWORD）或 --cookie")
    return HojClient(
        args.base,
        username=args.user if not args.cookie else None,
        password=password if not args.cookie else None,
        cookie=args.cookie,
    )


def show(data):
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def csv_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.reader(f))


def bool_arg(v):
    return str(v).strip().lower() in ("1", "true", "yes", "y")


# ---------- 题目 ----------

def cmd_languages(args):
    show(get_client(args).get_languages())


def cmd_tags(args):
    show(get_client(args).get_tags(oj=args.oj))


def cmd_problem_list(args):
    oj = get_client(args)
    show(oj.list_problems(args.limit, args.current_page, args.keyword, args.auth, args.oj))


def cmd_problem_get(args):
    show(get_client(args).get_problem(args.pid))


def cmd_problem_delete(args):
    oj = get_client(args)
    oj.delete_problem(args.pid)
    print(f"[ok] 已删除题目 {args.pid}")


def cmd_problem_auth(args):
    oj = get_client(args)
    problem = oj.get_problem(args.pid)
    problem["auth"] = args.auth
    oj.change_problem_auth(problem)
    print(f"[ok] 已修改题目 {args.pid} auth={args.auth}")


def cmd_problem_rejudge(args):
    show(get_client(args).rejudge(args.submit_id))


def cmd_problem_export(args):
    oj = get_client(args)
    path = oj.export_problem([int(x) for x in args.pids.split(",")], args.out)
    print(f"[ok] 已导出到 {path}")


def cmd_problem_import_zip(args):
    oj = get_client(args)
    if args.dry_run:
        print(f"[dry-run] 将导入 HOJ zip: {args.zip}")
        return
    oj.import_hoj_problem(args.zip)
    print("[ok] 已导入 HOJ zip")


def cmd_problem_import_hydro(args):
    oj = get_client(args)
    if args.dry_run:
        print(f"[dry-run] 将导入 Hydro zip: {args.zip}")
        return
    oj.import_hydro_problem(args.zip)
    print("[ok] 已导入 Hydro zip")


# ---------- 比赛 ----------

def contest_payload(args):
    payload = {}
    for key in ("id", "title", "type", "description", "auth", "pwd", "startTime",
                "endTime", "duration", "sealRank", "autoRealRank", "visible",
                "openPrint", "openAccountLimit", "rankShowName", "starAccount",
                "openRank", "oiRankScoreType", "allowEndSubmit"):
        val = getattr(args, key, None)
        if val is not None:
            payload[key] = val
    if args.duration_hours is not None:
        payload["duration"] = int(args.duration_hours * 3600)
    if args.star_account:
        payload["starAccount"] = args.star_account.split(",")
    return payload


def cmd_contest_list(args):
    show(get_client(args).list_contests(args.limit, args.current_page, args.keyword))


def cmd_contest_get(args):
    show(get_client(args).get_contest(args.cid))


def cmd_contest_create(args):
    oj = get_client(args)
    payload = contest_payload(args)
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    oj.add_contest(payload)
    print(f"[ok] 比赛已创建: {payload.get('title')}")


def cmd_contest_update(args):
    oj = get_client(args)
    payload = contest_payload(args)
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    oj.update_contest(payload)
    print(f"[ok] 比赛已更新: {args.id}")


def cmd_contest_delete(args):
    oj = get_client(args)
    oj.delete_contest(args.cid)
    print(f"[ok] 已删除比赛 {args.cid}")


def cmd_contest_clone(args):
    oj = get_client(args)
    oj.clone_contest(args.cid)
    print(f"[ok] 已克隆比赛 {args.cid}")


def cmd_contest_visible(args):
    oj = get_client(args)
    oj.change_contest_visible(args.cid, args.uid, args.visible)
    print(f"[ok] 比赛 {args.cid} visible={args.visible}")


def cmd_contest_problem_list(args):
    show(get_client(args).list_contest_problems(
        args.cid, args.limit, args.current_page, args.keyword, args.problem_type, args.oj))


def cmd_contest_problem_add(args):
    oj = get_client(args)
    dto = {"pid": args.pid, "cid": args.cid, "displayId": args.display_id}
    if args.dry_run:
        print(json.dumps(dto, ensure_ascii=False, indent=2))
        return
    oj.add_contest_problem_from_public(dto)
    print(f"[ok] 已从公共题库加入题目 {args.pid} -> 比赛 {args.cid}（{args.display_id}）")


def cmd_contest_problem_remove(args):
    oj = get_client(args)
    oj.delete_contest_problem(args.pid, args.cid)
    print(f"[ok] 已从比赛 {args.cid} 移除题目 {args.pid}")


def cmd_contest_problem_update(args):
    oj = get_client(args)
    obj = {k: v for k, v in {
        "cid": args.cid, "pid": args.pid,
        "displayId": args.display_id, "displayTitle": args.display_title,
        "color": args.color,
    }.items() if v is not None}
    if args.dry_run:
        print(json.dumps(obj, ensure_ascii=False, indent=2))
        return
    show(oj.set_contest_problem(obj))


def cmd_contest_announcement_add(args):
    oj = get_client(args)
    dto = {"cid": args.cid, "announcement": {"title": args.title, "content": args.content}}
    if args.dry_run:
        print(json.dumps(dto, ensure_ascii=False, indent=2))
        return
    oj.add_contest_announcement(dto)
    print(f"[ok] 已添加比赛公告 {args.title}")


def cmd_contest_announcement_update(args):
    oj = get_client(args)
    dto = {"cid": args.cid, "announcement": {"id": args.aid, "title": args.title, "content": args.content}}
    if args.dry_run:
        print(json.dumps(dto, ensure_ascii=False, indent=2))
        return
    oj.update_contest_announcement(dto)
    print(f"[ok] 已更新比赛公告 {args.aid}")


def cmd_contest_announcement_delete(args):
    oj = get_client(args)
    oj.delete_contest_announcement(args.aid)
    print(f"[ok] 已删除比赛公告 {args.aid}")


# ---------- 训练 ----------

def cmd_training_list(args):
    show(get_client(args).list_trainings(args.limit, args.current_page, args.keyword))


def cmd_training_get(args):
    show(get_client(args).get_training(args.tid))


def cmd_training_create(args):
    oj = get_client(args)
    dto = {"training": {
        "title": args.title,
        "description": args.description or "",
        "auth": args.auth or "Public",
        "privatePwd": args.private_pwd,
        "status": args.status,
        "rank": args.rank,
    }}
    if args.dry_run:
        print(json.dumps(dto, ensure_ascii=False, indent=2))
        return
    oj.add_training(dto)
    print(f"[ok] 训练已创建: {args.title}")


def cmd_training_update(args):
    oj = get_client(args)
    dto = {"training": {k: v for k, v in {
        "id": args.tid, "title": args.title, "description": args.description,
        "auth": args.auth, "privatePwd": args.private_pwd,
        "status": args.status, "rank": args.rank,
    }.items() if v is not None}}
    if args.dry_run:
        print(json.dumps(dto, ensure_ascii=False, indent=2))
        return
    oj.update_training(dto)
    print(f"[ok] 训练已更新: {args.tid}")


def cmd_training_delete(args):
    oj = get_client(args)
    oj.delete_training(args.tid)
    print(f"[ok] 已删除训练 {args.tid}")


def cmd_training_status(args):
    oj = get_client(args)
    oj.change_training_status(args.tid, args.author, args.status)
    print(f"[ok] 训练 {args.tid} status={args.status}")


def cmd_training_problem_add(args):
    oj = get_client(args)
    dto = {"pid": args.pid, "tid": args.tid, "displayId": args.display_id}
    if args.dry_run:
        print(json.dumps(dto, ensure_ascii=False, indent=2))
        return
    oj.add_training_problem_from_public(dto)
    print(f"[ok] 已加入题目 {args.pid} -> 训练 {args.tid}（{args.display_id}）")


def cmd_training_problem_remove(args):
    oj = get_client(args)
    oj.delete_training_problem(args.pid, args.tid)
    print(f"[ok] 已从训练 {args.tid} 移除题目 {args.pid}")


def cmd_training_problem_update(args):
    oj = get_client(args)
    obj = {k: v for k, v in {
        "tid": args.tid, "pid": args.pid, "displayId": args.display_id,
        "rank": args.rank,
    }.items() if v is not None}
    if args.dry_run:
        print(json.dumps(obj, ensure_ascii=False, indent=2))
        return
    oj.update_training_problem(obj)
    print(f"[ok] 已更新训练题目 {args.pid} @ {args.tid}")


# ---------- 用户 ----------

def cmd_user_list(args):
    show(get_client(args).list_users(args.limit, args.current_page, args.only_admin, args.keyword))


def cmd_user_edit(args):
    oj = get_client(args)
    dto = {"uid": args.uid, "username": args.username}
    for key, val in (("realname", args.realname), ("email", args.email),
                     ("password", args.password), ("type", args.type),
                     ("status", args.status), ("setNewPwd", args.set_new_pwd)):
        if val is not None:
            dto[key] = val
    if args.dry_run:
        print(json.dumps(dto, ensure_ascii=False, indent=2))
        return
    oj.edit_user(dto)
    print(f"[ok] 用户 {args.username} 已更新")


def cmd_user_delete(args):
    oj = get_client(args)
    oj.delete_users(args.uids.split(","))
    print(f"[ok] 已删除用户: {args.uids}")


def cmd_user_batch_insert(args):
    oj = get_client(args)
    users = csv_rows(args.users_file)
    if args.dry_run:
        print(f"[dry-run] 将插入 {len(users)} 行用户")
        return
    oj.insert_batch_users(users)
    print(f"[ok] 已批量插入 {len(users)} 名用户")


def cmd_user_generate(args):
    oj = get_client(args)
    with open(args.config, encoding="utf-8") as f:
        params = json.load(f)
    if args.dry_run:
        print(json.dumps(params, ensure_ascii=False, indent=2))
        return
    show(oj.generate_users(params))


# ---------- 团队 ----------

def cmd_group_list(args):
    show(get_client(args).list_groups(args.limit, args.current_page, args.keyword, args.auth, args.only_mine))


def cmd_group_get(args):
    show(get_client(args).get_group(args.gid))


def cmd_group_create(args):
    oj = get_client(args)
    obj = {k: v for k, v in {
        "name": args.name, "shortName": args.short_name, "brief": args.brief,
        "description": args.description, "auth": args.auth, "visible": args.visible,
        "code": args.code,
    }.items() if v is not None}
    if args.dry_run:
        print(json.dumps(obj, ensure_ascii=False, indent=2))
        return
    oj.add_group(obj)
    print(f"[ok] 团队已创建: {args.name}")


def cmd_group_update(args):
    oj = get_client(args)
    obj = {k: v for k, v in {
        "id": args.gid, "name": args.name, "shortName": args.short_name,
        "brief": args.brief, "description": args.description, "auth": args.auth,
        "visible": args.visible, "code": args.code,
    }.items() if v is not None}
    if args.dry_run:
        print(json.dumps(obj, ensure_ascii=False, indent=2))
        return
    oj.update_group(obj)
    print(f"[ok] 团队已更新: {args.gid}")


def cmd_group_delete(args):
    oj = get_client(args)
    oj.delete_group(args.gid)
    print(f"[ok] 已删除团队 {args.gid}")


def cmd_group_member_list(args):
    show(get_client(args).list_group_members(args.gid, args.limit, args.current_page, args.keyword, args.auth))


def cmd_group_member_add(args):
    oj = get_client(args)
    oj.add_group_member(args.gid, args.code, args.reason)
    print(f"[ok] 已加入/申请团队 {args.gid}")


def cmd_group_member_update(args):
    oj = get_client(args)
    obj = {k: v for k, v in {
        "gid": args.gid, "uid": args.uid, "auth": args.auth, "reason": args.reason,
    }.items() if v is not None}
    if args.dry_run:
        print(json.dumps(obj, ensure_ascii=False, indent=2))
        return
    oj.update_group_member(obj)
    print(f"[ok] 已更新团队成员 {args.uid} @ {args.gid}")


def cmd_group_member_delete(args):
    oj = get_client(args)
    oj.delete_group_member(args.uid, args.gid)
    print(f"[ok] 已移出用户 {args.uid}")

# ---------- 公告 ----------

def cmd_announcement_list(args):
    show(get_client(args).list_announcements(args.limit, args.current_page))


def cmd_announcement_create(args):
    oj = get_client(args)
    ann = {"title": args.title, "content": args.content}
    if args.dry_run:
        print(json.dumps(ann, ensure_ascii=False, indent=2))
        return
    oj.add_announcement(ann)
    print(f"[ok] 公告已创建: {args.title}")


def cmd_announcement_update(args):
    oj = get_client(args)
    ann = {"id": args.aid, "title": args.title, "content": args.content}
    if args.dry_run:
        print(json.dumps(ann, ensure_ascii=False, indent=2))
        return
    oj.update_announcement(ann)
    print(f"[ok] 公告已更新: {args.aid}")


def cmd_announcement_delete(args):
    oj = get_client(args)
    oj.delete_announcement(args.aid)
    print(f"[ok] 已删除公告 {args.aid}")

# ---------- 标签 ----------

def cmd_tag_create(args):
    oj = get_client(args)
    tag = {"name": args.name, "color": args.color, "oj": args.oj}
    if args.dry_run:
        print(json.dumps(tag, ensure_ascii=False, indent=2))
        return
    show(oj.add_tag(tag))


def cmd_tag_update(args):
    oj = get_client(args)
    tag = {"id": args.tid, "name": args.name, "color": args.color, "oj": args.oj}
    if args.dry_run:
        print(json.dumps(tag, ensure_ascii=False, indent=2))
        return
    oj.update_tag(tag)
    print(f"[ok] 标签已更新: {args.tid}")


def cmd_tag_delete(args):
    oj = get_client(args)
    oj.delete_tag(args.tid)
    print(f"[ok] 已删除标签 {args.tid}")

# ---------- 评测 ----------

def cmd_judge_rejudge(args):
    show(get_client(args).rejudge(args.submit_id))


def cmd_judge_manual(args):
    oj = get_client(args)
    show(oj.manual_judge(args.submit_id, args.status, args.score))


def cmd_judge_cancel(args):
    show(get_client(args).cancel_judge(args.submit_id))


# ---------- 系统 ----------

def cmd_dashboard(args):
    show(get_client(args).get_dashboard_info())


def cmd_service_info(args):
    show(get_client(args).get_service_info())


def main():
    ap = argparse.ArgumentParser(description="HOJ 管理 CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # 系统
    for name, fn, help_ in [
        ("languages", cmd_languages, "语言列表"),
        ("tags", cmd_tags, "标签列表"),
        ("dashboard", cmd_dashboard, "后台看板"),
        ("service-info", cmd_service_info, "服务信息"),
    ]:
        p = sub.add_parser(name, help=help_)
        common_args(p)
        if name == "tags":
            p.add_argument("--oj", default="ME")
        p.set_defaults(func=fn)

    # 题目
    p = sub.add_parser("problem-list", help="题目列表")
    common_args(p); p.add_argument("--limit", type=int, default=20); p.add_argument("--current-page", type=int, default=1)
    p.add_argument("--keyword"); p.add_argument("--auth", type=int); p.add_argument("--oj")
    p.set_defaults(func=cmd_problem_list)

    p = sub.add_parser("problem-get"); common_args(p); p.add_argument("--pid", required=True, type=int); p.set_defaults(func=cmd_problem_get)
    p = sub.add_parser("problem-delete"); common_args(p); p.add_argument("--pid", required=True, type=int); p.set_defaults(func=cmd_problem_delete)
    p = sub.add_parser("problem-auth"); common_args(p); p.add_argument("--pid", required=True, type=int); p.add_argument("--auth", required=True, type=int); p.set_defaults(func=cmd_problem_auth)
    p = sub.add_parser("problem-rejudge"); common_args(p); p.add_argument("--submit-id", required=True, type=int); p.set_defaults(func=cmd_problem_rejudge)
    p = sub.add_parser("problem-export"); common_args(p); p.add_argument("--pids", required=True); p.add_argument("--out"); p.set_defaults(func=cmd_problem_export)
    p = sub.add_parser("problem-import-zip"); common_args(p); p.add_argument("--zip", required=True); p.set_defaults(func=cmd_problem_import_zip)
    p = sub.add_parser("problem-import-hydro"); common_args(p); p.add_argument("--zip", required=True); p.set_defaults(func=cmd_problem_import_hydro)

    # 比赛
    p = sub.add_parser("contest-list"); common_args(p); p.add_argument("--limit", type=int, default=20); p.add_argument("--current-page", type=int, default=1); p.add_argument("--keyword"); p.set_defaults(func=cmd_contest_list)
    p = sub.add_parser("contest-get"); common_args(p); p.add_argument("--cid", required=True, type=int); p.set_defaults(func=cmd_contest_get)

    def add_contest_args(p):
        common_args(p)
        p.add_argument("--id", type=int)
        p.add_argument("--title"); p.add_argument("--type", type=int, choices=[0,1], default=1)
        p.add_argument("--description"); p.add_argument("--auth", type=int, choices=[0,1,2])
        p.add_argument("--pwd"); p.add_argument("--start-time"); p.add_argument("--end-time")
        p.add_argument("--duration-seconds", type=int, dest="duration")
        p.add_argument("--duration-hours", type=float, dest="duration_hours")
        p.add_argument("--seal-rank", type=bool_arg, nargs="?", const=True)
        p.add_argument("--auto-real-rank", type=bool_arg, nargs="?", const=True)
        p.add_argument("--visible", type=bool_arg, nargs="?", const=True)
        p.add_argument("--open-print", type=bool_arg, nargs="?", const=True)
        p.add_argument("--open-account-limit", type=bool_arg, nargs="?", const=True)
        p.add_argument("--rank-show-name"); p.add_argument("--star-account", dest="star_account")
        p.add_argument("--open-rank", type=bool_arg, nargs="?", const=True)
        p.add_argument("--oi-rank-score-type"); p.add_argument("--allow-end-submit", type=bool_arg, nargs="?", const=True)

    p = sub.add_parser("contest-create"); add_contest_args(p); p.set_defaults(func=cmd_contest_create)
    p = sub.add_parser("contest-update"); add_contest_args(p); p.set_defaults(func=cmd_contest_update)
    p = sub.add_parser("contest-delete"); common_args(p); p.add_argument("--cid", required=True, type=int); p.set_defaults(func=cmd_contest_delete)
    p = sub.add_parser("contest-clone"); common_args(p); p.add_argument("--cid", required=True, type=int); p.set_defaults(func=cmd_contest_clone)
    p = sub.add_parser("contest-visible"); common_args(p); p.add_argument("--cid", required=True, type=int); p.add_argument("--uid", required=True); p.add_argument("--visible", required=True, type=lambda x: str(x).lower()=="true"); p.set_defaults(func=cmd_contest_visible)
    p = sub.add_parser("contest-problem-list"); common_args(p); p.add_argument("--cid", required=True, type=int); p.add_argument("--limit", type=int, default=20); p.add_argument("--current-page", type=int, default=1); p.add_argument("--keyword"); p.add_argument("--problem-type", type=int); p.add_argument("--oj"); p.set_defaults(func=cmd_contest_problem_list)
    p = sub.add_parser("contest-problem-add"); common_args(p); p.add_argument("--pid", required=True, type=int); p.add_argument("--cid", required=True, type=int); p.add_argument("--display-id", required=True); p.set_defaults(func=cmd_contest_problem_add)
    p = sub.add_parser("contest-problem-remove"); common_args(p); p.add_argument("--pid", required=True, type=int); p.add_argument("--cid", required=True, type=int); p.set_defaults(func=cmd_contest_problem_remove)
    p = sub.add_parser("contest-problem-update"); common_args(p); p.add_argument("--pid", required=True, type=int); p.add_argument("--cid", required=True, type=int); p.add_argument("--display-id"); p.add_argument("--display-title"); p.add_argument("--color"); p.set_defaults(func=cmd_contest_problem_update)
    p = sub.add_parser("contest-announcement-add"); common_args(p); p.add_argument("--cid", required=True, type=int); p.add_argument("--title", required=True); p.add_argument("--content", required=True); p.set_defaults(func=cmd_contest_announcement_add)
    p = sub.add_parser("contest-announcement-update"); common_args(p); p.add_argument("--cid", required=True, type=int); p.add_argument("--aid", required=True, type=int); p.add_argument("--title", required=True); p.add_argument("--content", required=True); p.set_defaults(func=cmd_contest_announcement_update)
    p = sub.add_parser("contest-announcement-delete"); common_args(p); p.add_argument("--aid", required=True, type=int); p.set_defaults(func=cmd_contest_announcement_delete)

    # 训练
    p = sub.add_parser("training-list"); common_args(p); p.add_argument("--limit", type=int, default=20); p.add_argument("--current-page", type=int, default=1); p.add_argument("--keyword"); p.set_defaults(func=cmd_training_list)
    p = sub.add_parser("training-get"); common_args(p); p.add_argument("--tid", required=True, type=int); p.set_defaults(func=cmd_training_get)
    p = sub.add_parser("training-create"); common_args(p); p.add_argument("--title", required=True); p.add_argument("--description"); p.add_argument("--auth", default="Public"); p.add_argument("--private-pwd"); p.add_argument("--status", type=bool_arg, nargs="?", const=True, default=True); p.add_argument("--rank", type=int); p.set_defaults(func=cmd_training_create)
    p = sub.add_parser("training-update"); common_args(p); p.add_argument("--tid", required=True, type=int); p.add_argument("--title"); p.add_argument("--description"); p.add_argument("--auth"); p.add_argument("--private-pwd"); p.add_argument("--status", type=bool_arg, nargs="?", const=True); p.add_argument("--rank", type=int); p.set_defaults(func=cmd_training_update)
    p = sub.add_parser("training-delete"); common_args(p); p.add_argument("--tid", required=True, type=int); p.set_defaults(func=cmd_training_delete)
    p = sub.add_parser("training-status"); common_args(p); p.add_argument("--tid", required=True, type=int); p.add_argument("--author", required=True); p.add_argument("--status", required=True, type=lambda x: str(x).lower()=="true"); p.set_defaults(func=cmd_training_status)
    p = sub.add_parser("training-problem-add"); common_args(p); p.add_argument("--pid", required=True, type=int); p.add_argument("--tid", required=True, type=int); p.add_argument("--display-id", required=True); p.set_defaults(func=cmd_training_problem_add)
    p = sub.add_parser("training-problem-remove"); common_args(p); p.add_argument("--pid", required=True, type=int); p.add_argument("--tid", required=True, type=int); p.set_defaults(func=cmd_training_problem_remove)
    p = sub.add_parser("training-problem-update"); common_args(p); p.add_argument("--pid", required=True, type=int); p.add_argument("--tid", required=True, type=int); p.add_argument("--display-id"); p.add_argument("--rank", type=int); p.set_defaults(func=cmd_training_problem_update)

    # 用户
    p = sub.add_parser("user-list"); common_args(p); p.add_argument("--limit", type=int, default=20); p.add_argument("--current-page", type=int, default=1); p.add_argument("--only-admin", action="store_true"); p.add_argument("--keyword"); p.set_defaults(func=cmd_user_list)
    p = sub.add_parser("user-edit"); common_args(p); p.add_argument("--uid", required=True); p.add_argument("--username", required=True); p.add_argument("--realname"); p.add_argument("--email"); p.add_argument("--new-password", dest="password"); p.add_argument("--type", type=int); p.add_argument("--status", type=int); p.add_argument("--set-new-pwd", type=bool_arg, nargs="?", const=True); p.set_defaults(func=cmd_user_edit)
    p = sub.add_parser("user-delete"); common_args(p); p.add_argument("--uids", required=True); p.set_defaults(func=cmd_user_delete)
    p = sub.add_parser("user-batch-insert"); common_args(p); p.add_argument("--users-file", required=True); p.set_defaults(func=cmd_user_batch_insert)
    p = sub.add_parser("user-generate"); common_args(p); p.add_argument("--config", required=True); p.set_defaults(func=cmd_user_generate)

    # 团队
    p = sub.add_parser("group-list"); common_args(p); p.add_argument("--limit", type=int, default=20); p.add_argument("--current-page", type=int, default=1); p.add_argument("--keyword"); p.add_argument("--auth", type=int); p.add_argument("--only-mine", action="store_true"); p.set_defaults(func=cmd_group_list)
    p = sub.add_parser("group-get"); common_args(p); p.add_argument("--gid", required=True, type=int); p.set_defaults(func=cmd_group_get)
    p = sub.add_parser("group-create"); common_args(p); p.add_argument("--name", required=True); p.add_argument("--short-name"); p.add_argument("--brief"); p.add_argument("--description"); p.add_argument("--auth", type=int, choices=[1,2,3]); p.add_argument("--visible", type=bool_arg, nargs="?", const=True, default=True); p.add_argument("--code"); p.set_defaults(func=cmd_group_create)
    p = sub.add_parser("group-update"); common_args(p); p.add_argument("--gid", required=True, type=int); p.add_argument("--name"); p.add_argument("--short-name"); p.add_argument("--brief"); p.add_argument("--description"); p.add_argument("--auth", type=int, choices=[1,2,3]); p.add_argument("--visible", type=bool_arg, nargs="?", const=True); p.add_argument("--code"); p.set_defaults(func=cmd_group_update)
    p = sub.add_parser("group-delete"); common_args(p); p.add_argument("--gid", required=True, type=int); p.set_defaults(func=cmd_group_delete)
    p = sub.add_parser("group-member-list"); common_args(p); p.add_argument("--gid", required=True, type=int); p.add_argument("--limit", type=int, default=20); p.add_argument("--current-page", type=int, default=1); p.add_argument("--keyword"); p.add_argument("--auth", type=int); p.set_defaults(func=cmd_group_member_list)
    p = sub.add_parser("group-member-add"); common_args(p); p.add_argument("--gid", required=True, type=int); p.add_argument("--code"); p.add_argument("--reason"); p.set_defaults(func=cmd_group_member_add)
    p = sub.add_parser("group-member-update"); common_args(p); p.add_argument("--gid", required=True, type=int); p.add_argument("--uid", required=True); p.add_argument("--auth", type=int, choices=[3,4,5]); p.add_argument("--reason"); p.set_defaults(func=cmd_group_member_update)
    p = sub.add_parser("group-member-delete"); common_args(p); p.add_argument("--gid", required=True, type=int); p.add_argument("--uid", required=True); p.set_defaults(func=cmd_group_member_delete)

    # 公告
    p = sub.add_parser("announcement-list"); common_args(p); p.add_argument("--limit", type=int, default=20); p.add_argument("--current-page", type=int, default=1); p.set_defaults(func=cmd_announcement_list)
    p = sub.add_parser("announcement-create"); common_args(p); p.add_argument("--title", required=True); p.add_argument("--content", required=True); p.set_defaults(func=cmd_announcement_create)
    p = sub.add_parser("announcement-update"); common_args(p); p.add_argument("--aid", required=True, type=int); p.add_argument("--title", required=True); p.add_argument("--content", required=True); p.set_defaults(func=cmd_announcement_update)
    p = sub.add_parser("announcement-delete"); common_args(p); p.add_argument("--aid", required=True, type=int); p.set_defaults(func=cmd_announcement_delete)

    # 标签
    p = sub.add_parser("tag-create"); common_args(p); p.add_argument("--name", required=True); p.add_argument("--color", default="#1890ff"); p.add_argument("--oj", default="ME"); p.set_defaults(func=cmd_tag_create)
    p = sub.add_parser("tag-update"); common_args(p); p.add_argument("--tid", required=True, type=int); p.add_argument("--name", required=True); p.add_argument("--color", default="#1890ff"); p.add_argument("--oj", default="ME"); p.set_defaults(func=cmd_tag_update)
    p = sub.add_parser("tag-delete"); common_args(p); p.add_argument("--tid", required=True, type=int); p.set_defaults(func=cmd_tag_delete)

    # 评测
    p = sub.add_parser("judge-rejudge"); common_args(p); p.add_argument("--submit-id", required=True, type=int); p.set_defaults(func=cmd_judge_rejudge)
    p = sub.add_parser("judge-manual"); common_args(p); p.add_argument("--submit-id", required=True, type=int); p.add_argument("--status", required=True, type=int); p.add_argument("--score", type=int); p.set_defaults(func=cmd_judge_manual)
    p = sub.add_parser("judge-cancel"); common_args(p); p.add_argument("--submit-id", required=True, type=int); p.set_defaults(func=cmd_judge_cancel)

    args = ap.parse_args()
    if args.dry_run:
        print(f"[dry-run] 命令 {args.cmd} 已解析，未发送任何请求")
        return
    args.func(args)


if __name__ == "__main__":
    main()