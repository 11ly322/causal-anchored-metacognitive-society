# CAMS Audit Layer: a small, falsifiable audit interface for agent evidence

> 4-page workshop note skeleton. **No live result yet.** Numbers marked `[实测-合成]` are synthetic-bench only; `[TBD]` is unfilled.

## Abstract

Agents often return an answer and a confidence score, but not a stable object that an external system can audit. We describe CAMS Audit Layer: tool receipts are hashed into evidence, claims declare support ids, and a coverage/covariance gate returns either an answer or a structured refusal contract. The design is deliberately narrow: it does not claim understanding, a cognitive architecture, or model capability. It is falsifiable: if the audit layer does not reduce wrong accepts at matched coverage, it should be discarded.

## 1. Problem

- confidence is not provenance;
- a valid hash is not a valid inference;
- a refusal is often an empty value, not a usable contract;
- post-hoc detectors add another model to trust.

## 2. Method

### 2.1 Evidence and provenance

`Evidence` carries `checksum`, `scope`, `non_text`; `Claim` carries `supports` and `relation`. `ProvenanceTree` verifies existence, checksum, relation, scope, coverage. It does not do semantic entailment; this is an explicit limit.

### 2.2 Gate

Accept iff every claim verifies, coverage ≥0.80, covariance ≤0.60. Otherwise return a contract with `reason_code`, `evidence_coverage`, `provenance_summary`, `escalation_path`, `adapter_cost`.

### 2.3 Contract

The contract is versioned. An external script should distinguish no-risk / insufficient-evidence / measurement-failure without reading internal covariance.

## 3. Benchmark (synthetic)

100 tasks, 7 leakage categories, 50/50 dev/test. `[实测-合成]` on test split:

| method | coverage | accuracy | hallucination | unnecessary abstention |
|---|---:|---:|---:|---:|
| no-audit | 1.000 | 0.140 | 0.860 | 0.000 |
| logprob-gate | 0.860 | 0.000 | 1.000 | 0.140 |
| cams-lite | 0.280 | 0.860 | 0.500 | 0.000 |

Caveat: the comparison is **not** the preregistered H1; coverage is not matched and the tasks are synthetic. The `minority_evidence` category is a known failure: a valid receipt can still support the wrong majority answer.

## 4. Falsification and next step

- H1: matched-coverage hallucination reduction ≥15%, determined-rate drop ≤5pp.
- F3: external contract tri-state accuracy ≥0.90.
- F4: unnecessary abstention ≤10%.
- Current live status: `[TBD]`; no provider key or real receipts.
- If H1 fails, publish the negative result; do not rename the hypothesis.

## 5. Limitations

- no semantic entailment;
- synthetic tasks;
- no live model;
- refusal contract reason codes are coarse;
- 100 tasks are a v0, not 10³/10⁴.

## Negative-result template

> The audit layer did **not** reduce wrong accepts at matched coverage. Observed relative change: `[TBD]`; 95% CI: `[TBD]`; n=`[TBD]`. We therefore stop at v0 and do not claim an audit benefit.

## Positive-result template

> At matched coverage, the audit layer reduced wrong accepts by `[TBD]`% (95% CI `[TBD]`), with a determined-rate change of `[TBD]`pp. This is a live result (`[实测]`), not the synthetic bench.
