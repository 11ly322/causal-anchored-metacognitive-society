from cams_lite.types import Claim, Evidence, Span, canonical_json, content_checksum


def test_canonical_json_is_stable():
    assert canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'


def test_checksum_roundtrip():
    assert content_checksum("hello").startswith("sha256:")
    assert content_checksum({"b": 1, "a": 2}) == content_checksum({"a": 2, "b": 1})


def test_evidence_checksum_ok_and_to_dict():
    evidence = Evidence("e1", "sensor", "42", checksum=content_checksum("42"))
    assert evidence.checksum_ok()
    assert evidence.to_dict()["evidence_id"] == "e1"


def test_claim_and_span_serialization():
    claim = Claim("c1", "x", supports=("e1",), confidence=0.9)
    assert claim.to_dict()["supports"] == ["e1"]
    span = Span("s1", "tool", "text", receipt_id="e1", non_text=True)
    assert span.to_dict()["non_text"] is True
