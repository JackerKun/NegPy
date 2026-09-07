# 为 NegPy 做出贡献

> **简体中文翻译** · 译自 [`CONTRIBUTING.md`](../../CONTRIBUTING.md) · 对应 NegPy v0.58.0 · 若有出入，以英文原文为准

感谢你有兴趣为 **NegPy** 做出贡献！

## 🙋 认领 Issue

只有读取权限的贡献者无法使用 GitHub 的 assignee（指派）界面，因此 NegPy 允许你通过在 issue 上评论来自行指派：

- `/assign` — 将该 issue 指派给自己
- `/unassign` — 将自己从该 issue 移除

你的评论上出现 👀 表情回应，即表示命令已执行。

## 🛠️ 开发环境设置

NegPy 需要 **Python 3.13+**。我们使用 **uv** 管理环境和依赖。

### 1. 前置条件
如果尚未安装，请先安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)。

**扫描仪支持（可选）：**

- **SANE**（Linux/macOS）— Coolscan 及其他 SANE 胶片扫描仪。先安装系统库，再安装 `sane` 组（`uv sync --group sane` 或 `pip install negpy[sane]`）：
  - **Linux**（Debian/Ubuntu）：
    ```bash
    sudo pacman -S sane  # arch
    sudo apt install libsane-dev  # debian/ubuntu
    ```
  - **macOS**：
    ```bash
    brew install sane-backends
    ```

- **Plustek USB**（Windows/macOS/Linux）— 可选的 [pyopticfilm](https://github.com/jboneng/pyopticfilm) 驱动（8200i SE 和 8100 V2）：`uv sync --group plustek` 或 `pip install negpy[plustek]`。Windows 通过 pyopticfilm 安装 `libusb-package`（发布构建中已捆绑）。在 Windows 上，扫描之前先用 Zadig 为扫描仪的 USB id（`07b3:1825` 8200i SE，`07b3:1824` 8100 V2）绑定 WinUSB（厂商/SilverFast 驱动会冲突）。参见 [docs/PLUSTEK_WINDOWS.md](PLUSTEK_WINDOWS.md)。


### 2. Python 环境
`Makefile` 通过 `uv` 处理同步。运行以下命令来配置你的环境：

```bash
make install
```


### 3. 本地运行

```bash
make run
```

#### 用于开发的独立用户目录

NegPy 将其数据库、缓存、预设、日志和 `override.toml` 保存在同一个用户目录中——默认为 `Documents/NegPy`。如果你还将 NegPy 用于实际工作，请将开发构建指向另一个目录，让测试性编辑和陈旧缓存碰不到真实目录。

将 `NEGPY_USER_DIR` 设为绝对路径。`Makefile` 会读取一个可选的、被 gitignore 的 `.env.local`：

```make
# .env.local
NEGPY_USER_DIR = $(HOME)/negpy-devhome
```

`make run` 随后使用该目录，并在目录缺失时创建它。没有该文件时，一切保持原样。

要写 `$(HOME)`，而不是 `~` 或 `$HOME`：make 不展开 `~`，并把 `$HOME` 读成变量 `H` 后面跟着 `OME`。两者都会解析到代码库内部的路径，因此当值不是绝对路径时，make 会停下来告诉你。注意路径还必须符合所在平台——`/home/you/...` 是 Linux 路径，而 macOS 把你的主目录放在 `/Users/you` 下。

要在没有已保存编辑、没有缓存的状态下重新开始：

```bash
make clear-devhome
```

该目标会在一次确认后删除整个目录（`FORCE=1` 跳过确认），并且当 `NEGPY_USER_DIR` 未设置或指向默认目录时拒绝运行。你依赖的 `override.toml` 也在里面，因此请留一份副本以便放回。

有两样东西留在用户目录之外：

- `.negpy` 附属文件，写在源图像旁边。由开发构建写入的附属文件，会被提升进下一个打开该图像的安装的数据库。附属文件导出默认关闭；如果开启，请针对副本进行测试。
- 导出文件，无论你导出到哪里。

## 🏗️ 项目结构

代码库采用模块化架构：

- `negpy/domain/`：核心数据模型、类型和接口。
- `negpy/features/`：图像处理逻辑实现（曝光、几何、Lab 等）。
- `negpy/infrastructure/`：底层系统实现（GPU 资源、文件加载器）。
- `negpy/kernel/`：核心系统服务（日志、配置、缓存）。
- `negpy/services/`：高层编排（渲染引擎、导出服务）。
- `negpy/desktop/`：PyQt6 UI 实现（视图、控制器、工作线程）。
- `tests/`：单元与集成测试。

## 📐 编码规范

**提交前务必运行 `make format`。**

### 1. 风格与格式
- **Ruff**：同时用于 lint 和格式化。
- **类型标注**：所有新函数定义都必须有（强制执行 `ty`）。用 `cast` 绕过是不被认可的。
- **文档字符串**：为类和公共方法编写清晰、简洁的文档字符串。
- **风格**：字符串使用双引号，变量和函数使用 snake_case，类使用 PascalCase。

### 2. 测试
我们使用 `pytest`。新功能应在 `tests/` 目录中包含单元测试。

```bash
make test
```

`make test` 默认跳过标记为 `slow` 的测试（见 `pyproject.toml` 中的 `addopts`）。这包括 `tests/metrics/` 中的性能指标套件。

要运行指标测试并写出 JSON 结果文件：

```bash
NEGPY_METRICS_OUT=metrics.json uv run pytest tests/metrics/ -m "slow" -q
```

测试固件（Canon CR2、Nikon NEF、Sony ARW、Fuji RAF、Leica DNG）在首次运行时自动从 rawsamples.ch 下载（每个约 20–30 MB），并缓存在 `~/.cache/negpy-metrics/` 中。下载失败时测试会优雅地跳过。

要让测试使用本地文件而不下载，设置对应格式的环境变量：

```bash
NEGPY_PERF_RAW_CR2=/path/to/file.CR2 \
NEGPY_METRICS_OUT=metrics.json \
uv run pytest tests/metrics/ -m "slow" -q
```

可用的覆盖变量：`NEGPY_PERF_RAW_CR2`、`NEGPY_PERF_RAW_NEF`、`NEGPY_PERF_RAW_ARW`、`NEGPY_PERF_RAW_RAF`、`NEGPY_PERF_RAW_DNG`。

### 3. 工作流（Makefile）
`Makefile` 是开发者命令的核心权威来源，一切通过 `uv run` 执行：
- `make install`：配置环境并同步依赖。
- `make lint`：运行 Ruff 检查。
- `make type`：运行 `ty` 类型检查。
- `make test`：运行所有单元测试。
- `make format`：用 Ruff 自动格式化代码。
- `make all`：依次运行 lint、类型检查和测试。
- `make clean`：删除缓存和构建产物。
- `make clear-devhome`：删除开发用户目录（见[上文](#用于开发的独立用户目录)）。


## 📦 构建与打包

要为你当前的操作系统构建独立应用：

```bash
make build
```
这将通过 PyInstaller 触发 Python 后端构建。

在 macOS 上，可以用 `NEGPY_MACOS_ARCH` 选择 DMG 构建的目标架构。要在兼容的 macOS 环境中构建 Intel 版本，运行：

```bash
NEGPY_MACOS_ARCH=x86_64 make build
```
