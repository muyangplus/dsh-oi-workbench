# 多轮出题经验沉淀（Lessons Learned）

## 0. 题面文字硬约束（2026-10-11 用户口径）

- **正文禁止全角括号 `（）`、禁止破折号 `——`**：约束、澄清、附件引用全部改写成逗号分句或独立句子。
  例：`输入一个整数 $n$，其中 $1\le n\le 500$。`；`样例 3 及以后的样例见题目附件 xxx_samples.zip。`
  标题行只写题名，不写 `题名（pid）`，pid 只在 `spec.json`、题包名与封面表里出现。
- **禁止答案提示**：不写"此时答案必为 …""答案恒为 …""答案不超过 …""只需输出 …"；
  特殊性质只描述输入形态，例如写"所有 $a_i$ 相同"，不写"此时答案恒为 1"。
- 整卷 PDF 的题名头、注意事项模板、附件引用模板都已同步去掉括号；
  打包前先跑 `python generator/check_statement_style.py --vol <卷目录>`，ERROR 必须为 0。
- 反面教材（本次被用户指出的三处）：`# 信笺（letter）` 的标题括号、
  `（此时答案必为 $r-l+1$）` 的答案提示、`（见题目附件 …）` 的附件引用括号。

## 1. 中文文件编码

- 所有 `problem.md`、`VERIFICATION.md`、`solution.md` 等必须使用 **UTF-8 无 BOM**。
- **不要用 PowerShell 的 `Set-Content` 处理中文**，否则会把 UTF-8 内容按 GBK 误读再写出，导致乱码。
- 推荐使用：
  - `write` 工具直接写入；
  - Python `pathlib.Path.write_text(..., encoding="utf-8")`；
  - 若需批量清理行尾空白/BOM，用 Python 读写，不要用 `Get-Content` + `Set-Content`。

## 2. 样例与大样例

- 样例 1、2 内联在题面；样例 3 及之后为大样例。
- 大样例题面引用统一使用 PDF 风格：

  ```text
  见选手目录下的 <题目>/<题目>2.in 与 <题目>/<题目>2.ans。
  该样例满足测试点 6, 7, 8 的约束条件。
  ```

- 一道题可以有多条大样例，使用 `## 样例 4`、`## 样例 5` 继续追加。
- 交互题如果只有样例 1，应补一个 `sample/2.*` 占位，否则 `package_samples.py` 会中断。

## 3. 交互题与 SPJ

- 交互题：
  - `spec.json` 中 `judge.type="interactive"`，`judge.interactor="interactor.cpp"`；
  - interactor 源码放 `data/` 或 `checker/`；
  - 若 `build_package.py` 因 `spj=true` 要求 checker，可提供一个占位 `checker.cpp`。
- SPJ 题：
  - `spec.json` 中 `judge.spj=true`，`judge.checker="checker.cpp"`；
  - checker 源码放 `data/` 或 `checker/`。
- Lemon 导出：
  - 交互题 `.cdf` 中 `taskType=2`，`specialJudge` 指向 grader；
  - SPJ 题 `.cdf` 中 `specialJudge` 指向**编译后的可执行文件**（如 `data/<题目>/checker.exe`）；
  - LemonLime SPJ 必须使用 `registerLemonChecker()` 或手写 6 参数接口，不能直接放 `.cpp`；
  - 导出时需把 checker/interactor 复制到 `data/<题目>/` 下，并编译 `checker_lemon.cpp` 为 `checker.exe`。
- **LemonLime 交互题（NOI 风格）**：
  - 必须提供 `interact.h`、`__grader.cpp`、`std_lemon.cpp`；
  - `.cdf` 中设置：
    ```json
    "interactor": "interact/interact.h",
    "interactorName": "interact.h",
    "grader": "interact/__grader.cpp",
    "specialJudge": "interact/__grader.cpp"
    ```
  - 文件 IO 配置：`inputFileName="interact.in"`，`outputFileName="interact.out"`；
  - grader 必须读取 `interact.in`，并且**必须创建 `interact.out`**（即使为空），否则 LemonLime 报“无法打开选手输出文件”。
- **LemonLime SPJ**：
  - `.cdf` 中 `comparisonMode` 必须设为 `4`（自定义校验器模式），否则 Lemon 会按逐行比较而不是调用 checker。

## 4. 本地交互测试

- 双向管道泵线程在源 EOF 后必须关闭目标管道，否则选手程序会认为 stdin 未结束而卡死。
- 本地评测临时目录清理失败时，可使用 `TemporaryDirectory(ignore_cleanup_errors=True)` 避免沙箱权限问题。

## 5. 题目包完整性

- 每道题建议包含：
  - `problem.md`、`spec.json`
  - `sample/1.*`、`sample/2.*`
  - `data/`（25 个 in/out）
  - `std/`、`brute`、`wrong*`
  - `generator/`
  - `VERIFICATION.md`
  - `solution/solution.md`
- 打包前用 `tools/check_problem.py` 做完整性检查。

## 6. 子代理协作

- 子代理实现题目时，明确要求“中文文件用 write 工具或 Python 写，不要用 PowerShell Set-Content”。
- 长时间无文件产出或残留进程时，及时中断并在主会话接管。

## 7. HOJ 实例发布（实战）

- **鉴权**：HOJ 的 JWT 放在 `Authorization` 头里，**裸 token，不加 `Bearer`**；
  服务端还会校验 `sub` 是否仍在 Redis 中（被顶号即失效）。
  `HojClient(base, token=...)` 已支持；`POST /api/admin/login` 是账号密码通道。
- **发布通道要选对**：优先用 **HOJ 原生 zip + `POST /api/file/import-problem`**（需 root，即后台「导入题目」）。
  后端会自己完成：语言名 → `lid`、标签名 → `tid`（缺失自动建）、代码模板 `language` → `lid`、
  `author` 缺省填当前登录账号、测试数据落到 `testcase_base/problem_<id>`。
- **不要用 `POST /api/admin/problem` 直传 DTO**：`ProblemDTO.codeTemplates` 的元素是 `CodeTemplate`
  实体，字段是 **`lid`**；若照导入 zip 的写法传 `{"language":"C++"}`，`lid` 为空 → 外键失败，
  前端只看到 **HTTP 500 / “数据库中已有相同的数据导致重复冲突!”**（同一路径还要求自己填 `author`，否则写 NULL）。
- **`api/admin/problem?pid=` 的 `pid` 是数据库自增 id**，不是展示编号（`problemId`）；
  按展示编号找题目要先过 `api/admin/problem/get-problem-list`。
- **`api/get-problem-detail`（公开端点）实测 20~30 s/次**，批量复核千万别用它；
  字段与测试点走 admin 端点（亚秒级）。
- **大体积数据**（单题 30~70 MB）导入耗时 1~2 min 属正常，批量上传务必**串行**。
- **上传后复核三件套**：① admin 端点逐题核对题名/难度/点数/总分/IO 模式/时限内存；
  ② `api/file/download-testcase` 拉回 zip 与本地 `data/` 做 **md5 逐字节比对**（远端会多一个 `info` 元数据文件，正常）；
  ③ 抽查若干题在 Web 端渲染（题面、样例、数据范围表）。
- **难度字段是实例自定义的**：不要假设 0/1/2；先抓线上前端 bundle 里的 `PROBLEM_LEVEL` 或看已有题目的取值，
  再定档位映射（例：某实例为 6 级色阶 0 入门 … 5 省选/NOI）。
- **评测记录会留痕**：`POST /api/submit-problem-judge` 会产生公开提交记录（代码默认不分享，但 root/管理员可见）。
  `submit-problem-test-judge` 是"自定义输入自测"，**不会**跑全部测试点，别拿它当真机验题。
- **可重跑的批量上传器**：先把"编号 → 本地题目目录"做成清单脚本，上传前先查实例已有编号并跳过，
  失败重试 3 次并逐题落 JSON 日志（示例见用户仓库 `_tools/hoj/upload_volumes.py`）。

