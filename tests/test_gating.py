from cams_lite.gating import GateConfig, coverage_gate, covariance_marker
from cams_lite.provenance import ProvenanceTree
from cams_lite.types import Claim, Evidence, content_checksum


def tree_with(*evidence: Evidence) -> ProvenanceTree:
    tree = ProvenanceTree()
    tree.add_many(list(evidence))
    return tree


def valid_evidence() -> Evidence:
    return Evidence("e1", "sensor", "42", checksum=content_checksum("42"))


def test_accepts_verified_claim():
    tree = tree_with(valid_evidence())
    claim = Claim("c1", "answer", supports=("e1",), confidence=0.9)
    verdict = coverage_gate([claim], tree, answer="42")
    assert verdict.determined is True
    assert verdict.status == "accept"
    assert verdict.answer == "42"
    assert verdict.contract["reason_code"] == "NO_RISK"


def test_no_claims_abstains():
    verdict = coverage_gate([], ProvenanceTree(), answer="x")
    assert verdict.determined is False
    assert verdict.contract["reason_code"] == "INSUFFICIENT_EVIDENCE"


def test_invalid_checksum_is_measurement_failure():
    bad = Evidence("e1", "sensor", "42", checksum="sha256:nope")
    verdict = coverage_gate([Claim("c1", "answer", supports=("e1",))], tree_with(bad))
    assert verdict.determined is False
    assert verdict.contract["reason_code"] == "MEASUREMENT_FAILURE"


def test_out_of_scope_has_scope_reason():
    tree = tree_with(Evidence("e1", "sensor", "42", checksum=content_checksum("42"), scope="ood"))
    verdict = coverage_gate([Claim("c1", "answer", supports=("e1",), scope="in")], tree)
    assert verdict.contract["reason_code"] == "OUT_OF_SCOPE"


def test_high_covariance_abstains():
    tree = tree_with(valid_evidence())
    claim = Claim("c1", "answer", supports=("e1",), covariance=0.9)
    verdict = coverage_gate([claim], tree)
    assert verdict.determined is False
    assert verdict.contract["reason_code"] == "MEASUREMENT_FAILURE"


def test_contract_is_external_and_complete():
    tree = tree_with(valid_evidence())
    verdict = coverage_gate([Claim("c1", "answer", supports=("e1",))], tree)
    contract = verdict.contract
    for key in (
        "contract_version",
        "reason_code",
        "evidence_coverage",
        "provenance_summary",
        "escalation_path",
        "adapter_cost",
    ):
        assert key in contract
    assert verdict.to_dict()["contract"]["reason_code"] == contract["reason_code"]


def test_covariance_marker():
    marker = covariance_marker(Claim("c1", "x", covariance=0.8))
    assert marker["marker"] == "high_covariance"
    assert marker["action"] == "short_correction"


def test_custom_adapter_cost():
    tree = tree_with(valid_evidence())
    verdict = coverage_gate(
        [Claim("c1", "answer", supports=("e1",))],
        tree,
        config=GateConfig(adapter_cost=0.01),
    )
    assert verdict.contract["adapter_cost"] == 0.01
