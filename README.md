# agent-audit-kernel

一个可离线运行的审计原语：**工具回执 + 覆盖率门控 + 可依赖的拒绝契约**。

它不是通用模型，不是三层认知架构，也不是已验证的产品。当前是一个可评审、可离线复现的最小原型；没有 live 结果。

## 赌注

在错误代价高、需要审计的窄场景里，**门控外部工具回执**比**让模型自报置信度**更可靠。[假设]

外部回执提供可验证字段：工具 ID、退出码、stdout 哈希、输入摘要、nonce、时间戳、签名。在可信根下，模型不能单独伪造这些字段；demo 的 HMAC 只演示绑定。门控只决定三件事：

- `accept`：回执完整且覆盖足够；
- `MEASUREMENT_FAILURE`：工具或回执本身坏了；
- `INSUFFICIENT_EVIDENCE`：回执有效，但不足以支持结论。

关键不是多一个分类器，而是让“拒绝”变成外部 agent 可以依赖的结构化返回值。

## 不声称什么

- 不声称已证明该赌注；这是待检验假设，不是结果。[待定]
- 不声称“不可伪造”；只声称在可信根下可防篡改，且 demo 级 HMAC 仅用于演示。[设计]
- 不声称能替代通用大模型、通用对齐或安全审计。
- 不声称归档里的 pytest 覆盖率、合成 bench 或 mock 10k 是效度证据。[合成]
- 不声称能处理真实生产流量；没有 nonce 存储、密钥轮换、时钟同步和撤销机制。

## 最小数据流

```text
tool call
  -> receipt {receipt_id, tool_id, exit_code, stdout_hash,
              nonce, timestamp, signature, input_digest}
  -> verifier (trust root)
  -> gate (coverage + integrity + freshness)
  -> accept | MEASUREMENT_FAILURE | INSUFFICIENT_EVIDENCE
  -> contract {reason_code, evidence_coverage,
               provenance_summary, escalation_path}
```

- 回执是证据，不是模型自述。
- 门控只消费回执和声明，不消费模型内部置信度。
- 契约是给下一个 agent 的返回值，不是日志注解。

## 怎么跑

命令：

```bash
python demo/run.py --trace traces/accept.json
```

- 只依赖 Python 标准库；不联网，不装包。
- 7 条轨迹已落盘：3 条黄金（accept / measurement / insufficient）+ 4 个失败（篡改 stdout_hash、重放 nonce、空 checksum、无工具降级）。
- 全部返回预期结果；当前是 fixture clock + HMAC demo key，不是 live 安全证明。

**当前状态（Day 7，终检）：** 7 条轨迹均通过；新克隆可离线复现；契约字段见 `spec/GATE.md`。公共面：PR #1（draft，未合并）与 issues #2–#4；验收结果与七天清单位于 [`CHECKLIST.md`](CHECKLIST.md)。

| trace | 预期 |
|---|---|
| `traces/accept.json` | accept |
| `traces/measurement.json` | MEASUREMENT_FAILURE / STALE |
| `traces/insufficient.json` | INSUFFICIENT_EVIDENCE / LOW_COVERAGE |
| `traces/fail-tampered-stdout-hash.json` | MEASUREMENT_FAILURE / INTEGRITY |
| `traces/fail-replay-nonce.json` | MEASUREMENT_FAILURE / REPLAY |
| `traces/fail-empty-checksum.json` | MEASUREMENT_FAILURE / SCHEMA |
| `traces/fail-no-tool.json` | MEASUREMENT_FAILURE / NO_RECEIPT |

## 仓库地图

```text
README.md                 本页
spec/RECEIPT.md           回执契约、信任根、重放/新鲜度
spec/receipt.schema.json  可直接实现的 JSON schema
spec/GATE.md              accept / MEASUREMENT_FAILURE / INSUFFICIENT_EVIDENCE
demo/run.py               离线 demo，stdlib only
traces/                   黄金轨迹 + 失败轨迹
HYPOTHESES.md             H1–H4 与 falsifier
OPEN.md                   还不知道什么
CHECKLIST.md              七天清单与终检记录
archive/                  旧设计、旧原型、旧理论（非当前承诺）
```

## 证据标签

- `[设计]`：预注册的设计选择或阈值，不是结果。
- `[假设]`：待检验判断。
- `[待定]`：尚无数据或实现。
- `[合成]`：合成数据/mock，只用于演示，不是效度。

没有 `[实测]` 标签；当前没有 live 数据。

## 接走方式

对外只承诺一个窄接口：

1. 调用方给工具回执与声明；
2. kernel 返回一个 `contract`；
3. 调用方只读 `contract` 就能区分“可接受 / 证据不足 / 测量失败”。

如果调用方必须读内部协方差或模型置信度才能区分，这个接口就失败了。[设计]

## 历史

旧 CAMS v5.0 文档、审计层原型、bench、paper 和理论笔记都在 [`archive/`](archive/README.md)。它们保留用于溯源，不是当前 API，也不应作为结果引用。

## License

MIT；见 [`LICENSE`](LICENSE)。
