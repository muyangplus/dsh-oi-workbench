# version-records（版本记录仓库）

本项目**版本更新记录的唯一存放位置**。所有「更新了什么、当前是什么版本、接下来要做什么」都在本目录维护。

## 目录结构

```text
version-records/
├── README.md           # 本文件：约定说明
├── VERSION.md          # 版本号规范 + 当前版本 + 全版本速览表
├── changelog/          # 每个版本的更新记录（Keep a Changelog 风格）
│   └── vX.Y.Z.md
└── ROADMAP.md          # 分批迭代计划（路线图）
```

## 什么时候更新（纪律）

| 时机 | 动作 |
|---|---|
| 每完成一个功能批次 | 新增 `changelog/v<版本>.md`；更新 `VERSION.md` 的当前版本与速览表 |
| 修复 bug / 重构 | 追加到当前版本 changelog 的对应条目（`Fixed` / `Changed`） |
| 每次同步 public / 发布 | 核对 changelog、package.json 版本、git tag 三者一致 |

## 约定

- 版本号语义见 `VERSION.md`（SemVer）。
- changelog 条目格式：`- [Added|Changed|Fixed|Security] 描述`，中文描述，一句一个改动。
- Git 提交信息：dev 仓库允许 wip；**同步 public 前**必须压缩为标准英文 ASCII 提交
  （避免中文乱码，见 `DEVELOPMENT.md`「常见错误与经验」）。
- 本目录属于仓库内文档；是否随 npm 包发布（加入 package.json `files`）由每次发布时决定。
