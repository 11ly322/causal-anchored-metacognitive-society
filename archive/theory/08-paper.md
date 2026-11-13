# 08 — Paper skeleton (8–12 pages, theory only)

> Working title: **Trusted Receipts, Not Three Layers: A Theory of Auditable Abstention**
>
> Status: skeleton. Five main theorems: T1, T1′, T2, T4, T5. No experiments, no fabricated citations, no numbers presented as measured. Citation placeholders are `[TBD]`; full proofs are in `THEORY/03`–`THEORY/06`.

---

## Abstract

We study a class of “audit layers” that attach provenance, coverage, covariance, and a refusal contract to a base model’s claim. The design is often presented as a three-layer cognitive architecture. We separate what is identifiable from what is not.

First, under a precise “same information” condition, a single-layer wrapper that observes the same claim-evidence record can reproduce the three-layer system’s verdicts exactly (T1). Three layers are therefore not necessary for the audit function. Second, if the verifier distrusts the prover and receives a receipt that the prover cannot forge or replay, a single-layer wrapper without that receipt cannot guarantee grounding, while a receipt-checking wrapper can (T1′). The defensible distinction is the trusted receipt channel, not depth. Third, with text-only evidence and no shared trust anchor, no algorithm can distinguish a true world from a forged one at better than chance (T2); text-only “grounding certification” is impossible in that threat model. Fourth, the Bayes-optimal acceptance threshold is a likelihood ratio (T4); the value 0.55 is optimal only at a particular false-positive/false-negative cost ratio, and 4 is not a coverage sample size. Fifth, a finite-state evolutionary process converges only under irreducibility/aperiodicity or absorption; a two-strategy anti-coordination game with synchronous best response is a two-cycle, so “2000 rounds” is a budget, not a convergence proof (T5).

The resulting position is a pivot: the contribution is not “three layers” but a **trusted receipt + contract** interface. We state the falsifiers, the red-team paths that would make the program empty, and the conditions under which the negative result (T2) applies.

**Keywords**: provenance; abstention; selective prediction; trusted receipts; calibration; auditability; Markov chains.

---

## 1. Introduction

### 1.1 The problem

A base model returns a claim. An audit layer may return:

- accept;
- accept with a caveat;
- abstain with a reason;
- reject.

The design claim is that a layered structure — raw evidence, convergence, metacognitive gate — makes the output more trustworthy than a single model with a confidence score.

This paper asks four questions:

1. Is the three-layer structure necessary? (T1, T1′)
2. Can text-only evidence certify grounding? (T2)
3. Are the thresholds 0.55 and 4 optimal? (T4)
4. Does the 2000-round evolutionary process converge? (T5)

### 1.2 Contributions

1. **T1 (equivalence).** Same information ⇒ a table wrapper reproduces the layered verdicts. Depth is not identifiable from behavior.
2. **T1′ (separation).** A receipt that is unforgeable and fresh separates a receipt-checking wrapper from a text-only wrapper on a grounding task. The separation is in the trust model, not in depth.
3. **T2 (impossibility).** Text-only evidence from an untrusted source, with no shared anchor, cannot certify grounding; the minimax error is at least 1/2.
4. **T4 (thresholds).** The Bayes threshold is a likelihood ratio; 0.55 is optimal only under a specific cost ratio; 4 is not a coverage sample size.
5. **T5 (EGT).** Finite chains converge under irreducibility/aperiodicity or absorption; a 2-cycle counterexample defeats “2000 rounds ⇒ convergence”.

### 1.3 What this paper does not do

No experiments, no benchmark results, no model training, no citation of measured effects. Synthetic and mock results elsewhere are not evidence for the theorems. Empirical claims are `[TBD]`.

### 1.4 Pivot memo (one page)

**If T1 holds under same information, do not defend the three-layer architecture as the contribution.** The correct claim is weaker and more defensible:

> CAMS is an audit layer whose distinctive object is a **trusted receipt plus a versioned refusal contract**. The three-layer vocabulary is an implementation narrative, not an identifiable mechanism.

Consequences:

- The paper’s title should be about receipts/contracts, not “three layers”.
- The main empirical question is whether a receipt-checking wrapper beats a matched-coverage text-only baseline; that is F1′/F8′.
- The depth claim (L1/L2/L3) is at most an efficiency/engineering hypothesis; T1″ says a single layer with the same receipt can simulate it.
- If no trusted receipt is available, T2 applies: text-only grounding certification is impossible in the stated threat model. The honest output is `[TBD]`/negative result, not a stronger architecture claim.

This memo is intentionally part of the paper: it prevents the theory from being used to over-claim the architecture.

---

## 2. Model

### 2.1 Objects

A query is `q=(x,e,c,a)`:

- `x`: task input;
- `e`: evidence record (text or non-text);
- `c`: claim;
- `a`: answer/action.

A provenance tree `P` is a finite DAG with leaves `L`, internal nodes `I`, edges `E`, each node labeled by `content`, `source`, `scope`, `checksum`, `supports`, `relation`. `checksum` is a cryptographic hash; `source` is a trust label; `scope` is a predicate on contexts.

The audit layer outputs `Verdict=(status, reason_code, contract, κ, P)` where `status ∈ {accept, abstain, reject}`, `contract` is the external object in §2.3, `κ` is the covariance marker, `P` is the provenance tree.

### 2.2 Coverage and covariance

For a claim `c` and tree `P`:

```text
coverage(c,P) = |{l ∈ leaves(P) : l determines c}| / |leaves(P)|
```

`determines` is a task-specific relation; it is not inferred from text similarity. `κ` is a scalar in `[0,1]`; `κ>τ_κ` means “the evidence does not determine the claim”, not “the model is uncertain”.

### 2.3 Contract

The contract is a stable, versioned object:

```text
contract = {
  contract_version,
  reason_code ∈ {NO_RISK, INSUFFICIENT_EVIDENCE, MEASUREMENT_FAILURE, OUT_OF_SCOPE},
  evidence_coverage,
  provenance_digest,
  escalation_path,
  adapter_cost
}
```

`ContractSeparable` holds iff an external script that reads only `contract` can classify the four states at accuracy ≥0.90 without reading `κ` or `P`.

### 2.4 Three-layer legacy object

`L=(L1,L2,L3)` is the legacy CAMS pipeline:

- `L1`: evidence normalization;
- `L2`: convergence/gate;
- `L3`: metacognitive pass.

`A(q)` is the audit layer; `W` is a single-layer wrapper. `W` has the **same information** as `A` if it observes the same `q`, the same evidence/claim records, and the same table of `A`’s outputs on the finite query class; it does not observe hidden activations.

### 2.5 Trust model

- `A0`: text forger; can write any text, cannot produce a valid receipt for a source it does not control.
- `A1`: replay; can resend old receipts.
- `A2`: collusion of `k` sources.
- `A3`: selective reporting; may hide failures.
- `A4`: adaptive; knows the audit algorithm.

The receipt is a MAC/signature over `(session_id, claim_hash, nonce, content_digest, source_id, scope)`; the verifier holds the key or a trusted public key. This is an assumption, not a theorem.

---

## 3. T1 — Equivalence

### 定理 T1（同信息等价）

**假设**：
1. Query class `Q` is finite, or `A`’s behavior is finitely representable on `Q`.
2. `W` observes the same `q`, evidence, claim, and table of `A`’s outputs as `A`; no hidden activations.
3. `W` may implement any computable function of that information.

**结论**：
> There exists a wrapper `W` such that for all `q∈Q`, `W(q)=A(q)` (same status, reason code, contract, κ, provenance digest).

**证明**：
`Q` finite ⇒ enumerate `q`; define `W(q)=A(q)` by table lookup; compose with the audit interface. For infinite `Q` with finite representability, use the finite table on the quotient. The wrapper uses no information unavailable to `A`. ∎

**状态**：PROVEN.

**So what**：
> Depth is not identifiable from input–output behavior under same information. Any claim that “three layers are necessary” must specify an information or resource asymmetry, not just a wiring diagram.

**反例（证明失败）**：
> If `W` is restricted to a proper subclass (e.g., no receipt, no provenance, bounded compute), T1 does not apply; the restriction is the actual claim. A paper that says “three layers are necessary” without such a restriction is making an unfalsifiable architectural claim.

---

## 4. T1′ — Separation

### 定理 T1′（回执分离）

**假设**：
1. There is a task family `D` and a claim `c` whose truth is determined by a source `s` that the verifier does not control.
2. The verifier has a secret/key or trusted public key; `s` can produce a receipt `e` with a valid MAC/signature; `A0` cannot forge `e` for a new claim without the key.
3. `W_text` receives only `(x, text)`; `W_receipt` receives `(x, text, e)` and checks the receipt.
4. The receipt binds `(session_id, claim_hash, nonce, source_id, scope)`.

**结论**：
> There is an adversary `A1` (replay/forgery) such that `W_text` fails on `D` with probability at least 1/2, while `W_receipt` succeeds with probability 1−negl(λ). Hence receipt access is a real separation; depth is not needed for it.

**证明（构造）**：
- `W_text`: for a forged text, the transcript is identically distributed to a true text (T2); no test beats 1/2.
- `W_receipt`: verify MAC/signature, freshness (`nonce`), claim hash, source trust, scope; reject forged/replayed receipts. Under the assumption, forgery/replay fails except with negligible probability. ∎

**状态**：PROVEN under the receipt assumption.

**So what**：
> The defensible distinction is “has a trusted receipt” vs “does not”, not “three layers” vs “one layer”. The commercial contract is meaningful only on the receipt side.

**反例**：
> If the source is untrusted and the receipt is self-issued, `W_receipt` is just text plus a hash; T2 applies. If the verifier does not check freshness/scope, replay/scope attacks succeed (F6′/F7′).

---

## 5. T2 — Impossibility

### 定理 T2（纯文本不可区分）

**假设**：
1. `W` receives only text `x` (no receipt, no non-text measurement, no trusted anchor).
2. There exist two worlds `w0,w1` with the same text transcript `x` and different claim truth values.
3. The prior over `(w0,w1)` is not degenerate; the adversary may choose the pair.

**结论**：
> For any (possibly randomized) `W`, `sup_{w0,w1} Pr[W errs] ≥ 1/2`. No text-only algorithm certifies grounding in this threat model.

**证明**：
The transcript distributions are identical; by Le Cam/two-point method, the best test is a coin flip; the sum of Type I and Type II errors is ≥1. Hence the maximum error is ≥1/2. ∎

**状态**：PROVEN.

**So what**：
> A text-only “grounding certificate” is not a certificate; it is a claim about text. Signatures/hashes can establish integrity/provenance, but not world truth without a trusted source.

**反例/边界**：
> With a trusted anchor (signed sensor, execution receipt), T2 does not apply; the anchor is the assumption. With multiple independent sources, trust is a modeling assumption, not a text-only inference.

---

## 6. T4 — Thresholds

### 定理 T4（Bayes 阈值）

**假设**：
1. Null `H0: c=false`; alternative `H1: c=true`.
2. Likelihood ratio `Λ(e)=p(e|c=true)/p(e|c=false)`.
3. Costs: `C_FP` for accepting false, `C_FN` for rejecting true; priors `π0,π1`.

**结论**：
> The Bayes-optimal acceptance region is `Λ(e) ≥ (C_FP π0)/(C_FN π1)`. If `π0=π1`, the threshold is `p* = C_FP/(C_FP+C_FN)` in posterior form. `p*=0.55` iff `C_FP/(C_FP+C_FN)=0.55`, i.e. `C_FP≈1.222 C_FN`.

**证明**：
Posterior expected cost of accept is `π0 C_FP p(H0|e)`; of reject is `π1 C_FN p(H1|e)`; accept iff the former ≤ the latter; rearrange. ∎

**状态**：PROVEN (decision-theoretic).

**So what**：
> 0.55 is not a universal constant; it encodes a cost ratio. A paper must state the ratio, or report the threshold as a function of costs.

**反例**：
> `C_FP/C_FN=9` ⇒ `p*≈0.90`; using 0.55 is far too permissive. `C_FP/C_FN=1/9` ⇒ `p*≈0.10`; 0.55 is too conservative.

### 推论 T4′（4 不是覆盖样本量）

**假设**：coverage is estimated from `m` independent leaves; desired error `ε`, confidence `1−δ`.
**结论**：`m ≥ (1/(2ε²)) ln(2/δ)` (Hoeffding). For `ε=.1, δ=.05`, `m≥185`; for `ε=.05`, `m≥738`. `m_min=4` gives `ε≈0.49` under a normal approximation (≈0.68 under Hoeffding), far from 0.1.
**状态**：PROVEN; `m_min=4` is a coverage floor, not a statistical guarantee.

---

## 7. T5 — EGT

### 定理 T5（有限链收敛/周期）

**假设**：
1. Finite state space `𝒩`, Markov kernel `P`.
2. Either `P` irreducible and aperiodic, or absorbing with reachability.

**结论**：
- Irreducible/aperiodic ⇒ unique stationary `π`, `||μP^t−π||_TV→0`.
- Absorbing ⇒ absorption a.s.; finite expected time under reachability.
- Periodic/reducible ⇒ distribution convergence may fail; 2-cycle possible.

**证明（要点）**：
Finite + irreducible + aperiodic ⇒ primitive stochastic matrix; Perron–Frobenius; spectral gap <1. Absorbing: finite chain, reachability. Periodic: eigenvalue on unit circle; no convergence. ∎

**状态**：PROVEN (standard).

**2-cycle 反例**：
Two strategies `A,B`; payoff matrix `[[0,1],[1,0]]`; synchronous best response maps `A^N↔B^N`; 2000 rounds is 1000 cycles, no state convergence. ∎

**So what**：
> “2000 rounds” is not a convergence theorem. Need irreducibility/aperiodicity or absorption, plus a mixing/absorption bound; otherwise `[TBD]`.

---

## 8. Falsifiers (summary)

`THEORY/07` gives F1′–F8′ as “assumption ⇒ conclusion; negation = counterexample”. The paper reports:

- F1′ matched-coverage hallucination reduction; failure = <15% or coverage drop >5pp.
- F2′ skeleton ablation; failure = <10pp difference.
- F3′ contract tri-state separability; failure = accuracy <0.90 or need for κ.
- F4′ unnecessary abstention; failure = >10%.
- F5′ forged receipt; failure = accepted with bad checksum/source.
- F6′ replay; failure = old receipt accepted for new claim.
- F7′ scope; failure = out-of-scope accepted.
- F8′ live transfer; failure = direction reversal/CI crossing 0; no live data = `[TBD]`.

No empirical claim is made here. The falsifiers are the paper’s empirical contract.

---

## 9. Red team: three ways this is empty

### 9.1 Path 1 — T1 makes the architecture empty

If “same information” is allowed, T1 is a table lookup; the three layers are a narrative. **Response**: accept T1 and pivot to T1′. The paper’s contribution is receipts/contracts, not depth. If the authors refuse the pivot and keep claiming depth, the paper is empty.

### 9.2 Path 2 — the receipt channel is standard

MAC/signature/replay protection is standard cryptography; “trusted receipt” is not new. **Response**: the novelty, if any, is the **contract object** and the coverage/reason-code discipline, not the MAC. If the contract is just logging, F3′/F10′ fail and the commercial claim is empty. We do not claim cryptographic novelty.

### 9.3 Path 3 — the assumptions cannot be verified

T1′ assumes a trusted source/key; T2 says without it text-only grounding is impossible. If the deployment has no trusted anchor, the audit layer cannot deliver grounding; it can only report `INSUFFICIENT_EVIDENCE`/`MEASUREMENT_FAILURE`. **Response**: state the assumption explicitly; if it fails, the honest output is a negative result, not a stronger architecture. The theory’s value is making this boundary explicit.

### 9.4 If all three paths hold

Then the correct paper is a **negative result**: “text-only audit layers cannot certify grounding; trusted receipts are necessary but standard; the remaining contribution is a contract interface whose value is empirical and currently `[TBD]`.” This is a publishable negative result; it is not a three-layer cognitive architecture.

---

## 10. Related work (categories; citations `[TBD]`)

- Selective prediction / abstention: risk-coverage curves, Chow's rule; citation `[TBD]`.
- Conformal prediction: distribution-free coverage; citation `[TBD]`.
- Calibration: ECE, temperature scaling; citation `[TBD]`.
- Provenance / attestation: C2PA, in-toto, transparency logs; citation `[TBD]`.
- RAG attribution: sentence-level attribution, citation `[TBD]`.
- Multi-agent debate: does not create evidence; citation `[TBD]`.
- Trusted execution / receipts: TEEs, signed sensors; citation `[TBD]`.

The paper does not claim to supersede these; it locates CAMS as a composition of abstention, provenance, and contracts, with T1/T2 limiting what can be claimed.

---

## 11. Limitations and open problems

1. **T1′ assumption**: trusted source/key; without it, T2.
2. **T2 is text-only**: non-text receipts can escape; their trust is an assumption.
3. **T4 costs**: `C_FP,C_FN` are deployment-specific; 0.55 is not universal.
4. **T5**: mixing time/spectral gap `[TBD]`; 2000 is a budget.
5. **F1′/F8′**: no live data; `[TBD]`.
6. **Coverage**: `m_min` is not a statistical guarantee; T4′ gives sample sizes.
7. **Depth**: T1″ (proposition) says same receipt + single layer can simulate three layers; no depth separation proven; O1 open.

---

## 12. Conclusion

The theory supports a narrow claim:

> A trusted receipt channel plus a versioned, separable refusal contract is a defensible audit interface; three layers are not necessary under same information; text-only grounding certification is impossible without a trusted anchor; thresholds are cost-dependent; 2000 rounds is not convergence.

The broader cognitive-architecture claim is not supported by these theorems. The paper should be reviewed as a theory of **auditable abstention**, not as a theory of mind.

---

## Appendix A — Five theorem statements (compact)

| ID | Statement | Status |
|---|---|---|
| T1 | Same information ⇒ table wrapper reproduces `A` | PROVEN |
| T1′ | Trusted receipt separates from text-only under forgery/replay | PROVEN (assumption) |
| T2 | Text-only, untrusted source ⇒ minimax error ≥1/2 | PROVEN |
| T4 | Bayes threshold `C_FP π0/(C_FN π1)`; 0.55 iff cost ratio 0.55 | PROVEN |
| T5 | Finite chain converges iff irreducible/aperiodic or absorbing; 2-cycle counterexample | PROVEN |

## Appendix B — What would change the paper

- A depth separation theorem (O1) with a task family where same-receipt single-layer fails; currently OPEN.
- A live F1′/F8′ result with matched coverage and CI; currently `[TBD]`.
- A contract field study showing external scripts separate four states without κ; currently `[TBD]`.

## Appendix C — No-experiment statement

This is a theory paper. It contains no experiments, no benchmark numbers, no model training, and no measured effects. Any number in the repository labeled `[实测]` is out of scope for this paper; synthetic/mock results are not theorems.
