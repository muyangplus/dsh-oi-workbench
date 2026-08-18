#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hydro_api.py —— Hydro OJ REST 客户端（纯 Python 标准库 urllib，无第三方依赖）。

端点与字段全部来自 Hydro 官方源码（packages/hydrooj/src/handler/*.ts），
对应当前 master；若你的 Hydro 版本较旧，字段可能略有差异，以实例实际行为为准。

快速开始:
    from hydro_api import HydroClient
    oj = HydroClient("https://hydro.example.com", "root", "密码")   # 自动登录（或传 cookie）
    oj.create_problem(title="A+B", content="# A+B", pid="P1000", tag=["模拟"])
    oj.upload_testdata("P1000", "problem.zip")    # zip 自动解压进 testdata
    tid = oj.create_contest("OI 模拟赛 1", "2025-01-01", "08:30", 3.5, rule="oi", pids=[1000])
"""

import json
import mimetypes
import os
import uuid
from urllib import error, parse, request

DEFAULT_UA = "oi-workbench-hydro-bridge/1.0"


class HydroError(RuntimeError):
    """Hydro 返回的业务错误（HTTP 错误页 / JSON 错误体）。"""


class HydroClient:
    def __init__(self, base_url, username=None, password=None, cookie=None, domain="system",
                 timeout=60, verify=True):
        self.base = base_url.rstrip("/")
        self.domain = domain
        self.timeout = timeout
        self.verify = verify
        self.session = {}
        if cookie:
            self.session["Cookie"] = cookie
        elif username and password:
            self.login(username, password)

    # ---------- 基础请求 ----------

    def _url(self, path):
        if path.startswith("http"):
            return path
        path = path.lstrip("/")
        if path.startswith("d/"):
            return f"{self.base}/{path}"
        return f"{self.base}/d/{self.domain}/{path}"

    def _request(self, method, path, data=None, headers=None, raw=False, timeout=None):
        url = self._url(path)
        hdrs = {"User-Agent": DEFAULT_UA, **self.session}
        if headers:
            hdrs.update(headers)
        body = None
        if data is not None:
            if isinstance(data, dict):
                body = parse.urlencode(data).encode()
                hdrs.setdefault("Content-Type", "application/x-www-form-urlencoded")
            else:  # bytes
                body = data
        req = request.Request(url, data=body, headers=hdrs, method=method)
        try:
            with request.urlopen(req, timeout=timeout or self.timeout) as resp:
                if raw:
                    return resp.status, resp.read(), dict(resp.headers)
                text = resp.read().decode("utf-8", "replace")
                return resp.status, text, dict(resp.headers)
        except error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            if e.headers.get("Content-Type", "").startswith("application/json"):
                try:
                    detail = json.loads(body)
                    raise HydroError(f"{path}: HTTP {e.code} {detail}") from e
                except json.JSONDecodeError:
                    pass
            raise HydroError(f"{path}: HTTP {e.code} {body[:300]}") from e
        except error.URLError as e:
            raise HydroError(f"{path}: 网络错误 {e.reason}") from e

    def _json(self, method, path, data=None, headers=None):
        status, text, hdrs = self._request(method, path, data, headers)
        try:
            return json.loads(text) if text else {}
        except json.JSONDecodeError:
            return {"_raw": text[:500], "_status": status}

    def _multipart(self, method, path, fields, file_field, file_path, filename=None):
        """multipart/form-data 上传。file_field: 表单字段名（Hydro 用 'file'）。"""
        boundary = "----oiwb" + uuid.uuid4().hex
        parts = []
        for k, v in (fields or {}).items():
            parts.append(
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
            )
        with open(file_path, "rb") as f:
            content = f.read()
        fn = filename or os.path.basename(file_path)
        ctype = mimetypes.guess_type(fn)[0] or "application/octet-stream"
        parts.append(
            (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{file_field}\"; "
             f"filename=\"{fn}\"\r\nContent-Type: {ctype}\r\n\r\n").encode() + content + b"\r\n"
        )
        parts.append(f"--{boundary}--\r\n".encode())
        body = b"".join(parts)
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
        return self._json(method, path, body, headers)

    # ---------- 账号 ----------

    def login(self, username, password):
        data = {"uname": username, "password": password, "rememberme": "1"}
        status, text, headers = self._request("POST", "login", data)
        cookies = headers.get_all("Set-Cookie") or []
        if not cookies:
            raise HydroError(f"登录失败: HTTP {status} {text[:200]}")
        pairs = []
        for c in cookies:
            pair = c.split(";", 1)[0]
            if pair and pair not in pairs:
                pairs.append(pair)
        self.session["Cookie"] = "; ".join(pairs)
        return self

    def set_cookie(self, cookie_header):
        self.session["Cookie"] = cookie_header
        return self

    # ---------- 题目 ----------

    def create_problem(self, title, content="", pid="", hidden=False, difficulty=0, tag=None):
        """创建题目，返回 docId（数字）或自定义 pid。字段见 ProblemCreateHandler。"""
        data = {
            "title": title,
            "content": content,
            "hidden": "1" if hidden else "0",
            "difficulty": str(difficulty),
            "tag": ",".join(tag or []),
        }
        if pid:
            data["pid"] = pid
        res = self._json("POST", "problem/create", data)
        if not res.get("pid"):
            raise HydroError(f"创建题目失败: {res}")
        return res["pid"]

    def edit_problem(self, pid, title=None, content=None, new_pid=None, hidden=None, difficulty=None, tag=None):
        """编辑题目（ProblemEditHandler，POST /p/{pid}/edit）。"""
        data = {}
        if title is not None:
            data["title"] = title
        if content is not None:
            data["content"] = content
        if new_pid is not None:
            data["pid"] = new_pid
        if hidden is not None:
            data["hidden"] = "1" if hidden else "0"
        if difficulty is not None:
            data["difficulty"] = str(difficulty)
        if tag is not None:
            data["tag"] = ",".join(tag)
        if not data:
            return
        return self._json("POST", f"p/{pid}/edit", data)

    def upload_testdata(self, pid, zip_path, filename=None):
        """上传测试数据（zip 自动解压进 testdata）。等价于网页『上传数据』。"""
        return self._multipart(
            "POST", f"p/{pid}/files",
            {"operation": "upload_file", "type": "testdata"},
            "file", zip_path, filename,
        )

    def upload_file(self, pid, file_path, filename=None):
        """上传单个文件到 testdata（非 zip）。"""
        return self._multipart(
            "POST", f"p/{pid}/files",
            {"operation": "upload_file", "type": "testdata"},
            "file", file_path, filename,
        )

    def list_testdata(self, pid):
        """GET /p/{pid}/files —— 返回 testdata 文件列表（名称/大小）。"""
        res = self._json("GET", f"p/{pid}/files")
        return res.get("testdata", res)

    def download_testdata_file(self, pid, filename, out_path=None):
        """GET /p/{pid}/file/{filename}?type=testdata —— 下载数据文件。"""
        status, body, _ = self._request("GET", f"p/{pid}/file/{parse.quote(filename)}?type=testdata", raw=True)
        if status != 200:
            raise HydroError(f"下载 {filename}: HTTP {status}")
        if out_path:
            with open(out_path, "wb") as f:
                f.write(body)
            return out_path
        return body

    # ---------- 比赛 ----------

    def create_contest(self, title, begin_at_date, begin_at_time, duration_hours, content="",
                       rule="oi", pids=None, rated=False, auto_hide=False, langs=None, lock_minutes=None):
        """创建比赛。rule: oi|acm|ioi|strictioi|homework|ledo。
        pids: 题目 docId 列表（如 [1000, 1001]）。
        字段见 ContestEditHandler.postUpdate（operation=update）。"""
        data = {
            "operation": "update",
            "title": title,
            "content": content,
            "beginAtDate": begin_at_date,   # YYYY-MM-DD（服务器本地时区）
            "beginAtTime": begin_at_time,   # HH:mm
            "duration": str(duration_hours),
            "rule": rule,
            "pids": ",".join(str(p) for p in (pids or [])),
            "rated": "1" if rated else "0",
            "autoHide": "1" if auto_hide else "0",
        }
        if langs:
            data["langs"] = ",".join(langs)
        if lock_minutes:
            data["lock"] = str(lock_minutes)
        res = self._json("POST", "contest/create", data)
        if not res.get("tid"):
            raise HydroError(f"创建比赛失败: {res}")
        return res["tid"]

    def edit_contest(self, tid, **kwargs):
        """编辑比赛，字段同 create_contest。"""
        data = {"operation": "update", **{k: str(v) for k, v in kwargs.items()}}
        return self._json("POST", f"contest/{tid}/edit", data)

    def contest_add_users(self, tid, uids, unrank=False):
        """把用户加入比赛（operation=addUser）。uids: 数字 uid 列表。"""
        return self._json("POST", f"contest/{tid}/user", {
            "operation": "addUser", "uids": ",".join(str(u) for u in uids), "unrank": "1" if unrank else "0",
        })

    def contest_remove_user(self, tid, uid):
        """移除比赛用户（operation=removeUser，仅未开始时可移除）。"""
        return self._json("POST", f"contest/{tid}/user", {"operation": "removeUser", "uid": str(uid)})

    # ---------- 团队（域内分组）----------

    def list_groups(self):
        """GET /domain/group —— 域内团队列表。"""
        res = self._json("GET", "domain/group")
        return res.get("groups", res)

    def create_group(self, name, uids=None):
        """创建/更新团队（operation=update：不存在则创建，存在则覆盖成员）。"""
        return self._json("POST", "domain/group", {
            "operation": "update", "name": name, "uids": ",".join(str(u) for u in (uids or [])),
        })

    def delete_group(self, name):
        """删除团队（operation=del）。"""
        return self._json("POST", "domain/group", {"operation": "del", "name": name})
