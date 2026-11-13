# RELATED WORK — CAMS / CFP v5.0

> 修订说明：v5.0 把“与最近邻的差异”从口号改成可检验推论。本文只写机制差异与待检验含义；没有实测优势。引用的论文/规范是背景，不是本方案的成绩。

## 0. 证据分级

- `[设计]`：本方案的结构选择。
- `[假设]`：可从结构推出、但尚未实验的差异。
- `[实测]`：本仓库暂无；不得把引用论文的结果当成本方案结果。

## 1. 差异表

| 方法族 | 代表工作 | 提供的保证 | 主要成本 | 局限 | 与 CAMS/CFP 的差异 |
|---|---|---|---|---|---|
| **Selective prediction** | Geifman & El-Yaniv, *Selective Classification for Deep Neural Networks*, NeurIPS 2017 | 在选定覆盖率下约束风险 | 需要 coverage-risk 曲线与阈值选择 | 弃权是输出层动作；不解释证据来自哪里 | CFP 不让 `⊥` 变成离散弃权端口；协方差始终产生，契约携带原因/覆盖/溯源，而不是只给一个 confidence |
| **Conformal prediction** | Vovk et al. 2005；Angelopoulos & Bates, *A Gentle Introduction to Conformal Prediction*, arXiv:2107.07511 | 交换性假设下的边际覆盖率 | 校准集、非一致性分数 | 交换性/分布漂移下保证弱；集合预测不等于因果溯源 | CFP 不卖“分布无关覆盖”；它检验协方差门控的层间传递与溯源一致性，允许在分布漂移下失败 |
| **Calibration** | Guo et al., *On Calibration of Modern Neural Networks*, ICML 2017 | 概率与经验频率更一致 | 温度/矩阵缩放、校准集 | 校准不等于正确，也不保留证据路径 | CFP 的精度权重只改写传递强度，不改写内容；校准失败是 F3′/F8d 的失败，不是“再校准一下” |
| **RAG attribution** | Bohnet et al., *Attributed Question Answering*, arXiv:2212.08037；Gao et al., *RAG for LLMs: A Survey*, arXiv:2312.10997 | 答案可附引用/证据 | 检索、归因标注、上下文长度 | 引用常是事后附加；引用存在不等于推理使用了它 | CFP 把证据指纹放在 L1 生成路径上；确定输出必须有非符号叶 + 哈希溯源，不能只在答案后贴链接 |
| **Provenance / C2PA** | C2PA Technical Specification 2.1, c2pa.org | 内容来源与签名可验证 | 签名基础设施、密钥管理 | 证明“来自哪里”，不证明“内容为真” | CFP 把 provenance 限定为**单次推理的证据路径**，不是文件级来源；它明确不解决“传感器说谎” |
| **Multi-agent debate** | Du et al., *Improving Factuality and Reasoning in Language Models through Multiagent Debate*, arXiv:2305.14325 | 多轮互评可提高部分任务准确率 | 多轮调用、token 成本高 | 无结构保证；可能共识错误；难追溯 | CFP 不做投票/共识；群体只做局部稀疏路由、误差暴露、侧抑制；制度干预是局部列扰动 |
| **Hierarchical predictive coding** | Rao & Ballard 1999；Friston 2010 | 分层预测误差的规范框架 | 迭代推断成本 | 生物类比不能直接当工程证明 | CFP 借用“层级/精度”语言，但把它落成可观测接口与消融；不用“人脑也是这样”作论证 |

> 引用只用于定位差异；不是“我们的方法已被这些工作证明”。所有对比结论均为 `[假设]`，待 10³/10⁴ 检验。

## 2. 为什么 `A-skeleton` 不能复现 EGT 轨迹：可检验推论

`A-skeleton` = 保留三层骨架，去掉 H1–H4。若它仍能复现 EGT 的高协方差/确定模式，F1′ 失败，CFP 的“结构承重”主张失败。以下是可检验推论，不是已观察结果：

| # | 推论 `[假设]` | 观察量 | 对应判据 |
|---|---|---|---|
| I1 | 没有非符号叶，`A-skeleton` 的确定输出只能靠文本 token；溯源匹配率下降 | `PM` | F1′、F8a |
| I2 | 没有始终产生的协方差，弱证据下它更倾向低方差确定输出 | `d`、`Δdet` | F2′、F8b |
| I3 | 没有精度-only 回灌，高层可以改写内容，证据哈希在回灌后变化 | content hash 差分 | F8d、§12 泄漏路径 |
| I4 | 没有协方差门控，`T_π` 事件更少或与证据削弱无关 | `T_π` | F8c |
| I5 | 没有契约对象，外部脚本只能读内部 `Σ/μ` 才能区分三态 | `contract_probe_acc` | F10′ |
| I6 | 稠密路由没有覆盖记忆/侧抑制，冗余探测更多，单位算力结构增量更低 | `ROI_struct` | F9′ |
| I7 | 没有 `O_z`，相似输入但溯源不同的 `z` 更容易塌缩 | `z_sep` | F11′ |

**关键点**：这些推论必须能被 **A-skeleton 的实测**推翻。若 I1–I7 都不成立，CFP 相对骨架没有可观察优势，应停止扩展——这是 F1′ 的用途，不是失败后的补丁。

## 3. 与“更大会更好”的区分

- 本方案不把 100B 当解释；100B 只是合同覆盖上限。若 10⁴ 不承重，10⁵/100B 不改变性质。
- 与“多智能体社会模拟”的差异：本方案不做投票/共识/全局广播；群体只做局部稀疏路由和制度性局部扰动。
- 与“更强对齐”的差异：本方案不把 RLHF/事后检测当主要抗幻觉手段；它把约束放在生成路径的接口上。

## 4. 待补引用与信息

- `[TBD]`：selective prediction 在政治管理类任务上的公开基准；目前没有可引用的统一基准。
- `[TBD]`：C2PA 在模型推理 trace 上的行业实践；当前规范主要面向内容资产，不是单次推理。
- `[TBD]`：多智能体 debate 的长程成本数据；引用论文的任务/预算与本方案不同，不能直接比较。
- `[TBD]`：`A-skeleton` 的具体实现细节与参数预算，需在 10³ 预注册中冻结。

## 5. 引用（背景，不是本方案结果）

1. Y. Geifman, R. El-Yaniv. *Selective Classification for Deep Neural Networks.* NeurIPS 2017.
2. V. Vovk, A. Gammerman, G. Shafer. *Algorithmic Learning in a Random World.* Springer, 2005.
3. A. Angelopoulos, S. Bates. *A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification.* arXiv:2107.07511, 2021.
4. C. Guo, G. Pleiss, Y. Sun, K. Weinberger. *On Calibration of Modern Neural Networks.* ICML 2017.
5. B. Bohnet et al. *Attributed Question Answering: Evaluation and Modeling for Attributed Large Language Models.* arXiv:2212.08037, 2022.
6. Y. Gao et al. *Retrieval-Augmented Generation for Large Language Models: A Survey.* arXiv:2312.10997, 2023.
7. C2PA. *Technical Specification 2.1.* Coalition for Content Provenance and Authenticity, 2025.
8. Y. Du et al. *Improving Factuality and Reasoning in Language Models through Multiagent Debate.* arXiv:2305.14325, 2023.
9. R. P. N. Rao, D. H. Ballard. *Predictive coding in the visual cortex.* Nature Neuroscience, 1999.
10. K. Friston. *The free-energy principle: a unified brain theory?* Nature Reviews Neuroscience, 2010.
