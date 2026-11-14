# Hypotheses

状态标签：`[设计]` 接口已定但未实测；`[假设]` 有可证伪方向；`[待定]` 缺数据；`[合成]` 合成/mock。这里没有 H1 的实测结论。

| id | 假设 | 状态 | 失败条件 |
|---|---|---|---|
| H1 | 在匹配覆盖率下，带 receipt 的 claim 比 no-audit 基线产生更少无依据断言 | `[假设]` | 匹配覆盖率后差异消失，或 no-audit 更好 |
| H2 | 外部消费者只读 contract 即可区分 accept / measurement / insufficient | `[设计]` | 必须读内部协方差、logprob 或 claim 全文才能区分 |
| H3 | 在 demo 威胁模型内，HMAC + nonce 能挡住随手篡改与同一 trace 内重放 | `[设计]` | 篡改/重放被 accept |
| H4 | 审计层开销可被真实调用方接受 | `[待定]` | 延迟/成本超过调用方预算，或没有可测基线 |

## H1

- 不是 CAMS 的 H1；CAMS H1 已归档，不在本仓库主张范围内。
- 需要的对照：no-audit、logprob gate、cams-lite，匹配覆盖率。
- 当前只有合成 bench/mock；没有 live 工具回执，也没有 10k 代理。

## H2

- 验收入口：[spec/GATE.md](spec/GATE.md) 的三态定义。
- `demo/consume_contract.py` 已实现独立的 contract-only 探针；只读 `decision`、`reason_code`、`detail_code` 和 `provenance_summary.verified_leaves`。
- `python tools/check_contract_consumer.py` 已核对七份实际 demo 输出、四字段投影与异常输入；消费者在没有验证器和 trace 的独立目录中运行。[合成]
- H2 的离线接口验收已通过。真实框架消费者的可靠性、版本兼容与生产效度仍为 `[待定]`；这不是 H1 的证据。

## H3

- 当前签名是 HMAC demo key；不是生产信任锚。
- 重放检测只覆盖同一 trace 内的 nonce/receipt-id；跨进程持久化见 issue #2。
- 不声称“不可伪造”。

## H4

- 需要记录每次 gate 的 CPU 时间、I/O、以及调用方延迟预算。
- 当前没有真实调用方，因此 `[待定]`。
