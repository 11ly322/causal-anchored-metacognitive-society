# Gate contract v0

状态：`[设计]`。本文件定义 receipt 如何变成三个可依赖的返回值；它不是安全证明，也不是生产策略。

## 1. 三个返回值

gate 只返回三个 `decision`：

| decision | 含义 | 典型原因 |
|---|---|---|
| `accept` | 回执有效，覆盖足够，可以接受声明 | 所有必填证据已验证 |
| `MEASUREMENT_FAILURE` | 工具/回执/测量本身失败 | hash 不匹配、签名错、过期、重放、缺工具 |
| `INSUFFICIENT_EVIDENCE` | 回执有效，但不足以支持声明 | 覆盖率低、证据缺失、超出 scope |

不把“模型不确定”当第四种状态。模型置信度不是 gate 输入。

## 2. 输入

```text
gate(policy, claims, receipts, now)
```

- `policy`：`min_coverage`、`max_age_seconds`、`future_skew_seconds`、`tool_required`、`allowed_tools`、`allowed_scopes`、`trust_domain`。
- `claims`：每个 claim 带 `claim_id`、`text`、`evidence`（receipt id 列表）、`scope`、`required`。
- `receipts`：`spec/RECEIPT.md` 定义的对象。
- `now`：生产为真实 UTC 时间；demo 可用 fixture clock，但必须显式标 `[设计]`，不能伪装成 live。

## 3. 判定顺序

任一步失败，立即返回，不继续猜。

1. **tool 缺失**：`tool_required=true` 且没有 receipt → `MEASUREMENT_FAILURE`，`detail_code=NO_RECEIPT`。
2. **receipt 验证**：逐条执行 schema、hash、signature、timestamp、nonce/receipt_id 去重。任一失败 → `MEASUREMENT_FAILURE`，沿用 receipt 错误码。
3. **claim 绑定**：每个必填 claim 的 `evidence` 必须引用已验证的 receipt id；引用不存在 → `INSUFFICIENT_EVIDENCE`，`detail_code=MISSING_EVIDENCE`。
4. **scope**：claim 的 scope 必须在 `allowed_scopes`；否则 → `INSUFFICIENT_EVIDENCE`，`detail_code=OUT_OF_SCOPE`。
5. **覆盖率**：`coverage = verified_required_leaves / required_leaves`；`coverage < min_coverage` → `INSUFFICIENT_EVIDENCE`，`detail_code=LOW_COVERAGE`。
6. **通过**：所有必填 claim 有已验证证据，scope 合法，覆盖率达标 → `accept`，`reason_code=NO_RISK`。

`min_coverage` 默认 `0.80` `[设计]`；这是演示值，不是实证最优。

## 4. Contract 对象

gate 返回给外部 agent 的对象必须自足；外部脚本不得读取 gate 内部协方差或模型置信度。

```json
{
  "contract_version": "0.1",
  "decision": "accept",
  "reason_code": "NO_RISK",
  "detail_code": null,
  "evidence_coverage": 1.0,
  "provenance_summary": {
    "receipts": [
      {
        "receipt_id": "r-accept-001",
        "tool_id": "shell.echo",
        "stdout_hash": "sha256:..."
      }
    ],
    "verified_leaves": 1,
    "required_leaves": 1
  },
  "escalation_path": "none"
}
```

字段约束：

- `decision`：三个值之一；
- `reason_code`：`NO_RISK` / `MEASUREMENT_FAILURE` / `INSUFFICIENT_EVIDENCE`；
- `detail_code`：`NO_RECEIPT`、`SCHEMA`、`INTEGRITY`、`SIGNATURE`、`STALE`、`REPLAY`、`MISSING_EVIDENCE`、`OUT_OF_SCOPE`、`LOW_COVERAGE`、`TOOL_NOT_ALLOWED` 之一或 `null`；
- `evidence_coverage`：0–1 的浮点数；无证据时为 0；
- `provenance_summary`：只放 receipt id、tool id、hash；不放模型内部状态；
- `escalation_path`：`none` / `retry_tool` / `human_review`。

## 5. 三态可分离性

外部脚本只读 contract 时，必须能区分：

- `accept`：`decision=accept`；
- `MEASUREMENT_FAILURE`：`decision=MEASUREMENT_FAILURE`；
- `INSUFFICIENT_EVIDENCE`：`decision=INSUFFICIENT_EVIDENCE`。

如果脚本必须读内部协方差、模型 logprob 或 claim 全文才能区分三态，gate 失败。[设计]

## 6. 升级与重试

- `MEASUREMENT_FAILURE` 且 `detail_code` 属于可重试的测量问题（`NO_RECEIPT`、`STALE`、`INTEGRITY`）→ `escalation_path=retry_tool`。
- `SIGNATURE` 或 `REPLAY` → `escalation_path=human_review`；不自动重试，避免把攻击当抖动。
- `INSUFFICIENT_EVIDENCE` → 不自动接受；可以补证据后重新 gate，或转人工。
- `accept` → `none`。

重试不能改变 claim 或 scope；重试只换新 receipt。

## 7. 时间与 demo

- 生产 `now` 取真实 UTC；不接受客户端自报时间。
- demo 的 `fixture_now` 只用于可复现 trace；必须在 policy 中显式 `clock_mode=fixture`，并在输出标 `[合成]`。
- 没有 fixture 时，`timestamp` 超出 `max_age_seconds` 或未来超过 `future_skew_seconds` 一律拒绝。[设计]

## 8. 不做什么

- 不判断工具输出在世界上是否为真。
- 不判断模型是否理解。
- 不做内容安全、合规、许可证或隐私判断。
- 不把多个模型的投票当证据。
- 不用“覆盖率 100%”替代“结论正确”。

## 9. 验收

- [x] `python demo/run.py --trace traces/accept.json` 返回 `accept`，退出码 0。
- [x] `traces/measurement.json` → `MEASUREMENT_FAILURE` / `STALE`。
- [x] `traces/insufficient.json` → `INSUFFICIENT_EVIDENCE` / `LOW_COVERAGE`。
- [x] `traces/fail-tampered-stdout-hash.json` → `MEASUREMENT_FAILURE` / `INTEGRITY`。
- [x] `traces/fail-replay-nonce.json` → `MEASUREMENT_FAILURE` / `REPLAY`。
- [x] `traces/fail-empty-checksum.json` → `MEASUREMENT_FAILURE` / `SCHEMA`。
- [x] `traces/fail-no-tool.json` → `MEASUREMENT_FAILURE` / `NO_RECEIPT`（`tool_required=true` 时）。
- [ ] 外部脚本只读 contract 能区分三态（见 issue #3；H2 仍为 `[设计]`）。

没有 live 运行前，以上是本地 fixture 验收，不是 live 实测。[待定]
