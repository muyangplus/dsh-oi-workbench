#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hoj_ui.py —— HOJ 外部管理 UI（Python 标准库 HTTP 服务）。

替代 DSH 内部 render_ui：启动一个本地/局域网 Web UI，
由 Python 服务端代理 HOJ API，避免浏览器 file:// 与 CORS 问题。

用法:
    python ui/hoj_ui.py --base https://hoj.example.com --host 0.0.0.0 --port 8080

访问:
    http://localhost:8080/

功能:
    - 静态页面: ui/hoj-admin.html
    - API 代理: /api/* -> <HOJ_BASE>/api/*
    - 服务端保存 HOJ Cookie，刷新页面后仍可保持登录
    - 配置保存到 ~/.dsh-oi-workbench/hoj_config.json
"""

import argparse
import http.cookiejar
import json
import os
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

UI_DIR = Path(__file__).resolve().parent
CONFIG_DIR = Path.home() / ".dsh-oi-workbench"
CONFIG_FILE = CONFIG_DIR / "hoj_config.json"
COOKIE_FILE = CONFIG_DIR / "hoj_cookies.txt"

DEFAULT_BASE = "https://hoj.example.com"


def load_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_config(config):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


class HojProxyHandler(BaseHTTPRequestHandler):
    server_version = "hoj-ui/0.1"

    # ---------- 配置 ----------

    @property
    def base_url(self):
        return self.server.base_url.rstrip("/")

    def _send_json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, code, text, content_type="text/plain; charset=utf-8"):
        body = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ---------- 静态页面 ----------

    def _serve_index(self):
        index = UI_DIR / "hoj-admin.html"
        if not index.exists():
            self._send_text(500, "hoj-admin.html not found")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(index.stat().st_size))
        self.end_headers()
        with open(index, "rb") as f:
            self.wfile.write(f.read())

    # ---------- 代理 ----------

    def _proxy(self, method):
        if not self.base_url:
            self._send_json(400, {"error": "HOJ base URL 未配置，请先通过 /api/config 设置"})
            return
        path = self.path
        url = self.base_url + path
        headers = {k: v for k, v in self.headers.items() if k.lower() in (
            "content-type", "accept", "user-agent", "cookie", "x-requested-with")}
        data = None
        if method in ("POST", "PUT", "PATCH"):
            length = int(self.headers.get("Content-Length") or 0)
            data = self.rfile.read(length) if length else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with self.server.opener.open(req, timeout=60) as resp:
                body = resp.read()
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() in ("content-type", "content-length", "set-cookie"):
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(body)
                self.server.save_cookies()
        except urllib.error.HTTPError as e:
            body = e.read()
            self.send_response(e.code)
            for k, v in e.headers.items():
                if k.lower() in ("content-type", "content-length", "set-cookie"):
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)
            self.server.save_cookies()
        except Exception as e:
            self._send_json(502, {"error": str(e)})

    # ---------- 配置接口 ----------

    def _handle_config_get(self):
        self._send_json(200, {"base": self.base_url})

    def _handle_config_post(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            data = {}
        base = (data.get("base") or DEFAULT_BASE).strip().rstrip("/")
        self.server.base_url = base
        save_config({"base": base})
        self._send_json(200, {"base": base})

    # ---------- HTTP 方法 ----------

    def do_GET(self):
        if self.path == "/":
            self._serve_index()
        elif self.path == "/api/config":
            self._handle_config_get()
        elif self.path.startswith("/api/"):
            self._proxy("GET")
        else:
            self._send_text(404, "Not Found")

    def do_POST(self):
        if self.path == "/api/config":
            self._handle_config_post()
        elif self.path.startswith("/api/"):
            self._proxy("POST")
        else:
            self._send_text(404, "Not Found")

    def do_PUT(self):
        if self.path.startswith("/api/"):
            self._proxy("PUT")
        else:
            self._send_text(404, "Not Found")

    def do_DELETE(self):
        if self.path.startswith("/api/"):
            self._proxy("DELETE")
        else:
            self._send_text(404, "Not Found")

    def log_message(self, fmt, *args):
        sys.stderr.write("[hoj-ui] %s - %s\n" % (self.address_string(), fmt % args))


def main():
    ap = argparse.ArgumentParser(description="HOJ 外部管理 UI")
    ap.add_argument("--base", default=None, help="HOJ 实例地址，如 https://hoj.example.com")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=6163)
    args = ap.parse_args()

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config = load_config()
    base = (args.base or config.get("base") or DEFAULT_BASE).rstrip("/")
    save_config({"base": base})

    jar = http.cookiejar.MozillaCookieJar(str(COOKIE_FILE))
    if COOKIE_FILE.exists():
        try:
            jar.load(ignore_discard=True, ignore_expires=True)
        except Exception:
            pass
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    class Server(ThreadingHTTPServer):
        pass

    Server.base_url = base
    Server.opener = opener
    Server.jar = jar

    def save_cookies(self):
        try:
            self.jar.save(ignore_discard=True, ignore_expires=True)
        except Exception:
            pass

    Server.save_cookies = save_cookies
    server = Server((args.host, args.port), HojProxyHandler)
    print(f"[ok] HOJ UI 已启动: http://{args.host}:{args.port}")
    print(f"[ok] 代理目标: {base}")
    print("[info] 按 Ctrl+C 停止")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[ok] 已停止")
        server.server_close()


if __name__ == "__main__":
    main()