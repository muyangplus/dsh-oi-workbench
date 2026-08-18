# 生成器与本地评测（generator/）

把「题目目录」打包为 **Hydro** / **HOJ** 原生题目包，并支持本地 OI 评测。

## 使用

```powershell
# Hydro 包
python generator/build_package.py examples\demo --out P01.zip
python generator/verify_package.py P01.zip

# HOJ 包
python generator/build_hoj_package.py examples\demo --out P01-hoj.zip
python generator/verify_hoj_package.py P01-hoj.zip

# 本地评测（C++ 固定 -O2 -std=c++14 -static）
python generator/local_judge.py examples\demo --source std\std.cpp

# 一键校验 reference/ 全部自出参考题
python generator/build_all_reference.py
# 一键构建并校验 Hydro/HOJ zip
python generator/build_all_reference.py --build --out tmp/reference-zips
```

## 题目目录结构

```text
P01/
├── spec.json      # 配置（title/pid/tags/time/memory/subtasks/judgeCaseMode/fileIO/...）
├── problem.md     # 题面 Markdown
├── data/          # 隐藏测试数据 1.in/1.out（必需）
├── sample/        # 样例（可选）
├── std/           # 标程（可选）
└── solution/      # 题解（可选）
```

## spec.json 示例（OI 部分分，双 OJ 通用）

```json
{
  "title": "合并果子",
  "pid": "P1001",
  "tags": ["贪心", "堆"],
  "time": "1000ms",
  "memory": "256m",
  "stackLimit": 256,
  "type": "oi",
  "judgeCaseMode": "default",
  "languages": ["C++"],
  "cases": [
    {"input": "1.in", "output": "1.out", "score": 5},
    {"input": "2.in", "output": "2.out", "score": 5}
  ],
  "compile": {"cpp": "-O2 -std=c++14 -static"}
}
```

## 生成物布局

### Hydro（build_package.py）

| zip 内路径 | 导入行为 |
|---|---|
| `problem.yaml` | 标题/pid/标签/难度 |
| `problem.md` | 题面内容 |
| `testdata/config.yaml` | 评测配置：time/memory/subtasks/checker |
| `testdata/*.in/.out` | 测试数据 |
| `data/sample/*` | 展示样例 + 测试数据 |
| `std/*` | 导入为 AC 评测记录 |
| `solution/*` | 题解 |

### HOJ（build_hoj_package.py）

```text
P01-hoj.zip
├── problem_P1001.json   # HOJ 导入 JSON（judgeMode/samples/problem/languages/tags/...）
└── problem_P1001/       # 测试数据 1.in/1.out ...
```

`verify_hoj_package.py` 检查 JSON 格式、samples 文件存在、OI 总分 100、
judgeMode/judgeCaseMode 合法性。

## 本地评测（local_judge.py）

- 编译：`g++ -O2 -std=c++14 -static`
- 支持 stdio 与 `spec.json` 中的 `fileIO`
- 输出比较：OI 全文比较（过滤行末空格及文末换行）
- 逐点输出 AC/WA/TLE/RE 与得分
- Windows 本地时间仅参考；正式时限以全国统一评测机为准

## 导入 OJ

- Hydro：网页「从 Hydro 导入」或 `python hydro-bridge/publish_problem.py`
- HOJ：后台「题目管理 → 导入题目」或 `python hoj-bridge/publish_problem.py`