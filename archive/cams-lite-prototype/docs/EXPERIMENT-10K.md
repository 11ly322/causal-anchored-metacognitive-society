# EXPERIMENT-10K — audit-layer protocol

> 这是审计层的 10³/10⁴ 协议，不是 0.1B 模型实验，也不是政治模拟。当前无 live 数据。

## 1. 10³ 审计任务

- 1,000 个任务/回执；7 类泄漏；每类 ≥100；
- 3 个固定种子；5 个基线（no-audit、logprob、cams-lite、A-skeleton、contract-only）；
- 每个任务必须有机器可判的 ground truth 和 receipt 哈希；
- 生成/评分脚本在 `bench/` 与 `experiments/`。

## 2. 指标

- coverage = determined / N；
- hallucination rate = wrong determined / determined；
- unnecessary abstention = valid accept task 被拒 / 有效任务数；
- 契约三态准确率 = 外部脚本仅读 `contract` 的正确分类 / N；
- 复算一致率。

## 3. 10³ → 10⁴ 门槛

- F1 相对降低 ≥15%（匹配 coverage）；
- F3 ≥0.90；
- F4 ≤10%；
- F5 100%；
- 任一失败：停在 10³，写负结果，不扩 10⁴。

## 4. live 实验

需要真实工具回执（shell/browser/db）和 provider 预算；没有则 `[TBD]`。不得用合成任务冒充 live H1。

## 5. 停止规则

预算 ¥500 或 10,000 样本；中期只做预算/futility 检查；不因显著提前停。负结果必须落盘。
