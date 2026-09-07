# Windows USB 设置（Plustek OpticFilm）

> **简体中文翻译** · 译自 [`docs/PLUSTEK_WINDOWS.md`](../PLUSTEK_WINDOWS.md) · 对应 NegPy v0.58.0 · 若有出入，以英文原文为准

NegPy 的 Plustek USB 后端使用外部 [pyopticfilm](https://github.com/jboneng/pyopticfilm) 驱动（通过 PyUSB 调用 libusb）。需要 pyopticfilm **1.3.3** 或更高版本。Plustek 原装 Windows 驱动不得占用该设备。

## 要求

- Windows 10 或 11
- 支持的 Plustek OpticFilm 扫描仪：**8200i SE**（`07B3:1825`，GL128）和 **8100 V2**（`07B3:1824`，GL128）
- 使用 [Zadig](https://zadig.akeo.ie/) 绑定 WinUSB（或 libusbK）
- NegPy 安装了 `plustek` 可选依赖（`uv sync --group plustek` 或 `pip install negpy[plustek]`）。在 Windows 上，pyopticfilm 还会引入 `libusb-package`

## 1. 确认设备

接通扫描仪电源并连接 USB，然后：

1. 打开**设备管理器**
2. 在"图像设备"或"通用串行总线设备"下查找 Plustek
3. 属性 → 详细信息 → 硬件 ID 必须包含 `VID_07B3&PID_1825`

## 2. 绑定 WinUSB（Zadig）

1. 下载 [Zadig](https://zadig.akeo.ie/)
2. 选择 **Options → List All Devices**
3. 选择 Plustek Film Scanner（`07B3:1825`）
4. 将驱动替换为 **WinUSB**。libusbK 也可用
5. 保留 Plustek 原装驱动安装程序。之后恢复 VueScan 或厂商软件时需要它

绑定 WinUSB 期间，Plustek 原装 Windows 扫描应用无法看到该设备。

## 3. 运行 NegPy 并扫描

从源码目录：

```powershell
cd path\to\NegPy
uv sync --group plustek
make run
```

Windows 发布版本也可以使用。它打包了 pyopticfilm、PyUSB 和 libusb。在扫描选项卡中，将后端设为 **pyOpticfilm (Plustek)**。刷新设备列表。绑定 WinUSB 后 SE 即会出现。

## 4. 恢复厂商驱动

1. 拔出扫描仪
2. 设备管理器 → 卸载 WinUSB 设备。如有"删除驱动程序软件"选项请勾选
3. 重新安装 Plustek 或 VueScan 驱动包
4. 重新插入扫描仪

## 故障排除

| 症状 | 可能原因 |
|---------|----------------|
| 设备列表为空 | PID 错误、未连接、或仍在使用厂商驱动 |
| `DriverBindingError` 或访问被拒绝 | WinUSB 未绑定，或另一个应用占用了句柄 |
| `UsbError` 或链路故障 | 线缆或集线器问题。尝试直接连接主板端口 |
| UI 提示缺少 USB / PyUSB | 安装 plustek 组：`uv sync --group plustek` |
| 首次在某 DPI 扫描需要几秒 | 正常。AFE 加上一次暗场和一次白场校正条，与 SilverFast 相同的流程。之后按分辨率缓存 |
| ASIC shading ready（首选状态） | 日志显示彩色白场均值约 50–57k，`median_gain` 约 1.1–1.7x，然后出现 `ASIC shading ready`，图像 `shading=True` / DVDSET 开启。更改驱动后请删除 `plustek_calib` 并重新扫描，以重新测量校准 |
| 彩色白场均值约 50–57k | 正常。在单位增益下，DVDSET 返回 `raw − dark`，因此亮条接近满量程。采集数据中的 11–13k 数字是 SilverFast 由此计算出的*增益*（`0x2000` = 1.0），不是白场电平 |
| 中位增益超出 1.02–3.0x | 低于该范围说明校正条已达到目标，无需平坦化。高于该范围说明光路太暗。检查灯泡、AFE 增益，以及扫描头是否停在干净的归位铬面 |
| 校正或扫描中止后扫描头未归位 | 白场条在测量期间激活 `AGOHOME`，清除 SCAN 后停靠。若停靠超时，使用 SilverFast 或断电重启后重试 |
| Full 窗口下角落比 SilverFast 暗 | Full 窗口包含约 0.8 mm 的片夹铬面。校正仅按列进行，因此相比更窄的 SilverFast 画幅，这些边缘的残余 Y 衰减属于预期 |
| 正片非常暗直到你裁剪（底片上有白色边缘） | 片夹铬面比片基更亮，NegPy 自动边界锁定了它。两条路径都将边框高光钳位到胶片内区（`border highlight clamp…`）。在 ASIC 路径上这是必须的，因为 DVDSET 通过构造将该铬面映射到满量程。也可提高工艺 → **分析缓冲区**，或在自动分析前先裁剪 |
| 彩虹状垂直"条形码"条纹 | 上传的表索引方式与图像不同。测量数据进入了增益槽（增益应为 `0xFFFF × 0x2000 / white`，与 `1/white` 成正比），或 blob 打包时缺少块填充。AHB 表为 512 字节块，每块 126 个 `(dark, gain)` 对加两个 `gain = 0` 填充对，因此连续记录每块滑动 8 字节。删除 `plustek_calib` 并重新扫描 |
| 菱形或剪切场景（物体倾斜） | (1) 图像 X 方向缩小但 USB 仍按全行节奏传输。校正表必须覆盖每一个采集列（1800 下 Full 窗口约 2592 px）。(2) 1800 下出现奇数的 USB 裁剪宽度，例如 2455。输出宽度必须为偶数（`optical_span_alignment` 加偶数像素数）。删除 `plustek_calib`（缓存 v9+）并重新扫描。日志必须显示偶数的 `pixels=` |
| 底片非常暗或正片过亮（与 SilverFast 对比） | 两条路径参考的都是*归位*铬面，它比扫描位置的光更亮。在 1800 dpi 下片基落在满量程约 42%，约低 1.2 档，NegPy 测量到薄底片。`expose_film_base` 以单一标量增益（按最亮通道确定）提升它（`… exposure makeup gain=…`）。增益必须保持标量，否则会中和反转所需的橙色罩色 |
| 正片有强烈橙色或粉色偏色 | 检查 `AFE search done gains=…` 是否有通道达到或接近 `AFE_GAIN_MAX`（511）。在该极值处，该通道的暗场项钳位到 0（`dark0=(0, …)`），失去黑位并使整帧偏色。搜索会为钳位通道替换 SF 的 session-04 代码。持续钳位意味着 AFE 增益目标不可达。目标是 *AFE 条*电平，不是校正白场，因此不要将其提高到 SF 约 50k 的探测均值 |
| 正片有强烈绿色偏色 | 边框钳位上限必须是**逐通道**的。单一联合百分位将边距平坦化到中性灰，电平为最暗通道在胶片中永远达不到的值（session 004：联合 27432 对比绿色自身的 19306），导致自动 Dmin 从铬面测量绿色并将其提升 1.4x。检查 `border highlight clamp peak_p99.7=(r,g,b)`。每个数值必须刚好高于该通道自身的胶片峰值 |
| `white clipped at the rail` | 白场条被钉在 `0xFFFF` 附近，不携带可供平坦化的形状信息。降低 AFE 增益。DVDSET 保持关闭，主机端拉伸生效 |
| 扫描失败：白场均值低于 20000 | 单位增益后的校正条太暗，无法在 4x 增益钳位内达到目标。通常是过期的 AHB 条：暗场和 AFE 等待缓冲区在**归位**处有数据，而电机忙 `0xa5` 在那里未就绪。还需检查暗场时灯泡已关闭且扫描头在干净的归位铬面上。缓存 v6+ 会忽略塌缩的校准 |
| 扫描失败：彩色 ASIC shading / 干净归位场 | 扫描头不在干净的归位传感器上。停靠或断电重启后重试。胶片可以保持装载 |
