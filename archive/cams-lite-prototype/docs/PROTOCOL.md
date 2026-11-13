# PROTOCOL — CAMS Audit Layer v0

> 这是审计接口协议，不是认知架构，也不是模型训练说明。所有阈值是 `[设计]`；未跑 live 的数字是 `[TBD]`。

## 1. 输入

```text
AuditRequest {
  claims: Claim[],
  evidence: Evidence[],
  answer: string | null,
  escalation_path: string = "human_review"
}
```

`Evidence` 必须来自可复算的工具回执或物理测量；自然语言日志只能作为 `source` 元数据，不能单独充当 H4 的非文本叶。

## 2. 输出

```text
Verdict {
  status: "accept" | "abstain",
  answer: string | null,
  reason_code: "NO_RISK" | "INSUFFICIENT_EVIDENCE" |
               "MEASUREMENT_FAILURE" | "OUT_OF_SCOPE",
  coverage: number,
  covariance: number,
  provenance: { root_hash, evidence[], spans[] },
  contract: { contract_version, reason_code, evidence_coverage,
              provenance_summary, escalation_path, adapter_cost },
  claims: Claim[]
}
```

## 3. 不变量

- **P1 可复算**：校验和由内容计算；不可复算的 receipt 只能是 `MEASUREMENT_FAILURE`。
- **P2 支持显式**：`accept` 的每个 claim 至少一个 `supports`；空支持只能 `abstain`。
- **P3 范围匹配**：`scope` 不匹配只能是 `OUT_OF_SCOPE`。
- **P4 协方差参与**：`covariance > 0.60` 不得 `accept`；`⊥` 是事后标记，不是离散端口。
- **P5 契约稳定**：`contract` 字段与 `reason_code` 在版本内稳定；外部脚本不需要读内部协方差。
- **P6 无隐藏状态**：同一输入/回执/阈值 → 同一输出；不做随机采样。

## 4. 失败模式

| 模式 | 触发 | 外部可见结果 |
|---|---|---|
| 伪造回执 | 校验和不匹配 | `MEASUREMENT_FAILURE` |
| 缺证据 | 无 supports / 缺 id | `INSUFFICIENT_EVIDENCE` |
| 错误推理 | relation ≠ supports | `INSUFFICIENT_EVIDENCE` |
| 越界 | scope 不匹配 | `OUT_OF_SCOPE` |
| 过度保守 | 有效证据仍拒绝 | `unnecessary_abstention`（基准指标） |
| 契约泄漏 | 外部必须读内部协方差 | F10′ 失败 |

## 5. 与 H1–H4 的对应

H1 指纹 → P1；H2 支持/范围 → P2/P3；H3 协方差 → P4；H4 非文本叶 → 输入约束 + `non_text` 标志。它们不是“脑机制”，只是接口可测试条件。
