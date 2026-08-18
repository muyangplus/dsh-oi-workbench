# 参考题（Reference Problems）

本目录是 **dsh-oi-workbench 原创参考题**，仅陈述题目本身，不与任何官方比赛或官方标准关联。

## 内容

```text
reference/
├── entry/
│   ├── max-number/      # 数字串排序（字符串/贪心）
│   ├── spiral-seat/     # 螺旋座位（模拟/数学）
│   ├── xor-zero/        # 异或为零（前缀异或/计数）
│   └── triangle-count/  # 三角形计数（排序/双指针/组合）
└── intermediate/
    ├── team-assign/     # 三组分配（DP）
    ├── relay-mst/       # 网络中继（MST/枚举子集）
    ├── bracket-count/   # 括号序列计数（DP/组合）
    └── inversion-count/ # 逆序对计数（DP/排列计数）
```

每个题目目录均为完整题目包：

```text
max-number/
├── problem.md        # 题面
├── spec.json         # Hydro/HOJ 通用配置
├── sample/           # 题面样例
├── data/             # 10 个测试点 in/out
├── std/std.cpp       # 标程
├── brute.cpp         # 暴力对拍程序
└── generator/gen.py  # 数据生成器
```

## 说明

- 这些题目为本仓库原创内容，可按仓库许可证使用。
- 题目只包含题目描述、输入输出、数据范围、标程、数据生成器与验证记录。
- 不作为任何官方比赛的模拟题或仿真题。
