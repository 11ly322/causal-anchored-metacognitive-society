# 01 — Formal model

> 本文件只给定义与记号。定理在 `03`–`06`。所有“必须/最优/收敛”的句子若未标定理编号，都是 `[TBD]`，不是结论。  
> v5.0 的主对象是审计层 `A`；三层 `L` 只作可选实现（`docs/APPENDIX-OPTIONAL.md`），不是 v5.0 的主 claim。

## 1. 基本集合

| 符号 | 含义 |
|---|---|
| `Ω` | 世界状态集合；`s ∈ Ω` 是一个世界 |
| `X` | 任务/输入空间；`x ∈ X` 是问题、上下文、工具调用意图 |
| `T` | 纯文本通道取值空间（字符串、日志、自然语言） |
| `R` | 回执通道取值空间（shell/browser/db/传感器回执及其元数据） |
| `E` | 证据对象空间 |
| `C` | claim 空间 |
| `Y` | 答案空间；`y ∈ Y ∪ {⊥}` |
| `V` | verdict 空间 |
| `K` | 通道个数；legacy 例子 `K=12`，本文件不证明 12 必要 |

一次审计请求写作

```text
q = (x, e_{1:m}, c_{1:n}, a)
```

其中 `x` 是输入，`e_i ∈ E` 是提交的证据，`c_j ∈ C` 是 claim，`a ∈ Y ∪ {null}` 是候选答案。审计器不读取 `Ω`；它只读取 `q`。

## 2. 证据、claim、溯源树

### 2.1 Evidence

```text
e = (id, source, content, checksum, valid, scope, non_text)
```

- `checksum = h(content)` 是内容哈希；`h` 是公开函数。
- `valid ∈ {0,1}` 是回执层自报的有效性；审计器不能只信它，必须复算 `h(content)`。
- `scope ⊆ 2^Ω` 是回执声称适用的世界集合；`non_text ∈ {0,1}` 表示叶是否来自非文本通道。
- `source` 是来源标识；它不自动等于可信。

定义证据核验谓词

```text
VerifyE(e) ⇔ [ h(e.content) = e.checksum ] ∧ e.valid = 1 ∧ e.non_text = 1
```

`VerifyE` 只核验“内容未被改动 + 非文本叶”；它不核验内容是否为真。`non_text=0` 的文本日志不能单独充当 H4 叶（PROTOCOL §1）。

### 2.2 Claim 与支持关系

```text
c = (id, supports, relation, scope, text)
supports ⊆ E.id
relation ∈ {supports, non_sequitur, selection_bias}
```

`relation=supports` 表示“作者声称这些证据支持该 claim”；它不是语义蕴含的证明。`selection_bias` 表示作者自己承认只选了有利证据；审计器应拒绝把这种 claim 当作全覆盖。

### 2.3 Provenance tree

一个 provenance 结构是有向二分图

```text
P = (E ∪ C, S),   S ⊆ (E × C) ∪ (C × C)
```

边 `(e,c)` 表示 `e ∈ c.supports`；边 `(c,c')` 表示 claim 间依赖。根是最终答案 claim `c_root`。`P` 是 DAG（实现可检查无环；本文件假定 DAG）。

核验谓词：

```text
VerifyP(P) ⇔
  (∀e ∈ E: VerifyE(e))
  ∧ (∀c ∈ C: c.relation = supports)
  ∧ (∀c ∈ C: c.scope 与 x 的 scope 匹配)
  ∧ (∀c ∈ C: c.supports ≠ ∅)
  ∧ (root 可达)
```

注意：`VerifyP` 不检查 `c.text` 是否由 `supports` 语义推出。这是 v5.0 公开的漏洞（`CAMS.md` §2.2），也是 T2 的入口。

### 2.4 Coverage

令 `Req(q)` 是任务要求的 claim/证据对集合（由任务规范给定）。定义

```text
cov(q) = |{(c,e) ∈ Req(q): e ∈ c.supports ∧ VerifyE(e) ∧ scope_match(e,c)}| / |Req(q)|
```

若 `Req(q)=∅`，约定 `cov(q)=0`（空集不能自动算全覆盖）。实现可以把 `cov` 取 0/1 的粗粒度版本；理论结论只要求 `cov` 是 `[0,1]` 上的确定性函数。覆盖率是“已提交证据的覆盖”，不是世界覆盖（见 T2′）。

### 2.5 Covariance

`κ(q) ∈ [0,∞)` 是审计器对“当前证据/表征不足以支撑确定答案”的标量摘要。它可以是模型输出的协方差迹、校准残差、或任务定义的不确定度。**本文件不假定 `κ` 是概率；只假定它是确定性可复算的标量。** `⊥` 不是独立端口；它是 `κ > τ_κ` 的事后标记（R2 的 v5.0 版本）。

## 3. 门控与契约

### 3.1 Gate

给定覆盖率阈值 `τ_c ∈ [0,1]`、协方差阈值 `τ_κ ∈ [0,∞)`：

```text
Accept(q) ⇔ VerifyP(P_q) ∧ cov(q) ≥ τ_c ∧ κ(q) ≤ τ_κ
```

v5.0 的 v0 取 `τ_c=0.80`、`τ_κ=0.60`（设计参数，不是定理）。`τ_z=0.55` 是 legacy 参数；在 v5.0 中不出现，见 `05-parameters.md`。

### 3.2 Verdict 与 contract

```text
Verdict(q) = (
  status ∈ {accept, abstain},
  answer ∈ Y ∪ {null},
  reason_code ∈ {NO_RISK, INSUFFICIENT_EVIDENCE, MEASUREMENT_FAILURE, OUT_OF_SCOPE},
  cov, κ, root_hash,
  contract = (version, reason_code, cov, provenance_summary, escalation, adapter_cost),
  claims
)
```

`reason_code` 的优先级约定为：测量失败 > 越界 > 证据不足 > 无风险。这样外部脚本只读 `contract` 就能做四分类；若必须读 `κ` 才能区分，契约不可分离（F3/F10′ 失败）。

定义 **ContractSeparable(A)**：存在一个只读 `contract` 的映射

```text
D: Contract → {NO_RISK, INSUFFICIENT_EVIDENCE, MEASUREMENT_FAILURE, OUT_OF_SCOPE}
```

使 `D(Verdict(q).contract) = Verdict(q).reason_code` 对所有 `q` 成立。`D` 不需要知道 `κ`、`P` 或模型内部。

## 4. 审计层的性质

### 4.1 Provenance soundness（可证）

```text
ProvSound(A) ⇔ ∀q: Accept(q) ⇒ VerifyP(P_q) ∧ cov(q) ≥ τ_c ∧ κ(q) ≤ τ_κ
```

这是审计器对其**输入对象**的承诺；它不承诺 `c.text` 为真。

### 4.2 Grounding soundness（v5.0 不承诺）

固定世界 `s` 与 claim 真值谓词 `g_s(c) ∈ {0,1}`：

```text
GroundSound(A) ⇔ ∀q,s: Accept(q) ⇒ g_s(c_root)=1
```

`g_s` 是外部真值；`A` 只读 `q`，不读 `s`。`ProvSound` 与 `GroundSound` 是不同性质。v5.0 只声称前者；T2 说明后者在纯文本、无可信锚点时不可得。

### 4.3 Reproducibility

```text
Repro(A) ⇔ ∀q: A(q) 是确定性函数（同 q、同阈值、同版本 ⇒ 同 Verdict）
```

v5.0 明确禁止随机采样（PROTOCOL P6）。这是接口性质，不是统计性质。

### 4.4 Auditability（本目录的使用定义）

一个审计器 `A` 对任务族 `D` 是**可审计的**，若同时满足：

1. `ProvSound(A)`；
2. `Repro(A)`；
3. `ContractSeparable(A)`；
4. 对 `D` 中每个 `q`，`Verdict(q)` 的字段可由外部复算（哈希、coverage、reason_code）。

这个定义刻意不包含 `GroundSound`；后者是 T2 的主题。把“可审计”误写成“理解/真值保证”是 scope 违规（ledger N1）。

## 5. Legacy 三层模型 `L`

> 该模型来自 `docs/APPENDIX-OPTIONAL.md` 与旧 CFP 版本；v5.0 只把它作为可选实现，不作为主 claim。  
> 本文件定义它，是为了让 T1/T1′ 能讨论“层数是否必要”，而不是承认它必要。

### 5.1 通道

令 `K` 个通道 `C_1,...,C_K`；legacy 例子 `K=12`。每个通道产生

```text
o_i = (t_i, r_i, non_text_i)
```

其中 `t_i` 是文本部分，`r_i` 是回执部分（可为空）。至少一个 `r_i` 非空且 `non_text_i=1`（H4）。

### 5.2 三层

```text
L1: (o_1,...,o_K) ↦ y            # 通道隔离，每个通道单独编码
L2: y ↦ z ∈ Z ∪ {⊥}              # 固定 n 个收敛单元；τ_z 阈值；m_min 最小单元数
L3: z ↦ (answer, relation_graph)  # depends_on / precedes / scope_includes / contradicts
```

`L` 是随机/确定性映射；本文件把随机性写成对种子 `ω` 的条件化，固定 `ω` 后是确定性函数。`τ_z` 是 L2 的收敛阈值（legacy），`m_min` 是最小收敛单元数（legacy）。

### 5.3 可观察行为

`L` 的可观察行为是 `(answer, provenance, contract)` 的分布。T1 只谈这个分布；不谈内部 `y,z` 的语义。

## 6. Wrapper `W` 与“同信息”

一个 wrapper 是任意映射

```text
W: (x, e_{1:m}, c_{1:n}) → Verdict
```

它不共享 `L` 的内部结构，但可以读取与 `L` 相同的输入对象。

**同信息（ observational equivalence）**：`W` 与 `L` 同信息，若二者在同一个输入 `q` 上的可观察输入 σ-代数相同；等价地，存在一个共同的 observation `O(q)`，`W` 与 `L` 都只依赖 `O(q)`。本文不把“同参数”“同层数”“同训练数据”混入同信息；那些是结构/资源，不是观察。

T1 的“W 可模拟 L”需要可实现性假设：`W` 的函数类足够表达 `L` 在有限输入域上的行为（例如查表），或 `W` 被允许调用 `L` 的公开计算。没有这个假设，T1 只是“存在一个数学函数”，不是工程结论；`03-separation.md` 会明确标注。

## 7. 威胁模型接口（详见 02）

- `TextOnly`：审计器只看到 `T`，看不到 `R`。
- `Receipt`：审计器看到 `R`，且 `R` 带新鲜性/来源绑定。
- `Forger`：可生成任意文本/claim；不能伪造 `h` 的第二原像。
- `Replayer`：可重放旧 `(e, contract)`。
- `Colluder`：控制至多 `k` 个来源；`k` 与信任阈值是参数。
- `Selector`：可选择提交哪些证据；不提交的证据不可见。

## 8. EGT（legacy，非 v5.0 主 claim）

有限策略集 `S`，种群计数 `n ∈ ℕ^{|S|}`，`Σ n_i=N`。更新核 `P(n'|n)` 由复制/最优反应/变异组成。`P` 是有限状态 Markov 链；T5 讨论其收敛/周期。v5.0 没有 EGT 实验；`2000 轮`是 legacy 说法，不能作为 v5.0 的收敛证据。

## 9. 记号约定

- `1{·}` 是指示函数。
- `Δ(S)` 是 `S` 上概率单纯形。
- `Supp(μ)` 是分布 `μ` 的支撑集。
- `H(·)` 是 Shannon 熵；`H(X|Y)` 是条件熵。
- `J(P,Q)` 是 Jensen–Shannon 散度。
- 所有概率陈述默认在固定审计器版本、固定阈值、固定输入分布下；没有分布假设时写 `[TBD]`。
