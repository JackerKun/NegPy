<div align="center">
  <img src="../../media/icons/icon.svg" width="96" height="96" alt="NegPy Logo"><h1>NegPy</h1>

  [![CI](https://github.com/marcinz606/NegPy/actions/workflows/ci.yml/badge.svg)](https://github.com/marcinz606/NegPy/actions/workflows/ci.yml)
  [![Release](https://img.shields.io/github/v/release/marcinz606/NegPy)](https://github.com/marcinz606/NegPy/releases)
  [![Downloads](https://img.shields.io/github/downloads/marcinz606/NegPy/total)](https://github.com/marcinz606/NegPy/releases)
  [![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](../../LICENSE)
  [![Python](https://img.shields.io/badge/python-3.13%2B-blue)](../../pyproject.toml)
  [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
  [![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey)](#快速开始)
  [![Contributors](https://img.shields.io/github/contributors/marcinz606/NegPy)](https://github.com/marcinz606/NegPy/graphs/contributors)
  [![Discord](https://img.shields.io/badge/discord-join-5865F2?logo=discord&logoColor=white)](https://discord.gg/JySNzUWgwy)
</div>

> **简体中文翻译** · 译自 [`README.md`](../../README.md) · 对应 NegPy v0.58.0 · 若有出入，以英文原文为准

**NegPy** 是一个处理胶片负片的工具。我做它，是因为我想要一个专为胶片扫描打造、超越简单反相的工具。它模拟胶片与相纸的工作方式，同时还加入了一些实验室扫描仪软件式的便利功能。

它使用 **Python** 构建，原生运行于 Linux、macOS 与 Windows。

---

![alt text](../media/0500.png)

---

## 用户指南
**[点击阅读 USER_GUIDE.md](USER_GUIDE.md)** — 完整讲解 NegPy 的工作流程、功能与控件。

---

## 功能特性

**转换与胶片科学**
*   **无需相机配置文件**：不需要相机配置文件，也不需要框选边缘取色。数学方法根据通道感光特性中和橙色色罩。
*   **胶片物理**：在密度空间中对 **H&D 特性曲线**建模 — 非对称的趾部-线性-肩部响应，带有独立的 softplus 趾部/肩部拐点与 ISO-R 相纸反差等级 — 而不是简单的线性反相。
*   **智能自动转换**：逐帧的**自动密度**与**自动反差等级**对每张底片测光，得到合理的亮度/对比度 — 开箱即用，也易于微调。
*   **暗房相纸配置文件**：按相纸塑形曲线（色调、逐通道伽马、片基色调），映射自 Ilford/Kodak/Foma/Fuji 的数据表，可按卷选择。
*   **正片/幻灯片支持**：专用的**正片（反转片）模式**，带可选归一化，用于挽救过期或褪色的胶片。

**采集与输入**
*   **相机扫描**：用联机相机拍摄负片并直接进入 NegPy — 单张 RAW，或由 RGB [Scanlight](https://github.com/jackw01/scanlight) 驱动的自动红/绿/蓝窄带三联组，供三色扫描合并使用。macOS/Linux，可选依赖。[相机扫描指南](CAMERA_SCANNING.md)
*   **扫描仪支持**：直接控制兼容 SANE 的胶片扫描仪 — Plustek、Nikon Coolscan 等
*   **三色扫描**：将同一张底片的三次红/绿/蓝窄带曝光合并为一张低噪点的彩色扫描，并自动进行亚像素对齐以消除色边。
*   **平场校正**：通过对裸光源的参考扫描，校正光源或扫描仪带来的光照衰减/暗角。命名配置文件，按图切换。
*   **文件支持**：标准 RAW/TIFF，以及 Kodak Pakon 扫描仪原始文件等专有格式。

**编辑**
*   **加深与减淡**：暗房风格的局部加亮/压暗，使用手绘多边形蒙版 — 每个蒙版都有自己的 EV 强度与羽化。GPU 加速，并与 CPU 结果逐位一致。
*   **除尘**：自动与手动修复并合成颗粒 — 扫描干净又不显塑料感。
*   **批量归一化**：对全部已加载文件进行边界分析，取平均后应用于整卷。
*   **GPU 加速**：通过 Vulkan/Metal 实现实时处理与导出渲染。

**色彩与输出**
*   **色彩管理**：完整的 ICC 工作流程 — 自动检测显示器配置文件（Linux/macOS/Windows）、软打样含相纸/打印机配置文件、逐图输入/输出配置文件。
*   **印相就绪**：为打印而建的导出 — 边框控制、ICC 软打样、[动态文件名模板](TEMPLATING.md)、**导出预设**（保存 + 一键应用）以及**接触印相**。格式：JPEG、TIFF、PNG、WebP、JPEG XL。
*   **平扫/数字中间片导出**：平直、中性、宽色域的 **16 位 TIFF** 平扫母版，供 Lightroom/Darktable/Photoshop 使用，通过相机自身的矩阵将相机 RAW 映射到 ProPhoto。

**工作流程与数据**
*   **非破坏性**：从不触碰原始文件；编辑以配方形式存储。
*   **数据库**：编辑存储在以文件哈希为键的本地 SQLite 数据库中 — 移动或重命名文件不会丢失工作成果。
*   **持久化撤销/重做与历史**：每个文件最多 100 步编辑。**历史面板**列出每一步 — 可跳转到任意状态、创建分支，或导出较早的版本。重启后依然保留。
*   **元数据与器材库**：为原始胶片拍摄保存档案元数据 — 管理相机、镜头与胶片库，逐帧应用器材预设，并将真实的相机/镜头/ISO EXIF（以及 XMP 扫描标签）写入导出文件，让 Lightroom 显示你的胶片器材。[参见指南](USER_GUIDE.md#12-元数据选项卡)
*   **键盘快捷键**：[参见此处](KEYBOARD.md)

---

### 工作原理

[在此了解数学原理与流水线](PIPELINE.md)

---

## 快速开始

### 下载
从 **[Releases 页面](https://github.com/marcinz606/NegPy/releases)**获取适用于你操作系统的最新版本。

之后 NegPy 会自我保持更新：新版本发布时，左侧面板会显示 **⬇ 有可用更新** 链接，自动为你下载并安装，然后在新版本中重新打开。无需手动下载、卸载或重装。

#### Linux
我提供 `.AppImage`。用 `chmod +x` 赋予可执行权限后即可使用。

**扫描仪支持**需要系统安装 SANE：
```
sudo apt install libsane        # Debian/Ubuntu
sudo pacman -S sane             # Arch
```
或你的发行版对应的软件包。未安装也不影响应用启动；如果你不打算使用扫描仪，可以忽略。

**相机扫描支持**（可选）使用 `python-gphoto2` 进行联机拍摄，可能需要安装系统的 `libgphoto2`：
```
sudo pacman -S libgphoto2        # Arch
```
或查找你的发行版对应的软件包。

#### Nix
可以直接通过以下方式运行 NegPy：
```bash
nix run github:marcinz606/NegPy
```
或将其作为输入添加到你自己的 flake：
```nix
{
  inputs.negpy.url = "github:marcinz606/NegPy";
  outputs = { self, nixpkgs, negpy, ... }: {
    # negpy.packages.<system>.default
  };
}
```

#### 未签名软件警告
由于这是一个免费的业余项目，我不会向 Apple 或 Microsoft 支付开发者证书的“赎金”。首次运行时你会看到吓人的警告。

**macOS**：
1.  双击 `.dmg` 文件，并将应用拖入 `/Applications`。
2.  打开终端并运行：`xattr -cr /Applications/NegPy.app`（用于消除该警告）。
3.  启动应用。

如果你在 macOS 上自行构建 DMG，Intel 构建请设置 `NEGPY_MACOS_ARCH=x86_64`，Apple Silicon 请设置 `NEGPY_MACOS_ARCH=arm64`。

**扫描仪支持**需要通过 [Homebrew](https://brew.sh/) 安装 SANE：
```
brew install sane-backends
```
未安装也不影响应用启动；如果你不打算使用扫描仪，可以忽略。

**相机扫描支持**（可选）使用 `python-gphoto2`，可能需要通过 [Homebrew](https://brew.sh/) 安装 `libgphoto2`：
```
brew install libgphoto2
```

**Windows**：
1. 运行安装程序（忽略警告）
2. 启动应用并点过各项警告。

**扫描仪支持（Plustek OpticFilm）** — 8200i SE 与 8100 V2 — 使用可选的 `pyopticfilm` 驱动（`uv sync --group plustek` 或 `pip install negpy[plustek]`）。用 [Zadig](https://zadig.akeo.ie/) 将扫描仪绑定到 WinUSB（替换厂商/SilverFast 驱动；8200i SE 为 `07b3:1825`，8100 V2 为 `07b3:1824`）。Windows 发布版已捆绑 pyopticfilm、PyUSB 与 libusb。参见 [PLUSTEK_WINDOWS.md](PLUSTEK_WINDOWS.md)。相机扫描在 Windows 上仍不可用（libgphoto2 没有 Windows 构建）。

---

你也可以克隆仓库自行构建，说明见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 数据位置
所有内容都存放在你的 `Documents/NegPy` 文件夹中：
*   `edits.db`：你的编辑。
*   `settings.db`：全局设置，例如上次使用的导出设置或预览尺寸。
*   `cache/`：缩略图（可安全删除）。
*   `export/`：默认导出位置。
*   `icc/`：将相纸/打印机配置文件放到这里。
*   `override.toml`：启动覆盖项 — 见下方[故障排查 / override.toml](#故障排查)。

---

## 故障排查

如果 NegPy 启动时崩溃或出现渲染问题，请编辑 `Documents/NegPy/override.toml`。该文件在首次运行时自动创建，并带有适合你操作系统的合理默认值。`[performance]` 中的数值同样存在于**偏好设置**（`Ctrl + ,`）中；此文件中的值优先于对话框，这正是应用在无法启动时依然可用的原因。

```toml
[rendering]
# Options: "auto", "vulkan" (Linux/Win), "dx12" (Win), "metal" (macOS), "cpu"
backend = "vulkan"

[display]
# Qt scene-graph backend. Options: "auto", "vulkan", "d3d12", "metal", "opengl", "software"
qt_rhi_backend = "auto"

# Window system plugin (Linux only). Options: "auto", "xcb", "wayland"
qt_platform = "auto"

[performance]
# Cap GPU texture size in pixels — useful on low-VRAM cards. "auto" = no limit.
max_texture_size = "auto"

# Force HQ preview on/off. Uncomment to override saved preference.
# force_hq_preview = false

# Long edge of the interactive preview in pixels (512-8192). Higher is a sharper
# canvas and more VRAM per frame.
# preview_render_size = 1600

# Preview cache size — keeps recently-viewed photos in memory for instant navigation.
# Lower these on low-RAM machines. Uncomment to override defaults (~1.2 GB / 8 photos).
# preview_cache_max_bytes = 1200000000
# preview_cache_max_entries = 8

[logging]
# "debug", "info", "warning", "error"
level = "info"
```

设置 `backend = "cpu"` 会完全禁用 GPU 加速 — 如果 GPU 后端在你的硬件上崩溃，这会很有用。

---

## 路线图
以后想加入的功能：[ROADMAP.md](ROADMAP.md)

## 更新日志：

[CHANGELOG.md](CHANGELOG.md)

---

### 面向开发者

详情查看 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证
以 **[GPL-3](../../LICENSE)** 进行 Copyleft（著佐权）许可。

## 支持
如果你喜欢这个工具，也许可以送我一卷胶片，让我有更多测试数据 :)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/marcinzawalski)

---

## 中文文档索引

docs/zh/ 下的全部简体中文文档：

*   [USER_GUIDE.md](USER_GUIDE.md) — 完整用户指南：逐面板、逐控件的使用讲解。
*   [PIPELINE.md](PIPELINE.md) — 处理流水线：各阶段对像素做了什么及其数学原理。
*   [CHANGELOG.md](CHANGELOG.md) — 各版本更新日志。
*   [CAMERA_SCANNING.md](CAMERA_SCANNING.md) — 用联机相机翻拍负片的相机扫描指南。
*   [KEYBOARD.md](KEYBOARD.md) — 键盘快捷键参考。
*   [CROSSTALK.md](CROSSTALK.md) — 自定义串扰矩阵：格式、用法与自行调校。
*   [TEMPLATING.md](TEMPLATING.md) — 动态文件名模板（Jinja2）语法。
*   [CONTACT_SHEET_TEMPLATES.md](CONTACT_SHEET_TEMPLATES.md) — 接触印相的 `.toml` 版式模板。
*   [FILTERING.md](FILTERING.md) — 胶片条的搜索与过滤语法。
*   [PLUSTEK_WINDOWS.md](PLUSTEK_WINDOWS.md) — Windows 上 Plustek OpticFilm 的 USB 设置。
*   [ROADMAP.md](ROADMAP.md) — 后续计划路线图。
*   [CONTRIBUTING.md](CONTRIBUTING.md) — 贡献指南：构建与开发流程。
*   [NOTICE.md](NOTICE.md) — 第三方算法移植的法律声明。
*   [../FORK_SYNC.md](../FORK_SYNC.md) — Fork 同步与翻译流程（原文即中文，位于 docs/）。
