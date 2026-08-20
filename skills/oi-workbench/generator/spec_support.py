#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
spec_support.py —— spec.json 的 io / judge 解析共享工具（批次 2，v0.1.2）。

统一约定（新字段，同时兼容旧字段）：
    "io":    { "type": "standard" | "file", "input": "xxx.in", "output": "xxx.out" }
    "judge": {
        "type": "default" | "subtask" | "interactive" | "communication",
        "mode": "traditional" | "subtask" | "acm",   # 计分语义
        "spj": bool,
        "checker": "spj.cpp",
        "interactor": "interactor.cpp"
    }

旧字段兼容：
    "fileIO": {"input": "...", "output": "..."}         等效 io.type=file
    "judge.type": "special"                             等效 spj=true（配合 checker）
"""


def resolve_io(spec):
    """返回 (mode, input_name, output_name)。mode ∈ standard|file。"""
    io = spec.get("io") or {}
    if isinstance(io, dict) and io.get("type") == "file":
        return "file", io.get("input") or "problem.in", io.get("output") or "problem.out"
    fio = spec.get("fileIO")
    if isinstance(fio, dict) and (fio.get("input") or fio.get("output")):
        return "file", fio.get("input") or "problem.in", fio.get("output") or "problem.out"
    return "standard", None, None


def resolve_judge(spec):
    """返回归一化的 judge 字典：{type, mode, spj, checker, interactor}。"""
    judge = spec.get("judge") or {}
    if not isinstance(judge, dict):
        judge = {}
    judge = dict(judge)
    jtype = judge.get("type") or "default"
    if jtype == "special":
        jtype = "default"
        judge["spj"] = True
    if jtype == "communication":
        jtype = "interactive"          # 本地/打包按 interactive 处理
    if jtype == "interactive":
        judge["spj"] = True
    spj = bool(judge.get("spj"))
    return {
        "type": jtype,
        "mode": judge.get("mode"),
        "spj": spj,
        "checker": judge.get("checker"),
        "interactor": judge.get("interactor"),
    }


def resolve_mode(spec):
    """返回计分模式：traditional | subtask | acm。"""
    mode = (spec.get("judge") or {}).get("mode")
    if mode in ("traditional", "subtask", "acm"):
        return mode
    if str(spec.get("type", "oi")).lower() in ("acm", "0", "false"):
        return "acm"
    if spec.get("subtasks"):
        return "subtask"
    return "traditional"
