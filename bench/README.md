# AgentAudit-Bench v0

100 个合成审计任务，7 类泄漏，50/50 dev/test。**这是 `[实测-合成]`，不是 live H1。**

## 任务

- `sensor_lie`（15）：回执无效/错误；
- `bad_reasoning`（14）：证据有效但 relation 是 `non_sequitur`；
- `minority_evidence`（14）：多数/少数证据冲突；审计层可能仍接受错误答案（已知泄漏）；
- `precision_bias`（14）：`selection_bias` 支持关系；
- `ood`（14）：scope 不匹配；
- `overconservative`（15）：有效证据、低置信度；拒绝是成本；
- `quality_gaming`（14）：伪造校验和。

每题 JSON 含 `prompt`、`tool_receipts`、`candidate`、`ground_truth`、`checker`。`ground_truth.expected` 为 `accept` 或 `abstain`。

## 运行

```bash
python bench/run.py --split test
python bench/run.py --split test --subset 10
python bench/score.py bench/results/benchmark.json
```

方法：

- `no_audit`：全接受；
- `logprob_gate`：dev 校准到 coverage 0.80 的置信度阈值；
- `cams_lite`：证据指纹 + 覆盖 + 协方差门控。

## 当前合成结果

见 `bench/results/benchmark.json`。这些数字只说明代码在构造任务上的行为；不证明外部效度，也不是 H1 的 live 结果。

## 已知限制

- 语义蕴含没有被审计层解决；`minority_evidence` 会暴露这一点。
- 置信度基线没有真实 logprob；它用 `candidate.confidence` 模拟，明确标为 `[假设]`。
- 100 题是 v0，不是 10³/10⁴ 主实验。
