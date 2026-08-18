#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publish_problem.py —— 把 OI 工作台题目发布到 HOJ（HimitZH/HOJ）。

用法:
    # 方式一：先生成 HOJ 导入 zip，再导入（等价后台『导入题目』，需 root）
    python hoj-bridge\\publish_problem.py --base https://hoj.example.com \
        --user root --password 密码 --zip P1001-hoj.zip

    # 方式二：直接给题目目录，自动打包并导入
    python hoj-bridge\\publish_problem.py --base ... --user ... --password ... \
        --problem-dir examples\\demo

    # 方式三：通过 admin API 直传（不需 root 的后台导入权限，需要 problem_admin/admin）
    python hoj-bridge\\publish_problem.py --base ... --user ... --password ... \
        --problem-dir examples\\demo --direct

安全提示：
    - 不要明文把密码写进聊天/脚本；建议用环境变量 HOJ_PASSWORD 或 --cookie。
    - 登录凭据只经命令行参数/环境变量/网页 Cookie。
"""

import argparse
import os
import subprocess
import sys
import tempfile
import zipfile


def build_hoj_zip(problem_dir, out_zip):
    script = os.path.join(os.path.dirname(__file__), "..", "generator", "build_hoj_package.py")
    cmd = [sys.executable, script, problem_dir, "--out", out_zip]
    cp = subprocess.run(cmd, capture_output=True, text=True)
    if cp.returncode != 0:
        print(cp.stdout, file=sys.stderr)
        print(cp.stderr, file=sys.stderr)
        sys.exit("HOJ 打包失败")
    print(cp.stdout.strip())
    return out_zip


def read_json_from_zip(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        names = [n for n in z.namelist() if n.endswith(".json") and "/" not in n]
        if not names:
            return None
        import json
        return json.loads(z.read(names[0]).decode("utf-8"))


def make_testcase_zip(problem_dir, out_zip):
    data_dir = os.path.join(problem_dir, "data")
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(data_dir):
            for f in files:
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, data_dir).replace("\\", "/"))
    return out_zip


def direct_publish(oj, problem_dir, args):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generator"))
    from build_hoj_package import (build_case_list, build_hoj_payload, data_pairs,
                                   load_spec, validate_spec)

    pdir = os.path.normpath(problem_dir)
    spec = load_spec(pdir)
    cases = build_case_list(spec, data_pairs(os.path.join(pdir, "data")))
    errors = validate_spec(spec, cases, os.path.join(pdir, "data"))
    if errors:
        for e in errors:
            print(f"[error] {e}", file=sys.stderr)
        sys.exit("spec/数据校验失败")
    payload, ordered = build_hoj_payload(spec, cases, pdir)
    if args.dry_run:
        import json
        print("[dry-run] 将直接创建题目（admin API）")
        print(json.dumps({"problemId": payload["problem"]["problemId"],
                          "title": payload["problem"]["title"],
                          "type": "OI" if payload["problem"]["type"] == 1 else "ACM",
                          "judgeMode": payload["judgeMode"],
                          "judgeCaseMode": payload["problem"]["judgeCaseMode"],
                          "samples": len(ordered)}, ensure_ascii=False, indent=2))
        return None

    with tempfile.TemporaryDirectory(prefix="hoj-tc-") as tmp:
        tc_zip = os.path.join(tmp, "testcase.zip")
        make_testcase_zip(pdir, tc_zip)
        upload = oj.upload_testcase_zip(tc_zip, mode=payload["judgeCaseMode"], gid=args.gid)
        file_list = upload.get("fileList") or payload["samples"]
        file_dir = upload.get("fileListDir")
        if not file_dir:
            sys.exit("HOJ 未返回 fileListDir，上传测试数据失败")

        # 语言名称 -> id
        languages = []
        lang_map = {x.get("name"): x for x in (oj.get_languages() or [])}
        for name in payload.get("languages") or ["C++"]:
            lang = lang_map.get(name)
            if lang:
                languages.append({"id": lang.get("id"), "name": lang.get("name")})
            else:
                languages.append({"name": name})

        # tag 名 -> id；未找到的名称交给后端创建
        tags = []
        tag_list = oj.get_tags() or []
        tag_map = {(x.get("name"), x.get("oj") or "ME"): x for x in tag_list}
        for name in payload.get("tags") or []:
            tag = tag_map.get((name, "ME")) or tag_map.get((name, None))
            if tag:
                tags.append({"id": tag.get("id"), "name": tag.get("name")})
            else:
                tags.append({"name": name, "oj": "ME"})

        problem = dict(payload["problem"])
        problem.pop("id", None)
        # 与 uploadTestcaseZip 返回的 fileList 对齐，保证文件名一致
        samples = []
        for fl in file_list:
            entry = {"input": fl["input"], "output": fl["output"]}
            if payload["problem"]["type"] == 1:
                score = next((c.get("score") for c in ordered if c.get("input") == fl["input"]), None)
                if score is None:
                    score = 100 // max(1, len(file_list))
                entry["score"] = score
            if payload["judgeCaseMode"] in ("subtask_lowest", "subtask_average"):
                entry["groupNum"] = next((c.get("groupNum") for c in ordered if c.get("input") == fl["input"]), 1)
            samples.append(entry)

        dto = {
            "problem": problem,
            "samples": samples,
            "isUploadTestCase": True,
            "uploadTestcaseDir": file_dir,
            "judgeMode": payload["judgeMode"],
            "changeModeCode": False,
            "changeJudgeCaseMode": False,
            "languages": languages,
            "tags": tags,
            "codeTemplates": payload.get("codeTemplates") or [],
        }
        oj.add_problem(dto)
        print(f"[ok] 已创建题目（direct API）: {problem.get('problemId')} -> {oj.base}")
        return problem.get("problemId")


def main():
    ap = argparse.ArgumentParser(description="发布题目到 HOJ")
    ap.add_argument("--base", required=True)
    ap.add_argument("--user", default=None)
    ap.add_argument("--password", default=None, help="或用环境变量 HOJ_PASSWORD")
    ap.add_argument("--cookie", default=None)
    ap.add_argument("--zip", default=None, help="HOJ 导入 zip（已由 build_hoj_package.py 生成）")
    ap.add_argument("--hydro-zip", default=None, help="Hydro zip，通过 /api/file/import-hydro-problem 导入")
    ap.add_argument("--problem-dir", default=None, help="题目目录（自动打包为 HOJ zip）")
    ap.add_argument("--direct", action="store_true", help="不用后台导入接口，改用 admin API 直传")
    ap.add_argument("--gid", type=int, default=None, help="团队 ID（可选）")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    password = args.password or os.environ.get("HOJ_PASSWORD")
    if not args.cookie and not (args.user and password):
        sys.exit("需要 --user/--password（或环境变量 HOJ_PASSWORD）或 --cookie")
    if args.hydro_zip and args.zip:
        sys.exit("--zip 与 --hydro-zip 不能同时使用")
    if not (args.zip or args.hydro_zip or args.problem_dir):
        sys.exit("需要 --zip / --hydro-zip / --problem-dir 之一")

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from hoj_api import HojClient

    oj = None
    if not args.dry_run:
        oj = HojClient(args.base, username=args.user if not args.cookie else None,
                       password=password if not args.cookie else None,
                       cookie=args.cookie)
        if not args.cookie:
            print(f"[ok] 已登录 {args.user}")
    else:
        print("[dry-run] 不登录、不发送请求")

    if args.dry_run and not args.problem_dir:
        print("[dry-run] 未发送任何请求")
        return

    if args.problem_dir and args.direct:
        direct_publish(oj, args.problem_dir, args)
        return

    if args.problem_dir:
        with tempfile.TemporaryDirectory(prefix="hoj-pub-") as tmp:
            zip_path = os.path.join(tmp, "problem_hoj.zip")
            build_hoj_zip(args.problem_dir, zip_path)
            if args.dry_run:
                print(f"[dry-run] 将导入 {zip_path}")
                return
            oj.import_hoj_problem(zip_path)
        print("[ok] 已通过 /api/file/import-problem 导入")
        return

    if args.hydro_zip:
        if args.dry_run:
            print(f"[dry-run] 将导入 Hydro zip: {args.hydro_zip}")
            return
        oj.import_hydro_problem(args.hydro_zip)
        print("[ok] 已通过 /api/file/import-hydro-problem 导入")
        return

    if args.zip:
        if args.dry_run:
            print(f"[dry-run] 将导入 HOJ zip: {args.zip}")
            return
        # 若是 HOJ 原生 zip（含 problem_*.json），走 import-problem；否则提示
        payload = read_json_from_zip(args.zip)
        if payload is None:
            sys.exit("zip 中未找到 problem_*.json，请先用 build_hoj_package.py 生成 HOJ 包")
        oj.import_hoj_problem(args.zip)
        print("[ok] 已导入:", payload.get("problem", {}).get("problemId", args.zip))


if __name__ == "__main__":
    main()