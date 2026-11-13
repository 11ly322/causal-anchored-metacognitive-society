# PREREGISTRATION — CAMS Audit Layer v0

> 状态：`[设计]`。本文在 live 实验之前写定；没有 live 数据。合成基准数字不能替代本文的 H1。版本：v0.1；日期：2026-11-09。

## 1. 唯一主假设

**H1（主假设）**：在相同覆盖率下，CAMS 审计层（证据指纹 + 覆盖/协方差门控）比 logprob 阈值门控使**幻觉率相对降低 ≥15%**，且 **determined rate 下降 ≤5 个百分点**。

**H0**：相对降低 <15%，或 determined rate 下降 >5pp。

不另立“更好理解”“更强推理”等主假设。ECE、覆盖率校准只作安全性/描述性检查。

## 2. 操作化定义

- **determined**：`Verdict.status == "accept"` 且输出 answer。
- **coverage**：`determined / N`。
- **hallucination**：determined 且 answer 与 ground truth 不一致（或任务要求 abstain 却 determined）。
- **hallucination rate**：`wrong_determined / determined`；determined 为 0 时记 `[TBD]`，不记 0。
- **determined rate**：同 coverage。
- **unnecessary abstention**：有效 accept 任务被拒 / 有效 accept 任务数。
- **same coverage**：在 dev split 上把 logprob 阈值校准到目标 coverage；test 上 coverage 差 >1pp 则重加权或在预注册记录中判“不匹配”，不挑选有利点。

## 3. 数据与任务

- 任务：真实工具回执（shell/browser/db）或合成回执；每任务带机器可判 ground truth。
- 训练/开发/测试：dev 用于阈值校准；test 只评一次；不得在 test 上调阈值。
- 最小样本：1,000；最大：10,000；功效不足时写 `[TBD]` 并扩样本，不事后改 H1。
- 当前仓库只有 100 题合成基准；**不是 live H1 数据**。

## 4. 功效与样本量

`[TBD]`：需要 pilot 的 p0 估计。敏感性表（待填）：

| p0（基线幻觉率） | 目标相对降低 | 预估 n/组 | 备注 |
|---|---:|---:|---|
| 0.20 | 15% | `[TBD]` | 需 pilot |
| 0.30 | 15% | `[TBD]` | 需 pilot |
| 0.40 | 15% | `[TBD]` | 需 pilot |

不伪造功效数字。样本不足时，结论只能是“未决”，不是“通过”。

## 5. 随机化与配对

- 同一任务、同一模型/decoding；审计方法顺序随机。
- 配对比较；test 集不调阈值。
- 记录 model、decoding、receipt 哈希、审计层版本、时间戳。

## 6. 统计

- 配对 bootstrap 10,000 次；单侧 p<0.05；
- 报告 95% CI 与效应量；
- 多重比较（若加辅助指标）用 Holm 或 FDR；
- 不把“p<0.05 但效应量小于预注册最小值”判为通过。

## 7. 停止规则

- 预算上限 ¥500 或 10,000 样本，先到先停；
- 中期只做预算/futility 检查，不因显著提前停；
- 负结果必须写入 `paper/note.md` 的负模板，不删。

## 8. 分析计划

1. 主分析：H1 的幻觉率相对降低 + coverage 差。
2. 安全性：F3 契约三态、F4 过度保守、F7–F10。
3. 负结果：若 H1 失败，报告效应方向、CI、样本量、失败原因。
4. 不把合成基准结果写成 live H1。

## 9. 变更记录

- v0.1：初始预注册；所有样本量/功效为 `[TBD]`。
