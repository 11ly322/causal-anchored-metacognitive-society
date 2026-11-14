# 02 — Adversary model and security definitions

> 先定义攻击者能做什么，再谈 provenance 保证。  
> 本文件不给“CAMS 安全”的结论；它给条件：在哪些假设下，审计层的哪条性质成立；在哪些假设下，任何审计层都不可能成立。

## 1. 参与者

| 角色 | 能力 |
|---|---|
| `Prover` | 产生 claim、选择提交哪些 evidence、生成 `Verdict` |
| `Verifier` | 只读 `q=(x,e,c,a)` 与 `contract`，按 `A` 判定 |
| `Source_i` | 产生 `R` 回执；可有独立密钥/身份 |
| `World` | 决定 claim 的真值 `g_s(c)`；审计器不可直接读 |
| `Adversary` | 控制 Prover 与至多 `k` 个 Source；可选择文本、重放旧回执、合谋、选择性报告 |

审计器的输入不包含 `s`；它只包含 `q`。这是 T2 的信息论起点。

## 2. 攻击者能力等级

### A0 — Text forger

- 可生成任意字符串/claim/contract 文本；
- 不能计算 `h` 的第二原像（A3）；
- 不能伪造未知密钥的 MAC/签名；
- 不能产生新的非文本回执（没有传感器/工具访问）。

A0 是“纯文本不可认证”的最小对手。

### A1 — Replayer

在 A0 基础上：

- 可截获并重放任何以前被接受的 `(e, contract, claim)`；
- 可把旧回执附到新 claim 上；
- 不能改变回执内容而不破坏校验和。

A1 是“没有新鲜性绑定”的对手。

### A2 — Colluder(k)

在 A1 基础上：

- 控制至多 `k` 个来源；
- 被控来源可签/证明任意内容；
- 未被控来源仍诚实。

`k` 是信任阈值参数。若 `k` 等于全部来源，grounding 不可能；若存在至少一个诚实来源且 claim 必须由它支持，则可能。

### A3 — Selector

在 A2 基础上：

- 可选择提交证据的子集；
- 可省略不利回执；
- 不能伪造被省略回执的内容，但 Verifier 看不到它们。

A3 是 coverage 语义的关键对手：coverage 只覆盖“已提交”的证据。

### A4 — Adaptive

在 A3 基础上：

- 知道审计器版本、阈值、`contract` 格式；
- 可查询审计器（黑盒），但不能读其内部 `κ`/权重；
- 可针对固定阈值做最优文本。

A4 不允许读 `s`；否则审计问题退化。

## 3. 安全游戏

### 3.1 Grounding forgery game `G_ground(A, Adv)`

1. 挑战者采样 `s ← μ`，计算真值 `g_s`；
2. `Adv` 产生 `q`（可自适应，但不能读 `s` 的隐藏位）；
3. `A(q)` 返回 `Verdict`；
4. `Adv` 赢，若 `Verdict.status=accept` 且 `g_s(c_root)=0`。

定义 `Adv` 的优势

```text
Adv_ground(A, Adv) = Pr[win] - Pr[win | g_s(c_root)=1]
```

若 `A` 只做 provenance 检查，`Adv_ground` 可以很高；v5.0 不声称 `Adv_ground=0`。T2 说明在纯文本、无可信锚点时，任何 `A` 都有 `Adv_ground ≥ 1/2`（在对称先验下），除非它拒绝所有。

### 3.2 Receipt forgery game `G_receipt(A, Adv)`

1. 挑战者生成新回执 `e*`，内容 `m*`，`checksum=h(m*)`；
2. `Adv` 提交 `e'`，声称 `content'≠m*` 但 `checksum'=h(m*)`；
3. `A` 接受 `e'` 即 `Adv` 赢。

在 A3（抗第二原像）下，`Adv` 的优势是可忽略的；若 `h` 可碰撞，H1/P1 失效。这是密码学假设，不是 CAMS 的贡献。

### 3.3 Replay game `G_replay(A, Adv)`

1. 挑战者生成旧回执 `e_old` 对应世界 `s_old`，旧 contract `contract_old`；
2. 挑战者切换到新世界 `s_new`，其中 `g_{s_new}(c)=0`；
3. `Adv` 提交 `(e_old, contract_old, c)`，把旧回执附到新 claim；
4. `A` 接受即 `Adv` 赢。

若 `e_old` 不含 `session/nonce/claim_binding`，则 `A` 无法区分重放。定理/命题：**无新鲜性绑定的回执通道对 A1 不安全**（构造见 §5.1）。

### 3.4 Collusion game `G_collude(A, Adv, k)`

1. `Adv` 控制 `k` 个来源；
2. 其余来源诚实，但 `Adv` 可选择只让被控来源出现在 `q` 中；
3. `A` 接受一个仅由被控来源支持的假 claim 即 `Adv` 赢。

若 `k = |Sources|`，任何只读 `q` 的 `A` 都无法区分“全体合谋”与“真实世界”；这是信息论下界。若存在至少一个诚实来源且 claim 必须由它支持，则可通过来源阈值/多重签名降低优势，但不能消除 `k` 以内的合谋。

### 3.5 Selective reporting game `G_select(A, Adv)`

1. 世界 `s` 产生一组回执 `E_all`，其中一部分支持 `c`，一部分反驳 `c`；
2. `Adv` 选择 `E_sub ⊆ E_all` 提交；
3. `A` 看到 `coverage(E_sub)` 高，接受 `c`；
4. `Adv` 赢，若 `c` 在 `E_all` 下为假但 `A` 接受。

命题：**coverage 不能证明世界覆盖**；除非增加“完整性审计”（谁应该提交、遗漏检测、第三方见证）。这是 T2′ 的构造核心。

### 3.6 Contract game `G_contract(A, D)`

1. 外部脚本 `D` 只读 `contract`；
2. 对每个 `q`，`D` 要输出四类之一；
3. `D` 的准确率 `<0.90` 或需要读 `κ` 即失败（F3/F10′）。

`ContractSeparable(A)` 是 `G_contract` 的存在性条件；它是接口性质，不是安全性质。一个 contract 可以完全可分离，但仍然被 A3 选择性报告欺骗。

## 4. 安全定义（条件式）

| 定义 | 条件 | 保证 | 不保证 |
|---|---|---|---|
| `ProvSound` | `VerifyE/VerifyP` 正确、`τ_c,τ_κ` 固定 | 接受的 claim 有可复算的回执/范围/覆盖 | claim 语义为真 |
| `ReceiptAuth` | A3 哈希 + 来源签名/MAC + 新鲜性 | 回执未被篡改/重放 | 来源本身诚实 |
| `GroundSound` | 存在可信锚点 + 完整性 + 诚实来源 | 接受 ⇒ 世界真值 | 纯文本、无锚点时不可能（T2） |
| `ContractSep` | 原因码优先级确定、contract 字段足够 | 外部四分类 | 分类正确性依赖输入真实 |
| `CoverageFaithful` | 完整性假设 A4 + 遗漏审计 | coverage 接近世界覆盖 | 无完整性时只是提交覆盖（T2′） |

**重要**：v5.0 只公开声称 `ProvSound`、`Repro`、`ContractSep`；`GroundSound` 不是 v5.0 的承诺。把 `ProvSound` 当成 `GroundSound` 是范畴错误（ledger N1）。

## 5. 最小反例

### 5.1 重放反例（无新鲜性）

世界 `s0`：真实回执 `e0` 说“账户余额 100”。世界 `s1`：余额 0，但攻击者重放 `e0`。若 `e0` 不含 `session_id` 或 `claim_hash`，Verifier 看到 `VerifyE(e0)=1`、`supports` 指向 claim“余额 100”，会接受。`e0` 的校验和完全正确；问题不在完整性，而在**绑定**。

修复条件：回执必须绑定 `(session, claim_hash, nonce)`；仅签名内容不够。

### 5.2 选择性报告反例（coverage 欺骗）

世界产生 10 条回执：6 条支持 `c`，4 条反驳 `c`。攻击者只提交 6 条支持回执；`coverage=1.0`（相对于提交集合），`VerifyP` 通过。若任务规范要求全部 10 条，`Req(q)` 是 10，coverage 应为 0.6；但攻击者可以声称 `Req(q)` 只有 6 条。**没有外部完整性锚点，Verifier 无法区分“任务只要求 6 条”与“攻击者藏了 4 条”。**

修复条件：任务规范/第三方见证/遗漏审计；仅靠审计层内部 coverage 不够。

### 5.3 全体合谋反例（k=n）

若所有来源都被 A2 控制，它们可以对假 claim 生成自洽的回执、哈希、scope、coverage。Verifier 只读 `q`，看到的分布与真实世界不可区分（在来源能力对称时）。这是 T2 的多来源版本；没有“至少一个诚实来源”的假设，grounding 不可能。

## 6. 与 T1′ 的关系

T1′ 的构造需要一个**可信回执通道**：回执由世界/工具产生，攻击者不能伪造，且绑定到 claim。这个通道是 T1′ 的“分离资源”。它不是“三层”的资源；单层 wrapper 只要拿到同一通道也能成功（T1″）。因此：

- `R` 是安全资源；
- `L` 的层数是实现选择；
- `A` 是消费 `R` 的审计接口。

## 7. 不可声称清单

- 不声称“签名 = 真值”；签名只证来源/完整性。
- 不声称“coverage 高 = 世界覆盖高”；除非有完整性假设。
- 不声称“contract 可分离 = 审计安全”；它只是接口可读。
- 不声称“k-of-n 签名 = 抗全体合谋”；全体合谋是信息论下界。
- 不声称“本目录证明了 CAMS 安全”；本目录证明的是条件与不可能性边界。
