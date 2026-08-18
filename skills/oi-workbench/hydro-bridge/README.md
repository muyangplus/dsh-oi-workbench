# Hydro 对接（hydro-bridge/）

用 Hydro 的 HTTP API 直接管理**题目 / 比赛 / 团队**。所有端点与字段均来自
Hydro 官方源码（`packages/hydrooj/src/handler/*.ts`、`packages/ui-default/components/upload.tsx`），
并已在 `E:\work\dsh\reference\Hydro`（当前 master 浅克隆）中核对。

## 端点速查（均带 `/d/{domain}/` 前缀，默认 system 域）

| 操作 | 方法与路径 | 关键字段 |
|---|---|---|
| 登录 | `POST /d/{domain}/login` | uname, password |
| 创建题目 | `POST /d/{domain}/problem/create` | title, content, pid?, hidden, difficulty, tag |
| 编辑题目 | `POST /d/{domain}/p/{pid}/edit` | 同上 |
| 上传数据（zip 自动解压） | `POST /d/{domain}/p/{pid}/files` (multipart) | operation=upload_file, file, type=testdata |
| 题目数据列表 | `GET /d/{domain}/p/{pid}/files` | — |
| 下载数据文件 | `GET /d/{domain}/p/{pid}/file/{name}?type=testdata` | — |
| 创建比赛 | `POST /d/{domain}/contest/create` | operation=update, beginAtDate, beginAtTime, duration, title, rule, pids |
| 编辑比赛 | `POST /d/{domain}/contest/{tid}/edit` | 同上 |
| 比赛加人 | `POST /d/{domain}/contest/{tid}/user` | operation=addUser, uids |
| 比赛移人 | `POST /d/{domain}/contest/{tid}/user` | operation=removeUser, uid |
| 创建/更新团队 | `POST /d/{domain}/domain/group` | operation=update, name, uids |
| 删除团队 | `POST /d/{domain}/domain/group` | operation=del, name |
| 团队列表 | `GET /d/{domain}/domain/group` | — |

> 比赛 `rule` 取值（源码 model/contest.ts RULES）：`acm`、`oi`、`ioi`、`strictioi`、`homework`、`ledo`。
> OI 部分分比赛用 `rule=oi`。
> 请求体中的 `operation` 决定调用哪个 handler 方法（update/del/addUser/removeUser/uploadFile）。

## 文件

- `hydro_api.py` —— HydroClient 类（登录、题目、比赛、团队，纯标准库）
- `publish_problem.py` —— 发布题目包 zip 到 Hydro（创建题目 + 上传数据）
- `manage_contest.py` —— 建比赛/加选手/建团队（命令行）

## 使用示例

```powershell
# 发布题目包
python hydro-bridge\publish_problem.py P1001.zip --base https://hydro.example.com --user root --password xxx

# 建 OI 比赛并挂题
python hydro-bridge\manage_contest.py contest-create --base https://hydro.example.com `
  --user root --password xxx --title "OI 模拟赛" --date 2025-03-01 --time 08:30 `
  --duration 3.5 --rule oi --pids 1000,1001,1002 --rated

# 加选手
python hydro-bridge\manage_contest.py contest-add-users --base ... --user ... --password ... `
  --tid <比赛id> --uids 2,3,4

# 建团队
python hydro-bridge\manage_contest.py group-update --base ... --user ... --password ... `
  --name "高一集训队" --uids 2,3,4
```

## 安全提示

- **不要在命令行明文写密码**（会进 shell 历史）；优先用 `--cookie`（网页登录后复制 Cookie），
  或把密码放环境变量由脚本读取。
- 登录接口有速率限制（60 秒 30 次 / 每账号 5 次），批量操作请串行。
- 正式导入后请到网页核对：测试点/分数表、checker、题面渲染、隐藏状态。

## 与本工作台的关系

`generator/build_package.py` 生成的 zip 直接用 `publish_problem.py` 发布；
题目包格式细节见 `generator/README.md` 与 `templates/problem.yaml`。
