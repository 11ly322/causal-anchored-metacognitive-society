import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_five_bad_examples_are_explicit():
    files = sorted((ROOT / "bench" / "bad_examples").glob("*.json"))
    assert len(files) == 5
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["why_bad"]
        assert data["expected_failure"]
        assert data["verdict"]["determined"] is True
