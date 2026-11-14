# Known defects — archived prototype

This file records defects that existed at `18d8cd4`. It is not a bug-fix list for a supported package. The prototype is archived; do not cite it as validation.

## Defects

1. **Circular expectation labels.** `tools/build_bench.py:28-36` builds `EXPECT` by category, so the “expected” answer is generated from the same category label that the task is meant to test. The path often quoted as `bench/build_bench.py` does not exist.
2. **Zero-denominator hallucination.** `bench/score.py:35` reports `hallucination_rate = 0.0` when no output is determined, instead of `[TBD]`/undefined.
3. **Empty checksum accepted.** `cams_lite/types.py` originally returned `True` for an empty checksum. Patched in the archive; see `PATCHES.md`.
4. **Wrong reason code for high covariance.** `cams_lite/gating.py` originally mapped `covariance > 0.60` to `MEASUREMENT_FAILURE`, conflating uncertainty with measurement failure. Patched to `INSUFFICIENT_EVIDENCE`; see `PATCHES.md`.
5. **Replayable receipts.** Receipts had no nonce, timestamp, signature, trust root, or claim binding. A recorded receipt could be replayed. This is not fixed in the archive.
6. **Code health confused with validity.** The `pytest 32 passed / coverage 94.4%` line in PR #1 describes tests and line coverage. It does not establish audit validity, H1, or live performance.

## Status

- Items 3 and 4 are patched only in the archived copy.
- Items 1, 2, 5, and 6 remain documented, not repaired.
- No old test suite or bench was run after the archive patch.
- No score from this directory should appear on the front page.
