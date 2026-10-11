# testlib（第三方组件）

本目录包含 Codeforces/Polygon 使用的 **testlib.h**：

- 版本：**0.9.41**
- 作者：Mike Mirzayanov
- 版权：Copyright (c) 2015 Mike Mirzayanov
- 上游：<https://github.com/MikeMirzayanov/testlib>
- 许可：**MIT License**（见本目录 `LICENSE`）

## 使用

- 本地评测器 `generator/local_judge.py` 编译 checker / interactor 时会自动加
  `-I <本目录>`，因此 `#include "testlib.h"` 可直接编译。
- 若需升级 testlib，请从上游替换 `testlib.h`，并同步更新 `LICENSE` 与版本说明；
  **不得移除文件头版权声明**。
- 远程 OJ（Hydro/HOJ）通常自带 testlib，无需随题包上传本文件。

## 注意

- 本组件为第三方 MIT 代码，与 dsh-oi-workbench 的 Apache-2.0 原创代码分开管理；
  在发布/分发时保留本目录及 `LICENSE`。
