# 接触印相模板

> **简体中文翻译** · 译自 [`docs/CONTACT_SHEET_TEMPLATES.md`](../CONTACT_SHEET_TEMPLATES.md) · 对应 NegPy v0.58.0 · 若有出入，以英文原文为准

导出侧栏中的**接触印相**部分从纯 `.toml` 文件加载布局预设。**Default** 是你在应用内的基准布局，初始值为出厂设置 600 / 16 / 32 / 38。

---

## 文件夹

将模板文件放置于此：

```
~/NegPy/contact_sheets/
```

在 Windows 上通常为：

```
C:\Users\<you>\NegPy\contact_sheets\
```

NegPy 在启动时创建该文件夹。在应用中点击**保存为模板**，即可将当前布局设置写入文件。

---

## 文件格式

每个模板是一个 UTF-8 编码的 TOML 文件，包含一个显示名称和一个 `[layout]` 表：

```toml
name = "Tight 35mm"

[layout]
cell_px = 400
gap = 8
margin = 16
max_tiles = 48
```

| 键 | 含义 | 允许范围 |
|---|---|---|
| `cell_px` | 每个单元格长边（像素） | 100–4000 |
| `gap` | 单元格间距（像素） | 0–200 |
| `margin` | 网格周围的黑色边框（像素） | 0–500 |
| `max_tiles` | 每页帧数上限（超出后分页） | 1–200 |

省略的键回退到内置默认值（600 / 16 / 32 / 38）。

可选的顶层 `name` 字段显示在**模板**下拉菜单中。若未设置，NegPy 显示文件名词干（不含 `.toml`）。

---

## 示例

**NegPy 出厂默认（仅作参考，无需创建文件）**

```toml
name = "NegPy default"

[layout]
cell_px = 600
gap = 16
margin = 32
max_tiles = 38
```

**大单元格，每页更少**

```toml
name = "Large cells"

[layout]
cell_px = 900
gap = 20
margin = 40
max_tiles = 12
```

---

## 应用内行为

- 选择 **Default** 加载你保存的默认布局。初始值为出厂设置 600 / 16 / 32 / 38。
- 选择**命名模板**可将该 `.toml` 文件加载到微调框中。
- 在选中模板时更改微调框，NegPy 会更新该模板。Default 写入应用设置，命名模板重写为 `.toml` 文件。更改有约 500 ms 的防抖。
- **保存为模板**从当前微调框值创建一个**新的**命名文件。
- NegPy 在构建列表时忽略无效或不可读的文件。
- 如果你删除了已保存的模板文件，应用将在下次启动时回退到 **Default**。

模板仅控制网格布局。输出文件夹、单元格渲染和 JPEG 命名不受影响。
