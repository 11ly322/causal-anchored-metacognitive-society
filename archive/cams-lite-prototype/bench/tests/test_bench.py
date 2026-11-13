import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASKS = ROOT / "bench" / "tasks"


def test_task_count_and_categories():
    files = sorted(TASKS.glob("T*.json"))
    assert len(files) == 100
    categories = {json.loads(path.read_text(encoding="utf-8"))["category"] for path in files}
    assert len(categories) == 7


def test_every_task_has_required_fields():
    for path in sorted(TASKS.glob("T*.json")):
        task = json.loads(path.read_text(encoding="utf-8"))
        assert task["id"] == path.stem
        assert task["split"] in {"dev", "test"}
        assert task["ground_truth"]["expected"] in {"accept", "abstain"}
        assert task["tool_receipts"]
        assert task["candidate"]["claims"]


def test_bad_examples_and_results_dirs_exist_or_can_be_created():
    assert (ROOT / "bench" / "bad_examples").exists()
