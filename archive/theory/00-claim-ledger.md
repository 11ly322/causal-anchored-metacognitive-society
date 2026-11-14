# 00 — Claim ledger

> 目的：把 v5.0 文档中的“主张”与“定义/设计选择/经验数字”分开。  
> 规则：本目录中任何有论证重量的句子，必须能映射到下表的一行。没有映射的句子只能是定义、记号或 `[TBD]`，不能当作结论。  
> 状态：`PROVEN`（在写明假设下已证）、`CONDITIONAL`（条件定理）、`OPEN`、`COUNTEREXAMPLE`、`EMPIRICAL-SYNTHETIC`（只有合成数据）、`EMPIRICAL-LIVE`（当前无）、`TBD`。  
> 类型：`DEFINITION`、`ASSUMPTION`、`THEOREM`、`CONJECTURE`、`EMPIRICAL`、`DESIGN-SCORE`、`SCOPE`。  
> 记号：`L` = legacy 三层 CFP 架构；`A` = v5.0 audit layer；`W` = wrapper；`R` = receipt channel；`T` = text-only channel。

## 1. 主张表

| ID | 主张 | 类型 | 状态 | 来源/备注 |
|---|---|---|---|---|
| D1 | `A` 把一次调用映射为确定性 `Verdict`：`status, answer, reason_code, coverage, covariance, provenance, contract, claims`。 | DEFINITION | — | `docs/PROTOCOL.md` §2；不是经验主张 |
| D2 | `Evidence` 至少含 `id, source, content, checksum, valid, scope, non_text`。 | DEFINITION | — | `CAMS.md` §2.1；字段是接口约定 |
| D3 | `ProvenanceTree` 只检查证据存在、校验和、`supports` 关系、scope、coverage；不做语义蕴含。 | DEFINITION | — | `CAMS.md` §2.2；这是范围限制，不是能力主张 |
| D4 | `accept` 当且仅当所有 claim 通过 `Verify`、coverage ≥ 0.80、covariance ≤ 0.60。 | DEFINITION | — | v5.0 的 v0 门控；0.80/0.60 是设计参数 |
| D5 | 拒绝返回结构化 `contract`，含版本、原因码、证据覆盖率、溯源摘要、升级路径、适配器成本。 | DEFINITION | — | `CAMS.md` §2.4 |
| D6 | `coverage = determined/N`；`hallucination = wrong_determined/determined`。 | DEFINITION | — | `PREREGISTRATION.md` §2 |
| D7 | H1–H4 是审计接口不变量，不是脑机制。 | DEFINITION | — | `CAMS.md` §3；这是作者自己的范围声明 |
| A1 | 回执来源在审计时可信；校验和可由内容复算。 | ASSUMPTION | — | 否则 H1/P1 不成立；见 `02-adversary.md` |
| A2 | 至少一个叶证据来自非文本通道（工具回执/物理测量），且不是自然语言日志。 | ASSUMPTION | — | H4/PROTOCOL §1；这是“纯文本不可能”的边界条件 |
| A3 | 校验和函数在对抗者计算能力下抗第二原像/碰撞。 | ASSUMPTION | — | 否则伪造回执不可排除；密码学假设 |
| A4 | 审计时看到的回执集合对“该报告什么”是完整的；或选择性报告被单独审计。 | ASSUMPTION | — | 否则 coverage 只是“已提交证据的覆盖”，见 T2′/T5 |
| T1 | 对任意 `L`，存在一个同输入信息的 `W`，使 `W` 与 `L` 在全部可观察输入上同分布。 | THEOREM | PROVEN（条件：W 可实现该函数） | 见 `03-separation.md`；行为等价，非结构等价 |
| T1′ | 存在任务族与攻击者，使任何缺 `R` 的 `W` 失败，而带 `R` 的审计器成功。 | THEOREM | PROVEN（构造） | 见 `03-separation.md`；分离的是回执通道，不是层数 |
| T1″ | 不存在“同 `R`、仅层数不同”的分离定理；三层深度优势最多是归纳偏置猜想。 | THEOREM/负结果 | PROVEN（反例：单层查表） | 见 `03-separation.md` §4；触发 pivot |
| T2 | 在无可信锚点的纯文本通道下，任何验证器都不能同时保证 grounding 的 soundness 与 completeness。 | THEOREM | PROVEN（不可区分性） | 见 `04-limits.md`；签名只证来源，不证真值 |
| T2′ | `coverage` 不能证明“世界覆盖”；没有完整性假设时，选择性报告不可被覆盖数排除。 | THEOREM | PROVEN（构造） | 见 `02-adversary.md`/`04-limits.md`；这是审计层的边界 |
| T4 | 在 0-1 代价、校准后验 `p` 下，最优接受阈值为 `p* = C_FN/(C_FP+C_FN)`。 | THEOREM | PROVEN（决策论） | 见 `05-parameters.md`；标准贝叶斯决策 |
| T4′ | `τ_z=0.55` 不是分布-free 最优；它只在特定代价比/先验/校准映射下最优。 | THEOREM | PROVEN（反例族） | 见 `05-parameters.md`；0.55 是 legacy 参数，不在 v5.0 主 claim |
| T4″ | `m_min=4` 不能作为一般覆盖估计的最小样本量；在常见精度下需要远大于 4。 | THEOREM | PROVEN（下界） | 见 `05-parameters.md`；若 `m_min` 定义不同，需重述为 `[TBD]` |
| T5 | 有限状态 EGT 链若不可约且非周期，则收敛到唯一平稳分布；否则可周期/吸收。 | THEOREM | PROVEN（Markov 链） | 见 `06-egt.md`；标准有限链结论 |
| T5′ | 存在 2-周期 EGT 反例，使 2000 轮不收敛；轮数不是收敛证明。 | THEOREM | PROVEN（构造） | 见 `06-egt.md`；反协调博弈 |
| C1 | 三层结构（`x·1=y → y·n=z → z·n=脑`）带来审计上的必要优势。 | CONJECTURE | OPEN/无证明 | v5.0 已把它降为 optional appendix；T1/T1″ 反向 |
| C2 | `τ_z=0.55`、`m_min=4` 是最优参数。 | CONJECTURE | COUNTEREXAMPLE（一般情形） | 见 T4′/T4″；只在特定代价/定义下可成立 |
| C3 | 2000 轮 EGT 会收敛。 | CONJECTURE | COUNTEREXAMPLE（无变异） | 见 T5′；有变异时需另证 |
| C4 | legacy 12 通道是必要的。 | CONJECTURE | OPEN | v5.0 不再主张；本目录只把它作为 `K=12` 的例子，不证明必要性 |
| E1 | 合成基准 test（n=50）：CAMS coverage 0.28、hallucination 0.50；no-audit coverage 1.0、hallucination 0.86；logprob coverage 0.86、hallucination 1.0。 | EMPIRICAL | EMPIRICAL-SYNTHETIC | `bench/results/benchmark.json`；不是 live H1 |
| E2 | 10k mock：CAMS coverage 0.278、hallucination 0.508；`h1_status=[TBD]`。 | EMPIRICAL | EMPIRICAL-SYNTHETIC | `experiments/results.mock.json`；mock，不是 live |
| E3 | live H1：匹配 coverage 下幻觉率相对降低 ≥15%，determined rate 下降 ≤5pp。 | EMPIRICAL | TBD | `PREREGISTRATION.md`；无 live 数据 |
| S1 | `F6=0.80`、`V=[0.82,0.78,0.84]` 是“结构自评分”。 | DESIGN-SCORE | 非证据 | v4.x 的 rubric；v5.0 已弱化；不能当实验分数 |
| S2 | “100 题合成基准通过”不等于 H1 通过。 | SCOPE | — | 作者自己的限制；ledger 强制保留 |
| N1 | 本仓库不主张“理解”“意识”“脑模拟”“政治管理建议”“0.1B/100B 规模”。 | SCOPE | — | v5.0 README/主文档；负主张，不是定理 |
| N2 | 本目录不写代码、不跑实验、不修改原文档。 | SCOPE | — | 任务约束 |

## 2. 自评分与设计声明（单独列出，防止被当成证据）

- `F6=0.80`、`V=[0.82,0.78,0.84]`、`F1–F6` 的 0–1 分数是 **DESIGN-SCORE**，不是测量值。它们没有置信区间，不能进入定理陈述。
- 0.80 coverage、0.60 covariance、0.55 `τ_z`、4 `m_min` 是 **设计参数**。本目录只证明“在什么条件下某个阈值最优”，不证明这些常数普遍最优。
- 合成基准数字是 **EMPIRICAL-SYNTHETIC**；只能支持“代码在构造任务上按定义工作”，不能支持“真实世界审计有效”。
- 2000 轮、12 通道、三层是 **legacy/optional**；v5.0 主文档已不把它们作为主 claim。任何把它们写回主结论的句子，必须先新增一行 ledger 并标 `CONJECTURE`。

## 3. 红队路径（先登记，后展开）

1. **等价路径**：T1 表明三层与单层在 I/O 上不可区分；若“理解/审计优势”只体现在输出分布，三层主张是空的。见 `03-separation.md` §5、`08-paper.md` §0。
2. **文本不可能路径**：T2 表明纯文本不能认证 grounding；若审计层最终只吃文本，它只是另一个置信度包装。见 `04-limits.md`。
3. **参数任意路径**：T4′/T4″ 表明 0.55/4 没有普遍最优性；若论文的核心是这些常数，核心是空的。见 `05-parameters.md`。
4. **周期路径**：T5′ 表明 2000 轮可能只是 2-周期；若“收敛”是主 claim，主 claim 不成立。见 `06-egt.md`。
5. **契约/合谋路径**：coverage 只覆盖已提交证据；选择性报告和全体合谋可使 contract 看起来干净。见 `02-adversary.md` T2′。

## 4. 一句话主定理（供审稿人复述）

> 在“同信息”意义下，三层结构没有可观察的必然优势（T1）；可分离的是可信回执通道（T1′）；纯文本通道在无可信锚点时不能认证 grounding（T2）。CAMS 的可审稿核心不是“三层”，而是“回执 + 契约 + 可证伪的审计接口”。

这句话本身是本目录的 **SCOPE/结论**，不是新定理；它的两个支撑是 T1/T1′/T2。
