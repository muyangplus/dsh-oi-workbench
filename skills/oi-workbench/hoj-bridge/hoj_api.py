#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hoj_api.py —— HOJ（HimitZH/HOJ）REST 客户端。

纯 Python 标准库（urllib + cookiejar），无第三方依赖。
端点与字段来自仓库源码：
    hoj-springboot/DataBackup/src/main/java/top/hcode/hoj/controller/
    hoj-springboot/api/src/main/java/top/hcode/hoj/pojo/

常见用法:
    from hoj_api import HojClient
    oj = HojClient("https://hoj.example.com", "root", "密码")
    langs = oj.get_languages()
    oj.add_problem(payload)
    tid = oj.add_contest({...})
"""

import json
import mimetypes
import os
import uuid
from http.cookiejar import CookieJar
from urllib import error, parse, request

DEFAULT_UA = "dsh-oi-workbench-hoj-bridge/0.2"


class HojError(RuntimeError):
    """HOJ 业务/网络错误。"""


class HojClient:
    def __init__(self, base_url, username=None, password=None, cookie=None,
                 timeout=60, verify=True):
        self.base = base_url.rstrip("/")
        self.timeout = timeout
        self.verify = verify
        self.cookies = CookieJar()
        if not verify:
            # 仅用于自签名内网实例（用户需自行确认安全策略）
            import ssl
            self.ctx = ssl.create_default_context()
            self.ctx.check_hostname = False
            self.ctx.verify_mode = ssl.CERT_NONE
        else:
            self.ctx = None
        handlers = [request.HTTPCookieProcessor(self.cookies)]
        if self.ctx is not None:
            handlers.append(request.HTTPSHandler(context=self.ctx))
        self.opener = request.build_opener(*handlers)
        self.session_cookie = cookie
        if cookie:
            # 不解析，直接原样作为 Cookie 头发送；服务器 Set-Cookie 仍由 cookiejar 管理。
            pass
        elif username and password:
            self.login(username, password)

    # ---------- 基础请求 ----------

    def _url(self, path):
        if path.startswith("http"):
            return path
        return f"{self.base}/{path.lstrip('/')}"

    def _request(self, method, path, params=None, json_body=None,
                 multipart=None, raw=False, timeout=None):
        url = self._url(path)
        if params:
            url += ("&" if "?" in url else "?") + parse.urlencode(
                {k: v for k, v in params.items() if v is not None})
        hdrs = {"User-Agent": DEFAULT_UA}
        if self.session_cookie:
            hdrs["Cookie"] = self.session_cookie
        data = None
        if json_body is not None:
            data = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
            hdrs["Content-Type"] = "application/json; charset=utf-8"
        elif multipart is not None:
            boundary = "----hoj" + uuid.uuid4().hex
            fields = multipart.get("fields") or {}
            file_field = multipart.get("file_field", "file")
            file_path = multipart["file_path"]
            parts = []
            for k, v in fields.items():
                parts.append(
                    f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
                )
            with open(file_path, "rb") as f:
                content = f.read()
            filename = multipart.get("filename") or os.path.basename(file_path)
            ctype = multipart.get("content_type") or mimetypes.guess_type(filename)[0] or "application/octet-stream"
            parts.append(
                (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{file_field}\"; "
                 f"filename=\"{filename}\"\r\nContent-Type: {ctype}\r\n\r\n").encode()
                + content + b"\r\n"
            )
            parts.append(f"--{boundary}--\r\n".encode())
            data = b"".join(parts)
            hdrs["Content-Type"] = f"multipart/form-data; boundary={boundary}"

        req = request.Request(url, data=data, headers=hdrs, method=method.upper())
        try:
            with self.opener.open(req, timeout=timeout or self.timeout) as resp:
                body = resp.read()
                if raw:
                    return resp.status, body, dict(resp.headers)
                text = body.decode("utf-8", "replace")
                try:
                    data = json.loads(text) if text else {}
                except json.JSONDecodeError:
                    data = {"code": -1, "status": "error", "msg": text[:500], "data": None}
                if data.get("status") not in ("success", "SUCCESS", None) or data.get("code") not in (200, None):
                    # 兼容部分直接返回 data 的端点
                    if data.get("code") is not None:
                        raise HojError(f"{method} {path}: {data.get('msg') or data.get('status')} {data}")
                return resp.status, data, dict(resp.headers)
        except error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            try:
                detail = json.loads(body)
                raise HojError(f"{method} {path}: HTTP {e.code} {detail}") from e
            except json.JSONDecodeError:
                raise HojError(f"{method} {path}: HTTP {e.code} {body[:300]}") from e
        except error.URLError as e:
            raise HojError(f"{method} {path}: 网络错误 {e.reason}") from e

    def _request_data(self, method, path, **kwargs):
        status, data, _ = self._request(method, path, **kwargs)
        if isinstance(data, dict) and "data" in data:
            return data.get("data")
        return data

    # ---------- 账号 ----------

    def login(self, username, password):
        self._request_data("POST", "api/admin/login",
                           json_body={"username": username, "password": password})
        return self

    def logout(self):
        return self._request_data("GET", "api/admin/logout")

    def check_login(self):
        return self._request_data("GET", "api/admin/dashboard/get-dashboard-info")

    # ---------- 通用查询 ----------

    def get_languages(self):
        return self._request_data("GET", "api/languages")

    def get_tags(self, oj="ME"):
        return self._request_data("GET", "api/get-all-problem-tags", params={"oj": oj})

    def get_tag_classification(self, oj="ME"):
        return self._request_data("GET", "api/get-problem-tags-and-classification", params={"oj": oj})

    # ---------- 题目 ----------

    def list_problems(self, limit=20, current_page=1, keyword=None, auth=None, oj=None):
        return self._request_data("GET", "api/admin/problem/get-problem-list", params={
            "limit": limit, "currentPage": current_page, "keyword": keyword,
            "auth": auth, "oj": oj,
        })

    def get_problem(self, pid):
        return self._request_data("GET", "api/admin/problem", params={"pid": pid})

    def add_problem(self, problem_dto):
        return self._request_data("POST", "api/admin/problem", json_body=problem_dto)

    def update_problem(self, problem_dto):
        return self._request_data("PUT", "api/admin/problem", json_body=problem_dto)

    def delete_problem(self, pid):
        return self._request_data("DELETE", "api/admin/problem", params={"pid": pid})

    def change_problem_auth(self, problem_obj):
        return self._request_data("PUT", "api/admin/problem/change-problem-auth", json_body=problem_obj)

    def get_problem_cases(self, pid, is_upload=True):
        return self._request_data("GET", "api/admin/problem/get-problem-cases",
                                  params={"pid": pid, "isUpload": str(is_upload).lower()})

    def upload_testcase_zip(self, zip_path, mode="default", gid=None):
        """上传测试数据 zip，返回 {'fileList': [...], 'fileListDir': '...'}。"""
        return self._request_data("POST", "api/file/upload-testcase-zip",
                                  params={"mode": mode, "gid": gid},
                                  multipart={"file_path": zip_path, "file_field": "file"})

    def download_testcase(self, pid, out_path=None):
        status, body, _ = self._request("GET", "api/file/download-testcase",
                                        params={"pid": pid}, raw=True)
        if status != 200:
            raise HojError(f"下载测试数据失败: HTTP {status}")
        filename = out_path or f"problem_{pid}_testcase.zip"
        with open(filename, "wb") as f:
            f.write(body)
        return filename

    def import_hydro_problem(self, zip_path):
        return self._request_data("POST", "api/file/import-hydro-problem",
                                  multipart={"file_path": zip_path, "file_field": "file"})

    def import_hoj_problem(self, zip_path):
        """导入 HOJ 原生题目 zip（后台『导入题目』等价）。"""
        return self._request_data("POST", "api/file/import-problem",
                                  multipart={"file_path": zip_path, "file_field": "file"})

    def export_problem(self, pids, out_path=None):
        """导出题目（root）。pids 为 list。返回 zip 文件路径。"""
        params = [("pid", str(pid)) for pid in pids]
        url = self._url("api/file/export-problem?" + parse.urlencode(params))
        hdrs = {"User-Agent": DEFAULT_UA}
        if self.session_cookie:
            hdrs["Cookie"] = self.session_cookie
        req = request.Request(url, headers=hdrs)
        try:
            with self.opener.open(req, timeout=self.timeout) as resp:
                body = resp.read()
        except error.HTTPError as e:
            raise HojError(f"export-problem: HTTP {e.code} {e.read()[:200]}") from e
        filename = out_path or (("problem_" + "_".join(str(p) for p in pids)) + ".zip")
        with open(filename, "wb") as f:
            f.write(body)
        return filename

    def compile_spj(self, code, language):
        return self._request_data("POST", "api/admin/problem/compile-spj",
                                  json_body={"code": code, "language": language})

    def compile_interactive(self, code, language):
        return self._request_data("POST", "api/admin/problem/compile-interactive",
                                  json_body={"code": code, "language": language})

    def import_remote_problem(self, name, problem_id):
        return self._request_data("GET", "api/admin/problem/import-remote-oj-problem",
                                  params={"name": name, "problemId": problem_id})

    # ---------- 比赛 ----------

    def list_contests(self, limit=20, current_page=1, keyword=None):
        return self._request_data("GET", "api/admin/contest/get-contest-list",
                                  params={"limit": limit, "currentPage": current_page, "keyword": keyword})

    def get_contest(self, cid):
        return self._request_data("GET", "api/admin/contest", params={"cid": cid})

    def add_contest(self, contest_vo):
        return self._request_data("POST", "api/admin/contest", json_body=contest_vo)

    def update_contest(self, contest_vo):
        return self._request_data("PUT", "api/admin/contest", json_body=contest_vo)

    def delete_contest(self, cid):
        return self._request_data("DELETE", "api/admin/contest", params={"cid": cid})

    def clone_contest(self, cid):
        return self._request_data("GET", "api/admin/contest/clone", params={"cid": cid})

    def change_contest_visible(self, cid, uid, visible):
        return self._request_data("PUT", "api/admin/contest/change-contest-visible",
                                  params={"cid": cid, "uid": uid, "visible": str(visible).lower()})

    def list_contest_problems(self, cid, limit=20, current_page=1, keyword=None, problem_type=None, oj=None):
        return self._request_data("GET", "api/admin/contest/get-problem-list", params={
            "limit": limit, "currentPage": current_page, "keyword": keyword,
            "cid": cid, "problemType": problem_type, "oj": oj,
        })

    def get_contest_problem(self, pid):
        return self._request_data("GET", "api/admin/contest/problem", params={"pid": pid})

    def add_contest_problem(self, problem_dto):
        return self._request_data("POST", "api/admin/contest/problem", json_body=problem_dto)

    def update_contest_problem(self, problem_dto):
        return self._request_data("PUT", "api/admin/contest/problem", json_body=problem_dto)

    def delete_contest_problem(self, pid, cid=None):
        params = {"pid": pid}
        if cid is not None:
            params["cid"] = cid
        return self._request_data("DELETE", "api/admin/contest/problem", params=params)

    def set_contest_problem(self, contest_problem):
        return self._request_data("PUT", "api/admin/contest/contest-problem", json_body=contest_problem)

    def add_contest_problem_from_public(self, contest_problem_dto):
        return self._request_data("POST", "api/admin/contest/add-problem-from-public",
                                  json_body=contest_problem_dto)

    def list_contest_announcements(self, cid, limit=20, current_page=1):
        return self._request_data("GET", "api/admin/contest/announcement",
                                  params={"limit": limit, "currentPage": current_page, "cid": cid})

    def add_contest_announcement(self, announcement_dto):
        return self._request_data("POST", "api/admin/contest/announcement", json_body=announcement_dto)

    def update_contest_announcement(self, announcement_dto):
        return self._request_data("PUT", "api/admin/contest/announcement", json_body=announcement_dto)

    def delete_contest_announcement(self, aid):
        return self._request_data("DELETE", "api/admin/contest/announcement", params={"aid": aid})

    # ---------- 训练 ----------

    def list_trainings(self, limit=20, current_page=1, keyword=None):
        return self._request_data("GET", "api/admin/training/get-training-list",
                                  params={"limit": limit, "currentPage": current_page, "keyword": keyword})

    def get_training(self, tid):
        return self._request_data("GET", "api/admin/training", params={"tid": tid})

    def add_training(self, training_dto):
        return self._request_data("POST", "api/admin/training", json_body=training_dto)

    def update_training(self, training_dto):
        return self._request_data("PUT", "api/admin/training", json_body=training_dto)

    def delete_training(self, tid):
        return self._request_data("DELETE", "api/admin/training", params={"tid": tid})

    def change_training_status(self, tid, author, status):
        return self._request_data("PUT", "api/admin/training/change-training-status",
                                  params={"tid": tid, "author": author, "status": str(status).lower()})

    def list_training_problems(self, tid, limit=20, current_page=1, keyword=None, query_existed=False):
        return self._request_data("GET", "api/admin/training/get-problem-list", params={
            "limit": limit, "currentPage": current_page, "keyword": keyword,
            "queryExisted": str(query_existed).lower(), "tid": tid,
        })

    def add_training_problem_from_public(self, training_problem_dto):
        return self._request_data("POST", "api/admin/training/add-problem-from-public",
                                  json_body=training_problem_dto)

    def update_training_problem(self, training_problem):
        return self._request_data("PUT", "api/admin/training/problem", json_body=training_problem)

    def delete_training_problem(self, pid, tid=None):
        params = {"pid": pid}
        if tid is not None:
            params["tid"] = tid
        return self._request_data("DELETE", "api/admin/training/problem", params=params)

    # ---------- 用户 ----------

    def list_users(self, limit=20, current_page=1, only_admin=False, keyword=None):
        return self._request_data("GET", "api/admin/user/get-user-list", params={
            "limit": limit, "currentPage": current_page,
            "onlyAdmin": str(only_admin).lower(), "keyword": keyword,
        })

    def edit_user(self, edit_dto):
        return self._request_data("PUT", "api/admin/user/edit-user", json_body=edit_dto)

    def delete_users(self, uid_list):
        return self._request_data("DELETE", "api/admin/user/delete-user",
                                  json_body={"ids": uid_list})

    def insert_batch_users(self, users):
        """users: [[username,password,email,...], ...]"""
        return self._request_data("POST", "api/admin/user/insert-batch-user",
                                  json_body={"users": users})

    def generate_users(self, params):
        return self._request_data("POST", "api/admin/user/generate-user", json_body=params)

    # ---------- 团队 ----------

    def list_groups(self, limit=20, current_page=1, keyword=None, auth=None, only_mine=False):
        return self._request_data("GET", "api/get-group-list", params={
            "limit": limit, "currentPage": current_page, "keyword": keyword,
            "auth": auth, "onlyMine": str(only_mine).lower(),
        })

    def get_group(self, gid):
        return self._request_data("GET", "api/get-group-detail", params={"gid": gid})

    def add_group(self, group_obj):
        return self._request_data("POST", "api/group", json_body=group_obj)

    def update_group(self, group_obj):
        return self._request_data("PUT", "api/group", json_body=group_obj)

    def delete_group(self, gid):
        return self._request_data("DELETE", "api/group", params={"gid": gid})

    def list_group_members(self, gid, limit=20, current_page=1, keyword=None, auth=None):
        return self._request_data("GET", "api/group/get-member-list", params={
            "limit": limit, "currentPage": current_page, "keyword": keyword,
            "auth": auth, "gid": gid,
        })

    def list_group_applications(self, gid, limit=20, current_page=1, keyword=None, auth=None):
        return self._request_data("GET", "api/group/get-apply-list", params={
            "limit": limit, "currentPage": current_page, "keyword": keyword,
            "auth": auth, "gid": gid,
        })

    def add_group_member(self, gid, code=None, reason=None):
        return self._request_data("POST", "api/group/member",
                                  params={"gid": gid, "code": code, "reason": reason})

    def update_group_member(self, group_member):
        return self._request_data("PUT", "api/group/member", json_body=group_member)

    def delete_group_member(self, uid, gid):
        return self._request_data("DELETE", "api/group/member", params={"uid": uid, "gid": gid})

    # ---------- 公告 ----------

    def list_announcements(self, limit=20, current_page=1):
        return self._request_data("GET", "api/admin/announcement",
                                  params={"limit": limit, "currentPage": current_page})

    def add_announcement(self, announcement):
        return self._request_data("POST", "api/admin/announcement", json_body=announcement)

    def update_announcement(self, announcement):
        return self._request_data("PUT", "api/admin/announcement", json_body=announcement)

    def delete_announcement(self, aid):
        return self._request_data("DELETE", "api/admin/announcement", params={"aid": aid})

    # ---------- 标签 ----------

    def add_tag(self, tag):
        return self._request_data("POST", "api/admin/tag", json_body=tag)

    def update_tag(self, tag):
        return self._request_data("PUT", "api/admin/tag", json_body=tag)

    def delete_tag(self, tid):
        return self._request_data("DELETE", "api/admin/tag", params={"tid": tid})

    # ---------- 评测 ----------

    def rejudge(self, submit_id):
        return self._request_data("GET", "api/admin/judge/rejudge", params={"submitId": submit_id})

    def rejudge_contest_problem(self, cid, pid):
        return self._request_data("GET", "api/admin/judge/rejudge-contest-problem",
                                  params={"cid": cid, "pid": pid})

    def manual_judge(self, submit_id, status, score=None):
        params = {"submitId": submit_id, "status": status}
        if score is not None:
            params["score"] = score
        return self._request_data("GET", "api/admin/judge/manual-judge", params=params)

    def cancel_judge(self, submit_id):
        return self._request_data("GET", "api/admin/judge/cancel-judge", params={"submitId": submit_id})

    # ---------- 系统 ----------

    def get_dashboard_info(self):
        return self._request_data("GET", "api/admin/dashboard/get-dashboard-info")

    def get_service_info(self):
        return self._request_data("GET", "api/admin/config/get-service-info")

    def get_judge_service_info(self):
        return self._request_data("GET", "api/admin/config/get-judge-service-info")


if __name__ == "__main__":
    print("hoj_api.py: import as a module; see manage_hoj.py for CLI.")