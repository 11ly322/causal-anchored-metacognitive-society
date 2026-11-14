# CAMS Audit Layer — design note

> **状态**：[设计] 研究原型，不是已完成的认知架构，不是模型能力主张，不包含 0.1B 训练或 100B 部署。
>
> 这个仓库只做一个窄问题：**当 Agent 给出一个答案时，外部能否只依赖它返回的证据对象，判断“可接受 / 证据不足 / 测量失败 / 越界”？** 能，才算可审计；不能，就只是另一个置信度分数。

## 1. 问题

通用 Agent 的输出通常只有文本和置信度。外部系统无法区分：

- 证据是真的，推理也成立；
- 证据是真的，但推理不成立；
- 证据是伪造的，或回执被篡改；
- 证据来自另一个分布/范围；
- 模型只是“看起来很确定”。

后验检测（再训一个判别器、投票、自我一致性）不能从结构上排除这些路径。CAMS 的选择是把“可审计”放到输出接口上，而不是事后猜测。

## 2. 审计层的最小机制

### 2.1 证据指纹

每个工具回执变成一个 `Evidence`：

```text
evidence_id, source, content, checksum, valid, scope, non_text
```

`checksum` 必须能由内容复算；不一致就是 `MEASUREMENT_FAILURE`，不是“低置信度”。

### 2.2 溯源树

每个答案由若干 `Claim` 组成，每个 `Claim` 显式声明 `supports`（证据 id 列表）。`ProvenanceTree` 只验证：

- 证据存在；
- 校验和一致；
- claim 的 relation 是 `supports`（不是 `non_sequitur` / `selection_bias`）；
- scope 匹配；
- 覆盖率为 1。

它**不**做语义蕴含判断。这个限制是公开的：一个有效哈希仍可能支持错误结论；基准把这个泄漏路径保留下来，不假装消灭。

### 2.3 覆盖 + 协方差门控

`coverage_gate` 输出两类结果：

- `accept`：所有 claim 验证通过，coverage ≥ 0.80，covariance ≤ 0.60；
- `abstain`：否则。

`⊥` 不是离散输出端口，而是 `covariance > τ_cov` 的事后标记；每层始终输出分布，门控消费这个分布。

### 2.4 结构化拒绝契约

拒绝不是空值，而是稳定对象：

```json
{
  "contract_version": "1.0",
  "reason_code": "INSUFFICIENT_EVIDENCE",
  "evidence_coverage": 0.0,
  "provenance_summary": "sha256:...",
  "escalation_path": "human_review",
  "adapter_cost": 0.0
}
```

`reason_code` 只有四个：`NO_RISK`、`INSUFFICIENT_EVIDENCE`、`MEASUREMENT_FAILURE`、`OUT_OF_SCOPE`。外部脚本必须能只读这个对象区分三态；需要读内部协方差才算区分，则契约失败（F10′）。

## 3. 协议不变量（H1–H4）

| 编号 | 不变量 | 可观察失败 |
|---|---|---|
| H1 | 证据指纹可由内容复算；不可伪造 | 校验和不匹配却被接受 |
| H2 | 每个接受 claim 有显式支持与 scope | 无 supports 仍输出答案 |
| H3 | 协方差参与门控，不是事后日志 | 高协方差仍 determined |
| H4 | 至少一个非文本叶（工具回执/物理测量） | 纯文本自证被接受 |

这些是**审计接口约束**，不是“脑机制”。把它们写成 H1–H4 只是为了可测试。

## 4. 可观察输出

每次调用返回：

```text
status, answer, reason_code, coverage, covariance,
provenance.root_hash, contract{...}, claims[]
```

审计日志可以复算：同一输入 + 同一 receipt 哈希 → 同一 `Verdict`。没有随机采样、没有隐藏状态。

## 5. 证伪

主假设 H1（见 [`PREREGISTRATION.md`](PREREGISTRATION.md)）：

> 在相同覆盖率下，协方差/覆盖门控比 logprob 阈值使幻觉率相对降低 ≥15%，且 determined rate 下降 ≤5 个百分点。

失败条件：

- 相对降低 <15%，或 determined rate 下降 >5pp；
- 外部脚本不能只读 `contract` 区分三态；
- 去掉 H1–H4 的骨架与完整审计层无可区分差异；
- 合成基准的收益不能迁移到 live 回执。

合成基准（100 题）只用于代码行为回归，**不**作为 H1 的 live 证据。

## 6. 10³ 与 10⁴

- **10³**：1,000 个审计任务/回执，3 seeds，检查 `contract` 三态、覆盖率、错误接受；
- **10⁴**：在 10³ 通过后，扩到 10,000 个任务；
- **live**：需要真实工具回执和 provider 预算；没有就写 `[TBD]`，不填假数。

## 7. 它不是什么

- 不是“理解”的证明；
- 不是 0.1B 模型训练方案；
- 不是 100B 智能体社会；
- 不是政治管理模拟；
- 不是另一个置信度分类器。

它只是一个可失败、可复算的审计层。若它不能降低错误接受率，就应被丢弃。

## 8. 代码与文档

- 代码：`cams_lite/`、`tests/`、`examples/`
- 基准：`bench/`
- 预注册：`PREREGISTRATION.md`
- 协议：`docs/PROTOCOL.md`
- 可选三层说明：`docs/APPENDIX-OPTIONAL.md`

## 9. 许可证

MIT。
