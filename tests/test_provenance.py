from cams_lite.provenance import ProvenanceTree
from cams_lite.types import Claim, Evidence, content_checksum


def make_tree() -> ProvenanceTree:
    tree = ProvenanceTree()
    tree.add_many(
        [
            Evidence("e1", "sensor", "42", checksum=content_checksum("42")),
            Evidence("e2", "db", "row-7", checksum=content_checksum("row-7")),
            Evidence("e3", "sensor", "bad", checksum="sha256:not-the-hash"),
        ]
    )
    return tree


def test_valid_claim_verifies_with_full_coverage():
    tree = make_tree()
    result = tree.verify_claim(Claim("c1", "answer", supports=("e1", "e2")))
    assert result["verified"] is True
    assert result["coverage"] == 1.0
    assert result["reason"] == "OK"
    assert result["span_ids"] == ["span:e1", "span:e2"]


def test_missing_support_is_not_verified():
    result = make_tree().verify_claim(Claim("c1", "answer", supports=("e9",)))
    assert result["verified"] is False
    assert result["reason"] == "MISSING_SUPPORT"


def test_bad_checksum_is_invalid_evidence():
    result = make_tree().verify_claim(Claim("c1", "answer", supports=("e3",)))
    assert result["verified"] is False
    assert result["reason"] == "INVALID_EVIDENCE"


def test_non_sequitur_is_rejected():
    result = make_tree().verify_claim(
        Claim("c1", "answer", supports=("e1",), relation="non_sequitur")
    )
    assert result["verified"] is False
    assert result["reason"] == "NON_SEQUITUR"


def test_scope_mismatch_is_rejected():
    tree = ProvenanceTree()
    tree.add_evidence(
        Evidence("e1", "sensor", "42", checksum=content_checksum("42"), scope="ood")
    )
    result = tree.verify_claim(Claim("c1", "answer", supports=("e1",), scope="in"))
    assert result["verified"] is False
    assert result["reason"] == "OUT_OF_SCOPE"


def test_partial_coverage_and_non_text_leaf():
    tree = ProvenanceTree()
    tree.add_evidence(
        Evidence("e1", "sensor", "42", checksum=content_checksum("42"), non_text=True)
    )
    result = tree.verify_claim(Claim("c1", "answer", supports=("e1", "missing")))
    assert result["coverage"] == 0.5
    assert result["non_text"] is True


def test_empty_support_is_rejected():
    result = make_tree().verify_claim(Claim("c1", "answer", supports=()))
    assert result["reason"] == "NO_SUPPORT"


def test_root_hash_and_to_dict():
    tree = make_tree()
    first = tree.root_hash()
    assert first.startswith("sha256:")
    assert tree.to_dict()["root_hash"] == first
    assert tree.has_evidence("e1")
    assert "e1" in tree.evidence_ids()
    assert len(tree.verify_claims([Claim("c1", "x", supports=("e1",))])) == 1
