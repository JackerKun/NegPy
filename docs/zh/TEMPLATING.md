# 文件名模板

> **简体中文翻译** · 译自 [`docs/TEMPLATING.md`](../TEMPLATING.md) · 对应 NegPy v0.58.0 · 若有出入，以英文原文为准

NegPy 在**导出**和**扫描**侧栏中使用 **Jinja2** 实现动态文件命名。

---

## 导出侧栏

### 可用变量

| 变量 | 说明 | 示例输出 |
| :--- | :--- | :--- |
| `{{ original_name }}` | 源文件的基础文件名（不含扩展名）。 | `DSC0123` |
| `{{ colorspace }}` | 目标导出色彩空间。 | `sRGB`、`Adobe RGB` |
| `{{ format }}` | 导出文件格式（JPEG、TIFF 等）。 | `JPEG`、`TIFF` |
| `{{ paper_ratio }}` | 所选宽高比。 | `3:2`、`Original` |
| `{{ size }}` | 打印尺寸，单位厘米（使用"原始分辨率"时为空）。 | `30cm` |
| `{{ dpi }}` | 导出 DPI（使用"原始分辨率"时为空）。 | `300dpi` |
| `{{ target_px }}` | 目标长边像素尺寸（仅在像素模式下有值）。 | `2048px` |
| `{{ border }}` | 宽度 > 0 时插入 "border"，否则为空。 | `border` |
| `{{ date }}` | 当前日期，YYYYMMDD 格式。 | `20260125` |
| `{{ roll }}` | Scanlight 采集胶卷名（元数据 → 胶卷），或从 `{roll}_Frame{NNN}` 词干解析。不是整卷分析的归一化名称。 | `Roll001` |
| `{{ frame }}` | 采集帧号（整数），或从词干解析。未知时为空（`none`）。使用 `{{ frame\|pad(3) }}` 或 `{{ frame_padded }}` 进行零填充。`"%03d" % frame` 仅在帧号已设置时有效；否则整个模式回退为 `original_name`。 | `12` |
| `{{ frame_padded }}` | 零填充帧号（`012`），未知时为空。等同于 `{{ frame\|pad(3) }}`。 | `012` |
| `{{ camera }}` | 相机品牌 + 型号。 | `Mamiya 7` |
| `{{ camera_make }}` / `{{ camera_model }}` | 相机品牌 / 型号（分开）。 | `Mamiya`、`7` |
| `{{ lens }}` | 镜头型号（型号为空时使用品牌）。 | `80mm f/4` |
| `{{ lens_make }}` / `{{ lens_model }}` | 镜头品牌 / 型号（分开）。 | |
| `{{ focal_length }}` | 镜头焦距，单位毫米。 | `80` |
| `{{ film }}` | 胶卷名称。 | `Portra 400` |
| `{{ film_iso }}` | 胶卷 ISO。 | `400` |
| `{{ film_manufacturer }}` | 胶卷制造商。 | `Kodak` |
| `{{ film_color_type }}` | 胶卷色彩类型。 | `Color negative` |
| `{{ film_format }}` | 胶卷规格（35mm、120 等）。与导出 `{{ format }}` 不同。 | `35mm` |
| `{{ developer }}` | 显影液。 | `D-76` |
| `{{ dilution }}` | 显影液稀释比。 | `1+1` |
| `{{ push_pull }}` | 增减感，整数（−3…+3，0 = 正常）。 | `1` |
| `{{ development_time }}` | 显影时间，mm-ss 格式（冒号不适合文件名）。 | `9-30` |
| `{{ development_temperature }}` | 显影温度，单位 °C。 | `20` |
| `{{ scanning }}` | 扫描方式备注。 | `DSLR copy-stand` |
| `{{ exposure }}` | 元数据中的曝光覆盖文本。 | `1/125s f/2.8` |
| `{{ capture_date }}` | 原始拍摄日期，YYYYMMDD 格式。部分日期补全到当月首日。未设置时为空。 | `19980714` |
| `{{ capture_year }}` | 原始拍摄年份。未设置时为空。 | `1998` |

器材和工艺数值来自**元数据**面板，或批量处理中每个文件保存的元数据。空字段渲染为空字符串，因此其周围的分隔符会折叠。NegPy 会从元数据值中去除不适合路径的字符。

### 示例

| 模式 | 结果 |
| :--- | :--- |
| `{{ original_name }}` | `DSC0123.jpg` |
| `{{ date }}_{{ original_name }}_{{ colorspace }}` | `20260125_DSC0123_Adobe_RGB.jpg` |
| `{{ original_name }}_{{ size }}_{{ dpi }}_{{ border }}` | `DSC0123_30cm_300dpi_border.jpg` |
| `PRINT_{{ original_name }}_{{ paper_ratio }}` | `PRINT_DSC0123_3:2.jpg` |
| `{{ roll }}_Frame{{ frame\|pad(3) }}_{{ film }}_{{ film_iso }}` | `Roll001_Frame012_Portra_400_400.jpg` |
| `{{ film }}_{{ camera }}_{{ original_name }}` | `Portra_400_Mamiya_7_DSC0123.jpg` |

---

## 扫描侧栏

### 可用变量

| 变量 | 说明 | 示例输出 |
| :--- | :--- | :--- |
| `{{ date }}` | 当前日期，YYYYMMDD 格式。 | `20260125` |
| `{{ seq }}` | 序列号（整数，自动递增以避免覆盖）。 | `1`、`2`、… |

要对序列号进行零填充，使用 Python 的 `%` 格式运算符：`{{ "%03d" % seq }}`。

### 示例

| 模式 | 结果 |
| :--- | :--- |
| `{{ date }}_{{ "%03d" % seq }}` | `20260125_001.tif` |
| `roll_{{ date }}_{{ seq }}` | `roll_20260125_1.tif` |
| `plustek_{{ date }}_{{ "%04d" % seq }}` | `plustek_20260125_0001.tif` |

### 自动递增

序列号在每个扫描会话中从 `1` 开始。它持续递增，直到文件名在磁盘上不存在。NegPy **永远不会覆盖**已有文件。

---

## 文件名清理

两个侧栏对渲染后的模板应用相同的分隔符清理规则：

*   变量之间的空格、连字符和下划线折叠为**单个下划线**（`_`）。
*   移除首尾分隔符。
*   当变量为空时（例如未设置边框时的 `{{ border }}`），其周围的分隔符会被清理。
*   `{{ original_name }}`（仅导出）原样插入。原始文件名中的连字符、空格和下划线完全保留。

**示例：**
模式：`{{ original_name }} - {{ border }} - final`
*   有边框：`DSC0123_border_final.jpg`
*   无边框：`DSC0123_final.jpg`
