# Patches applied to the archived prototype

Date: 2026-11-13. Scope: archived copy only.

These are narrow semantic fixes required for an honest archive. They do not make the prototype usable, validated, or current.

## 1. Empty checksum

File: `cams_lite/types.py`

Before:

```python
def checksum_ok(self) -> bool:
    if not self.checksum:
        return True
```

After:

```python
def checksum_ok(self) -> bool:
    if not self.checksum:
        return False
```

Reason: an absent checksum is not a passed check.

## 2. High covariance reason code

File: `cams_lite/gating.py`

Before:

```python
elif covariance > cfg.tau_cov:
    reason_code = "MEASUREMENT_FAILURE"
```

After:

```python
elif covariance > cfg.tau_cov:
    reason_code = "INSUFFICIENT_EVIDENCE"
```

Reason: high uncertainty is not a measurement failure. The four public reason codes remain unchanged; a detailed high-covariance marker belongs in the new gate spec, not this old code.

## Not patched

- `tools/build_bench.py` circular expectations.
- `bench/score.py` zero-denominator hallucination.
- Missing nonce / timestamp / signature / claim binding.
- PR #1 verification wording.

No tests were rerun. The archive is not a supported build.
