# CAMS / CFP v5.0

**本仓库是研究设计文档，不是实现或完成实验。**  
它提出三层收敛分区与 H1–H4 约束，用可复算证伪实验检验“可审计理解”；不主张已达到或可替代通用大模型。

**证据图例**  
`[设计]` 预注册选择/阈值，不是结果；`[假设]` 待检验估计；`[实测]` 有可复算数据——**当前无 `[实测]`**。未标 `[实测]` 的数字不得当结果引用。

## 一句话定位

面向“错误代价高、需要审计”的 Agent 的结构化研究提案，不与通用大模型比能力；核心不是更大的模型，而是证据指纹、始终产生的协方差、非符号溯源叶，以及可被外部依赖的拒绝契约。

## 30 分钟阅读路径

1. 本页 + [`docs/FALSIFICATION.md`](docs/FALSIFICATION.md)：什么结果算失败。
2. [`docs/EXPERIMENT-10K.md`](docs/EXPERIMENT-10K.md)：2–4 周、单人可跑的 10³ kill test。
3. [`docs/RELATED-WORK.md`](docs/RELATED-WORK.md)：与 selective prediction/conformal/calibration/RAG attribution/C2PA/debate 的差异。
4. [`Causal-Anchored Metacognitive Society, CAMS.md`](<Causal-Anchored Metacognitive Society, CAMS.md>)：完整方案（含假设、失败哈希、legacy 说明）。
5. [`docs/ROADMAP.md`](docs/ROADMAP.md)：G0→G3 的 go/no-go。
6. [`CAMS-通俗解释.md`](CAMS-通俗解释.md)：非专业读者版。

## 文件树

```text
.
├── README.md
├── Causal-Anchored Metacognitive Society, CAMS.md   # 主文档 v5.0
├── CAMS-通俗解释.md
├── LICENSE
└── docs/
    ├── FALSIFICATION.md
    ├── EXPERIMENT-10K.md
    ├── RELATED-WORK.md
    └── ROADMAP.md
```

## v5.0 改了什么

- 新增 `docs/FALSIFICATION.md`：F1′–F8′ 逐条改为可执行判据表（指标/阈值/检验/样本量/通过失败/实验编号）；F9′–F11′ 单列。
- 新增 `docs/EXPERIMENT-10K.md`：10³ kill test；`x_ns` 操作化为 tool execution receipt；5 个基线；停止规则、预算、失败模式。
- 新增 `docs/RELATED-WORK.md`：差异表 + “为什么 `A-skeleton` 不能复现 EGT”的 7 条可检验推论。
- 新增 `docs/ROADMAP.md`：G0→G3；每阶段交付物、go/no-go、预算、风险。
- 主文档：删除历史 Pareto 祖先表（旧 rubric 分数不可比）；F1–F6 降级为“设计自检清单”；补符号表与数字来源约定；“政治管理”降为一个应用场景。
- 不再使用无实测支撑的排名式表述。

## 当前状态（诚实版）

- **v5.0 是文档级评审版**：没有 10³/10⁴/10⁵ 运行，没有外部契约脚本，没有 `A-noAmort`/`A-noOrth`/`A-skeleton` 的实测。
- 主文档里的 F6=0.80、V=[0.82,0.78,0.84]、Pareto/failure 记录均为**设计自检/rubric**；不是实验结果，不能作为“已理解/已收敛”的证据。
- 100B 只是**合同覆盖上限**，不是 100B 份独立权重；10⁴ 不承重时，100B 不会改变性质。
- §12 仍列 7 条泄漏路径；它们没有被“结构约束”消灭，只是被定位到接口。

## 审稿人最该看的三个问题

1. **F1′**：`A-skeleton` 能不能复现 EGT？能，则结构不承重，停止。
2. **10³**：`T_π` 在同等预算下是否显著高于骨架，且 `D_π`/溯源/模式分离同向？不能，则不扩 10⁴。
3. **F10′**：外部脚本能否只读 `contract` 区分三态？不能，则“商业可验证”只是内部说法。

## License

MIT；见 [`LICENSE`](LICENSE)。
