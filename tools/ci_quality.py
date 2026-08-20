#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ci_quality.py —— CI 代码质量检查（仅 Python 标准库，无需 g++）。

覆盖（决定 CI 是否放行）：
  1. 版本一致性：package.json version == version-records/VERSION.md 当前版本，
     且 version-records/changelog/v<version>.md 存在；
  2. spec_support：io（新字段 / 旧 fileIO / 缺省）、judge（special→spj、interactive、
     checker）、mode（显式 / type=acm / subtasks / 缺省）解析断言；
  3. build_package 的 config.yaml 映射（纯函数）：file IO 输出 inputFile/outputFile；
     spj 输出 checker/testlib；subtasks 输出 subtasks；
  4. ui/user_content.py：--help、kb validate（空数据根）、ref validate 一个内置参考题；
  5. generator 打包器 --check 一个内置参考题（build_package / build_hoj_package）。

退出码 0 = 全绿。
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parent.parent               # tools/ -> 仓库根
SKILL = REPO / "skills" / "oi-workbench"
GEN = SKILL / "generator"
sys.path.insert(0, str(GEN))

failures = []


def check(name, fn):
    try:
        fn()
        print("[ok] %s" % name)
    except AssertionError as e:
        failures.append(name)
        print("[FAIL] %s: %s" % (name, e))
    except Exception as e:  # noqa: BLE001 —— CI 报告用
        failures.append(name)
        print("[FAIL] %s: %s: %s" % (name, type(e).__name__, e))


def version_consistency():
    pkg = json.loads((REPO / "package.json").read_text(encoding="utf-8"))
    ver = str(pkg["version"])
    vm = (REPO / "version-records" / "VERSION.md").read_text(encoding="utf-8")
    assert ("| 当前版本（dev 仓库） | %s |" % ver) in vm, "VERSION.md 未记录当前版本 %s" % ver
    cl = REPO / "version-records" / "changelog" / ("v%s.md" % ver)
    assert cl.is_file(), "缺少 changelog/v%s.md" % ver


def spec_io_check():
    from spec_support import resolve_io
    assert resolve_io({"io": {"type": "file", "input": "a.in", "output": "a.out"}}) == ("file", "a.in", "a.out")
    assert resolve_io({"fileIO": {"input": "b.in", "output": "b.out"}}) == ("file", "b.in", "b.out")
    assert resolve_io({"io": {"type": "standard"}})[0] == "standard"
    assert resolve_io({})[0] == "standard"


def spec_judge_check():
    from spec_support import resolve_judge
    j = resolve_judge({"judge": {"type": "special", "checker": "spj.cpp"}})
    assert j["spj"] is True and j["checker"] == "spj.cpp" and j["type"] == "default"
    assert resolve_judge({"judge": {"spj": True}})["spj"] is True
    assert resolve_judge({"judge": {"type": "interactive", "interactor": "i.cpp"}})["interactor"] == "i.cpp"
    assert resolve_judge({})["spj"] is False


def spec_mode_check():
    from spec_support import resolve_mode
    assert resolve_mode({"judge": {"mode": "acm"}}) == "acm"
    assert resolve_mode({"judge": {"mode": "subtask"}}) == "subtask"
    assert resolve_mode({"type": "acm"}) == "acm"
    assert resolve_mode({"subtasks": [{"score": 100, "cases": []}]}) == "subtask"
    assert resolve_mode({}) == "traditional"


def config_mapping_check():
    import build_package
    cfg = build_package.build_config_yaml(
        {"title": "t", "io": {"type": "file", "input": "a.in", "output": "a.out"}}, ["1.in", "2.in"], None)
    assert "inputFile: a.in" in cfg and "outputFile: a.out" in cfg, cfg
    cfg2 = build_package.build_config_yaml(
        {"title": "t", "judge": {"spj": True, "checker": "spj.cpp"}}, ["1.in", "2.in"], None)
    assert "checker_type: testlib" in cfg2 and "checker: spj.cpp" in cfg2, cfg2
    cfg3 = build_package.build_config_yaml(
        {"title": "t", "subtasks": [{"score": 40, "cases": [{"input": "1.in", "output": "1.out"}]}]},
        ["1.in", "2.in"], None)
    assert "subtasks:" in cfg3, cfg3


def user_content_check():
    ucp = SKILL / "ui" / "user_content.py"
    env = dict(os.environ)
    env.setdefault("PYTHONUTF8", "1")
    r = subprocess.run([sys.executable, str(ucp), "--help"], capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    with tempfile.TemporaryDirectory(prefix="oiwb-ci-") as home:
        r2 = subprocess.run([sys.executable, str(ucp), "--home", home, "kb", "validate"],
                            capture_output=True, text=True, env=env)
        assert r2.returncode == 0, r2.stdout + r2.stderr
        ref = SKILL / "reference" / "entry" / "max-number"
        r3 = subprocess.run([sys.executable, str(ucp), "--home", home, "ref", "validate", str(ref)],
                            capture_output=True, text=True, env=env)
        assert r3.returncode == 0, r3.stdout + r3.stderr


def generator_check():
    ref = SKILL / "reference" / "entry" / "max-number"
    for script in ("build_package.py", "build_hoj_package.py"):
        r = subprocess.run([sys.executable, str(GEN / script), str(ref), "--check"],
                           capture_output=True, text=True)
        assert r.returncode == 0, "%s: %s%s" % (script, r.stdout, r.stderr)


def reference_consistency_check():
    """参考题一致性：测试点表格点数 == data 对数 == spec cases 数（以题面为准）。"""
    import regenerate_reference
    regenerate_reference.ensure_all()   # 无提交 data：先按生成器+std 现场重造
    import re as _re
    for level in ("entry", "intermediate"):
        ldir = SKILL / "reference" / level
        if not ldir.is_dir():
            continue
        for p in sorted(ldir.iterdir()):
            if not (p / "spec.json").is_file():
                continue
            spec = json.loads((p / "spec.json").read_text(encoding="utf-8"))
            subtasks = spec.get("subtasks") or []
            cases = spec.get("cases") or []
            if subtasks:
                n_cases = sum(len(st.get("cases") or []) for st in subtasks)
            else:
                n_cases = len(cases)
            data_count = len(list((p / "data").glob("*.in"))) if (p / "data").is_dir() else 0
            md = (p / "problem.md").read_text(encoding="utf-8")
            m_table = _re.search(r"^\| 测试点[^\n]*\n(?:\|[^\n]+\n)+", md, _re.M)
            total = 0
            if m_table:
                for row in m_table.group(0).splitlines()[1:]:
                    cells = [c.strip() for c in row.strip().strip("|").split("|")]
                    if not cells:
                        continue
                    first = cells[0].replace("$", "").replace("\\sim", "-")
                    for part in first.split(","):
                        part = part.strip()
                        mm = _re.match(r"^(\d+)\s*[-–]\s*(\d+)$", part)
                        if mm:
                            total += int(mm.group(2)) - int(mm.group(1)) + 1
                        elif _re.match(r"^\d+$", part):
                            total += 1
            name = "%s/%s" % (level, p.name)
            assert n_cases == data_count, "%s: spec cases(%d) != data 点数(%d)" % (name, n_cases, data_count)
            assert total == data_count, "%s: 题面表格点数(%d) != data 点数(%d)" % (name, total, data_count)


def main():
    for name, fn in [
        ("version-consistency", version_consistency),
        ("spec-io", spec_io_check),
        ("spec-judge", spec_judge_check),
        ("spec-mode", spec_mode_check),
        ("config-mapping", config_mapping_check),
        ("user-content-cli", user_content_check),
        ("generator-check", generator_check),
        ("reference-consistency", reference_consistency_check),
    ]:
        check(name, fn)
    if failures:
        print("[result] %d 项失败: %s" % (len(failures), ", ".join(failures)))
        sys.exit(1)
    print("[result] 全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
