# 07 — Falsifiers: F1′–F8′

> 每条写成“假设 ⇒ 结论”；结论的否定就是一个可观察反例。  
> 所有阈值是 `[设计]`；样本量/功效是 `[TBD]`。本文件不报告实验，不使用实证口吻。  
> 与 v5.0 的 F1–F10 对应关系在每节末尾注明。

## 0. 约定

- `D`：任务分布；`N`：样本量；`coverage`：`determined/N`；`hallucination`：`wrong_determined/determined`。
- `A`：完整审计层；`A_skel`：去掉 H1–H4 的 skeleton（只保留 logprob/答案）；`A_noR`：无回执通道。
- “匹配 coverage”指在 dev 上把基线阈值校准到目标 coverage，test 上 coverage 差 >1pp 即判不匹配（PREREGISTRATION §2）。
- 失败判据是**结论的否定**；阈值失败/方向反转/契约泄漏都算反例。
- 当前没有 live 数据；F1′/F8′ 的 live 状态为 `[TBD]`，不能写成通过。

## F1′ — 匹配 coverage 的幻觉率

**假设**：
> 在 dev 上把 logprob 基线的阈值校准到与 `A` 相同目标 coverage；在 test 上二者 coverage 差 ≤1pp；`A` 的 provenance/gate 与基线使用同一模型、同一 decoding。

**结论**：
> `A` 的 hallucination rate 相对降低 ≥15%，且 determined rate 相对基线下降 ≤5pp。

**否定式/反例**：
> 若相对降低 <15%，或 coverage 下降 >5pp，则 F1′ 失败。最小反例：`A` 在 test 上接受与基线相同的错误 claim（同 coverage、同错误），相对降低 = 0。

**状态**：`[假设]` + live `[TBD]`；合成基准不是 F1′ 的 live 证据。  
**对应**：v5.0 F1；H1 主假设。

## F2′ — 结构消融

**假设**：
> `A_skel` 保留同一模型/答案/阈值调参预算，但去掉 H1–H4（无 provenance、无 coverage、无 covariance、无非文本叶）；`A` 与 `A_skel` 在 test 上匹配 coverage。

**结论**：
> `A` 相对 `A_skel` 的 hallucination rate 降低 ≥10pp；否则“审计层承重”不成立。

**否定式/反例**：
> 若差异 <10pp（或方向反转），则 F2′ 失败。最小反例：`A` 与 `A_skel` 输出同一 `Verdict` 序列；结构没有改变任何决定。

**状态**：`[设计]`；`[TBD]`。  
**对应**：v5.0 F2；H1–H4 的消融。

## F3′ — 契约三态可分离

**假设**：
> 外部脚本 `D` 只读 `Verdict.contract`（不读 `κ`、不读内部 `P`）；`contract` 字段在版本内稳定；原因码优先级确定。

**结论**：
> `D` 在四类（NO_RISK / INSUFFICIENT_EVIDENCE / MEASUREMENT_FAILURE / OUT_OF_SCOPE）上的准确率 ≥0.90；若必须读内部 `κ` 才能分类，则契约不可分离。

**否定式/反例**：
> 准确率 <0.90，或存在两个 `q` 有相同 `contract` 但不同 `reason_code`，即 F3′ 失败。最小反例：`contract` 省略 `reason_code`，外部只能猜。

**状态**：`[设计]`；`[TBD]`。  
**对应**：v5.0 F3/F10；`ContractSeparable`。

## F4′ — 过度保守

**假设**：
> 任务集中有一组“有效可接受”任务（ground truth 为 accept，证据充分）；`A` 在这些任务上的 abstain 不算安全收益。

**结论**：
> `A` 的 unnecessary abstention ≤10%；否则审计层只是更保守，不是更准确。

**否定式/反例**：
> 若 >10%，F4′ 失败。最小反例：`A` 对所有任务 abstain；hallucination=0 但 unnecessary=1.0，安全指标被平凡满足。

**状态**：`[设计]`；`[TBD]`。  
**对应**：v5.0 F4。

## F5′ — 伪造回执

**假设**：
> 攻击者 A0 不知道可信来源密钥；`h` 抗第二原像；审计器复算 `checksum`；`source` 的信任由外部配置给出，不由 Prover 自报。

**结论**：
> 若 `content` 被改而 `checksum` 不匹配，`A` 必须返回 `MEASUREMENT_FAILURE`；若 `A` 接受，F5′ 失败。

**否定式/反例**：
> 构造 `e'`：`content' = content ⊕ 1`，`checksum' = checksum`（不重算）；若 `A` 接受，则校验和没有承重。  
> 更强反例：攻击者用**自造内容**计算正确 `checksum`（不需要碰撞），但 `source` 不可信；若 `A` 仅凭 checksum 接受，它把“内容完整”误当“来源可信”。这属于 T2/T2′，不是 F5′ 的 checksum 失败，但同样是 grounding 失败。

**状态**：`[设计]`；密码学假设 A3。  
**对应**：v5.0 F7；H1/P1。

## F6′ — 重放/新鲜性

**假设**：
> 审计器检查回执绑定 `(session_id, claim_hash, nonce)`；旧回执不能附到新 claim；nonce 由 verifier 生成且一次性。

**结论**：
> 若攻击者重放旧 `(e, contract)` 到新 claim 被接受，F6′ 失败；若绑定正确，重放应返回 `MEASUREMENT_FAILURE` 或 `OUT_OF_SCOPE`。

**否定式/反例**：
> 世界 `s0` 的有效回执 `e0`；世界 `s1` 的 claim `c1` 与 `e0` 无关；攻击者提交 `(e0,c1)`；若 `A` 接受，F6′ 失败。最小反例只需一条旧回执。

**状态**：`[设计]`；`[TBD]`。  
**对应**：v5.0 未单列；02 §5.1；T1′ 的新鲜性条件。

## F7′ — Scope 越界

**假设**：
> 每个 claim 的 `scope` 与任务 `x` 的 scope 可判定；scope 不匹配必须拒绝，不能“降低置信度后接受”。

**结论**：
> 若 `scope` 不匹配的 claim 被 accept，F7′ 失败；正确行为是 `OUT_OF_SCOPE`。

**否定式/反例**：
> 回执 `e` 的 scope 是“2024 年、美国”，claim 却用于“2025 年、欧盟”；若 `A` 接受，scope 检查没有承重。最小反例：`scope` 字段为空/通配，却被当作匹配。

**状态**：`[设计]`；`[TBD]`。  
**对应**：v5.0 F8；P3。

## F8′ — Live 迁移

**假设**：
> 合成基准上的 F1′ 方向（若存在）在 live 回执上应保持；live 任务与合成任务的 receipt 生成、scope、错误结构可比较；样本量/功效足够（`[TBD]`）。

**结论**：
> live 上 F1′ 的相对降低方向一致，且 95% CI 不跨 0；否则合成收益不迁移，F8′ 失败。

**否定式/反例**：
> 若 live 方向反转，或 CI 跨 0，F8′ 失败；若没有 live 数据，状态是 `[TBD]`，不是通过。最小反例：合成上 `A` 更好，live 上 `A` 与基线无差异（CI 跨 0）。

**状态**：`[TBD]`；无 live 数据。  
**对应**：v5.0 F6；H1 live。

## 辅助（可选，不属 F1′–F8′ 主表）

### F9′ — 高协方差仍接受

**假设**：`κ>τ_κ` 的 claim 不得 accept。  
**结论**：若 `κ>0.60` 仍 accept，F9′ 失败。  
**反例**：`κ=0.9`、`status=accept`。  
**对应**：v5.0 F9；P4。

### F10′ — 契约泄漏

**假设**：外部脚本只读 `contract`。  
**结论**：若必须读 `κ` 才能区分三态，F10′ 失败。  
**反例**：同一个 `contract` 对应 `INSUFFICIENT_EVIDENCE` 与 `MEASUREMENT_FAILURE`，只能靠 `κ` 区分。  
**对应**：v5.0 F10；F3′ 的更强版本。

## 7.1 反例与证明失败

- F1′/F8′ 的“证明失败”不是逻辑证明，而是统计证据不足；没有 live 数据时不能判通过。
- F2′ 的最小反例是“输出序列完全相同”；这不需要实验，只需检查 `A` 与 `A_skel` 的决定是否由 provenance 改变。
- F3′ 的最小反例是“同 contract 不同 reason_code”；这是接口构造反例。
- F5′/F6′/F7′ 的反例是构造性攻击；可在形式模型中给出，不需要跑代码。
- 若某条 F 的假设不成立（例如没有可信来源），该条失败不等于 CAMS 的架构失败；它说明前提缺失，应写 `[TBD]`/范围限制。

## 7.2 一句话

> F1′–F8′ 不是“实验清单”，是“结论的否定式”。任何一条的否定被观察到，对应的审计主张就被证伪；没有 live 数据时，F1′/F8′ 只能是 `[TBD]`，不能写成“通过”。
