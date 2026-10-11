# 连续剧情 / 连载规范（story.yaml）

> 目标：同场共享主线 + 跨场次连载；用 `story.yaml` 剧本仓库维护角色/场景/道具/
> 伏笔的连续性，并用 `generator/story_continuity.py` 自动检查。

## 1. 剧本文件位置

- 一场比赛：`<比赛>/story.yaml`（与题目目录同级）。
- 跨场次连载：可在同一仓库根维护多个 `story.yaml`，通过 `title` 区分场次，
  并在 `previous` 字段引用上一场剧本文件，实现跨场连续性检查。

## 2. 字段约定

```yaml
title: 银河远征第一场        # 场次/连载名
previous: 银河远征第零场       # 可选：上一场剧本标题（跨场检查用）
episodes:
  - id: 1
    title: 选拔
    introduced: [队长, 阿强]   # 本集新登场角色/地点/道具（无则省略）
    characters: [队长, 阿强]
    locations: [报名处]
    props: [旧口哨]
    plot: 选拔队员
    unresolved: [牛肉面之谜]   # 本集留下伏笔
  - id: 2
    title: 补给
    characters: [老马, 队长]
    locations: [首都]
    props: [铃铛]
    plot: 运输补给
    uses_unresolved: [牛肉面之谜]  # 本集回收/提及上一集伏笔
    resolved: [牛肉面之谜]        # 本集解决该伏笔
```

- `episodes[].id` 必须为正整数且全剧唯一。
- `introduced` 用于声明“首次登场”；某角色/地点/道具若在 `characters/locations/props`
  中出现，但其 `introduced` 声明集在更晚的集数，则视为连续性错误。
- `unresolved` 与 `resolved` 用于伏笔闭环：`resolved` 中出现的伏笔必须来自
  之前某集的 `unresolved` 或 `uses_unresolved`；`uses_unresolved` 必须能在之前
  某集的 `unresolved` 中找到。

## 3. 检查命令

```powershell
python generator/story_continuity.py story.yaml
python generator/story_continuity.py --all <剧本仓库目录>   # 递归检查所有 story.yaml
```

退出码：发现错误返回 1；仅有警告（如未回收伏笔）返回 0 并提示。
