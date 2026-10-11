# HOJ 对接（hoj-bridge/）

针对 [HimitZH/HOJ](https://github.com/HimitZH/HOJ) 的完整管理桥接。
纯 Python 标准库（urllib + cookiejar），无第三方依赖。

端点与字段来自仓库源码：
`hoj-springboot/DataBackup/src/main/java/top/hcode/hoj/controller/*.java`、
`hoj-springboot/api/src/main/java/top/hcode/hoj/pojo/*.java`、
`docs/docs/use/import-problem.md`。

## 文件

- `hoj_api.py` —— HojClient 类（登录、题目、比赛、训练、用户、团队、公告、标签、评测、系统）
- `publish_problem.py` —— 发布题目包（HOJ 原生 zip / Hydro zip / admin API 直传）
- `manage_hoj.py` —— 命令行完整管理

## 能力清单

| 模块 | 操作 |
|---|---|
| 账号 | `login` / `logout` / dashboard |
| 题目 | list/get/add/update/delete/auth、测试数据上传/下载、导入 Hydro/HOJ zip、导出 zip、编译 SPJ/交互、远程导入、重判 |
| 比赛 | list/get/create/update/delete/clone/visible、比赛题目增删/排序、比赛公告 |
| 训练 | list/get/create/update/delete/status、题目加入/移除 |
| 用户 | list/edit/delete/batch-insert/generate |
| 团队 | list/get/create/update/delete、成员列表/申请/增删 |
| 公告 | list/create/update/delete |
| 标签 | list/create/update/delete |
| 评测 | rejudge / rejudge-contest-problem / manual-judge / cancel-judge |
| 系统 | dashboard / service-info / judge-service-info |

## 快速开始

```powershell
# 已经拿到网页 JWT 时（推荐：Authorization 头原值，裸 token 不加 Bearer）
$env:HOJ_TOKEN = "<jwt>"

# 发布题目目录（自动生成 HOJ 包并经 /api/file/import-problem 导入，需 root）
python hoj-bridge\publish_problem.py --base https://oj.example.com --problem-dir examples\demo

# 直接通过 admin API 创建（需要 problem_admin/admin；注意 codeTemplates 必须给 lid）
python hoj-bridge\publish_problem.py --base ... --token <jwt> --problem-dir examples\demo --direct

# 覆盖题目展示 ID（整卷批量上传时连续编号）
python hoj-bridge\publish_problem.py --base ... --token <jwt> --problem-dir ... --direct --problem-id X1241

# 环境变量方式避免密码进入命令行历史
$env:HOJ_PASSWORD = "你的密码"

# 题目列表
python hoj-bridge\manage_hoj.py problem-list --base ... --user root --limit 10

# 创建 OI 比赛
python hoj-bridge\manage_hoj.py contest-create --base ... --user root `
  --title "OI 模拟赛" --type 1 --start "2025-11-01T08:30:00.000Z" `
  --end "2025-11-01T12:00:00.000Z" --duration-seconds 12600

# 批量导入用户
python hoj-bridge\manage_hoj.py user-batch-insert --base ... --user root --users-file users.csv

# 重判提交
python hoj-bridge\manage_hoj.py judge-rejudge --base ... --user root --submit-id 12345
```

## 两条发布通道怎么选

| 通道 | 接口 | 适用 |
|---|---|---|
| **HOJ 原生 zip（推荐）** | `POST /api/file/import-problem`（需 root） | 后端自动做 语言/标签/代码模板 名称→id、`author` 缺省、测试数据落盘；用 `build_hoj_package.py` 的 `--problem-id` 覆盖展示 ID |
| admin 直传 DTO | `POST /api/admin/problem` | 需要精确控制字段时。**`codeTemplates` 必须给 `lid`（语言 id）**，传 `language` 名字会外键失败报 500；`author` 需自己填 |

> 注意：`api/admin/problem?pid=` 的 `pid` 是**数据库自增 id**，不是展示编号；
> 按展示编号查题先走 `api/admin/problem/get-problem-list`。
> 公开端点 `api/get-problem-detail` 在大实例上可能 20~30 s/次，批量核对请用 admin 端点。

## 安全提示

- **不要明文写密码**；优先 `--cookie` 或环境变量 `HOJ_PASSWORD`。
- HOJ `/api/file/import-problem` 仅 `root` 可用；非 root 请用 `--direct`。
- 批量管理先加 `--dry-run`。
- 导入后到网页核对：分数表、`judgeCaseMode`、`spj/interactive`、file IO、题面渲染。