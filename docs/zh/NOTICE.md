> **简体中文翻译** · 译自 [`NOTICE.md`](../../NOTICE.md) · 对应 NegPy v0.58.0 · 若有出入，以英文原文为准

> **本文件为英文 NOTICE.md 的参考译文；法律效力以英文原文为准。**

negpy/features/retouch/logic.py 中的 IR 灰尘重建移植了 digital-fauxice 的算法概念（连续缺陷评分、评分加权多尺度重建、原始下限写入规则、内半径路由与羽化合成），Copyright (c) 2026 Rohan Pandula, MIT License。
https://github.com/rohanpandula/digital-fauxice

negpy/features/retouch/openice.py 中的 OpenICE IR 重建方法移植了 openICE 的算法，Copyright (C) 2026 <a6o>, GNU General Public License v3.0 — 与 NegPy 发布所用的许可相同。
https://github.com/marcinz606/openICE

openICE 是 Applied Science Fiction 的 Digital ICE 的独立重新实现，用于互操作性和研究。Digital ICE 是 Eastman Kodak Company 的商标；Nikon、Coolscan 和 Nikon Scan 是 Nikon Corporation 的商标。openICE 和 NegPy 均与其无关联或获得其认可；这些名称仅标识所互操作的格式和硬件。

Plustek USB 驱动位于独立的 [pyopticfilm](https://github.com/jboneng/pyopticfilm) 包中。NegPy 通过 `negpy/infrastructure/scanners/plustek_backend.py` 集成该驱动。该驱动包含源自或参考 SANE Project genesys 后端（Scanner Access Now Easy）的材料，GNU GPL：

  https://gitlab.com/sane-project/backends

相关上游区域包括（不限于）：backend/genesys USB 协议、寄存器表、电机/传感器/前端表，以及图像管线辅助函数。Plustek、OpticFilm 及相关名称是其各自所有者的商标；NegPy 与 Plustek Inc. 无关联或获得其认可。
