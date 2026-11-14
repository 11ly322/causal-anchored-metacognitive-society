# Receipt contract v0

状态：`[设计]`。本文件定义一个工具回执的最小契约；它不是模型置信度，不是安全证明，也不是生产协议。

## 1. 范围

一个 receipt 对应**一次工具调用**，不是一次模型回答。

它要回答四个问题：

1. 哪个工具被调用了；
2. 工具返回什么、退出码是什么；
3. 返回内容有没有被改动；
4. 这条回执是不是这次调用产生的、而不是重放的。

本契约**不**回答：

- 工具本身是否可信；
- 工具输出是否在世界上为真；
- 模型是否“理解”了输出；
- 调用方的业务规则是否合理。

这些属于 gate、claim 和外部审计，不属于 receipt。

## 2. 字段

| 字段 | 类型 | 必填 | 规则 |
|---|---|---|---|
| `receipt_id` | string | 是 | 8–128 字符，`[A-Za-z0-9._:-]`；每次调用唯一 |
| `tool_id` | string | 是 | 1–128 字符；稳定的工具标识，不是显示名 |
| `exit_code` | integer | 是 | 0–255；工具进程的真实退出码 |
| `stdout_hash` | string | 是 | `sha256:<64 hex>`；对 stdout **原始字节**的 SHA-256 |
| `nonce` | string | 是 | 16–64 字符；至少 128 bit 随机；每次调用新生成 |
| `timestamp` | string | 是 | RFC 3339 / ISO 8601，带 UTC `Z`；签名时间，不是文件修改时间 |
| `signature` | string | 是 | `hmac-sha256:<hex>` 或 `ed25519:<base64>`；覆盖 §3 的规范字节 |
| `input_digest` | string | 是 | `sha256:<64 hex>`；对工具调用的规范输入摘要 |
| `stderr_hash` | string | 否 | 同 `stdout_hash`；只用于诊断 |
| `metadata` | object | 否 | 扩展字段；**不参与**信任判断 |

空字符串不是“通过”。空 `stdout_hash`、空 `nonce`、空 `signature` 一律拒绝。

## 3. 规范字节与签名

签名者计算：

```text
canonical = UTF-8(JSON with sorted keys, no extra whitespace,
                  all fields except signature)
message   = b"agent-audit-receipt-v1\n" + canonical
signature = HMAC-SHA256(key, message)          # demo
          = Ed25519(private_key, message)      # production target
```

约束：

- 键排序必须是字典序；数组保持原顺序。
- 不做 Unicode 归一化；统一按 UTF-8 字节。
- 不把 `signature` 字段本身放进 `canonical`。
- 不把 `metadata` 当作证据；验证方可忽略，签名仍覆盖它，因为它是回执的一部分。

**演示级信任根。** demo 使用 HMAC 共享密钥，密钥来自 `CAMS_DEMO_HMAC_KEY`；未设置时使用公开的 `demo-key-not-secret`。这只能演示“绑定与篡改检测”，不能证明来源，也不能防持有密钥的一方。[设计]

**生产目标。** 使用非对称签名（Ed25519 或 ECDSA P-256），公钥通过独立 trust root 分发；密钥轮换、撤销、时钟同步不在本文件范围。[待定]

## 4. 输入与输出绑定

`input_digest` 的计算对象是规范输入：

```text
{
  "tool_id": "...",
  "args": [...],
  "stdin": "..." | null
}
```

排序键后 UTF-8，再 SHA-256。

`stdout_hash` 对工具 stdout 的原始字节计算；不先做 JSON 解析，不先 trim，不先换行归一化。

`exit_code != 0` 不自动等于“无证据”：它可能是有意义的失败结果。gate 负责解释退出码；receipt 只记录事实。

## 5. 新鲜度与重放

- `timestamp` 必须是 UTC；默认接受窗口为 `now ± 300s`。[设计]
- 未来时间超过 `+60s` 直接拒绝，避免时钟漂移掩盖重放。[设计]
- `nonce` 在同一 trust domain 内一次性使用；重复 nonce 拒绝。
- `receipt_id` 也应去重；重复 id 视为 replay 或实现错误。
- demo 只在进程内保存 nonce 集合；进程重启后不保留。生产需要持久化 nonce/ID 存储和过期清理。[待定]
- 仅有合法签名、但 nonce 已见过的回执，仍然拒绝。

## 6. 验证顺序

验证器必须按顺序做，任一步失败即拒绝：

1. JSON 可解析，字段集合符合 schema；
2. 必填字段非空，类型正确；
3. `stdout_hash`/`input_digest` 格式合法；
4. 重算 `stdout_hash` 与 `input_digest`；
5. 按 §3 重算签名并比较；
6. 检查 `timestamp` 窗口；
7. 检查 `nonce`/`receipt_id` 是否已使用；
8. 返回 `verified` 或结构化错误码。

错误码：

| 错误码 | 含义 |
|---|---|
| `SCHEMA` | 缺字段、类型错、空值 |
| `INTEGRITY` | hash 不匹配 |
| `SIGNATURE` | 签名不匹配 |
| `STALE` | 时间窗外 |
| `REPLAY` | nonce 或 id 已使用 |
| `NO_RECEIPT` | 需要回执但没有 |

## 7. Gate 需要的输入

gate 不应读取模型内部置信度来决定 receipt 是否有效。它只消费：

- `receipt`（本文件）；
- `claim`（被支持的断言）；
- `coverage`（claim 覆盖了哪些证据叶）；
- `scope`（声明适用范围）；
- `policy`（阈值、时间窗、允许的 tool_id）。

gate 的输出与详细判定在 `spec/GATE.md`。

## 8. 安全边界

本契约在可信根下提供：

- 内容完整性：改动 stdout 会导致 hash/签名失败；
- 来源绑定：签名覆盖 receipt 字段；
- 新鲜度：时间窗与 nonce 降低重放；
- 可追溯：receipt_id/tool_id/input_digest 可被外部引用。

本契约**不**提供：

- 工具真实性（工具可能撒谎）；
- 输出在世界上的真实性；
- 密钥保密（HMAC 共享密钥尤其不是）；
- 生产级持久化、撤销、轮换、审计合规；
- 对恶意签名者的防护（持有密钥者可以签任何东西）。

## 9. 演示与生产

| 项 | demo | 生产目标 |
|---|---|---|
| 签名 | HMAC-SHA256 共享密钥 | Ed25519/ECDSA，公钥 trust root |
| nonce 存储 | 进程内 set | 持久化、TTL、跨实例 |
| 时间窗 | ±300s | 按部署校准，监控时钟漂移 |
| 密钥 | 公开 demo key / env | KMS/HSM，轮换与撤销 |
| 生态 | 单机离线 | 多租户、审计、限流 |

## 10. 验收

- [ ] `spec/receipt.schema.json` 能校验所有 golden trace。
- [ ] 空 `stdout_hash`、空 `nonce`、空 `signature` 均拒绝。
- [ ] 改动 stdout 一个字节，`INTEGRITY` 失败。
- [ ] 改动任一签名字段，`SIGNATURE` 失败。
- [ ] 同一 nonce 第二次提交，`REPLAY` 失败。
- [ ] 时间窗外，`STALE` 失败。
- [ ] 验证器不读取模型置信度。

没有 live receipt 之前，以上只是设计验收，不是实测。[待定]
