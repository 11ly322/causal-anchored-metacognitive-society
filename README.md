# CAMS / CFP

**Causal-Anchored Metacognitive Society**  
*Convergent Functional Partitioning*

This repository contains the **CAMS / CFP research document only**. It does not contain an implementation, demo, model weights, run data, or executable code.

## Document

- [`Causal-Anchored Metacognitive Society, CAMS.md`](<Causal-Anchored Metacognitive Society, CAMS.md>) — the complete scheme:
  - `x·1=y → y·n=z → z·n=脑`: three-layer convergent functional partitioning;
  - H1–H4: evidence fingerprint with non-symbol leaf, always-on covariance (not discrete abstention), precision-only top-down, provenance;
  - v4.2 three-objective upgrade: amortized initialization + short correction; versioned refusal contract for `⊥`; sparse orthogonalization + relational constraint satisfaction;
  - F1′–F11′ falsification conditions against budget-matched baselines, including `A-noAmort`, `A-contract-raw`, and `A-noOrth`;
  - a 10⁴–10⁵ minimal experiment with evidence weakening, top-down temptation, delayed evidence, contract probing, and compute/accuracy ablations.

- [`CAMS-通俗解释.md`](CAMS-通俗解释.md) — a plain-language explanation for non-specialists.

## Status

**CAMS / CFP v4.2** — documentation-level state after the Round 1–15 three-objective rewrite. The document reports its own iteration state, Pareto archive, F6 score, three-objective vector `V=[V1,V2,V3]`, contract/orthogonality/compute status tables, and unresolved hallucination leak paths. These are design-level bookkeeping, not experimental evidence: no 10⁴ run, no external contract probe, and no `A-noAmort`/`A-noOrth` result exists yet.

## Scope

This is a research proposal, not a policy recommendation system. It does not claim that machine understanding has been achieved, and it does not replace the 10⁴–10⁵ experiment described in the document.

The anti-hallucination claims are **structural**: H1–H4 close specific generation paths. They do not make hallucination impossible in an absolute sense; sensor lies, true-evidence-wrong-inference, minority-evidence averaging, precision-selection bias, and out-of-distribution thresholds remain open leak paths (see the document's final section).

## License

The document is released under the **MIT License**; see [`LICENSE`](LICENSE).

## Citation

If you use this document, cite it as:

> CAMS contributors. *Causal-Anchored Metacognitive Society (CAMS) / CFP: convergent functional partitioning with structural anti-hallucination constraints.* 2026.
